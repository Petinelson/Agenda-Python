from flask import Flask, request, redirect, url_for, render_template, session, flash
from flask_session import Session
import os
import uuid

load_dotenv()

app = Flask(__name__)
app.secret_key = 'chave_secreta'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

caminho_base = os.path.dirname(__file__)
caminho_login_txt = os.path.join(caminho_base, 'modules', 'login.txt')
caminho_pessoas_txt = os.path.join(caminho_base, 'modules', 'pessoas.txt')

def verificar_e_criar_arquivos():
    for caminho in [caminho_login_txt, caminho_pessoas_txt]:
        if not os.path.exists(caminho):
            with open(caminho, 'a') as f:
                pass

verificar_e_criar_arquivos()

def verificar_credenciais(username, password):
    with open(caminho_login_txt, 'r') as f:
        for line in f:
            usuario, senha = line.strip().split(',')
            if usuario == username and senha == password:
                return True
    return False

@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        id_unico = str(uuid.uuid4())
        with open(caminho_pessoas_txt, 'a') as arquivo:
            arquivo.write(f"{id_unico},{nome},{email}\n")
        flash('Pessoa adicionada com sucesso!')
        return redirect(url_for('index'))
    return render_template('adicionar.html')

@app.route('/deletar/<id_unico>')
def deletar(id_unico):
    pessoas_novas = []
    with open(caminho_pessoas_txt, 'r') as arquivo:
        for linha in arquivo:
            partes = linha.strip().split(',')
            if partes[0] != id_unico:
                pessoas_novas.append(linha)
    with open(caminho_pessoas_txt, 'w') as arquivo:
        arquivo.writelines(pessoas_novas)
    flash('Pessoa deletada com sucesso!')
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if verificar_credenciais(username, password):
            session['usuario_logado'] = username
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario_logado', None)
    return redirect(url_for('login'))

def obter_pessoas():
    pessoas = []
    with open(caminho_pessoas_txt, 'r') as arquivo:
        for linha in arquivo:
            partes = linha.strip().split(',')
            if len(partes) == 3:
                id_unico, nome, email = partes
                pessoas.append({'id': id_unico, 'nome': nome, 'email': email})
            else:
                print(f"Linha mal formatada: {linha}")
    return pessoas

@app.route('/')
def index():
    if 'usuario_logado' not in session:
        return redirect(url_for('login'))
    username = session['usuario_logado']
    pessoas = obter_pessoas()
    return render_template('index.html', pessoas=pessoas, username=username)

@app.context_processor
def injetar_username():
    return dict(username=session.get('usuario_logado'))

if __name__ == '__main__':
    """app.run(debug=True, host='0.0.0.0')"""
