"""Tkinter GUI for the Book Manager.

Provides a simple graphical interface to list, add, remove, increase/decrease
quantity and search books. It re‑uses the :class:`BookManager` implementation
from ``book_manager.py``.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# Import the core manager
from book_manager import BookManager
from style import apply_style, COLORS, FONTS


class BookManagerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de Livros")
        self.geometry("1180x700")
        self.minsize(980, 620)

        # Aplica tema / estilos globais
        self.style = apply_style(self)
        self.configure(bg=COLORS["bg"])

        self.manager = BookManager()
        self.selected_original_title = None

        self.create_widgets()
        self.refresh_list()

    # ---------------------------------------------------------------------
    # UI construction
    # ---------------------------------------------------------------------
    def create_widgets(self):
        # Frame principal para dar margem e fundo consistente
        main_frame = ttk.Frame(self, style="Main.TFrame", padding=(10, 10, 10, 10))
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top frame – controls for add / remove
        control_frame = ttk.LabelFrame(main_frame, text="Cadastro e edição", style="Panel.TLabelframe")
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Primeira linha
        ttk.Label(control_frame, text="Autor:", style="Panel.TLabel").grid(row=0, column=0, sticky=tk.W, padx=(8, 4), pady=(8, 2))
        self.author_entry = ttk.Entry(control_frame, width=24)
        self.author_entry.grid(row=0, column=1, padx=(0, 10), pady=(8, 2), sticky="ew")

        ttk.Label(control_frame, text="Título:", style="Panel.TLabel").grid(row=0, column=2, sticky=tk.W, padx=(0, 4), pady=(8, 2))
        self.title_entry = ttk.Entry(control_frame, width=34)
        self.title_entry.grid(row=0, column=3, padx=(0, 10), pady=(8, 2), sticky="ew")

        ttk.Label(control_frame, text="Qtd:", style="Panel.TLabel").grid(row=0, column=4, sticky=tk.W, padx=(0, 4), pady=(8, 2))
        self.qty_entry = ttk.Entry(control_frame, width=8)
        self.qty_entry.grid(row=0, column=5, padx=(0, 8), pady=(8, 2), sticky="w")
        self.qty_entry.insert(0, "1")

        # Segunda linha - campos adicionais
        ttk.Label(control_frame, text="ISBN:", style="Panel.TLabel").grid(row=1, column=0, sticky=tk.W, padx=(8, 4), pady=(4, 2))
        self.isbn_entry = ttk.Entry(control_frame, width=20)
        self.isbn_entry.grid(row=1, column=1, padx=(0, 10), pady=(4, 2), sticky="ew")

        ttk.Label(control_frame, text="Editora:", style="Panel.TLabel").grid(row=1, column=2, sticky=tk.W, padx=(0, 4), pady=(4, 2))
        self.editora_entry = ttk.Entry(control_frame, width=20)
        self.editora_entry.grid(row=1, column=3, padx=(0, 10), pady=(4, 2), sticky="ew")

        ttk.Label(control_frame, text="Ano:", style="Panel.TLabel").grid(row=1, column=4, sticky=tk.W, padx=(0, 4), pady=(4, 2))
        self.ano_entry = ttk.Entry(control_frame, width=10)
        self.ano_entry.grid(row=1, column=5, padx=(0, 8), pady=(4, 2), sticky="w")

        ttk.Label(control_frame, text="Gênero:", style="Panel.TLabel").grid(row=1, column=6, sticky=tk.W, padx=(0, 4), pady=(4, 2))
        self.genero_entry = ttk.Entry(control_frame, width=22)
        self.genero_entry.grid(row=1, column=7, padx=(0, 8), pady=(4, 2), sticky="ew")

        # Terceira linha - botões de ação
        actions_frame = ttk.Frame(control_frame, style="Panel.TFrame")
        actions_frame.grid(row=2, column=0, columnspan=8, sticky="ew", padx=8, pady=(8, 8))
        actions_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        ttk.Button(actions_frame, text="Adicionar", style="Primary.TButton", command=self.add_book).grid(row=0, column=0, padx=4, sticky="ew")
        ttk.Button(actions_frame, text="Salvar edição", style="Primary.TButton", command=self.update_book).grid(row=0, column=1, padx=4, sticky="ew")
        ttk.Button(actions_frame, text="Limpar", command=self.clear_form).grid(row=0, column=2, padx=4, sticky="ew")
        ttk.Button(actions_frame, text="Remover", style="Danger.TButton", command=self.remove_book).grid(row=0, column=3, padx=4, sticky="ew")
        ttk.Button(actions_frame, text="+ Qtd", command=self.increase_quantity).grid(row=0, column=4, padx=4, sticky="ew")
        ttk.Button(actions_frame, text="- Qtd", command=self.decrease_quantity).grid(row=0, column=5, padx=4, sticky="ew")

        control_frame.grid_columnconfigure(1, weight=2)
        control_frame.grid_columnconfigure(3, weight=3)
        control_frame.grid_columnconfigure(7, weight=2)

        # Search frame
        search_frame = ttk.LabelFrame(main_frame, text="Buscar", style="Panel.TLabelframe")
        search_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(search_frame, text="Autor:", style="Panel.TLabel").grid(row=0, column=0, sticky=tk.W, padx=(8, 4), pady=8)
        self.search_author = ttk.Entry(search_frame, width=20)
        self.search_author.grid(row=0, column=1, padx=(0, 8), pady=8, sticky="ew")
        ttk.Button(search_frame, text="Buscar autor", command=self.search_by_author).grid(row=0, column=2, padx=(0, 8), pady=8, sticky="ew")

        ttk.Label(search_frame, text="Título:", style="Panel.TLabel").grid(row=0, column=3, sticky=tk.W, padx=(0, 4), pady=8)
        self.search_title = ttk.Entry(search_frame, width=30)
        self.search_title.grid(row=0, column=4, padx=(0, 8), pady=8, sticky="ew")
        ttk.Button(search_frame, text="Buscar título", command=self.search_by_title).grid(row=0, column=5, padx=(0, 8), pady=8, sticky="ew")

        search_frame.grid_columnconfigure(1, weight=2)
        search_frame.grid_columnconfigure(4, weight=3)

        # Título da lista
        header_frame = ttk.Frame(main_frame, style="Main.TFrame")
        header_frame.pack(fill=tk.X, pady=(4, 0))
        ttk.Label(header_frame, text="Livros cadastrados", style="Section.TLabel").pack(anchor=tk.W)

        # Tabela para exibir livros
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        columns = ("autor", "titulo", "quantidade", "isbn", "editora", "ano", "genero")
        self.book_list = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            style="Books.Treeview",
        )
        self.book_list.heading("autor", text="Autor")
        self.book_list.heading("titulo", text="Título")
        self.book_list.heading("quantidade", text="Qtd")
        self.book_list.heading("isbn", text="ISBN")
        self.book_list.heading("editora", text="Editora")
        self.book_list.heading("ano", text="Ano")
        self.book_list.heading("genero", text="Gênero")

        self.book_list.column("autor", width=220, anchor=tk.W, stretch=True)
        self.book_list.column("titulo", width=320, anchor=tk.W, stretch=True)
        self.book_list.column("quantidade", width=70, anchor=tk.CENTER, stretch=False)
        self.book_list.column("isbn", width=140, anchor=tk.W, stretch=True)
        self.book_list.column("editora", width=180, anchor=tk.W, stretch=True)
        self.book_list.column("ano", width=80, anchor=tk.CENTER, stretch=False)
        self.book_list.column("genero", width=150, anchor=tk.W, stretch=True)

        scrollbar_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.book_list.yview)
        scrollbar_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.book_list.xview)
        self.book_list.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.book_list.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        self.book_list.tag_configure("odd", background="#f7fafc")
        self.book_list.tag_configure("even", background="#ffffff")

        self.book_list.bind("<<TreeviewSelect>>", self.on_book_select)

    # ---------------------------------------------------------------------
    # Helper methods
    # ---------------------------------------------------------------------
    def refresh_list(self, books=None):
        """Refresh the table with the given books or all books if None."""
        self.book_list.delete(*self.book_list.get_children())
        if books is None:
            books = self.manager.list_books()
        for b in books:
            index = len(self.book_list.get_children())
            tag = "even" if index % 2 == 0 else "odd"
            self.book_list.insert(
                "",
                tk.END,
                values=(
                    b.autor,
                    b.titulo,
                    b.quantidade,
                    b.isbn,
                    b.editora,
                    b.ano,
                    b.genero,
                ),
                tags=(tag,),
            )
        self.selected_original_title = None

    def get_selected_title(self):
        """Return the title of the currently selected table item, or None."""
        item_id = self.book_list.focus()
        if not item_id:
            return None
        values = self.book_list.item(item_id, "values")
        if not values:
            return None
        return values[1]

    def clear_form(self):
        self.author_entry.delete(0, tk.END)
        self.title_entry.delete(0, tk.END)
        self.qty_entry.delete(0, tk.END)
        self.qty_entry.insert(0, "1")
        self.isbn_entry.delete(0, tk.END)
        self.editora_entry.delete(0, tk.END)
        self.ano_entry.delete(0, tk.END)
        self.genero_entry.delete(0, tk.END)
        self.selected_original_title = None

    def on_book_select(self, _event=None):
        item_id = self.book_list.focus()
        if not item_id:
            return
        values = self.book_list.item(item_id, "values")
        if len(values) < 7:
            return

        autor, titulo, quantidade, isbn, editora, ano, genero = values
        self.author_entry.delete(0, tk.END)
        self.author_entry.insert(0, autor)
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, titulo)
        self.qty_entry.delete(0, tk.END)
        self.qty_entry.insert(0, str(quantidade))
        self.isbn_entry.delete(0, tk.END)
        self.isbn_entry.insert(0, isbn)
        self.editora_entry.delete(0, tk.END)
        self.editora_entry.insert(0, editora)
        self.ano_entry.delete(0, tk.END)
        self.ano_entry.insert(0, ano)
        self.genero_entry.delete(0, tk.END)
        self.genero_entry.insert(0, genero)

        self.selected_original_title = titulo

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
        self.manager.add_book(
            autor,
            titulo,
            quantidade,
            self.isbn_entry.get().strip(),
            self.editora_entry.get().strip(),
            self.ano_entry.get().strip(),
            self.genero_entry.get().strip(),
        )
        self.refresh_list()
        self.clear_form()

    def update_book(self):
        if not self.selected_original_title:
            messagebox.showwarning("Aviso", "Selecione um livro na tabela para editar.")
            return

        autor = self.author_entry.get().strip()
        titulo = self.title_entry.get().strip()
        isbn = self.isbn_entry.get().strip()
        editora = self.editora_entry.get().strip()
        ano = self.ano_entry.get().strip()
        genero = self.genero_entry.get().strip()
        try:
            quantidade = int(self.qty_entry.get())
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser um número inteiro.")
            return

        if not autor or not titulo:
            messagebox.showerror("Erro", "Autor e Título são obrigatórios.")
            return

        updated = self.manager.update_book(
            self.selected_original_title,
            autor,
            titulo,
            quantidade,
            isbn,
            editora,
            ano,
            genero,
        )
        if not updated:
            messagebox.showerror(
                "Erro",
                "Não foi possível atualizar. Verifique se o título já existe.",
            )
            return

        self.refresh_list()
        self.clear_form()

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
