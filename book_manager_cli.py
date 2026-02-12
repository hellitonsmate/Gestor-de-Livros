"""Shell interativo para gerenciamento de livros.

Execute:
    python book_manager_cli.py

Depois use comandos no prompt ``livros>``.
"""

from __future__ import annotations

import cmd
import shlex
from typing import List

from book_manager import BookManager, Book, prompt_backend_in_terminal


class BookManagerShell(cmd.Cmd):
    intro = (
        "Gestor de Livros (modo interativo)\n"
        "Digite 'help' para listar comandos.\n"
        "Digite 'exit' para sair."
    )
    prompt = "livros> "

    def __init__(self) -> None:
        super().__init__()
        self.manager = BookManager(
            auto_configure=True,
            choice_provider=prompt_backend_in_terminal,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _split_args(self, arg: str) -> List[str]:
        try:
            return shlex.split(arg)
        except ValueError as exc:
            print(f"Erro ao interpretar argumentos: {exc}")
            return []

    def _print_books(self, books: List[Book]) -> None:
        if not books:
            print("Nenhum livro encontrado.")
            return
        print("-" * 110)
        print(f"{'Autor':<25} {'Título':<35} {'Qtd':<4} {'ISBN':<15} {'Editora':<15} {'Ano':<6} {'Gênero':<12}")
        print("-" * 110)
        for b in books:
            print(
                f"{b.autor[:25]:<25} "
                f"{b.titulo[:35]:<35} "
                f"{b.quantidade:<4} "
                f"{b.isbn[:15]:<15} "
                f"{b.editora[:15]:<15} "
                f"{b.ano[:6]:<6} "
                f"{b.genero[:12]:<12}"
            )
        print("-" * 110)

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------
    def do_list(self, arg: str) -> None:
        """Lista todos os livros: list"""
        self._print_books(self.manager.list_books())

    def do_add(self, arg: str) -> None:
        """Adiciona livro.

        Uso:
          add "Autor" "Título" [quantidade] [isbn] [editora] [ano] [genero]
        """
        args = self._split_args(arg)
        if len(args) < 2:
            print('Uso: add "Autor" "Título" [quantidade] [isbn] [editora] [ano] [genero]')
            return
        autor, titulo = args[0], args[1]
        quantidade = 1
        if len(args) >= 3:
            try:
                quantidade = int(args[2])
            except ValueError:
                print("Quantidade deve ser inteiro.")
                return
        isbn = args[3] if len(args) >= 4 else ""
        editora = args[4] if len(args) >= 5 else ""
        ano = args[5] if len(args) >= 6 else ""
        genero = args[6] if len(args) >= 7 else ""

        self.manager.add_book(autor, titulo, quantidade, isbn, editora, ano, genero)
        print(f"Livro '{titulo}' adicionado/atualizado com sucesso.")

    def do_edit(self, arg: str) -> None:
        """Edita um livro existente.

        Uso:
          edit "titulo_original" "novo_autor" "novo_titulo" quantidade [isbn] [editora] [ano] [genero]
        """
        args = self._split_args(arg)
        if len(args) < 4:
            print('Uso: edit "titulo_original" "novo_autor" "novo_titulo" quantidade [isbn] [editora] [ano] [genero]')
            return
        original_titulo, autor, titulo = args[0], args[1], args[2]
        try:
            quantidade = int(args[3])
        except ValueError:
            print("Quantidade deve ser inteiro.")
            return
        isbn = args[4] if len(args) >= 5 else ""
        editora = args[5] if len(args) >= 6 else ""
        ano = args[6] if len(args) >= 7 else ""
        genero = args[7] if len(args) >= 8 else ""

        ok = self.manager.update_book(
            original_titulo, autor, titulo, quantidade, isbn, editora, ano, genero
        )
        if ok:
            print(f"Livro '{original_titulo}' atualizado com sucesso.")
        else:
            print("Não foi possível atualizar (livro não encontrado ou título já existente).")

    def do_remove(self, arg: str) -> None:
        """Remove livro por título.

        Uso:
          remove "Título"
        """
        args = self._split_args(arg)
        if len(args) != 1:
            print('Uso: remove "Título"')
            return
        titulo = args[0]
        if self.manager.remove_book(titulo):
            print(f"Livro '{titulo}' removido.")
        else:
            print(f"Livro '{titulo}' não encontrado.")

    def do_inc(self, arg: str) -> None:
        """Aumenta quantidade.

        Uso:
          inc "Título" [quantidade]
        """
        args = self._split_args(arg)
        if len(args) < 1:
            print('Uso: inc "Título" [quantidade]')
            return
        titulo = args[0]
        amount = 1
        if len(args) >= 2:
            try:
                amount = int(args[1])
            except ValueError:
                print("Quantidade deve ser inteiro.")
                return
        if self.manager.increase_quantity(titulo, amount):
            print("Quantidade aumentada.")
        else:
            print(f"Livro '{titulo}' não encontrado.")

    def do_dec(self, arg: str) -> None:
        """Diminui quantidade.

        Uso:
          dec "Título" [quantidade]
        """
        args = self._split_args(arg)
        if len(args) < 1:
            print('Uso: dec "Título" [quantidade]')
            return
        titulo = args[0]
        amount = 1
        if len(args) >= 2:
            try:
                amount = int(args[1])
            except ValueError:
                print("Quantidade deve ser inteiro.")
                return
        if self.manager.decrease_quantity(titulo, amount):
            print("Quantidade diminuída.")
        else:
            print(f"Livro '{titulo}' não encontrado.")

    def do_find_author(self, arg: str) -> None:
        """Busca por autor.

        Uso:
          find_author "Autor"
        """
        args = self._split_args(arg)
        if len(args) != 1:
            print('Uso: find_author "Autor"')
            return
        self._print_books(self.manager.find_by_author(args[0]))

    def do_find_title(self, arg: str) -> None:
        """Busca por título.

        Uso:
          find_title "Título"
        """
        args = self._split_args(arg)
        if len(args) != 1:
            print('Uso: find_title "Título"')
            return
        self._print_books(self.manager.find_by_title(args[0]))

    def do_help_cmds(self, arg: str) -> None:
        """Mostra comandos principais: help_cmds"""
        print("Comandos: list, add, edit, remove, inc, dec, find_author, find_title, exit")
        print('Exemplo: add "Machado de Assis" "Dom Casmurro" 2')

    def do_exit(self, arg: str) -> bool:
        """Sai do shell: exit"""
        print("Saindo.")
        return True

    def do_quit(self, arg: str) -> bool:
        """Sai do shell: quit"""
        return self.do_exit(arg)

    def do_EOF(self, arg: str) -> bool:  # Ctrl+D
        print()
        return self.do_exit(arg)

    def emptyline(self) -> None:
        # Evita repetir o último comando ao apertar Enter em branco.
        return


def main() -> None:
    BookManagerShell().cmdloop()


if __name__ == "__main__":
    main()
