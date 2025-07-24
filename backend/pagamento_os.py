import sqlite3
from datetime import datetime
from db_utils import conectar_bd, fechar_bd
# --- Importações necessárias dos outros módulos ---
# Estas importações devem estar no topo do seu arquivo.
from ordem_servico import registrar_historico_status, gerar_mensagem_status

# --- Funções de Conexão com o Banco de Dados (centralizadas ou replicadas) ---
#def conectar_bd(nome_banco="assistencia_tecnica.db"):
#    """
#    Conecta ao banco de dados SQLite. Se o banco não existir, ele será criado.
#    Retorna o objeto de conexão e o cursor.
#    """
#    conn = None
#    try:
#        conn = sqlite3.connect(nome_banco)
#        conn.row_factory = sqlite3.Row # Permite acessar colunas por nome
#        cursor = conn.cursor()
#        return conn, cursor
#    except sqlite3.Error as e:
#        print(f"Erro ao conectar ao banco de dados: {e}")
#        return None, None
#
#def fechar_bd(conn):
#   """Fecha a conexão com o banco de dados."""
#   if conn:
#       conn.close()

# --- Funções de Pagamento ---

def registrar_pagamento_os(cursor, conn):
    """
    Permite registrar o pagamento de uma Ordem de Serviço.
    Só pode ser feito se a OS estiver no status 'Serviço pronto' ou 'Aguardando pagamento'.
    Atualiza o valor total (com desconto), forma de pagamento, parcelamento e data de pagamento.
    Muda o status da OS para 'Finalizando' ou 'Aguardando pagamento' (se ainda não estiver).
    """
    print("\n--- Registrar Pagamento de OS ---")
    os_id_str = input("Digite o ID da OS para registrar o pagamento: ").strip()
    if not os_id_str.isdigit():
        print("ID inválido. Por favor, digite um número.")
        return

    os_id = int(os_id_str)

    # Verifica o status da OS e busca informações essenciais
    cursor.execute("SELECT id, status, valor_total, tipo_equipamento, cliente_id FROM ordens_servico WHERE id = ?", (os_id,))
    os_info = cursor.fetchone()

    if not os_info:
        print(f"OS nº {os_id} não encontrada.")
        return
    
    # Busca informações do cliente para as mensagens
    cursor.execute("SELECT * FROM clientes WHERE id = ?", (os_info['cliente_id'],))
    cliente_info = cursor.fetchone()

    # Se a OS não estiver nos status permitidos para pagamento
    if os_info['status'] not in ("Serviço pronto", "Aguardando pagamento"):
        print(f"Erro: A OS nº {os_id} está com status '{os_info['status']}'.")
        print("O pagamento só pode ser registrado para OSs com status 'Serviço pronto' ou 'Aguardando pagamento'.")
        return

    valor_atual = os_info['valor_total']
    if valor_atual is None: # Garante que valor_atual é um número, mesmo se for nulo no BD
        valor_atual = 0.0

    print(f"Valor atual do serviço para OS nº {os_id}: R${valor_atual:.2f}")

    desconto = 0.0
    while True:
        desconto_str = input("Aplicar Desconto (R$, ex: 10.00, ou 0 para nenhum): ").strip()
        if not desconto_str:
            desconto_str = "0" # Assume 0 se vazio
        try:
            desconto = float(desconto_str)
            if desconto < 0:
                print("Desconto não pode ser negativo.")
                continue
            if desconto > valor_atual:
                print("Desconto não pode ser maior que o valor total.")
                continue
            break
        except ValueError:
            print("Valor de desconto inválido. Digite um número.")
    
    valor_final = valor_atual - desconto
    print(f"Valor a pagar (com desconto): R${valor_final:.2f}")

    print("\nFormas de Pagamento:")
    print("1. Dinheiro")
    print("2. PIX")
    print("3. Cartão de Débito")
    print("4. Cartão de Crédito")
    formas_pagamento = {
        '1': 'Dinheiro', '2': 'PIX', '3': 'Cartão de Débito', '4': 'Cartão de Crédito'
    }
    while True:
        escolha_forma = input("Escolha a forma de pagamento (1-4): ").strip()
        if escolha_forma in formas_pagamento:
            forma_pagamento = formas_pagamento[escolha_forma]
            break
        else:
            print("Opção inválida.")
    
    parcelamento = "À vista"
    if forma_pagamento == 'Cartão de Crédito':
        parcelamento = input("Parcelamento (ex: 3x, 6x, à vista): ").strip()
        if not parcelamento:
            parcelamento = "À vista" # Padrão se não informado

    data_pagamento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Lógica para atualização do status programática
    # Se a OS está em "Serviço pronto", move para "Aguardando pagamento" antes de finalizar.
    if os_info['status'] == "Serviço pronto":
        try:
            status_anterior_para_aguardando = os_info['status']
            cursor.execute("""
                UPDATE ordens_servico
                SET status = ?
                WHERE id = ?
            """, ("Aguardando pagamento", os_id))
            conn.commit()
            registrar_historico_status(cursor, conn, os_id, status_anterior_para_aguardando, "Aguardando pagamento")
            
            # Gerar e exibir a mensagem de "Aguardando pagamento"
            os_info_para_msg = {'id': os_id, 'tipo_equipamento': os_info['tipo_equipamento'], 'valor_total': valor_final}
            print("\n--- Mensagem Automática para o Cliente ---")
            print(gerar_mensagem_status(os_info_para_msg, cliente_info, "Aguardando pagamento"))
            print("------------------------------------------")

            print(f"Status da OS nº {os_id} atualizado para 'Aguardando pagamento'.")
        except sqlite3.Error as e:
            print(f"Erro ao atualizar status para 'Aguardando pagamento': {e}")
            return # Aborta o registro de pagamento se a mudança de status falhar

    # O status final da OS será "Finalizando" após o registro dos detalhes do pagamento
    novo_status_final = "Finalizando"

    # Bloco principal de atualização da OS com os detalhes do pagamento e status final
    try:
        cursor.execute("""
            UPDATE ordens_servico
            SET valor_total = ?,
                desconto = ?,
                forma_pagamento = ?,
                parcelamento = ?,
                data_pagamento = ?,
                status = ?
            WHERE id = ?
        """, (valor_final, desconto, forma_pagamento, parcelamento, data_pagamento, novo_status_final, os_id))
        conn.commit()
        print(f"Pagamento da OS nº {os_id} registrado com sucesso!")
        print(f"Valor Final: R${valor_final:.2f} | Forma: {forma_pagamento} | Parcelamento: {parcelamento}")

        # Registra o histórico de finalização e gera a mensagem "Finalizando"
        # Para ser mais robusto, buscamos o status ATUAL da OS antes de registrar "Finalizando"
        # Isso garante que pegamos o status correto caso a OS tenha mudado para "Aguardando pagamento"
        # no bloco acima.
        cursor.execute("SELECT status FROM ordens_servico WHERE id = ?", (os_id,))
        status_antes_de_finalizar = cursor.fetchone()['status']

        registrar_historico_status(cursor, conn, os_id, status_antes_de_finalizar, novo_status_final)
        
        print("\n--- Mensagem Automática para o Cliente ---")
        os_info_final = {'id': os_id, 'tipo_equipamento': os_info['tipo_equipamento'], 'valor_total': valor_final} # Usar valor_final aqui
        print(gerar_mensagem_status(os_info_final, cliente_info, novo_status_final))
        print("------------------------------------------")


    except sqlite3.Error as e:
        print(f"Erro ao registrar pagamento: {e}")

# --- Função Principal para Execução ---
def main():
    """Menu para gerenciar pagamentos."""
    conn, cursor = conectar_bd()

    if conn and cursor:
        # Nota: As colunas de pagamento devem ter sido adicionadas à tabela ordens_servico
        # executando o script 'ordem_servico.py' uma vez após a sua edição.
        
        while True:
            print("\n--- Menu Pagamento ---")
            print("1. Registrar Pagamento de OS")
            print("0. Sair")

            opcao = input("Escolha uma opção: ").strip()

            if opcao == '1':
                registrar_pagamento_os(cursor, conn)
            elif opcao == '0':
                print("Saindo do módulo de pagamentos.")
                break
            else:
                print("Opção inválida. Tente novamente.")
        
        fechar_bd(conn)

if __name__ == "__main__":
    main()