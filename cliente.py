import requests
import os
from time import sleep
from rich import print
from rich.table import Table

base_url = 'http://127.0.0.1:5000'

def titulo(msg):
    os.system('cls')
    print('='*30)
    print(f'|{msg:^28}|')
    print('='*30)


def deletar_cliente(token):
    cabecalho_seg = {
        'Authorization': f'Bearer {token}'
    }

    id_cliente = int(input('ID: '))

    response = requests.delete(f'{base_url}/clientes/{id_cliente}')

    if response.status_code == 200:
        print('Sucesso, produto atualizado')
        input('Aperte ENTER para voltar')
    else:
        erro = response.json().get('erro', 'Erro desconhecido')
        print(f"\n❌ Bloqueado pela API: {erro}")



def atualizar_cliente(token):
    dados = {}
    cabecalho_seg = {
        'Authorization': f'Bearer {token}'
    }
    while True:
        titulo('ATUALIZAR CLIENTE')
        print('1-Nome')
        print('2-CPF')
        print('3-Email')
        print('4-Permissão')
        print('5-Logout')
        try:
            while True:
                opcao = int(input('Opção: '))
                if opcao < 1 or opcao > 5: print('Escolha uma opção válida!')
                else: break
        except ValueError: print('Digite um número inteiro')
        else:
            id_cliente = int(input('ID(aperte 0 caso mão queira atualizar nada): '))
            if opcao == 1:
                nome_novo = input('Nome atualizado: ')
                dados['nome'] = nome_novo
            elif opcao == 2:
                cpf_novo = input('CPF atualizado: ')
                dados['cpf'] = cpf_novo
            elif opcao == 3:
                email_novo = input('Email atualizado: ')
                dados['email'] = email_novo
            elif opcao == 4:
                permissao_nova = input('Permissão atualizado: ')
                dados['permissoes'] = permissao_nova
            elif opcao == 5:
                response = requests.patch(f'{base_url}/clientes/{id_cliente}', json=dados, headers=cabecalho_seg)
                
                if response.status_code == 200:
                    print('Sucesso, produto atualizado')
                    input('Aperte ENTER para voltar')
                    break
                else:
                    erro = response.json().get('erro', 'Erro desconhecido')
                    print(f"\n❌ Bloqueado pela API: {erro}")
                    break

            elif id_cliente == 0: break


def lista_clientes(token):
    cabecalho_seguranca = {
        'Authorization':f'Bearer {token}'
    }

    response = requests.get(f'{base_url}/clientes',headers=cabecalho_seguranca)

    if response.status_code == 200:
        data = response.json()
        colunas = ['ID','NOME','CPF','EMAIL','PERMISSÃO']
        tabela = Table(title='CLIENTE')
        for coluna in colunas:
            tabela.add_column(coluna, justify='center', style='blue')
        for user in data:
            tabela.add_row(
                str(user['id']),
                user['nome'],
                user['cpf'],
                user['email'],
                user['permissoes'])
        print(tabela)
        input('Aperte ENTER para voltar')
    else:
        print(f"\n❌ ERRO DETALHADO DA API: {response.json()}") 
        input("Aperte ENTER para continuar...")


def adicionar_produto(token):
    titulo('ADICIONAR PRODUTO')
    try:
        nome = input('Nome: ')
        preco_custo = float(input('Preço de Custo (ex: 2.50): '))
        preco_venda = float(input('Preço de Venda (ex: 5.00): '))
        quantidade = int(input('Quantidade no Estoque: '))
        categoria = input('Categoria (ex: Frutas, Bebidas): ')
        ativo = int(input('Produto está ativo? (1 para Sim, 0 para Não): '))
    except ValueError: 
        print('\n❌ Erro: Você digitou letras onde deveriam ser números (Preço/Quantidade)!')
        input('Aperte ENTER para voltar ao menu...')
        return
    else:
        dados_produto = {
            'nome': nome,
            'preco_custo':preco_custo,
            'preco_venda':preco_venda,
            'quantidade_estoque':quantidade,
            'categoria':categoria,
            'ativo':ativo
        }

        cabecalho_seguranca = {
            'Authorization': f'Bearer {token}'
        }

        response = requests.post(f'{base_url}/inventario', json=dados_produto, headers=cabecalho_seguranca)

        if response.status_code == 200:
            print(f"\n✅ Sucesso: {response.json()['msg']}")
        else:
            erro = response.json().get('erro', 'Erro desconhecido na API')
            print(f"\n❌ Bloqueado pela API: {erro}")
        
    input('\nAperte ENTER para voltar ao menu...')


