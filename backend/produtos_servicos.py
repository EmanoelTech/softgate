# backend/produtos_servicos.py
import sqlite3
# --- Importação ÚNICA E CORRETA das funções de BD do módulo utilitário ---
from db_utils import conectar_bd, fechar_bd 


# --- A linha 'from produtos_servicos import (...)' DEVE SER REMOVIDA DAQUI.
# Ela é que está causando o erro de importação circular.


# --- AS DEFINIÇÕES 'conectar_bd' e 'fechar_bd' DEVEM SER REMOVIDAS/COMENTADAS
# (parece que você já fez isso, o que é ótimo!)
#def conectar_bd(nome_banco="assistencia_tecnica.db"):
#    conn = None
#    try:
#        conn = sqlite3.connect(nome_banco)
#        conn.row_factory = sqlite3.Row
#        cursor = conn.cursor()
#        return conn, cursor
#    except sqlite3.Error as e:
#        print(f"Erro ao conectar ao banco de dados: {e}")
#        return None, None
#
#def fechar_bd(conn):
#    if conn:
#        conn.close()

# --- 1. Modelagem das Tabelas de Produtos e Serviços ---
def criar_tabelas_produtos_servicos(cursor):
    """
    Cria as tabelas 'produtos' e 'servicos' no banco de dados, se não existirem.
    """
    try:
        # Tabela de Produtos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                descricao TEXT,
                preco REAL NOT NULL,
                estoque INTEGER NOT NULL DEFAULT 0
            );
        """)
        # print("Tabela 'produtos' verificada/criada com sucesso.") # Comentado para uso com API

        # Tabela de Serviços
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS servicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                descricao TEXT,
                preco REAL NOT NULL
            );
        """)
        # print("Tabela 'servicos' verificada/criada com sucesso.") # Comentado para uso com API

    except sqlite3.Error as e:
        print(f"Erro ao criar tabelas de produtos/serviços: {e}")
        raise # Levantar o erro para que o Flask possa capturá-lo

# --- 2. Funções CRUD para Produtos ---

def cadastrar_produto(cursor, conn):
    """Permite cadastrar um novo produto (para uso standalone do módulo)."""
    print("\n--- Cadastro de Novo Produto ---")
    nome = input("Nome do Produto: ").strip()
    if not nome:
        print("Nome do produto é obrigatório.")
        return False, "Nome do produto é obrigatório." # Retorna status para Flask
    
    descricao = input("Descrição do Produto (opcional): ").strip()

    while True:
        try:
            preco = float(input("Preço do Produto (ex: 12.50): ").strip())
            if preco < 0:
                print("Preço não pode ser negativo.")
                continue
            break
        except ValueError:
            print("Preço inválido. Digite um número.")
    
    while True:
        try:
            estoque = int(input("Quantidade em Estoque: ").strip())
            if estoque < 0:
                print("Estoque não pode ser negativo.")
                continue
            break
        except ValueError:
            print("Estoque inválido. Digite um número inteiro.")

    try:
        cursor.execute("""
            INSERT INTO produtos (nome, descricao, preco, estoque)
            VALUES (?, ?, ?, ?)
        """, (nome, descricao, preco, estoque))
        conn.commit()
        print(f"Produto '{nome}' cadastrado com sucesso!")
        return True, "Produto cadastrado com sucesso!" # Retorna status para Flask
    except sqlite3.IntegrityError:
        print(f"Erro: Produto com nome '{nome}' já existe.")
        return False, f"Erro: Produto com nome '{nome}' já existe."
    except sqlite3.Error as e:
        print(f"Erro ao cadastrar produto: {e}")
        return False, f"Erro ao cadastrar produto: {e}"

def listar_produtos(cursor):
    """Lista todos os produtos cadastrados. Retorna uma lista de objetos sqlite3.Row."""
    try:
        cursor.execute("SELECT * FROM produtos ORDER BY nome")
        produtos = cursor.fetchall()
        # print("\n--- Produtos Cadastrados ---") # Comentado para API
        # if not produtos:
        #     print("Nenhum produto cadastrado ainda.") # Comentado para API
        # for produto in produtos: # Comentado para API
        #     print(f"ID: {produto['id']} | Nome: {produto['nome']} | Preço: R${produto['preco']:.2f} | Estoque: {produto['estoque']}")
        #     if produto['descricao']:
        #         print(f"  Descrição: {produto['descricao']}")
        #     print("-" * 30)
        return produtos # <--- RETORNA A LISTA, SEMPRE
    except sqlite3.Error as e:
        print(f"Erro ao listar produtos: {e}")
        return [] # Retorna lista vazia em caso de erro


