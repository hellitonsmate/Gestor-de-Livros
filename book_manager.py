"""Book Manager

A simple command‑line application to manage a collection of books.
It can import the initial list from an Excel file (provided in the
project root) and then allows the user to list, add, remove and search
books.

Usage examples:

  python book_manager.py list
  python book_manager.py add "New Author" "New Title" 5
  python book_manager.py remove "Old Title"
  python book_manager.py find-author "Author Name"
  python book_manager.py find-title "Partial Title"

The data is stored in the Excel file ``RELAÇÃO DE LIVROS.xlsx``.  Any
changes made through the CLI are persisted back to this file.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional

import pandas as pd

# Path to the Excel file (relative to this script)
EXCEL_PATH = Path(__file__).with_name("RELAÇÃO DE LIVROS.xlsx")


@dataclass
class Book:
    """Simple data container for a book."""

    autor: str
    titulo: str
    quantidade: int = 1

    @classmethod
    def from_series(cls, series: pd.Series) -> "Book":
        # The Excel file may have column names that are not ideal – we
        # normalise them when loading.
        autor = str(series["autor"]).strip()
        titulo = str(series["titulo"]).strip()
        # ``quantidade`` may be a float (pandas default) – cast safely.
        if pd.isna(series["quantidade"]):
            quantidade = 1
        else:
            quantidade = int(series["quantidade"])
        return cls(autor=autor, titulo=titulo, quantidade=quantidade)

    def to_dict(self) -> dict:
        return asdict(self)


class BookManager:
    """Handles loading, persisting and manipulating the collection of books."""

    def __init__(self, excel_path: Path = EXCEL_PATH):
        self.excel_path = excel_path
        self.books: List[Book] = []
        self._load()

    # ---------------------------------------------------------------------
    # Persistence
    # ---------------------------------------------------------------------
    def _load(self) -> None:
        """Load books from the Excel file.

        The Excel file may either have a title row followed by a header row
        (as in the original version) **or** it may have proper column names
        in the first row (e.g. ``Autor``, ``Livro``, ``Qtd``).  This method
        attempts to read the file with a header on the first row; if the
        expected columns are not present it falls back to the original
        format (skip the title row).
        """
        if not self.excel_path.exists():
            # No file – start with an empty collection.
            self.books = []
            return

        # Try reading with the first row as header (common case).
        df = pd.read_excel(self.excel_path, header=0)
        df.columns = [str(c).lower().strip() for c in df.columns]
        # Determine which columns correspond to author, title, quantity.
        # Accept "livro" as an alias for "titulo".
        col_map = {c: c for c in df.columns}
        if "livro" in col_map:
            col_map["livro"] = "titulo"
        # Ensure we have at least author and title columns.
        if "autor" not in col_map or ("titulo" not in col_map and "livro" not in df.columns):
            # Fallback to original format where the first row is a title.
            df = pd.read_excel(self.excel_path, header=1)
            df.columns = [str(c).lower().strip() for c in df.columns]
            col_map = {c: c for c in df.columns}
        # Rename columns to standard names.
        rename_dict = {}
        for original, standard in col_map.items():
            if original != standard:
                rename_dict[original] = standard
        df = df.rename(columns=rename_dict)
        # Identify quantity column (the one that is not autor or titulo).
        expected = {"autor", "titulo"}
        quantity_col = (set(df.columns) - expected).pop()
        df = df.rename(columns={quantity_col: "quantidade"})
        # Fill missing quantities with 1 and ensure integer type.
        df["quantidade"] = df["quantidade"].fillna(1).astype(int)
        self.books = [Book.from_series(row) for _, row in df.iterrows()]

    def _save(self) -> None:
        """Persist the current list of books back to the Excel file.

        The file is written with the same three‑column layout used for the
        original import (AUTOR, TITULO, quantidade).  We keep the original
        first‑row title line for compatibility.
        """
        try:
            from openpyxl import Workbook
        except ImportError:
            raise ImportError("openpyxl is required to save the Excel file")
        wb = Workbook()
        ws = wb.active
        # Title row (first row)
        ws.append(["RELAÇÃO DE LIVROS / REMIÇÃO PELA LEITURA", "", ""])  # title row
        # Header row (second row)
        ws.append(["autor", "titulo", "quantidade"])  # header row
        # Data rows
        for book in self.books:
            ws.append([book.autor, book.titulo, book.quantidade])
        wb.save(self.excel_path)

    # ---------------------------------------------------------------------
    # CRUD operations
    # ---------------------------------------------------------------------
    def list_books(self) -> List[Book]:
        return self.books

    def add_book(self, autor: str, titulo: str, quantidade: int = 1) -> None:
        # Check if the book already exists (by title). If it does, we just
        # increase the quantity.
        for book in self.books:
            if book.titulo.lower() == titulo.lower():
                book.quantidade += quantidade
                break
        else:
            self.books.append(Book(autor=autor, titulo=titulo, quantidade=quantidade))
        self._save()

    def remove_book(self, titulo: str) -> bool:
        """Remove a book by its title.

        Returns ``True`` if a book was removed, ``False`` otherwise.
        """
        original_len = len(self.books)
        self.books = [b for b in self.books if b.titulo.lower() != titulo.lower()]
        if len(self.books) != original_len:
            self._save()
            return True
        return False

    def increase_quantity(self, titulo: str, amount: int = 1) -> bool:
        """Increase the quantity of a book identified by its title.

        Returns ``True`` if the book was found and updated, ``False`` otherwise.
        """
        for book in self.books:
            if book.titulo.lower() == titulo.lower():
                book.quantidade += amount
                self._save()
                return True
        return False

    def decrease_quantity(self, titulo: str, amount: int = 1) -> bool:
        """Decrease the quantity of a book identified by its title.

        Quantity will not go below zero. Returns ``True`` if the book was
        found and updated, ``False`` otherwise.
        """
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
# Command‑line interface
# -------------------------------------------------------------------------
def _print_books(books: List[Book]) -> None:
    if not books:
        print("Nenhum livro encontrado.")
        return
    for i, b in enumerate(books, 1):
        print(f"{i}. Autor: {b.autor} | Título: {b.titulo} | Quantidade: {b.quantidade}")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Gestor de livros")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    subparsers.add_parser("list", help="Lista todos os livros")

    # add
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

    # remove
    parser_rm = subparsers.add_parser("remove", help="Remove um livro pelo título")
    parser_rm.add_argument("titulo", help="Título do livro a remover")

    # find‑author
    parser_fa = subparsers.add_parser(
        "find-author", help="Busca livros por nome do autor"
    )
    parser_fa.add_argument("autor", help="Nome (ou parte) do autor")

    # find‑title
    parser_ft = subparsers.add_parser(
        "find-title", help="Busca livros por título"
    )
    parser_ft.add_argument("titulo", help="Título (ou parte) a buscar")

    args = parser.parse_args(argv)
    manager = BookManager()

    if args.command == "list":
        _print_books(manager.list_books())
    elif args.command == "add":
        manager.add_book(args.autor, args.titulo, args.quantidade)
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
