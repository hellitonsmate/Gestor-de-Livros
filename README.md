# Gestor de Livros

Este é um pequeno gerenciador de livros em Python que lê os dados de um arquivo Excel (`RELAÇÃO DE LIVROS.xlsx`) e permite operações via linha de comando:

- **list** – lista todos os livros
- **add "Autor" "Título" [quantidade]** – adiciona um novo livro (ou aumenta a quantidade se o título já existir)
- **remove "Título"** – remove um livro pelo título
- **find-author "Autor"** – busca livros por nome do autor (ou parte dele)
- **find-title "Título"** – busca livros por título (ou parte dele)

## Dependências

```bash
pip install -r requirements.txt
```

## Uso

### Linha de comando
```bash
python book_manager.py list
python book_manager.py add "Novo Autor" "Novo Título" 2
python book_manager.py find-author "Autor"
```

### Interface gráfica
```bash
python book_manager_gui.py
```

### Shell interativo (CLI)
```bash
python book_manager_cli.py
```

No prompt `livros>`, use comandos como:

```text
list
add "Machado de Assis" "Dom Casmurro" 2
edit "Dom Casmurro" "Machado de Assis" "Dom Casmurro (Edição Nova)" 3
remove "Dom Casmurro (Edição Nova)"
inc "Memórias Póstumas de Brás Cubas" 1
dec "Memórias Póstumas de Brás Cubas" 1
find_author "Machado"
find_title "Casmurro"
exit
```

Os dados são persistidos no mesmo arquivo Excel.


```bash
python book_manager.py list
python book_manager.py add "Novo Autor" "Novo Título" 2
python book_manager.py find-author "Autor" 
```

Os dados são persistidos de volta ao mesmo arquivo Excel.
