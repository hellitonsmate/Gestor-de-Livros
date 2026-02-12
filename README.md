# Gestor de Livros

Este é um pequeno gerenciador de livros em Python com suporte a dois tipos de persistência:

- Excel (`.xlsx`)
- SQLite (`.db`)

Na primeira execução, o sistema abre uma configuração inicial para escolher qual base usar.
A escolha é salva em `storage_config.json` e será reutilizada nas próximas execuções.

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

## Primeira execução

Ao abrir GUI/CLI/comandos pela primeira vez:

- você escolhe `Excel` ou `SQLite`
- se escolher Excel, o sistema cria `RELAÇÃO DE LIVROS.xlsx`
- se escolher SQLite, o sistema cria `livros.db`
- a decisão fica registrada em `storage_config.json`

Depois disso, o programa usa sempre o backend configurado inicialmente.
