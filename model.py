import fdb


class Livros:
    def __init__(self, id_livro, titulo, autor, ano_publicacao):
        self.id_livro = id_livro
        self.titulo = titulo
        self.autor = autor
        self.ano_publicacao = ano_publicacao


class Usuarios:
    def __init__(self, id_usuario, nome, senha, email):
        self.id_usuario = id_usuario
        self.nome = nome
        self.senha = senha
        self.email = email