def atualizar_produto(token):
    try:
        id_produto = int(input('Qual o ID do produto que deseja atualizar? '))
    except ValueError:
        print('❌ O ID deve ser um número inteiro!')
        return
    dados = {}
    dados_seguranca = {
        'Authorization': f'Bearer {token}'
    }
    while True:
        titulo('ATUALIZAR PRODUTO') 
        print('1-Nome')
        print('2-Preço custo')
        print('3-Preço venda')
        print('4-Quantidade no estoque')
        print('5-Categoria')
        print('6-Ativo')
        print('7-Sair')
        try:
            opcao = int(input('Opçaõ: '))
        except ValueError: 
            print('Digite uma opçaõ válida!')
        else:
            if opcao == 1:
                nome_novo = input('Nome atualizado: ')
                dados['nome'] = nome_novo
            elif opcao == 2: 
                preco_custo_novo = float(input('Custo atualizado: '))
                dados['preco_custo'] = preco_custo_novo
            elif opcao == 3: 
                preco_venda_novo = float(input('Valor de venda atualizado: '))
                dados['preco_venda'] = preco_venda_novo
            elif opcao == 4:
                quantidade_nova = int(input('Quantidade atualizada: '))
                dados['quantidade_estoque'] = quantidade_nova
            elif opcao == 5: 
                categoria_nova = input('Categoria (ex: Frutas, Bebidas): ')
                dados['categoria'] = categoria_nova
            elif opcao == 6: 
                ativo = int(input('Produto está ativo? (1 para Sim, 0 para Não): '))
                dados['ativo'] = ativo
            elif opcao == 7:
                response = requests.patch(f'{base_url}/inventario/{id_produto}', json=dados, headers=dados_seguranca)

                if response.status_code == 200:
                    print('Sucesso, produto atualizado')
                    input('Aperte ENTER para voltar')
                    break
                else:
                    erro = response.json().get('erro', 'Erro desconhecido')
                    print(f"\n❌ Bloqueado pela API: {erro}")
                    break


def deletar_produto(token):
    titulo('DELETAR PRODUTO')
    try:
        id_produto = int(input('Qual o ID do produto que deseja atualizar? '))
    except ValueError:
        print('❌ O ID deve ser um número inteiro!')
        return
    
    dados = {
        'id_produto':id_produto
    }

    cabecalho_segurancao = {
        'Authorization':f'Bearer {token}'
    }

    response = requests.delete(f'{base_url}/inventario/{id_produto}', headers=cabecalho_segurancao)

    if response.status_code == 200:
        print('Sucesso, produto atualizado')
        input('Aperte ENTER para voltar')
    else:
        erro = response.json().get('erro', 'Erro desconhecido')
        print(f"\n❌ Bloqueado pela API: {erro}")


def ver_estoque(token):
    response = requests.get(f'{base_url}/inventario')

    if response.status_code == 200:
        data = response.json()
        colunas = ['ID','NOME','CUSTO','VENDA','ESTOQUE','CATEGORIA','ATIVO']
        tabela = Table(title='CLIENTE')
        for coluna in colunas:
            tabela.add_column(coluna, justify='center', style='blue')
        for user in data:
            tabela.add_row(
                str(user['id_produto']),
                user['nome'],
                str(user['preco_custo']),
                str(user['preco_venda']),
                str(user['quantidade_estoque']),
                user['categoria'],
                str(user['ativo']))
        print(tabela)
        input('Aperte ENTER para voltar')


def ver_inventario():
    response = requests.get(f'{base_url}/inventario')

    if response.status_code == 200:
        data = response.json()
        colunas = ['NOME','VENDA','ESTOQUE','CATEGORIA','ATIVO']
        tabela = Table(title='CLIENTE')
        for coluna in colunas:
            tabela.add_column(coluna, justify='center', style='blue')
        for user in data:
            tabela.add_row(
                user['nome'],
                str(user['preco_venda']),
                str(user['quantidade_estoque']),
                user['categoria'],
                str(user['ativo']))
        print(tabela)
        input('Aperte ENTER para voltar')

