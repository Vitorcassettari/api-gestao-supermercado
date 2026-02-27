import pymysql
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
import os
from datetime import timedelta

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2) # Demora 2 horas para expirar
jwt = JWTManager(app)

config = {
    'host': os.getenv('db_host'),
    'user': os.getenv('db_user'),
    'password': os.getenv('db_password'),
    'database': os.getenv('db_name'),
    'cursorclass': pymysql.cursors.DictCursor,
    'port': os.getenv('db_port'),
    'ssl': {'ssl': {}}
}

def conectar_banco():
    conexao = pymysql.connect(**config)
    cursor = conexao.cursor()
    return conexao, cursor



def verificar_admin(id_escondido):
    conexao, cursor = conectar_banco()

    sql = 'SELECT permissoes FROM CLIENTES WHERE id = %s'
    cursor.execute(sql, (id_escondido,))
    usuario_banco = cursor.fetchone()

    conexao.close()

    if not usuario_banco: return jsonify({'erro':'Usuário não encontrado!'}),400

    if usuario_banco['permissoes'] != 'admin': return jsonify({'erro': 'Acesso Negado 403: Apenas administradores podem alterar o estoque!'}), 403

    return None


#========================================================================LOGIN=============================================================================
@app.route('/login',methods=['POST'])
def verificar_login():
    conexao,cursor = conectar_banco()

    data = request.get_json()

    sql = 'SELECT id, password, permissoes FROM CLIENTES WHERE EMAIL = %s'
    valores = (data['email'],)

    cursor.execute(sql, valores)
    resultado = cursor.fetchone()

    conexao.close()

    if not resultado: return jsonify({'erro':'Email ou Senha incorretos'}),400
    else:
        if check_password_hash(resultado['password'] ,data['password']): 
            meu_id = resultado['id']
            token_vip = create_access_token(identity=str(meu_id))
            return jsonify({
                'msg': 'Login realizado com sucesso!',
                'token': token_vip,
                'permissoes': resultado['permissoes']}),200
        else: 
            return jsonify({'erro':'Email ou Senha incorretos'}),400


#=================================================================CLIENTE=========================================================================
@app.route('/clientes',methods=['GET'])
@jwt_required()
def listar_clientes():
    conexao,cursor = conectar_banco()

    cursor.execute('SELECT id, nome, cpf, email, permissoes FROM CLIENTES')
    usuarios = cursor.fetchall()

    conexao.close()

    return(jsonify(usuarios)), 200

@app.route('/clientes',methods=['POST'])
def cadastrar_cliente():
    conexao,cursor = conectar_banco()
    data = request.get_json()

    permissao = 'user'
    
    if data['cpf'].isdigit(): 
        pass
    else: return 'Erro 400 - Digite um CPF válido', 400

    sql = 'INSERT INTO CLIENTES (nome,password, cpf, email, permissoes) VALUES (%s,%s,%s,%s,%s)'
    valores = (data['nome'],generate_password_hash(data['password']),data['cpf'],data['email'],permissao)

    cursor.execute(sql,valores)
    conexao.commit()

    conexao.close()

    return jsonify({'msg':'Cliente cadastrado com sucesso!'}), 200


@app.route('/clientes/<int:id>',methods=['PATCH'])
@jwt_required()
def atualizar_cliente(id):
    conexao,cursor = conectar_banco()
    id_escondido = get_jwt_identity()

    verificar_admin(id_escondido)
    erro_permissao = verificar_admin(id_escondido)

    if erro_permissao: 
        conexao.close()
        return erro_permissao


    data = request.get_json()

    campos = []
    valores = []

    if 'nome' in data:
        campos.append('nome = %s')
        valores.append(data['nome'])
    
    if 'password' in data:
        campos.append('password = %s')
        valores.append(generate_password_hash(data['password']))

    if 'cpf' in data:
        campos.append('cpf = %s')
        valores.append(data['cpf'])

    if 'email' in data:
        campos.append('email = %s')
        valores.append(data['email'])

    if 'permissoes' in data:
        campos.append('permissoes = %s')
        valores.append(data['permissoes'])

    if not campos:
        return {"erro": "Nenhum campo para atualizar"}, 400

    sql = f"UPDATE CLIENTES SET {','.join(campos)} WHERE ID = %s"
    valores.append(id)

    cursor.execute(sql, valores)
    conexao.commit()

    conexao.close()

    return jsonify({'msg':'Cliente atualizado com sucesso'}),200


