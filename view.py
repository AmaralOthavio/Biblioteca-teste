import jwt
import os
from flask import jsonify, request, send_file
from flask_bcrypt import generate_password_hash, check_password_hash
from fpdf import FPDF
from main import app, con

senha_secreta = app.config['SECRET_KEY']


def generate_token(user_id):
    payload = {"id_usuario": user_id}
    token = jwt.encode(payload, senha_secreta, algorithm='HS256')
    return token


def remover_bearer(token):
    if token.startswith("Bearer "):
        return token[len("Bearer "):]
    else:
        return token


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


@app.route('/livros/relatorio', methods=['GET'])
def gerar_relatorio():
    cursor = con.cursor()
    cursor.execute("SELECT id_livro, titulo, autor, ano_publicacao FROM livros")
    livros = cursor.fetchall()
    cursor.close()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "Relatorio de Livros", ln=True, align='C')
    pdf.ln(5)  # Espaço entre o título e a linha
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())  # Linha abaixo do título
    pdf.ln(5)  # Espaço após a linha

    pdf.set_font("Arial", size=12)
    for livro in livros:
        pdf.cell(200, 10, f"ID: {livro[0]} - {livro[1]} - {livro[2]} - {livro[3]}", ln=True)

    contador_livros = len(livros)
    pdf.ln(10)  # Espaço antes do contador
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, f"Total de livros cadastrados: {contador_livros}", ln=True, align='C')

    pdf_path = "relatorio_livros.pdf"
    pdf.output(pdf_path)

    return send_file(pdf_path, as_attachment=True, mimetype='application/pdf')


@app.route('/livro', methods=['POST'])
def livro_post():

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'mensagem': 'Token de autenticação necessário'}), 401
    token = remover_bearer(token)
    try:
        payload = jwt.decode(token, senha_secreta, algorithms=['HS256'])
        id_usuario = payload['id_usuario']
    except jwt.ExpiredSignatureError:
        return jsonify({'mensagem': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'mensagem': 'Token inválido'}), 401

    data = request.form.to_dict()

    imagem = request.files.get('imagem')  # Arquivo enviado
    titulo = data.get('titulo')
    autor = data.get('autor')
    ano_publicacao = data.get('ano_publicacao')

    cur = con.cursor()
    cur.execute("SELECT 1 FROM LIVROS WHERE TITULO = ?", (titulo,))

    if cur.fetchone():
        return jsonify('Livro já cadastrado')

    cur.execute("INSERT INTO LIVROS (TITULO,AUTOR, ANO_PUBLICACAO) VALUES (?, ?, ?) RETURNING ID_LIVRO", (titulo, autor, ano_publicacao))
    livro_id = cur.fetchone()[0]

    con.commit()
    cur.close()

    if imagem:
        nome_imagem = f"{livro_id}.jpeg"
        pasta_destino = os.path.join(app.config['UPLOAD_FOLDER'], "Livros")
        os.makedirs(pasta_destino, exist_ok=True)
        imagem_path = os.path.join(pasta_destino, nome_imagem)
        imagem.save(imagem_path)

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


@app.route('/livro/<int:id_livro>', methods=['DELETE'])
def deletar_livro(id_livro):
    cursor = con.cursor()

    cursor.execute("SELECT 1 FROM livros WHERE ID_LIVRO = ?", (id_livro,))
    if not cursor.fetchone():
        cursor.close()
        return jsonify({"error": "Livro não encontrado"}), 404

    cursor.execute("DELETE FROM livros WHERE ID_LIVRO = ?", (id_livro,))
    con.commit()
    cursor.close()

    return jsonify({
        'message': "Livro excluído com sucesso!",
        'id_livro': id_livro
    })

# Rotas de usuário a partir daqui


@app.route('/usuarios', methods=['GET'])
def trazer_usuarios():
    cur = con.cursor()
    cur.execute("SELECT ID_USUARIO, NOME, EMAIL, SENHA FROM USUARIOS")
    usuarios = cur.fetchall()
    usuarios_dic = []
    for usuario in usuarios:
        usuarios_dic.append({
            'id_usuario': usuario[0],
            'nome': usuario[1],
            'email': usuario[2],
            'senha': usuario[3]
        })
    return jsonify(usuarios=usuarios_dic, mensagem='Lista de usuários')


