import sqlite3
from datetime import datetime
from db_utils import conectar_bd, fechar_bd
# --- Funções de Conexão com o Banco de Dados ---
# Replicadas aqui por conveniência, mas podem ser centralizadas em um módulo de utilidades.
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

# --- Geração de Mensagens de Aniversário ---

def gerar_mensagem_aniversario(cliente_info):
    """
    Gera a mensagem de aniversário personalizada para Pessoa Física ou Jurídica.
    """
    nome_empresa = "SoftGate Eletrônica" 

    if cliente_info['tipo_pessoa'] == 'PF':
        nome = cliente_info['nome']
        mensagem = (
            f"Feliz Aniversário, {nome}! A equipe da {nome_empresa} deseja muita saúde, "
            f"conquistas e felicidades! Aproveite 10% de desconto em qualquer serviço até o fim da semana!"
        )
    elif cliente_info['tipo_pessoa'] == 'PJ':
        razao_social = cliente_info['razao_social']
        mensagem = (
            f"Parabéns, {razao_social}! Neste dia especial, a equipe da {nome_empresa} parabeniza toda a "
            f"equipe da sua empresa. Desejamos sucesso e crescimento contínuo nos seus negócios! Conte sempre conosco."
        )
    else:
        mensagem = "Tipo de cliente desconhecido para mensagem de aniversário."
    
    return mensagem

def enviar_mensagens_aniversario_hoje():
    """
    Verifica os clientes que fazem aniversário hoje e gera suas mensagens.
    Simula o 'envio' imprimindo no console.
    """
    conn, cursor = conectar_bd()

    if not conn or not cursor:
        print("Não foi possível conectar ao banco de dados para verificar aniversários.")
        return

    hoje = datetime.now()
    mes_atual = hoje.strftime("%m")
    dia_atual = hoje.strftime("%d")

    print(f"\n--- Verificando Aniversariantes do Dia {dia_atual}/{mes_atual} ---")

    try:
        # Busca por Pessoas Físicas que fazem aniversário hoje
        # Extrai o mês e o dia da data_nascimento (AAAA-MM-DD)
        cursor.execute("""
            SELECT id, nome, tipo_pessoa, whatsapp, data_nascimento
            FROM clientes
            WHERE tipo_pessoa = 'PF' AND SUBSTR(data_nascimento, 6, 2) = ? AND SUBSTR(data_nascimento, 9, 2) = ?
        """, (mes_atual, dia_atual))
        aniversariantes_pf = cursor.fetchall()

        # Busca por Pessoas Jurídicas que fazem aniversário hoje
        # Assumimos que o "aniversário" da PJ pode ser a data de abertura do CNPJ
        # (se tivéssemos essa data no cadastro, ou uma data de fundação específica).
        # Para este projeto, como não temos uma data de fundação para PJ,
        # vamos usar uma abordagem simplificada ou ignorar PJ por enquanto.
        # OU, podemos usar a "data de nascimento" do Responsável se quisermos enviar para o contato principal.
        # Por enquanto, vou focar na PF como exemplo principal.
        # Se você tiver uma data para PJ, a query seria similar à PF, adaptando o campo.

        if not aniversariantes_pf:
            print("Nenhum aniversariante encontrado para hoje.")
            # Você pode adicionar a lógica para aniversariantes PJ aqui, se tiver um campo de data
            # e depois combinar com os resultados de PF.
            # Por exemplo:
            # cursor.execute("SELECT id, razao_social, tipo_pessoa, whatsapp FROM clientes WHERE tipo_pessoa = 'PJ' AND ...")
            # aniversariantes_pj = cursor.fetchall()
            # if not aniversariantes_pf and not aniversariantes_pj:
            #     print("Nenhum aniversariante encontrado para hoje.")

        for cliente in aniversariantes_pf:
            print(f"\nGerando mensagem para {cliente['nome']} (ID: {cliente['id']})...")
            mensagem = gerar_mensagem_aniversario(cliente)
            print(f"Mensagem gerada para {cliente['nome']}:")
            print("------------------------------------------------------------------")
            print(mensagem)
            print("------------------------------------------------------------------")
            print(f"Simulando envio para WhatsApp: {cliente['whatsapp']}")

        # Se houver lógica para PJ:
        # for cliente in aniversariantes_pj:
        #     print(f"\nGerando mensagem para {cliente['razao_social']} (ID: {cliente['id']})...")
        #     mensagem = gerar_mensagem_aniversario(cliente)
        #     print(f"Mensagem gerada para {cliente['razao_social']}:")
        #     print("------------------------------------------------------------------")
        #     print(mensagem)
        #     print("------------------------------------------------------------------")
        #     print(f"Simulando envio para WhatsApp: {cliente['whatsapp']}")

    except sqlite3.Error as e:
        print(f"Erro ao buscar aniversariantes: {e}")
    finally:
        fechar_bd(conn)

# --- Função Principal para Execução ---
if __name__ == "__main__":
    # Para testar, você pode criar um cliente com a data de nascimento de hoje
    # Usando o modulo_clientes.py, cadastre um PF com a data de hoje (YYYY-MM-DD)
    # Por exemplo, se hoje é 23 de julho de 2025, use '2000-07-23' ou '1995-07-23'
    # para a Data de Nascimento.
    enviar_mensagens_aniversario_hoje()