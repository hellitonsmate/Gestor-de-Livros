"""Tkinter GUI for the Book Manager.

Provides a simple graphical interface to list, add, remove, increase/decrease
quantity and search books. It re‑uses the :class:`BookManager` implementation
from ``book_manager.py``.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from pathlib import Path

# Import the core manager
from book_manager import BookManager, Book


class BookManagerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de Livros")
        self.geometry("800x600")

        self.manager = BookManager()

        self.create_widgets()
        self.refresh_list()

    # ---------------------------------------------------------------------
    # UI construction
    # ---------------------------------------------------------------------
    def create_widgets(self):
        # Top frame – controls for add / remove
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(control_frame, text="Autor:").grid(row=0, column=0, sticky=tk.W)
        self.author_entry = ttk.Entry(control_frame, width=20)
        self.author_entry.grid(row=0, column=1, padx=5)

        ttk.Label(control_frame, text="Título:").grid(row=0, column=2, sticky=tk.W)
        self.title_entry = ttk.Entry(control_frame, width=30)
        self.title_entry.grid(row=0, column=3, padx=5)

        ttk.Label(control_frame, text="Qtd:").grid(row=0, column=4, sticky=tk.W)
        self.qty_entry = ttk.Entry(control_frame, width=5)
        self.qty_entry.grid(row=0, column=5, padx=5)
        self.qty_entry.insert(0, "1")

        ttk.Button(control_frame, text="Adicionar", command=self.add_book).grid(row=0, column=6, padx=5)
        ttk.Button(control_frame, text="Remover", command=self.remove_book).grid(row=0, column=7, padx=5)
        ttk.Button(control_frame, text="+ Qtd", command=self.increase_quantity).grid(row=0, column=8, padx=5)
        ttk.Button(control_frame, text="- Qtd", command=self.decrease_quantity).grid(row=0, column=9, padx=5)

        # Search frame
        search_frame = ttk.LabelFrame(self, text="Buscar")
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(search_frame, text="Autor:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.search_author = ttk.Entry(search_frame, width=20)
        self.search_author.grid(row=0, column=1, padx=5)
        ttk.Button(search_frame, text="Buscar", command=self.search_by_author).grid(row=0, column=2, padx=5)

        ttk.Label(search_frame, text="Título:").grid(row=0, column=3, sticky=tk.W, padx=5)
        self.search_title = ttk.Entry(search_frame, width=30)
        self.search_title.grid(row=0, column=4, padx=5)
        ttk.Button(search_frame, text="Buscar", command=self.search_by_title).grid(row=0, column=5, padx=5)

        # Listbox to display books
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.book_list = tk.Listbox(list_frame, font=("Courier", 10))
        self.book_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.book_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.book_list.config(yscrollcommand=scrollbar.set)

    # ---------------------------------------------------------------------
    # Helper methods
    # ---------------------------------------------------------------------
    def refresh_list(self, books=None):
        """Refresh the listbox with the given books or all books if None."""
        self.book_list.delete(0, tk.END)
        if books is None:
            books = self.manager.list_books()
        for b in books:
            line = f"Autor: {b.autor:<30} | Título: {b.titulo:<40} | Qtd: {b.quantidade}"
            self.book_list.insert(tk.END, line)

    def get_selected_title(self):
        """Return the title of the currently selected list item, or None."""
        try:
            selection = self.book_list.curselection()[0]
            line = self.book_list.get(selection)
            # The line format is fixed; split on '|'
            parts = line.split("|")
            title_part = parts[1]  # " Título: ... "
            title = title_part.split(":", 1)[1].strip()
            return title
        except Exception:
            return None

    # ---------------------------------------------------------------------
    # Command callbacks
    # ---------------------------------------------------------------------
    def add_book(self):
        autor = self.author_entry.get().strip()
        titulo = self.title_entry.get().strip()
        try:
            quantidade = int(self.qty_entry.get())
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser um número inteiro.")
            return
        if not autor or not titulo:
            messagebox.showerror("Erro", "Autor e Título são obrigatórios.")
            return
        self.manager.add_book(autor, titulo, quantidade)
        self.refresh_list()
        self.author_entry.delete(0, tk.END)
        self.title_entry.delete(0, tk.END)
        self.qty_entry.delete(0, tk.END)
        self.qty_entry.insert(0, "1")

    def remove_book(self):
        titulo = self.get_selected_title()
        if not titulo:
            messagebox.showwarning("Aviso", "Selecione um livro na lista para remover.")
            return
        if self.manager.remove_book(titulo):
            self.refresh_list()
        else:
            messagebox.showerror("Erro", f"Livro '{titulo}' não encontrado.")

    def increase_quantity(self):
        titulo = self.get_selected_title()
        if not titulo:
            messagebox.showwarning("Aviso", "Selecione um livro para aumentar a quantidade.")
            return
        amount = simpledialog.askinteger("Aumentar", "Quantos a mais?", minvalue=1, initialvalue=1)
        if amount:
            self.manager.increase_quantity(titulo, amount)
            self.refresh_list()

    def decrease_quantity(self):
        titulo = self.get_selected_title()
        if not titulo:
            messagebox.showwarning("Aviso", "Selecione um livro para diminuir a quantidade.")
            return
        amount = simpledialog.askinteger("Diminuir", "Quantos a menos?", minvalue=1, initialvalue=1)
        if amount:
            self.manager.decrease_quantity(titulo, amount)
            self.refresh_list()

    def search_by_author(self):
        autor = self.search_author.get().strip()
        if not autor:
            self.refresh_list()
            return
        results = self.manager.find_by_author(autor)
        self.refresh_list(results)

    def search_by_title(self):
        titulo = self.search_title.get().strip()
        if not titulo:
            self.refresh_list()
            return
        results = self.manager.find_by_title(titulo)
        self.refresh_list(results)


if __name__ == "__main__":
    app = BookManagerGUI()
    app.mainloop()
