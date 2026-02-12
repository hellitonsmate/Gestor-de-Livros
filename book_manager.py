"""Book Manager

Gerencia uma coleção de livros com persistência em Excel ou SQLite.
Na primeira execução, o backend é configurado e salvo em
``storage_config.json``. Depois disso, o sistema sempre usa a opção
escolhida inicialmente.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, List, Optional

import pandas as pd

# Arquivos padrão (relativos a este script)
BASE_DIR = Path(__file__).resolve().parent
EXCEL_PATH = BASE_DIR / "RELAÇÃO DE LIVROS.xlsx"
SQLITE_PATH = BASE_DIR / "livros.db"
CONFIG_PATH = BASE_DIR / "storage_config.json"


@dataclass
class Book:
    """Simple data container for a book."""

    autor: str
    titulo: str
    quantidade: int = 1
    isbn: str = ""
    editora: str = ""
    ano: str = ""
    genero: str = ""

    @classmethod
    def from_series(cls, series: pd.Series) -> "Book":
        autor = str(series.get("autor", "")).strip()
        titulo = str(series.get("titulo", "")).strip()
        if pd.isna(series.get("quantidade")):
            quantidade = 1
        else:
            quantidade = int(series["quantidade"])
        isbn = str(series.get("isbn", "")).strip() if "isbn" in series else ""
        editora = str(series.get("editora", "")).strip() if "editora" in series else ""
        ano = str(series.get("ano", "")).strip() if "ano" in series else ""
        genero = str(series.get("genero", "")).strip() if "genero" in series else ""
        return cls(
            autor=autor,
            titulo=titulo,
            quantidade=quantidade,
            isbn=isbn,
            editora=editora,
            ano=ano,
            genero=genero,
        )

    def to_dict(self) -> dict:
        return asdict(self)


class ExcelStorage:
    def __init__(self, excel_path: Path):
        self.excel_path = excel_path

    def load_books(self) -> List[Book]:
        if not self.excel_path.exists():
            return []

        df = pd.read_excel(self.excel_path, header=0)
        df.columns = [str(c).lower().strip() for c in df.columns]
        col_map = {c: c for c in df.columns}
        if "livro" in col_map:
            col_map["livro"] = "titulo"

        if "autor" not in col_map or ("titulo" not in col_map and "livro" not in df.columns):
            df = pd.read_excel(self.excel_path, header=1)
            df.columns = [str(c).lower().strip() for c in df.columns]
            col_map = {c: c for c in df.columns}
            if "livro" in col_map:
                col_map["livro"] = "titulo"

        rename_dict = {}
        for original, standard in col_map.items():
            if original != standard:
                rename_dict[original] = standard
        df = df.rename(columns=rename_dict)

        known_cols = {"autor", "titulo", "livro", "isbn", "editora", "ano", "genero"}
        remaining_cols = set(df.columns) - known_cols
        if remaining_cols and "quantidade" not in df.columns:
            quantity_col = remaining_cols.pop()
            df = df.rename(columns={quantity_col: "quantidade"})

        if "quantidade" in df.columns:
            df["quantidade"] = df["quantidade"].fillna(1).astype(int)
        else:
            df["quantidade"] = 1

        return [Book.from_series(row) for _, row in df.iterrows()]

    def save_books(self, books: List[Book]) -> None:
        try:
            from openpyxl import Workbook
        except ImportError as exc:
            raise ImportError("openpyxl is required to save the Excel file") from exc

        wb = Workbook()
        ws = wb.active
        ws.append(["RELAÇÃO DE LIVROS / REMIÇÃO PELA LEITURA", "", "", "", "", "", ""])
        ws.append(["autor", "titulo", "quantidade", "isbn", "editora", "ano", "genero"])
        for book in books:
            ws.append(
                [
                    book.autor,
                    book.titulo,
                    book.quantidade,
                    book.isbn,
                    book.editora,
                    book.ano,
                    book.genero,
                ]
            )
        wb.save(self.excel_path)


class SQLiteStorage:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    autor TEXT NOT NULL,
                    titulo TEXT NOT NULL,
                    quantidade INTEGER NOT NULL DEFAULT 1,
                    isbn TEXT NOT NULL DEFAULT '',
                    editora TEXT NOT NULL DEFAULT '',
                    ano TEXT NOT NULL DEFAULT '',
                    genero TEXT NOT NULL DEFAULT ''
                )
                """
            )
            conn.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_books_titulo_nocase ON books (titulo COLLATE NOCASE)"
            )
            conn.commit()

    def load_books(self) -> List[Book]:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT autor, titulo, quantidade, isbn, editora, ano, genero FROM books ORDER BY titulo COLLATE NOCASE"
            ).fetchall()

        return [
            Book(
                autor=str(row[0]),
                titulo=str(row[1]),
                quantidade=int(row[2]),
                isbn=str(row[3]),
                editora=str(row[4]),
                ano=str(row[5]),
                genero=str(row[6]),
            )
            for row in rows
        ]

    def save_books(self, books: List[Book]) -> None:
        with self._get_conn() as conn:
            conn.execute("DELETE FROM books")
            conn.executemany(
                """
                INSERT INTO books (autor, titulo, quantidade, isbn, editora, ano, genero)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        b.autor,
                        b.titulo,
                        int(b.quantidade),
                        b.isbn,
                        b.editora,
                        b.ano,
                        b.genero,
                    )
                    for b in books
                ],
            )
            conn.commit()


def load_storage_config(config_path: Path = CONFIG_PATH) -> Optional[dict]:
    if not config_path.exists():
        return None
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None

    backend = config.get("backend")
    path = config.get("path")
    if backend not in {"excel", "sqlite"} or not isinstance(path, str):
        return None
    return {"backend": backend, "path": path}


def save_storage_config(backend: str, path: Path, config_path: Path = CONFIG_PATH) -> None:
    payload = {"backend": backend, "path": str(path)}
    config_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def create_excel_file(path: Path) -> None:
    if path.exists():
        return
    ExcelStorage(path).save_books([])


def create_sqlite_file(path: Path) -> None:
    SQLiteStorage(path)


def prompt_backend_in_terminal() -> Optional[str]:
    if not sys.stdin.isatty():
        # Ambiente não interativo: usa Excel por padrão.
        return "excel"

    print("Primeira execução: escolha a base de dados inicial.")
    print("1) Excel (cria arquivo .xlsx)")
    print("2) SQLite (cria arquivo .db)")
    while True:
        choice = input("Escolha [1/2]: ").strip()
        if choice == "1":
            return "excel"
        if choice == "2":
            return "sqlite"
        if choice.lower() in {"q", "quit", "exit"}:
            return None
        print("Opção inválida. Digite 1 ou 2.")


def ensure_storage_config(
    choice_provider: Optional[Callable[[], Optional[str]]] = None,
    config_path: Path = CONFIG_PATH,
) -> dict:
    config = load_storage_config(config_path)
    if config:
        return config

    if choice_provider is None:
        backend = "excel"
    else:
        backend = choice_provider()

    if backend not in {"excel", "sqlite"}:
        raise RuntimeError("Configuração inicial cancelada pelo usuário.")

    data_path = EXCEL_PATH if backend == "excel" else SQLITE_PATH
    if backend == "excel":
        create_excel_file(data_path)
    else:
        create_sqlite_file(data_path)

    save_storage_config(backend, data_path, config_path=config_path)
    return {"backend": backend, "path": str(data_path)}


class BookManager:
    """Handles loading, persisting and manipulating the collection of books."""

    def __init__(
        self,
        backend: Optional[str] = None,
        storage_path: Optional[Path] = None,
        auto_configure: bool = False,
        choice_provider: Optional[Callable[[], Optional[str]]] = None,
    ):
        if backend is None:
            config = load_storage_config()
            if config is None:
                if not auto_configure:
                    raise RuntimeError(
                        "Sistema não configurado. Execute a configuração inicial primeiro."
                    )
                config = ensure_storage_config(choice_provider=choice_provider)
            backend = config["backend"]
            storage_path = Path(config["path"])

        if storage_path is None:
            storage_path = EXCEL_PATH if backend == "excel" else SQLITE_PATH

        if backend == "excel":
            self.storage = ExcelStorage(Path(storage_path))
        elif backend == "sqlite":
            self.storage = SQLiteStorage(Path(storage_path))
        else:
            raise ValueError("Backend inválido. Use 'excel' ou 'sqlite'.")

        self.backend = backend
        self.storage_path = Path(storage_path)
        self.books: List[Book] = []
        self._load()

    def _load(self) -> None:
        self.books = self.storage.load_books()

    def _save(self) -> None:
        self.storage.save_books(self.books)

    # ---------------------------------------------------------------------
    # CRUD operations
    # ---------------------------------------------------------------------
    def list_books(self) -> List[Book]:
        return self.books

    def add_book(
        self,
        autor: str,
        titulo: str,
        quantidade: int = 1,
        isbn: str = "",
        editora: str = "",
        ano: str = "",
        genero: str = "",
    ) -> None:
        for book in self.books:
            if book.titulo.lower() == titulo.lower():
                book.quantidade += quantidade
                break
        else:
            self.books.append(
                Book(
                    autor=autor,
                    titulo=titulo,
                    quantidade=quantidade,
                    isbn=isbn,
                    editora=editora,
                    ano=ano,
                    genero=genero,
                )
            )
        self._save()

    def remove_book(self, titulo: str) -> bool:
        original_len = len(self.books)
        self.books = [b for b in self.books if b.titulo.lower() != titulo.lower()]
        if len(self.books) != original_len:
            self._save()
            return True
        return False

    def update_book(
        self,
        original_titulo: str,
        autor: str,
        titulo: str,
        quantidade: int,
        isbn: str = "",
        editora: str = "",
        ano: str = "",
        genero: str = "",
    ) -> bool:
        target = None
        for book in self.books:
            if book.titulo.lower() == original_titulo.lower():
                target = book
                break

        if target is None:
            return False

        for book in self.books:
            if book is target:
                continue
            if book.titulo.lower() == titulo.lower():
                return False

        target.autor = autor
        target.titulo = titulo
        target.quantidade = quantidade
        target.isbn = isbn
        target.editora = editora
        target.ano = ano
        target.genero = genero
        self._save()
        return True

    def increase_quantity(self, titulo: str, amount: int = 1) -> bool:
        for book in self.books:
            if book.titulo.lower() == titulo.lower():
                book.quantidade += amount
                self._save()
                return True
        return False

    def decrease_quantity(self, titulo: str, amount: int = 1) -> bool:
        for book in self.books:
            if book.titulo.lower() == titulo.lower():
                book.quantidade = max(0, book.quantidade - amount)
                self._save()
                return True
        return False

    def find_by_author(self, autor: str) -> List[Book]:
        return [b for b in self.books if autor.lower() in b.autor.lower()]

    def find_by_title(self, titulo: str) -> List[Book]:
        return [b for b in self.books if titulo.lower() in b.titulo.lower()]


# -------------------------------------------------------------------------
# Command-line interface
# -------------------------------------------------------------------------
def _print_books(books: List[Book]) -> None:
    if not books:
        print("Nenhum livro encontrado.")
        return
    for i, b in enumerate(books, 1):
        info_parts = [f"Autor: {b.autor}", f"Título: {b.titulo}", f"Qtd: {b.quantidade}"]
        if b.isbn:
            info_parts.append(f"ISBN: {b.isbn}")
        if b.editora:
            info_parts.append(f"Editora: {b.editora}")
        if b.ano:
            info_parts.append(f"Ano: {b.ano}")
        if b.genero:
            info_parts.append(f"Gênero: {b.genero}")
        print(f"{i}. {' | '.join(info_parts)}")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Gestor de livros")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="Lista todos os livros")

    parser_add = subparsers.add_parser("add", help="Adiciona um novo livro")
    parser_add.add_argument("autor", help="Nome do autor")
    parser_add.add_argument("titulo", help="Título do livro")
    parser_add.add_argument(
        "quantidade",
        type=int,
        nargs="?",
        default=1,
        help="Quantidade (padrão 1)",
    )
    parser_add.add_argument("--isbn", help="ISBN do livro", default="")
    parser_add.add_argument("--editora", help="Editora do livro", default="")
    parser_add.add_argument("--ano", help="Ano de publicação", default="")
    parser_add.add_argument("--genero", help="Gênero do livro", default="")

    parser_rm = subparsers.add_parser("remove", help="Remove um livro pelo título")
    parser_rm.add_argument("titulo", help="Título do livro a remover")

    parser_fa = subparsers.add_parser("find-author", help="Busca livros por nome do autor")
    parser_fa.add_argument("autor", help="Nome (ou parte) do autor")

    parser_ft = subparsers.add_parser("find-title", help="Busca livros por título")
    parser_ft.add_argument("titulo", help="Título (ou parte) a buscar")

    args = parser.parse_args(argv)
    manager = BookManager(auto_configure=True, choice_provider=prompt_backend_in_terminal)

    if args.command == "list":
        _print_books(manager.list_books())
    elif args.command == "add":
        manager.add_book(
            args.autor,
            args.titulo,
            args.quantidade,
            args.isbn,
            args.editora,
            args.ano,
            args.genero,
        )
        print("Livro adicionado com sucesso.")
    elif args.command == "remove":
        removed = manager.remove_book(args.titulo)
        if removed:
            print("Livro removido.")
        else:
            print("Livro não encontrado.")
    elif args.command == "find-author":
        _print_books(manager.find_by_author(args.autor))
    elif args.command == "find-title":
        _print_books(manager.find_by_title(args.titulo))
    else:
        parser.print_help()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