def atualizar_produto(cursor, conn):
    """Permite atualizar as informações de um produto existente (para uso standalone do módulo)."""
    print("\n--- Atualizar Produto ---")
    produto_id_str = input("Digite o ID do produto que deseja atualizar: ").strip()
    if not produto_id_str.isdigit():
        print("ID inválido. Por favor, digite um número.")
        return False, "ID inválido."

    produto_id = int(produto_id_str)

    cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
    produto = cursor.fetchone()

    if not produto:
        print(f"Produto com ID {produto_id} não encontrado.")
        return False, f"Produto com ID {produto_id} não encontrado."

    print(f"Editando produto: {produto['nome']}")
    print("Deixe o campo em branco para manter o valor atual.")

    novo_nome = input(f"Novo Nome ({produto['nome']}): ").strip() or produto['nome']
    nova_descricao = input(f"Nova Descrição ({produto['descricao'] if produto['descricao'] else 'N/A'}): ").strip()
    nova_descricao = nova_descricao if nova_descricao != 'N/A' else None # Ajusta para None se digitado N/A

    novo_preco = produto['preco']
    while True:
        novo_preco_str = input(f"Novo Preço ({produto['preco']:.2f}): ").strip()
        if not novo_preco_str:
            break # Mantém o preço atual
        try:
            novo_preco = float(novo_preco_str)
            if novo_preco < 0:
                print("Preço não pode ser negativo.")
                continue
            break
        except ValueError:
            print("Preço inválido. Digite um número.")

    novo_estoque = produto['estoque']
    while True:
        novo_estoque_str = input(f"Novo Estoque ({produto['estoque']}): ").strip()
        if not novo_estoque_str:
            break # Mantém o estoque atual
        try:
            novo_estoque = int(novo_estoque_str)
            if novo_estoque < 0:
                print("Estoque não pode ser negativo.")
                continue
            break
        except ValueError:
            print("Estoque inválido. Digite um número inteiro.")

    try:
        cursor.execute("""
            UPDATE produtos
            SET nome = ?, descricao = ?, preco = ?, estoque = ?
            WHERE id = ?
        """, (novo_nome, nova_descricao, novo_preco, novo_estoque, produto_id))
        conn.commit()
        print(f"Produto '{novo_nome}' atualizado com sucesso!")
        return True, "Produto atualizado com sucesso!"
    except sqlite3.IntegrityError:
        print(f"Erro: Produto com nome '{novo_nome}' já existe.")
        return False, f"Erro: Produto com nome '{novo_nome}' já existe."
    except sqlite3.Error as e:
        print(f"Erro ao atualizar produto: {e}")
        return False, f"Erro ao atualizar produto: {e}"

def excluir_produto(cursor, conn):
    """Permite excluir um produto pelo ID (para uso standalone do módulo)."""
    print("\n--- Excluir Produto ---")
    produto_id_str = input("Digite o ID do produto que deseja excluir: ").strip()
    if not produto_id_str.isdigit():
        print("ID inválido. Por favor, digite um número.")
        return False, "ID inválido."

    produto_id = int(produto_id_str)

    cursor.execute("SELECT id, nome FROM produtos WHERE id = ?", (produto_id,))
    produto_existe = cursor.fetchone()

    if not produto_existe:
        print(f"Produto com ID {produto_id} não encontrado.")
        return False, f"Produto com ID {produto_id} não encontrado."

    confirmacao = input(f"Tem certeza que deseja excluir o produto '{produto_existe['nome']}' (ID: {produto_id})? (s/N): ").strip().lower()
    if confirmacao == 's':
        try:
            cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
            conn.commit()
            print(f"Produto '{produto_existe['nome']}' (ID: {produto_id}) excluído com sucesso!")
            return True, "Produto excluído com sucesso!"
        except sqlite3.Error as e:
            print(f"Erro ao excluir produto: {e}")
            return False, f"Erro ao excluir produto: {e}"
    else:
        print("Exclusão cancelada.")
        return False, "Exclusão cancelada."


# --- 3. Funções CRUD para Serviços ---