@app.route('/usuario', methods=['POST'])
def inserir_usuario():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    # Validações de senha
    simbolos = ['!', '@', '#', '$', '%', '¨', '&', '*', '(', ')', '-', '_', '+', '=', '§', '"', "'",
                '|', ':', ';', '?', '°', '<', '>', '{', '}', '[', ']', ',', '.', '*', '~', '´', '`',
                'º', 'ª', '/', '^', '¹', '²', '³', '£', '¢', '¬']
    numeros = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
    numeros_usados = 0
    simbolos_usados = 0
    for simbolo in simbolos:
        if simbolo in senha:
            simbolos_usados += 1
    for numero in numeros:
        if numero in senha:
            numeros_usados += 1

    if len(senha) < 8:
        return jsonify(mensagem='Erro: A senha precisa ter pelo menos 8 caracteres')
    if simbolos_usados < 1:
        return jsonify(mensagem='Erro: A senha precisa ter pelo menos 1 símbolo do seu teclado')
    if numeros_usados < 1:
        return jsonify(mensagem='Erro: A senha precisa ter pelo menos um número')
    # Fim das validações de senha

    cur = con.cursor()
    cur.execute("SELECT 1 FROM USUARIOS WHERE email = ?", (email,))

    if cur.fetchone():
        return jsonify(mensagem='Este e-mail já possui uma conta')

    senha = generate_password_hash(senha).decode("utf-8")

    cur.execute("INSERT INTO USUARIOS(NOME, EMAIL, SENHA) VALUES (?, ?, ?)", (nome, email, senha))

    con.commit()
    cur.close()

    return jsonify({
        'mensagem': 'Usuário cadastrado com sucesso',
        'usuario': {
            'nome': nome,
            'email': email,
            'senha': senha
        }
    })


@app.route('/usuario/<int:id_usuario>', methods=['PUT'])
def editar_usuario(id_usuario):
    cur = con.cursor()
    cur.execute("SELECT ID_USUARIO, NOME, EMAIL, SENHA FROM USUARIOS WHERE ID_USUARIO = ?", (id_usuario, ))
    usuario_data = cur.fetchone()

    if not usuario_data:
        cur.close()
        return jsonify(mensagem="Usuário não foi encontrado")

    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    # Validações de senha
    simbolos = ['!', '@', '#', '$', '%', '¨', '&', '*', '(', ')', '-', '_', '+', '=', '§', '"', "'",
                '|', ':', ';', '?', '°', '<', '>', '{', '}', '[', ']', ',', '.', '*', '~', '´', '`',
                'º', 'ª', '/', '^', '¹', '²', '³', '£', '¢', '¬']
    numeros = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
    numeros_usados = 0
    simbolos_usados = 0
    for simbolo in simbolos:
        if simbolo in senha:
            simbolos_usados += 1
    for numero in numeros:
        if numero in senha:
            numeros_usados += 1

    if len(senha) < 8:
        cur.close()
        return jsonify(mensagem='Erro: A senha precisa ter pelo menos 8 caracteres')
    if simbolos_usados < 1:
        cur.close()
        return jsonify(mensagem='Erro: A senha precisa ter pelo menos 1 símbolo do seu teclado')
    if numeros_usados < 1:
        cur.close()
        return jsonify(mensagem='Erro: A senha precisa ter pelo menos um número')
    # Fim das validações de senha

    cur.execute("UPDATE USUARIOS SET NOME = ?, EMAIL = ?, SENHA = ? WHERE ID_USUARIO = ?",
                (nome, email, senha, id_usuario))
    con.commit()
    cur.close()

    return jsonify({
        'message': 'Usuário editado com sucesso!',
        'livro': {
            'nome': nome,
            'email': email,
            'senha': senha
        }
    })


@app.route('/usuario/<int:id_usuario>', methods=['DELETE'])
def deletar_usuario(id_usuario):
    cursor = con.cursor()

    cursor.execute("SELECT 1 FROM USUARIOS WHERE ID_USUARIO = ?", (id_usuario,))
    if not cursor.fetchone():
        cursor.close()
        return jsonify({"error": "Usuário não encontrado"}), 404

    cursor.execute("DELETE FROM USUARIOS WHERE ID_USUARIO = ?", (id_usuario,))
    con.commit()
    cursor.close()

    return jsonify({
        'message': "Usuário excluído com sucesso!",
        'id_livro': id_usuario
    })


@app.route('/login', methods=['POST'])
def efetuar_login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    cur = con.cursor()

    # pegar a senha criptografada baseada no email digitado
    cur.execute('SELECT SENHA, ID_USUARIO FROM USUARIOS WHERE EMAIL = ?', (email,))
    resultado = cur.fetchone()
    senha_criptografada = resultado[0]
    id_usuario = resultado[1]

    if check_password_hash(senha_criptografada, senha):
        token = generate_token(id_usuario)
        return jsonify({"mensagem": 'Login efetuado com sucesso', "token": token}), 200
    
    return jsonify(mensagem="Login falhado, usuário ou senha incorretos")