def permissoes(permissao, token):
    while True:
        titulo('MENU PRINCIPAL')
        if permissao == 'admin':
            print('1-Ver estoque')
            print('2-Adicionar novo produto')
            print('3-Atualizar Produto') 
            print('4-Deletar Produto')
            print('5-Atualizar Cliente')
            print('6-Deletar cliente')
            print('7-Ver Lista de Clientes')
            print('8-Sair (Logout)')
            try:
                while True:
                    opcao = int(input('Opção: '))
                    if opcao < 1 or opcao > 8: print('Digite uma opção válida')
                    else: break
            except KeyboardInterrupt: print('Escolha uma opção')
            except ValueError: print('Digite um número inteiro')
            else: 
                if opcao == 1:
                    ver_estoque(token)
                elif opcao == 2:
                    adicionar_produto(token)
                elif opcao == 3:
                    atualizar_produto(token)
                elif opcao == 4:
                    deletar_produto(token)
                elif opcao == 5:
                    atualizar_cliente(token)
                elif opcao == 5:
                    deletar_cliente(token)
                elif opcao == 7:
                    lista_clientes(token)
                elif opcao == 8:
                    break
        else:
            print('1-Ver produtos')
            print('2-Sair')
            try:
                while True:
                    opcao = int(input('Opção: '))
                    if opcao < 1 or opcao > 2: print('Digite uma opção válida')
                    else: break
            except KeyboardInterrupt: print('Escolha uma opção')
            except ValueError: print('Digite um número inteiro')
            else:
                if opcao == 1:
                    ver_inventario()
                elif opcao == 2: break



def login():
    while True:
                try:
                    sleep(1)
                    titulo('LOGIN')
                    email = input('Email: ')
                    senha = input('Senha: ')
                    sucesso, permissao, token = verificar_usuario(email, senha)
                except KeyboardInterrupt: print('Digite todas as informações pedidas')
                else:
                    if sucesso: break
    permissoes(permissao, token)


def listar_usuario():
    response = requests.get(f'{base_url}/clientes')

    if response.status_code == 200:
        data = response.json()
        os.system('cls')
        print('='*116)
        print(f'|{"USUÁRIO":^114}|')
        print('='*116)
        for user in data:
            print(f"|{user['id']:^3}|{user['nome']:^30}|{user['idade']:^30}|{user['email']:^40}|{user['permissoes']:^7}|")
        print('='*116)
    else: print(f"Request failed with status code {response.status_code}") 


def verificar_usuario(email, senha):
    dados = {
        'email': email,
        'password': senha
    }

    response = requests.post(f'{base_url}/login',json=dados)

    if response.status_code == 200: 
        dados_api = response.json()
        permissao_usuario = dados_api['permissoes']
        token = dados_api['token']
        print(f"\n✅ {dados_api['msg']}")
        return True, permissao_usuario, token
    else: 
        erro = response.json()
        print(f"\n❌ {erro}")
        return False, None, None
    

def criar_usuario(nome, senha, cpf, email):
    dados = {
                'nome': nome,
                'password': senha,
                'cpf': cpf,
                'email': email,
            }
    
    response = requests.post(f'{base_url}/clientes',json=dados)

    if response.status_code == 200:
        dados_api = response.json() #Pega o que a API enviou para o cliente
        print(f"\n✅ {dados_api['msg']}")
        return True
    else:
        print(f"\n❌ {response.json()['erro']}")
        return False



def main():
    while True:
        titulo('Menu')
        print('1-Login')
        print('2-Cadastro')
        try:
            opcao = int(input('Opçao: '))
        except KeyboardInterrupt: print('Escolha uma opção certa')
        else:
            if opcao == 1:
                login()
            else:
                while True:
                    try:
                        titulo('CADASTRO')
                        nome = input('Nome completo: ')
                        cpf = input('CPF(apenas os números): ')
                        email = input('Email: ')
                        senha = input('Senha: ')
                        sucesso = criar_usuario(nome, senha, cpf, email)
                    except KeyboardInterrupt: print('Digite todas as informações pedidas')
                    else:
                        if sucesso: break
                login()


main()