def cadastrar_servico(cursor, conn):
    """Permite cadastrar um novo serviço (para uso standalone do módulo)."""
    print("\n--- Cadastro de Novo Serviço ---")
    nome = input("Nome do Serviço: ").strip()
    if not nome:
        print("Nome do serviço é obrigatório.")
        return False, "Nome do serviço é obrigatório."

    descricao = input("Descrição do Serviço (opcional): ").strip()

    while True:
        try:
            preco = float(input("Preço do Serviço (ex: 50.00): ").strip())
            if preco < 0:
                print("Preço não pode ser negativo.")
                continue
            break
        except ValueError:
            print("Preço inválido. Digite um número.")

    try:
        cursor.execute("""
            INSERT INTO servicos (nome, descricao, preco)
            VALUES (?, ?, ?)
        """, (nome, descricao, preco))
        conn.commit()
        print(f"Serviço '{nome}' cadastrado com sucesso!")
        return True, "Serviço cadastrado com sucesso!"
    except sqlite3.IntegrityError:
        print(f"Erro: Serviço com nome '{nome}' já existe.")
        return False, f"Erro: Serviço com nome '{nome}' já existe."
    except sqlite3.Error as e:
        print(f"Erro ao cadastrar serviço: {e}")
        return False, f"Erro ao cadastrar serviço: {e}"

def listar_servicos(cursor):
    """Lista todos os serviços cadastrados. Retorna uma lista de objetos sqlite3.Row."""
    try:
        cursor.execute("SELECT * FROM servicos ORDER BY nome")
        servicos = cursor.fetchall()
        # print("\n--- Serviços Cadastrados ---") # Comentado para API
        # if not servicos:
        #     print("Nenhum serviço cadastrado ainda.") # Comentado para API
        # for servico in servicos: # Comentado para API
        #     print(f"ID: {servico['id']} | Nome: {servico['nome']} | Preço: R${servico['preco']:.2f}")
        #     if servico['descricao']:
        #         print(f"  Descrição: {servico['descricao']}")
        #     print("-" * 30)
        return servicos # <--- RETORNA A LISTA, SEMPRE
    except sqlite3.Error as e:
        print(f"Erro ao listar serviços: {e}")
        return [] # Retorna lista vazia em caso de erro

def atualizar_servico(cursor, conn):
    """Permite atualizar as informações de um serviço existente (para uso standalone do módulo)."""
    print("\n--- Atualizar Serviço ---")
    servico_id_str = input("Digite o ID do serviço que deseja atualizar: ").strip()
    if not servico_id_str.isdigit():
        print("ID inválido. Por favor, digite um número.")
        return False, "ID inválido."

    servico_id = int(servico_id_str)

    cursor.execute("SELECT * FROM servicos WHERE id = ?", (servico_id,))
    servico = cursor.fetchone()

    if not servico:
        print(f"Serviço com ID {servico_id} não encontrado.")
        return False, f"Serviço com ID {servico_id} não encontrado."

    print(f"Editando serviço: {servico['nome']}")
    print("Deixe o campo em branco para manter o valor atual.")

    novo_nome = input(f"Novo Nome ({servico['nome']}): ").strip() or servico['nome']
    nova_descricao = input(f"Nova Descrição ({servico['descricao'] if servico['descricao'] else 'N/A'}): ").strip()
    nova_descricao = nova_descricao if nova_descricao != 'N/A' else None

    novo_preco = servico['preco']
    while True:
        novo_preco_str = input(f"Novo Preço ({servico['preco']:.2f}): ").strip()
        if not novo_preco_str:
            break
        try:
            novo_preco = float(novo_preco_str)
            if novo_preco < 0:
                print("Preço não pode ser negativo.")
                continue
            break
        except ValueError:
            print("Preço inválido. Digite um número.")

    try:
        cursor.execute("""
            UPDATE servicos
            SET nome = ?, descricao = ?, preco = ?
            WHERE id = ?
        """, (novo_nome, nova_descricao, novo_preco, servico_id))
        conn.commit()
        print(f"Serviço '{novo_nome}' atualizado com sucesso!")
        return True, "Serviço atualizado com sucesso!"
    except sqlite3.IntegrityError:
        print(f"Erro: Serviço com nome '{novo_nome}' já existe.")
        return False, f"Erro: Serviço com nome '{novo_nome}' já existe."
    except sqlite3.Error as e:
        print(f"Erro ao atualizar serviço: {e}")
        return False, f"Erro ao atualizar serviço: {e}"