@app.route('/clientes/<int:id>',methods=['DELETE'])
@jwt_required()
def deletar_cliente(id):
    conexao,cursor = conectar_banco()
    id_escondido = get_jwt_identity()

    verificar_admin(id_escondido)
    erro_permissao = verificar_admin(id_escondido)

    if erro_permissao: 
        conexao.close()
        return erro_permissao

    sql = 'DELETE FROM CLIENTES WHERE id = %s'

    cursor.execute(sql, (id,))
    conexao.commit()

    conexao.close()
    return jsonify({'msg': 'Cliente deletado com sucesso!'}), 200

# =================================================INVENTARIO-=====================================================================
@app.route('/inventario',methods=['GET'])
def listar_inventario():
    conexao,cursor = conectar_banco()
    cursor.execute('SELECT * FROM INVENTARIO')
    inventario = cursor.fetchall()

    conexao.close()

    return jsonify(inventario), 200


@app.route('/inventario',methods=['POST'])
@jwt_required()
def criar_produto():
    conexao,cursor = conectar_banco()
    id_escondido = get_jwt_identity()

    erro_permissao = verificar_admin(id_escondido)

    if erro_permissao: 
        conexao.close()
        return erro_permissao

    data = request.get_json() #Dados que o cliente enviou

    conexao, cursor = conectar_banco()

    if data['preco_venda'] < 0 or data['preco_custo'] < 0 or data['quantidade_estoque'] < 0: return jsonify({'erro': 'Preço ou quantidade não podem ser negativos!'}), 400
    if data['preco_venda'] < data['preco_custo']: return jsonify({'erro': 'Você não pode vender com prejuízo!'}), 400

    sql = 'INSERT INTO INVENTARIO (nome, preco_custo, preco_venda, quantidade_estoque, categoria, ativo) VALUES (%s,%s,%s,%s,%s,%s)'
    valores = (data['nome'],data['preco_custo'],data['preco_venda'],data['quantidade_estoque'],data['categoria'],data['ativo'],)

    cursor.execute(sql, valores)
    conexao.commit()
    conexao.close()

    return(jsonify({'msg':'Produto criado com sucesso!'})), 200


@app.route('/inventario/<int:id_produto>',methods=['PATCH'])
@jwt_required()
def atualizar_produto(id_produto):
    conexao,cursor = conectar_banco()
    id_escondido = get_jwt_identity()

    verificar_admin(id_escondido)
    erro_permissao = verificar_admin(id_escondido)

    if erro_permissao: 
        conexao.close()
        return erro_permissao

    data = request.get_json()

    campo = []
    valores = []

    if 'nome' in data:
        campo.append('nome = %s')
        valores.append(data['nome'])

    if 'preco_custo' in data:
        if data['preco_custo'] < 0: return 'Erro', 400
        else:
            campo.append('preco_custo = %s')
            valores.append(data['preco_custo'])

    if 'preco_venda' in data:
        if data['preco_venda'] < 0: return 'Erro', 400
        else:
            campo.append('preco_venda = %s')
            valores.append(data['preco_venda'])

    if 'quantidade_estoque' in data:
        if data['quantidade_estoque'] < 0: return 'Erro', 400
        else:
            campo.append('quantidade_estoque = %s')
            valores.append(data['quantidade_estoque'])

    if 'categoria' in data:
        campo.append('categoria = %s')
        valores.append(data['categoria'])

    if 'ativo' in data:
        campo.append('ativo = %s')
        valores.append(data['ativo'])

    sql = f"UPDATE INVENTARIO SET {','.join(campo)} WHERE id_produto = %s"
    valores.append(id_produto)

    cursor.execute(sql, valores)
    conexao.commit()

    conexao.close()

    return jsonify({'msg':'Produto atualizado com sucesso!'}), 200


@app.route('/inventario/<int:id_produto>',methods=['DELETE'])
@jwt_required()
def deletar_produto(id_produto):
    conexao,cursor = conectar_banco()
    id_escondido = get_jwt_identity()

    verificar_admin(id_escondido)
    erro_permissao = verificar_admin(id_escondido)
    
    if erro_permissao: 
        conexao.close()
        return erro_permissao

    sql = 'DELETE FROM INVENTARIO WHERE id_produto = %s'
    cursor.execute(sql, (id_produto,))
    conexao.commit()

    conexao.close()

    return jsonify({'msg': 'Produto deletado com sucesso!'}), 200


if __name__ == '__main__':
    print(app.run(debug=True))