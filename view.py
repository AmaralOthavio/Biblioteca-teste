from flask import Flask, jsonify
from main import app, con


@app.route('/livros', methods=['GET'])
def livro():
    cur = con.cursor()
    cur.execute("SELECT ID_LIVRO, TITULO, AUTOR, ANO_PUBLICACAO FROM LIVROS")
    livros = cur.fetchall()
    livros_dic = []
    for livro in livros:
        livros_dic.append({
            'id_livro':livro[0],
            'titulo': livro[1],
            'autor': livro[2],
            'ano_publicacao': livro[3]
        })
    return jsonify(livros=livros_dic, mensagem='Lista de livros')
