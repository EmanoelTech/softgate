# modulo_clientes.py
import sqlite3
import re
# Importar do novo módulo de utilidades de banco de dados
from db_utils import conectar_bd, fechar_bd 
from datetime import datetime

# --- 1. Configuração Inicial e Conexão com o Banco de Dados ---
# Função para conectar ao banco de dados
#def conectar_bd(nome_banco="assistencia_tecnica.db"):
#    """
#   Conecta ao banco de dados SQLite. Se o banco não existir, ele será criado.
#    Retorna o objeto de conexão e o cursor.
#    """
#    conn = None
#    try:
#        conn = sqlite3.connect(nome_banco)
#        # Permite acessar colunas por nome
#        conn.row_factory = sqlite3.Row
#        cursor = conn.cursor()
#        # print(f"Conectado ao banco de dados: {nome_banco}") # Comentado para uso com API
#        return conn, cursor
#    except sqlite3.Error as e:
#        # print(f"Erro ao conectar ao banco de dados: {e}") # Comentado para uso com API
#        return None, None#
#
# Função para fechar a conexão com o banco de dados
#def fechar_bd(conn):
#    """Fecha a conexão com o banco de dados."""
#    if conn:
#        conn.close()
        # print("Conexão com o banco de dados fechada.") # Comentado para uso com API