def excluir_servico(cursor, conn):
    """Permite excluir um serviço pelo ID (para uso standalone do módulo)."""
    print("\n--- Excluir Serviço ---")
    servico_id_str = input("Digite o ID do serviço que deseja excluir: ").strip()
    if not servico_id_str.isdigit():
        print("ID inválido. Por favor, digite um número.")
        return False, "ID inválido."

    servico_id = int(servico_id_str)

    cursor.execute("SELECT id, nome FROM servicos WHERE id = ?", (servico_id,))
    servico_existe = cursor.fetchone()

    if not servico_existe:
        print(f"Serviço com ID {servico_id} não encontrado.")
        return False, f"Serviço com ID {servico_id} não encontrado."

    confirmacao = input(f"Tem certeza que deseja excluir o serviço '{servico_existe['nome']}' (ID: {servico_id})? (s/N): ").strip().lower()
    if confirmacao == 's':
        try:
            cursor.execute("DELETE FROM servicos WHERE id = ?", (servico_id,))
            conn.commit()
            print(f"Serviço '{servico_existe['nome']}' (ID: {servico_id}) excluído com sucesso!")
            return True, "Serviço excluído com sucesso!"
        except sqlite3.Error as e:
            print(f"Erro ao excluir serviço: {e}")
            return False, f"Erro ao excluir serviço: {e}"
    else:
        print("Exclusão cancelada.")
        return False, "Exclusão cancelada."

# --- Função Principal para Testar este Módulo (uso standalone) ---

def main():
    """Função principal para demonstrar as funcionalidades dos módulos de produtos e serviços."""
    conn, cursor = conectar_bd() # Agora conecta através do db_utils

    if conn and cursor:
        criar_tabelas_produtos_servicos(cursor)

        while True:
            print("\n--- Menu Produtos e Serviços ---")
            print("1. Gerenciar Produtos")
            print("2. Gerenciar Serviços")
            print("0. Sair")

            opcao_principal = input("Escolha uma opção: ").strip()

            if opcao_principal == '1':
                while True:
                    print("\n--- Submenu Produtos ---")
                    print("1. Cadastrar Produto")
                    print("2. Listar Produtos")
                    print("3. Atualizar Produto")
                    print("4. Excluir Produto")
                    print("0. Voltar ao Menu Principal")

                    opcao_produto = input("Escolha uma opção: ").strip()
                    if opcao_produto == '1':
                        cadastrar_produto(cursor, conn)
                    elif opcao_produto == '2':
                        # Esta função retorna a lista, você pode exibir no console aqui
                        produtos = listar_produtos(cursor)
                        if produtos:
                            print("\n--- Produtos Cadastrados ---")
                            for p in produtos:
                                print(f"ID: {p['id']} | Nome: {p['nome']} | Preço: R${p['preco']:.2f} | Estoque: {p['estoque']}")
                                if p['descricao']:
                                    print(f"  Descrição: {p['descricao']}")
                                print("-" * 30)
                        else:
                            print("Nenhum produto cadastrado ainda.")
                    elif opcao_produto == '3':
                        atualizar_produto(cursor, conn)
                    elif opcao_produto == '4':
                        excluir_produto(cursor, conn)
                    elif opcao_produto == '0':
                        break
                    else:
                        print("Opção inválida. Tente novamente.")

            elif opcao_principal == '2':
                while True:
                    print("\n--- Submenu Serviços ---")
                    print("1. Cadastrar Serviço")
                    print("2. Listar Serviços")
                    print("3. Atualizar Serviço")
                    print("4. Excluir Serviço")
                    print("0. Voltar ao Menu Principal")

                    opcao_servico = input("Escolha uma opção: ").strip()
                    if opcao_servico == '1':
                        cadastrar_servico(cursor, conn)
                    elif opcao_servico == '2':
                        # Esta função retorna a lista, você pode exibir no console aqui
                        servicos = listar_servicos(cursor)
                        if servicos:
                            print("\n--- Serviços Cadastrados ---")
                            for s in servicos:
                                print(f"ID: {s['id']} | Nome: {s['nome']} | Preço: R${s['preco']:.2f}")
                                if s['descricao']:
                                    print(f"  Descrição: {s['descricao']}")
                                print("-" * 30)
                        else:
                            print("Nenhum serviço cadastrado ainda.")
                    elif opcao_servico == '3':
                        atualizar_servico(cursor, conn)
                    elif opcao_servico == '4':
                        excluir_servico(cursor, conn)
                    elif opcao_servico == '0':
                        break
                    else:
                        print("Opção inválida. Tente novamente.")

            elif opcao_principal == '0':
                print("Saindo do módulo de produtos e serviços.")
                break
            else:
                print("Opção inválida. Tente novamente.")

        fechar_bd(conn)

if __name__ == "__main__":
    main()