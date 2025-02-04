from flask import Flask, jsonify, request
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


@app.route('/livro', methods=['POST'])
def livro_post():
    data = request.get_json()
    titulo = data.get('titulo')
    autor = data.get('autor')
    ano_publicacao = data.get('ano_publicacao')

    cur = con.cursor()
    cur.execute("SELECT 1 FROM LIVROS WHERE TITULO = ?", (titulo,))

    if cur.fetchone():
        return jsonify('Livro já cadastrado')

    cur.execute("INSERT INTO LIVROS(TITULO,AUTOR, ANO_PUBLICACAO) VALUES (?, ?, ?)", (titulo, autor, ano_publicacao))

    con.commit()
    cur.close()

    return jsonify({
        'mensagem': 'Livro cadastrado com sucesso',
        'livro': {
            'titulo': titulo,
            'autor': autor,
            'ano_publicacao': ano_publicacao
        }
    })


@app.route('/livro/<int:id_livro>', methods=['PUT'])
def livro_put(id_livro):
    cur = con.cursor()
    cur.execute("SELECT ID_LIVRO, TITULO, AUTOR, ANO_PUBLICACAO FROM LIVROS WHERE ID_LIVRO = ?", (id_livro, ))
    livro_data = cur.fetchone()

    if not livro_data:
        cur.close()
        return jsonify(mensagem="Livro não foi encontrado")

    data = request.get_json()
    titulo = data.get('titulo')
    autor = data.get('autor')
    ano_publicacao = data.get('ano_publicacao')

    cur.execute("UPDATE LIVROS SET TITULO = ?, AUTOR = ?, ANO_PUBLICACAO = ? WHERE ID_LIVRO = ?",
                (titulo, autor, ano_publicacao, id_livro))
    con.commit()
    con.close()

    return jsonify({
        'message': 'Livro editado com sucesso!',
        'livro': {
            'titulo': titulo,
            'autor': autor,
            'ano_publicacao': ano_publicacao
        }
    })