# --- 2. Modelagem da Tabela de Clientes ---
def criar_tabela_clientes(cursor):
    """
    Cria a tabela 'clientes' no banco de dados, se ela não existir.
    Armazena informações para Pessoa Física e Jurídica.
    """
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_pessoa TEXT NOT NULL CHECK(tipo_pessoa IN ('PF', 'PJ')),
                nome TEXT, -- Nome para PF
                razao_social TEXT, -- Razão Social para PJ
                cpf TEXT UNIQUE, -- CPF para PF (único)
                cnpj TEXT UNIQUE, -- CNPJ para PJ (único)
                data_nascimento TEXT, -- Data de nascimento para PF (formato YYYY-MM-DD)
                responsavel TEXT, -- Responsável para PJ
                whatsapp TEXT NOT NULL
            );
        """)
        # print("Tabela 'clientes' verificada/criada com sucesso.") # Comentado para uso com API
    except sqlite3.Error as e:
        print(f"Erro ao criar tabela 'clientes': {e}") # Manter este print para erros críticos
        raise # Levantar o erro para que o Flask possa capturá-lo

# --- Funções Auxiliares de Validação (Opcional, mas útil para robustez) ---
def validar_cpf(cpf):
    """Valida se o CPF tem o formato correto (11 dígitos numéricos)."""
    # Adicionando validação básica de CPF - pode ser expandida para validação de dígitos verificadores
    if not re.fullmatch(r'\d{11}', cpf):
        return False
    # Poderíamos adicionar a lógica de validação de CPF real aqui, mas para manter simples por enquanto.
    return True

def validar_cnpj(cnpj):
    """Valida se o CNPJ tem o formato correto (14 dígitos numéricos)."""
    # Adicionando validação básica de CNPJ - pode ser expandida
    if not re.fullmatch(r'\d{14}', cnpj):
        return False
    # Poderíamos adicionar a lógica de validação de CNPJ real aqui, mas para manter simples por enquanto.
    return True

# --- 3. Funções CRUD para Clientes ---

# OBS: As funções de CRUD abaixo (cadastrar, atualizar, excluir)
# foram adaptadas no `app.py` do Flask para receber dados via JSON.
# Para manter a modularidade, você pode criar uma "camada de serviço" no backend
# que essas funções originais seriam chamadas internamente, mas sem a interação de console (input/print).
# Por agora, estou mantendo-as como estavam com os inputs para que possam ser testadas isoladamente,
# mas o Flask não as chamará diretamente com `input()`.

def cadastrar_cliente(cursor, conn):
    """
    Permite cadastrar um novo cliente, seja Pessoa Física (PF) ou Jurídica (PJ).
    Solicita as informações ao usuário (para uso standalone do módulo).
    """
    print("\n--- Cadastro de Novo Cliente ---")
    while True:
        tipo = input("Tipo de Pessoa (PF/PJ): ").strip().upper()
        if tipo in ('PF', 'PJ'):
            break
        else:
            print("Tipo inválido. Por favor, digite 'PF' ou 'PJ'.")

    whatsapp = input("WhatsApp (somente números, ex: 5511987654321): ").strip()
    if not whatsapp:
        print("WhatsApp é um campo obrigatório.")
        return

    if tipo == 'PF':
        nome = input("Nome do Cliente: ").strip()
        cpf = input("CPF (somente números): ").strip()
        data_nascimento = input("Data de Nascimento (AAAA-MM-DD): ").strip()

        if not (nome and cpf and data_nascimento):
            print("Nome, CPF e Data de Nascimento são obrigatórios para Pessoa Física.")
            return
        if not validar_cpf(cpf):
            print("CPF inválido. Deve conter 11 dígitos numéricos.")
            return

        try:
            cursor.execute("""
                INSERT INTO clientes (tipo_pessoa, nome, cpf, data_nascimento, whatsapp)
                VALUES (?, ?, ?, ?, ?)
            """, (tipo, nome, cpf, data_nascimento, whatsapp))
            conn.commit()
            print(f"Cliente PF '{nome}' cadastrado com sucesso!")
        except sqlite3.IntegrityError:
            print(f"Erro: CPF '{cpf}' já cadastrado.")
        except sqlite3.Error as e:
            print(f"Erro ao cadastrar cliente PF: {e}")

    elif tipo == 'PJ':
        razao_social = input("Razão Social: ").strip()
        cnpj = input("CNPJ (somente números): ").strip()
        responsavel = input("Nome do Responsável: ").strip()

        if not (razao_social and cnpj and responsavel):
            print("Razão Social, CNPJ e Responsável são obrigatórios para Pessoa Jurídica.")
            return
        if not validar_cnpj(cnpj):
            print("CNPJ inválido. Deve conter 14 dígitos numéricos.")
            return

        try:
            cursor.execute("""
                INSERT INTO clientes (tipo_pessoa, razao_social, cnpj, responsavel, whatsapp)
                VALUES (?, ?, ?, ?, ?)
            """, (tipo, razao_social, cnpj, responsavel, whatsapp))
            conn.commit()
            print(f"Cliente PJ '{razao_social}' cadastrado com sucesso!")
        except sqlite3.IntegrityError:
            print(f"Erro: CNPJ '{cnpj}' já cadastrado.")
        except sqlite3.Error as e:
            print(f"Erro ao cadastrar cliente PJ: {e}")


def listar_clientes(cursor):
    """
    Lista todos os clientes cadastrados.
    Retorna uma lista de objetos sqlite3.Row.
    """
    try:
        cursor.execute("SELECT * FROM clientes ORDER BY tipo_pessoa, nome, razao_social")
        clientes = cursor.fetchall()
        # print("--- Clientes Cadastrados ---") # Comentar para uso via API
        # if not clientes:
        #     print("Nenhum cliente cadastrado ainda.") # Comentar para uso via API
        # else:
        #     for cliente in clientes:
        #         print(f"ID: {cliente['id']} | Tipo: {cliente['tipo_pessoa']}")
        #         if cliente['tipo_pessoa'] == 'PF':
        #             print(f"  Nome: {cliente['nome']} | CPF: {cliente['cpf']} | Nasc.: {cliente['data_nascimento']} | WhatsApp: {cliente['whatsapp']}")
        #         elif cliente['tipo_pessoa'] == 'PJ':
        #             print(f"  Razão Social: {cliente['razao_social']} | CNPJ: {cliente['cnpj']} | Responsável: {cliente['responsavel']} | WhatsApp: {cliente['whatsapp']}")
        #         print("-" * 30)
        return clientes # GARANTE QUE SEMPRE RETORNA UMA LISTA (PODE SER VAZIA)
    except sqlite3.Error as e:
        print(f"Erro ao listar clientes: {e}")
        return [] # Retorna lista vazia em caso de erro

def buscar_cliente(cursor, termo_busca):
    """
    Busca clientes por nome, razão social, CPF ou CNPJ.
    Retorna uma lista de clientes encontrados.
    """
    termo_busca = f"%{termo_busca}%" # Para buscar partes do nome/número
    try:
        cursor.execute("""
            SELECT * FROM clientes
            WHERE nome LIKE ? OR razao_social LIKE ? OR cpf LIKE ? OR cnpj LIKE ?
            ORDER BY tipo_pessoa, nome, razao_social
        """, (termo_busca, termo_busca, termo_busca, termo_busca))
        clientes = cursor.fetchall()
        return clientes # Retorna a lista de resultados (pode ser vazia)
    except sqlite3.Error as e:
        print(f"Erro ao buscar cliente: {e}")
        return [] # Retorna lista vazia em caso de erro

def exibir_resultados_busca(clientes):
    """Exibe os resultados de uma busca de clientes (para uso standalone do módulo)."""
    if not clientes:
        print("Nenhum cliente encontrado com o termo informado.")
        return

    print("\n--- Clientes Encontrados ---")
    for cliente in clientes:
        print(f"ID: {cliente['id']} | Tipo: {cliente['tipo_pessoa']}")
        if cliente['tipo_pessoa'] == 'PF':
            print(f"  Nome: {cliente['nome']} | CPF: {cliente['cpf']} | Nasc.: {cliente['data_nascimento']} | WhatsApp: {cliente['whatsapp']}")
        elif cliente['tipo_pessoa'] == 'PJ':
            print(f"  Razão Social: {cliente['razao_social']} | CNPJ: {cliente['cnpj']} | Responsável: {cliente['responsavel']} | WhatsApp: {cliente['whatsapp']}")
        print("-" * 30)

def atualizar_cliente(cursor, conn):
    """Permite atualizar as informações de um cliente existente."""
    print("\n--- Atualizar Cliente ---")
    cliente_id = input("Digite o ID do cliente que deseja atualizar: ").strip()
    if not cliente_id.isdigit():
        print("ID inválido. Por favor, digite um número.")
        return

    cliente_id = int(cliente_id)

    # Verifica se o cliente existe
    cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
    cliente = cursor.fetchone()

    if not cliente:
        print(f"Cliente com ID {cliente_id} não encontrado.")
        return

    print(f"Editando cliente: {cliente['nome'] if cliente['tipo_pessoa'] == 'PF' else cliente['razao_social']}")
    print("Deixe o campo em branco para manter o valor atual.")

    if cliente['tipo_pessoa'] == 'PF':
        novo_nome = input(f"Novo Nome ({cliente['nome']}): ").strip() or cliente['nome']
        nova_data_nascimento = input(f"Nova Data de Nascimento ({cliente['data_nascimento']}): ").strip() or cliente['data_nascimento']
        novo_whatsapp = input(f"Novo WhatsApp ({cliente['whatsapp']}): ").strip() or cliente['whatsapp']

        try:
            cursor.execute("""
                UPDATE clientes
                SET nome = ?, data_nascimento = ?, whatsapp = ?
                WHERE id = ?
            """, (novo_nome, nova_data_nascimento, novo_whatsapp, cliente_id))
            conn.commit()
            print(f"Cliente PF '{novo_nome}' atualizado com sucesso!")
        except sqlite3.Error as e:
            print(f"Erro ao atualizar cliente PF: {e}")

    elif cliente['tipo_pessoa'] == 'PJ':
        nova_razao_social = input(f"Nova Razão Social ({cliente['razao_social']}): ").strip() or cliente['razao_social']
        novo_responsavel = input(f"Novo Responsável ({cliente['responsavel']}): ").strip() or cliente['responsavel']
        novo_whatsapp = input(f"Novo WhatsApp ({cliente['whatsapp']}): ").strip() or cliente['whatsapp']

        try:
            cursor.execute("""
                UPDATE clientes
                SET razao_social = ?, responsavel = ?, whatsapp = ?
                WHERE id = ?
            """, (nova_razao_social, novo_responsavel, novo_whatsapp, cliente_id))
            conn.commit()
            print(f"Cliente PJ '{nova_razao_social}' atualizado com sucesso!")
        except sqlite3.Error as e:
            print(f"Erro ao atualizar cliente PJ: {e}")

def excluir_cliente(cursor, conn):
    """Permite excluir um cliente pelo ID."""
    print("\n--- Excluir Cliente ---")
    cliente_id = input("Digite o ID do cliente que deseja excluir: ").strip()
    if not cliente_id.isdigit():
        print("ID inválido. Por favor, digite um número.")
        return

    cliente_id = int(cliente_id)

    # Verifica se o cliente existe
    cursor.execute("SELECT id FROM clientes WHERE id = ?", (cliente_id,))
    cliente_existe = cursor.fetchone()

    if not cliente_existe:
        print(f"Cliente com ID {cliente_id} não encontrado.")
        return

    confirmacao = input(f"Tem certeza que deseja excluir o cliente ID {cliente_id}? (s/N): ").strip().lower()
    if confirmacao == 's':
        try:
            cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
            conn.commit()
            print(f"Cliente ID {cliente_id} excluído com sucesso!")
        except sqlite3.Error as e:
            print(f"Erro ao excluir cliente: {e}")
    else:
        print("Exclusão cancelada.")

# --- 4. Testando o Módulo (Função Principal para uso standalone) ---

def main():
    """Função principal para demonstrar as funcionalidades do módulo de clientes (uso via console)."""
    conn, cursor = conectar_bd()

    if conn and cursor:
        criar_tabela_clientes(cursor)

        while True:
            print("\n--- Menu Cliente ---")
            print("1. Cadastrar Cliente")
            print("2. Listar Clientes")
            print("3. Buscar Cliente")
            print("4. Atualizar Cliente")
            print("5. Excluir Cliente")
            print("0. Sair")

            opcao = input("Escolha uma opção: ").strip()

            if opcao == '1':
                cadastrar_cliente(cursor, conn)
            elif opcao == '2':
                listar_clientes(cursor) # Para o main, mantemos a impressão
            elif opcao == '3':
                termo = input("Digite o nome, razão social, CPF ou CNPJ para buscar: ").strip()
                if termo:
                    resultados = buscar_cliente(cursor, termo)
                    exibir_resultados_busca(resultados) # Para o main, usamos a função de exibição
                else:
                    print("Termo de busca não pode ser vazio.")
            elif opcao == '4':
                atualizar_cliente(cursor, conn)
            elif opcao == '5':
                excluir_cliente(cursor, conn)
            elif opcao == '0':
                print("Saindo do módulo de clientes.")
                break
            else:
                print("Opção inválida. Por favor, tente novamente.")

        fechar_bd(conn)

if __name__ == "__main__":
    main()