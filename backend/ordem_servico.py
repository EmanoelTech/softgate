import sqlite3
from datetime import datetime
from db_utils import conectar_bd, fechar_bd
# --- Funções de Conexão com o Banco de Dados ---
# Replicadas aqui para que o módulo possa ser executado independentemente para testes.
# Em um projeto real, idealmente estariam em um arquivo utilitário e seriam importadas.
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
#
# --- 1. Modelagem das Tabelas para Ordem de Serviço ---
def criar_tabelas_os(cursor):
    """
    Cria as tabelas relacionadas à Ordem de Serviço, se não existirem.
    Inclui Ordem_Servico, Itens_OS_Produtos, Itens_OS_Servicos, Checklist_OS, Historico_Status_OS.
    Também adiciona colunas para os detalhes de pagamento à tabela ordens_servico.
    """
    try:
        # Tabela Ordem_Servico
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ordens_servico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                tipo_equipamento TEXT NOT NULL,
                descricao_problema TEXT,
                data_abertura TEXT NOT NULL, -- YYYY-MM-DD HH:MM:SS
                data_conclusao TEXT,
                status TEXT NOT NULL,
                observacoes_tecnico TEXT,
                valor_total REAL DEFAULT 0.0,
                garantia TEXT, -- Ex: 90 dias, 1 ano
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            );
        """)
        print("Tabela 'ordens_servico' verificada/criada com sucesso.")

        # Adicionar novas colunas se não existirem (para pagamento)
        try:
            cursor.execute("ALTER TABLE ordens_servico ADD COLUMN desconto REAL DEFAULT 0.0;")
            print("Coluna 'desconto' adicionada a 'ordens_servico'.")
        except sqlite3.OperationalError:
            pass # Coluna 'desconto' já existe

        try:
            cursor.execute("ALTER TABLE ordens_servico ADD COLUMN forma_pagamento TEXT;")
            print("Coluna 'forma_pagamento' adicionada a 'ordens_servico'.")
        except sqlite3.OperationalError:
            pass # Coluna 'forma_pagamento' já existe

        try:
            cursor.execute("ALTER TABLE ordens_servico ADD COLUMN parcelamento TEXT;")
            print("Coluna 'parcelamento' adicionada a 'ordens_servico'.")
        except sqlite3.OperationalError:
            pass # Coluna 'parcelamento' já existe

        try:
            cursor.execute("ALTER TABLE ordens_servico ADD COLUMN data_pagamento TEXT;")
            print("Coluna 'data_pagamento' adicionada a 'ordens_servico'.")
        except sqlite3.OperationalError:
            pass # Coluna 'data_pagamento' já existe

        # Tabela Itens_OS_Produtos (produtos utilizados na OS)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS itens_os_produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                os_id INTEGER NOT NULL,
                produto_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                preco_unitario REAL NOT NULL,
                FOREIGN KEY (os_id) REFERENCES ordens_servico(id),
                FOREIGN KEY (produto_id) REFERENCES produtos(id)
            );
        """)
        print("Tabela 'itens_os_produtos' verificada/criada com sucesso.")

        # Tabela Itens_OS_Servicos (serviços realizados na OS)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS itens_os_servicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                os_id INTEGER NOT NULL,
                servico_id INTEGER NOT NULL,
                preco_unitario REAL NOT NULL,
                FOREIGN KEY (os_id) REFERENCES ordens_servico(id),
                FOREIGN KEY (servico_id) REFERENCES servicos(id)
            );
        """)
        print("Tabela 'itens_os_servicos' verificada/criada com sucesso.")

        # Tabela Checklist_OS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checklist_os (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                os_id INTEGER NOT NULL,
                pergunta TEXT NOT NULL,
                resposta TEXT NOT NULL, -- Sim/Não/Texto
                FOREIGN KEY (os_id) REFERENCES ordens_servico(id)
            );
        """)
        print("Tabela 'checklist_os' verificada/criada com sucesso.")

        # Tabela Historico_Status_OS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historico_status_os (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                os_id INTEGER NOT NULL,
                status_anterior TEXT,
                status_novo TEXT NOT NULL,
                data_mudanca TEXT NOT NULL, -- YYYY-MM-DD HH:MM:SS
                FOREIGN KEY (os_id) REFERENCES ordens_servico(id)
            );
        """)
        print("Tabela 'historico_status_os' verificada/criada com sucesso.")

    except sqlite3.Error as e:
        print(f"Erro ao criar tabelas da OS: {e}")

# --- 2. Funções CRUD e Operacionais para Ordem de Serviço ---

def gerar_mensagem_status(os_info, cliente_info, status_novo):
    """
    Simula a geração de mensagens automáticas baseadas no status da OS.
    Futuramente, esta função seria mais sofisticada e integrada com API de mensagens.
    """
    nome_empresa = "SoftGate Eletrônica" # Substitua pelo nome da sua empresa

    mensagens = {
        "Em aberto": {
            "PF": f"Olá {cliente_info['nome']}, sua Ordem de Serviço nº {os_info['id']} foi registrada com sucesso para seu {os_info['tipo_equipamento']}. Em breve nossa equipe iniciará o atendimento técnico. Qualquer dúvida, estamos à disposição. {nome_empresa}",
            "PJ": f"Prezado(a) {cliente_info['razao_social']}, informamos que a Ordem de Serviço nº {os_info['id']} para o(s) equipamento(s) {os_info['tipo_equipamento']} foi aberta com sucesso. Em breve um de nossos técnicos dará continuidade ao atendimento."
        },
        "Aguardando aprovação": {
            "PF": f"Oi {cliente_info['nome']}, finalizamos a avaliação do seu {os_info['tipo_equipamento']}. O serviço está aguardando sua aprovação para prosseguirmos. Clique aqui para visualizar: [LINK_OS]",
            "PJ": f"{cliente_info['razao_social']}, o equipamento {os_info['tipo_equipamento']} já foi avaliado e está aguardando aprovação para iniciar o serviço. Visualize os detalhes: [LINK_OS]"
        },
        "Aprovado": f"O serviço foi aprovado com sucesso! Em breve iniciaremos os procedimentos técnicos no equipamento.",
        "Aguardando peças": f"Olá! A OS nº {os_info['id']} está aguardando a chegada de peças para continuidade do serviço. Assim que tivermos uma atualização, entraremos em contato.",
        "Na bancada": f"Oi {cliente_info['nome']}, seu equipamento está agora sendo atendido por um técnico especializado. Assim que houver atualização no diagnóstico, informaremos.",
        "Em testes": f"Seu equipamento está em fase de testes para garantir a qualidade do serviço realizado. Em breve retornaremos com novidades.",
        "Serviço concluído": f"O serviço técnico foi concluído com sucesso! Em breve você poderá retirar seu equipamento ou solicitar a entrega. Veja os detalhes da garantia, peças utilizadas e valores finais no link: [LINK_OS]",
        "Aguardando pagamento": {
            "PF": f"Olá {cliente_info['nome']}, seu equipamento já está pronto e aguardando o pagamento para ser liberado. Valor final: R$ {os_info['valor_total']:.2f}. Formas de pagamento: PIX, cartão ou dinheiro. [LINK_OS]",
            "PJ": f"Prezado(a) {cliente_info['razao_social']}, seu equipamento já está pronto e aguardando o pagamento para ser liberado. Valor final: R$ {os_info['valor_total']:.2f}. Formas de pagamento: PIX, cartão ou dinheiro. [LINK_OS]"
        },
        "Abandonado": f"Atenção, {cliente_info['nome']}. Sua OS nº {os_info['id']} está com mais de [X] dias sem movimentação. Consideramos a possibilidade de abandono. Entre em contato com urgência para evitar taxas ou perda da garantia.",
        "Retorno com garantia": f"Oi {cliente_info['nome']}, recebemos seu equipamento novamente com solicitação de garantia. Ele está sendo priorizado com base no atendimento anterior. Entraremos em contato com atualizações.",
        "Retorno sem garantia": f"Olá {cliente_info['nome']}, recebemos novamente seu equipamento, mas o prazo de garantia expirou. Será aberta uma nova OS e feita nova avaliação técnica.",
        "Finalizando": f"Tudo pronto! Sua OS está sendo finalizada e os documentos de garantia e pagamento estão sendo organizados. Obrigado por confiar na {nome_empresa}!"
    }

    mensagem = mensagens.get(status_novo, "Mensagem padrão: Status atualizado.")
    if isinstance(mensagem, dict):
        return mensagem.get(cliente_info['tipo_pessoa'], "Mensagem padrão: Status atualizado.")
    return mensagem


def abrir_os(cursor, conn):
    """
    Abre uma nova Ordem de Serviço.
    Requer a seleção de um cliente existente e a realização do checklist inicial.
    """
    print("\n--- Abrir Nova Ordem de Serviço ---")
    cliente_id = None
    while True:
        termo_cliente = input("Digite o ID, Nome, CPF ou CNPJ do cliente: ").strip()
        if not termo_cliente:
            print("Termo de busca não pode ser vazio.")
            continue

        # Tentar buscar cliente pelo ID primeiro, se for numérico
        if termo_cliente.isdigit():
            cursor.execute("SELECT * FROM clientes WHERE id = ?", (int(termo_cliente),))
            clientes_encontrados = cursor.fetchall()
        else: # Senão, buscar por nome/documento
            termo_busca_like = f"%{termo_cliente}%"
            cursor.execute("""
                SELECT * FROM clientes
                WHERE nome LIKE ? OR razao_social LIKE ? OR cpf LIKE ? OR cnpj LIKE ?
            """, (termo_busca_like, termo_busca_like, termo_busca_like, termo_busca_like))
            clientes_encontrados = cursor.fetchall()

        if not clientes_encontrados:
            print("Nenhum cliente encontrado. Por favor, tente novamente ou cadastre o cliente.")
            # Aqui, idealmente, teríamos um botão/opção para cadastrar novo cliente.
            # Por enquanto, vamos pedir para tentar de novo ou voltar.
            continuar = input("Deseja tentar buscar outro cliente? (s/N): ").strip().lower()
            if continuar != 's':
                return # Aborta a abertura da OS
        else:
            if len(clientes_encontrados) > 1:
                print("Múltiplos clientes encontrados. Por favor, seja mais específico ou escolha um ID:")
                for c in clientes_encontrados:
                    print(f"ID: {c['id']} | Tipo: {c['tipo_pessoa']} | {'Nome: ' + c['nome'] if c['tipo_pessoa'] == 'PF' else 'Razão Social: ' + c['razao_social']} | WhatsApp: {c['whatsapp']}")
                while True:
                    try:
                        selecao_id = int(input("Digite o ID do cliente desejado: ").strip())
                        cliente_selecionado = next((c for c in clientes_encontrados if c['id'] == selecao_id), None)
                        if cliente_selecionado:
                            cliente_id = cliente_selecionado['id']
                            print(f"Cliente selecionado: {cliente_selecionado['nome'] if cliente_selecionado['tipo_pessoa'] == 'PF' else cliente_selecionado['razao_social']}")
                            break
                        else:
                            print("ID inválido na seleção. Tente novamente.")
                    except ValueError:
                        print("Entrada inválida. Digite um número.")
            else:
                cliente_selecionado = clientes_encontrados[0]
                cliente_id = cliente_selecionado['id']
                print(f"Cliente selecionado: {cliente_selecionado['nome'] if cliente_selecionado['tipo_pessoa'] == 'PF' else cliente_selecionado['razao_social']}")
            break

    tipo_equipamento = input("Tipo de Equipamento (Notebook, Celular, Impressora, Rede, etc.): ").strip()
    if not tipo_equipamento:
        print("Tipo de equipamento é obrigatório.")
        return

    descricao_problema = input("Descrição Inicial do Problema: ").strip()

    data_abertura = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_inicial = "Em aberto"

    try:
        cursor.execute("""
            INSERT INTO ordens_servico (cliente_id, tipo_equipamento, descricao_problema, data_abertura, status)
            VALUES (?, ?, ?, ?, ?)
        """, (cliente_id, tipo_equipamento, descricao_problema, data_abertura, status_inicial))
        os_id = cursor.lastrowid # Pega o ID da OS recém-criada
        conn.commit()
        print(f"Ordem de Serviço nº {os_id} aberta com sucesso!")

        # Adicionar histórico de status
        registrar_historico_status(cursor, conn, os_id, None, status_inicial)

        # Gerar e exibir mensagem inicial
        print("\n--- Mensagem Automática para o Cliente ---")
        print(gerar_mensagem_status({'id': os_id, 'tipo_equipamento': tipo_equipamento, 'valor_total': 0.0}, cliente_selecionado, status_inicial))
        print("------------------------------------------")

        # Checklist inicial
        print("\n--- Realizando Checklist Inicial ---")
        realizar_checklist(cursor, conn, os_id, tipo_equipamento)

    except sqlite3.Error as e:
        print(f"Erro ao abrir OS: {e}")

def registrar_historico_status(cursor, conn, os_id, status_anterior, status_novo):
    """Registra uma mudança de status no histórico da OS."""
    data_mudanca = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute("""
            INSERT INTO historico_status_os (os_id, status_anterior, status_novo, data_mudanca)
            VALUES (?, ?, ?, ?)
        """, (os_id, status_anterior, status_novo, data_mudanca))
        conn.commit()
        print(f"Histórico: Status da OS {os_id} alterado para '{status_novo}'.")
    except sqlite3.Error as e:
        print(f"Erro ao registrar histórico de status: {e}")

def realizar_checklist(cursor, conn, os_id, tipo_equipamento):
    """
    Executa o checklist específico para o tipo de equipamento.
    Os exemplos são baseados no notebook, mas pode ser expandido.
    """
    print(f"\nChecklist para {tipo_equipamento}:")

    # Exemplo de checklist para Notebook
    if "notebook" in tipo_equipamento.lower():
        perguntas = [
            "Notebook acompanha a fonte de alimentação? (Sim/Não)",
            "Notebook liga? (Sim/Não)",
            "Se liga, tem imagem? (Sim/Não/Não se aplica)",
            "Se liga, teclado funciona? (Sim/Não/Não se aplica)",
            "Se liga, periféricos (USB, áudio) OK? (Sim/Não/Não se aplica)"
        ]
    else: # Checklist genérico para outros tipos ou se não houver um específico
        perguntas = [
            f"{tipo_equipamento} liga? (Sim/Não)",
            "Há avarias visíveis? (Sim/Não)",
            "Acessórios acompanham? (Sim/Não/Quais)"
        ]

    for pergunta in perguntas:
        resposta = input(f"- {pergunta}: ").strip()
        try:
            cursor.execute("""
                INSERT INTO checklist_os (os_id, pergunta, resposta)
                VALUES (?, ?, ?)
            """, (os_id, pergunta, resposta))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao registrar checklist: {e}")

    avarias = input("Avarias gerais (campo aberto): ").strip()
    if avarias:
        try:
            cursor.execute("""
                INSERT INTO checklist_os (os_id, pergunta, resposta)
                VALUES (?, ?, ?)
            """, (os_id, "Avarias visíveis (campo aberto)", avarias))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao registrar avarias: {e}")
    print("Checklist concluído.")


def listar_oss(cursor, status=None, cliente_id=None):
    """Lista as Ordens de Serviço com filtros opcionais."""
    print("\n--- Ordens de Serviço ---")
    query = "SELECT os.*, c.nome AS cliente_nome, c.razao_social AS cliente_razao_social, c.tipo_pessoa FROM ordens_servico os JOIN clientes c ON os.cliente_id = c.id"
    params = []
    conditions = []

    if status:
        conditions.append("os.status = ?")
        params.append(status)
    if cliente_id:
        conditions.append("os.cliente_id = ?")
        params.append(cliente_id)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY os.data_abertura DESC"

    try:
        cursor.execute(query, params)
        oss = cursor.fetchall()
        if not oss:
            print("Nenhuma OS encontrada com os critérios informados.")
            return []

        for os in oss:
            cliente_nome_exibicao = os['cliente_nome'] if os['tipo_pessoa'] == 'PF' else os['cliente_razao_social']
            print(f"OS ID: {os['id']} | Cliente: {cliente_nome_exibicao} | Equipamento: {os['tipo_equipamento']} | Status: {os['status']}")
            print(f"  Abertura: {os['data_abertura']} | Valor Total: R${os['valor_total']:.2f}")
            print("-" * 40)
        return oss
    except sqlite3.Error as e:
        print(f"Erro ao listar OSs: {e}")
        return []

def visualizar_detalhes_os(cursor, os_id):
    """Visualiza todos os detalhes de uma OS específica."""
    print(f"\n--- Detalhes da Ordem de Serviço nº {os_id} ---")
    try:
        cursor.execute("""
            SELECT os.*, c.nome AS cliente_nome, c.razao_social AS cliente_razao_social, c.tipo_pessoa, c.whatsapp
            FROM ordens_servico os
            JOIN clientes c ON os.cliente_id = c.id
            WHERE os.id = ?
        """, (os_id,))
        os_info = cursor.fetchone()

        if not os_info:
            print(f"OS nº {os_id} não encontrada.")
            return

        cliente_nome_exibicao = os_info['cliente_nome'] if os_info['tipo_pessoa'] == 'PF' else os_info['razao_social']

        print(f"ID da OS: {os_info['id']}")
        print(f"Cliente: {cliente_nome_exibicao} ({os_info['tipo_pessoa']}) - WhatsApp: {os_info['whatsapp']}")
        print(f"Equipamento: {os_info['tipo_equipamento']}")
        print(f"Problema Reportado: {os_info['descricao_problema']}")
        print(f"Data de Abertura: {os_info['data_abertura']}")
        print(f"Status Atual: {os_info['status']}")
        print(f"Observações do Técnico: {os_info['observacoes_tecnico'] if os_info['observacoes_tecnico'] else 'N/A'}")
        print(f"Valor Total: R${os_info['valor_total']:.2f}")
        print(f"Garantia: {os_info['garantia'] if os_info['garantia'] else 'N/A'}")
        print(f"Data de Conclusão: {os_info['data_conclusao'] if os_info['data_conclusao'] else 'N/A'}")

        print("\n--- Checklist ---")
        cursor.execute("SELECT pergunta, resposta FROM checklist_os WHERE os_id = ?", (os_id,))
        checklist = cursor.fetchall()
        if checklist:
            for item in checklist:
                print(f"- {item['pergunta']}: {item['resposta']}")
        else:
            print("Nenhum item de checklist registrado.")

        print("\n--- Produtos Utilizados ---")
        cursor.execute("""
            SELECT ip.quantidade, ip.preco_unitario, p.nome AS produto_nome
            FROM itens_os_produtos ip
            JOIN produtos p ON ip.produto_id = p.id
            WHERE ip.os_id = ?
        """, (os_id,))
        produtos_os = cursor.fetchall()
        if produtos_os:
            for item in produtos_os:
                print(f"- {item['quantidade']}x {item['produto_nome']} (R${item['preco_unitario']:.2f} cada)")
        else:
            print("Nenhum produto utilizado.")

        print("\n--- Serviços Realizados ---")
        cursor.execute("""
            SELECT isv.preco_unitario, s.nome AS servico_nome
            FROM itens_os_servicos isv
            JOIN servicos s ON isv.servico_id = s.id
            WHERE isv.os_id = ?
        """, (os_id,))
        servicos_os = cursor.fetchall()
        if servicos_os:
            for item in servicos_os:
                print(f"- {item['servico_nome']} (R${item['preco_unitario']:.2f})")
        else:
            print("Nenhum serviço realizado.")

        print("\n--- Histórico de Status ---")
        cursor.execute("SELECT status_anterior, status_novo, data_mudanca FROM historico_status_os WHERE os_id = ? ORDER BY data_mudanca", (os_id,))
        historico = cursor.fetchall()
        if historico:
            for item in historico:
                print(f"  {item['data_mudanca']}: De '{item['status_anterior'] if item['status_anterior'] else 'N/A'}' para '{item['status_novo']}'")
        else:
            print("Nenhum histórico de status.")

        return os_info # Retorna as informações da OS para uso em outras funções
    except sqlite3.Error as e:
        print(f"Erro ao visualizar detalhes da OS: {e}")
        return None

def atualizar_status_os(cursor, conn, os_id):
    """Permite atualizar o status de uma OS e gera a mensagem automática."""
    print(f"\n--- Atualizar Status da OS nº {os_id} ---")
    cursor.execute("SELECT status, cliente_id, tipo_equipamento, valor_total FROM ordens_servico WHERE id = ?", (os_id,))
    os_atual = cursor.fetchone()

    if not os_atual:
        print(f"OS nº {os_id} não encontrada.")
        return

    cursor.execute("SELECT * FROM clientes WHERE id = ?", (os_atual['cliente_id'],))
    cliente_info = cursor.fetchone()

    status_permitidos = [
        "Em aberto", "Aguardando aprovação", "Aprovado", "Aguardando peças",
        "Na bancada", "Em testes", "Serviço concluído", "Serviço pronto",
        "Aguardando pagamento", "Abandonado", "Retorno com garantia", "Retorno sem garantia", "Finalizando"
    ]
    print(f"Status atual: {os_atual['status']}")
    print("Opções de status:")
    for i, status in enumerate(status_permitidos):
        print(f"{i+1}. {status}")

    while True:
        try:
            escolha = int(input("Digite o número do novo status: ").strip())
            if 1 <= escolha <= len(status_permitidos):
                novo_status = status_permitidos[escolha - 1]
                break
            else:
                print("Opção inválida.")
        except ValueError:
            print("Entrada inválida. Digite um número.")

    if novo_status == os_atual['status']:
        print("Status não foi alterado.")
        return

   # Acessa diretamente e verifica se é None. Se for, atribui um valor padrão.
    observacoes_tecnico = os_atual['observacoes_tecnico'] if 'observacoes_tecnico' in os_atual and os_atual['observacoes_tecnico'] is not None else None
    garantia = os_atual['garantia'] if 'garantia' in os_atual and os_atual['garantia'] is not None else None
    data_conclusao = os_atual['data_conclusao'] if 'data_conclusao' in os_atual and os_atual['data_conclusao'] is not None else None
    valor_total = os_atual['valor_total'] if 'valor_total' in os_atual and os_atual['valor_total'] is not None else 0.0 # Valor padrão 0.0 para total

    if novo_status == "Na bancada":
        obs_input = input("Adicionar/Atualizar Observação do Técnico: ").strip()
        if obs_input:
            observacoes_tecnico = obs_input
    elif novo_status == "Serviço pronto":
        # Permite adicionar produtos e serviços ANTES de finalizar
        print("\n--- Adicionar Produtos/Serviços (Opcional) ---")
        adicionar_itens_os(cursor, conn, os_id)
        # Calcula valor total (pode ser recalculado automaticamente aqui)
        valor_total = calcular_valor_total_os(cursor, os_id)
        garantia = input("Definir Prazo de Garantia (ex: 90 dias, 1 ano): ").strip() or garantia
        data_conclusao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elif novo_status == "Serviço concluído":
        # Mensagem pode ser enviada, mas edição de itens só se for "Serviço pronto"
        pass # Nenhuma ação especial no código backend aqui, a menos que queira reforçar data_conclusao
    elif novo_status == "Aguardando pagamento":
        # O valor total já deve estar calculado do "Serviço pronto"
        # Aqui podemos ter a tela de pagamento em um módulo futuro
        pass
    # Adicionar outras lógicas para cada status conforme necessário

    try:
        cursor.execute("""
            UPDATE ordens_servico
            SET status = ?, observacoes_tecnico = ?, garantia = ?, data_conclusao = ?, valor_total = ?
            WHERE id = ?
        """, (novo_status, observacoes_tecnico, garantia, data_conclusao, valor_total, os_id))
        conn.commit()
        print(f"Status da OS nº {os_id} atualizado para '{novo_status}' com sucesso!")

        # Registrar histórico
        registrar_historico_status(cursor, conn, os_id, os_atual['status'], novo_status)

        # Gerar e exibir mensagem automática
        os_info_atualizada = {'id': os_id, 'tipo_equipamento': os_atual['tipo_equipamento'], 'valor_total': valor_total}
        print("\n--- Mensagem Automática para o Cliente ---")
        print(gerar_mensagem_status(os_info_atualizada, cliente_info, novo_status))
        print("------------------------------------------")

    except sqlite3.Error as e:
        print(f"Erro ao atualizar status da OS: {e}")

def adicionar_itens_os(cursor, conn, os_id):
    """Permite adicionar produtos e serviços a uma OS."""
    print(f"\n--- Adicionar Itens à OS nº {os_id} ---")

    while True:
        print("\nO que deseja adicionar?")
        print("1. Produto")
        print("2. Serviço")
        print("0. Voltar")
        escolha = input("Opção: ").strip()

        if escolha == '1':
            # Adicionar Produto
            cursor.execute("SELECT id, nome, preco, estoque FROM produtos ORDER BY nome")
            produtos_disponiveis = cursor.fetchall()
            if not produtos_disponiveis:
                print("Nenhum produto cadastrado para adicionar.")
                continue
            print("\nProdutos disponíveis:")
            for p in produtos_disponiveis:
                print(f"ID: {p['id']} | Nome: {p['nome']} | Preço: R${p['preco']:.2f} | Estoque: {p['estoque']}")

            while True:
                try:
                    prod_id = int(input("Digite o ID do produto a adicionar (0 para cancelar): ").strip())
                    if prod_id == 0:
                        break
                    produto_selecionado = next((p for p in produtos_disponiveis if p['id'] == prod_id), None)
                    if not produto_selecionado:
                        print("ID de produto inválido.")
                        continue
                    
                    quantidade = int(input(f"Quantidade de '{produto_selecionado['nome']}': ").strip())
                    if quantidade <= 0:
                        print("Quantidade deve ser positiva.")
                        continue
                    if quantidade > produto_selecionado['estoque']:
                        print(f"Estoque insuficiente. Disponível: {produto_selecionado['estoque']}")
                        continue
                    
                    preco_unitario = produto_selecionado['preco'] # Pega o preço atual do produto
                    
                    cursor.execute("""
                        INSERT INTO itens_os_produtos (os_id, produto_id, quantidade, preco_unitario)
                        VALUES (?, ?, ?, ?)
                    """, (os_id, prod_id, quantidade, preco_unitario))
                    
                    # Atualizar estoque
                    cursor.execute("UPDATE produtos SET estoque = estoque - ? WHERE id = ?", (quantidade, prod_id))
                    conn.commit()
                    print(f"{quantidade}x '{produto_selecionado['nome']}' adicionado à OS.")
                    break
                except ValueError:
                    print("Entrada inválida. Digite um número.")
                except sqlite3.Error as e:
                    print(f"Erro ao adicionar produto à OS: {e}")
                    break

        elif escolha == '2':
            # Adicionar Serviço
            cursor.execute("SELECT id, nome, preco FROM servicos ORDER BY nome")
            servicos_disponiveis = cursor.fetchall()
            if not servicos_disponiveis:
                print("Nenhum serviço cadastrado para adicionar.")
                continue
            print("\nServiços disponíveis:")
            for s in servicos_disponiveis:
                print(f"ID: {s['id']} | Nome: {s['nome']} | Preço: R${s['preco']:.2f}")

            while True:
                try:
                    serv_id = int(input("Digite o ID do serviço a adicionar (0 para cancelar): ").strip())
                    if serv_id == 0:
                        break
                    servico_selecionado = next((s for s in servicos_disponiveis if s['id'] == serv_id), None)
                    if not servico_selecionado:
                        print("ID de serviço inválido.")
                        continue
                    
                    preco_unitario = servico_selecionado['preco'] # Pega o preço atual do serviço
                    
                    cursor.execute("""
                        INSERT INTO itens_os_servicos (os_id, servico_id, preco_unitario)
                        VALUES (?, ?, ?)
                    """, (os_id, serv_id, preco_unitario))
                    conn.commit()
                    print(f"Serviço '{servico_selecionado['nome']}' adicionado à OS.")
                    break
                except ValueError:
                    print("Entrada inválida. Digite um número.")
                except sqlite3.Error as e:
                    print(f"Erro ao adicionar serviço à OS: {e}")
                    break

        elif escolha == '0':
            break
        else:
            print("Opção inválida.")
    
    # Recalcular e atualizar o valor total na OS principal
    novo_valor_total = calcular_valor_total_os(cursor, os_id)
    cursor.execute("UPDATE ordens_servico SET valor_total = ? WHERE id = ?", (novo_valor_total, os_id))
    conn.commit()
    print(f"Valor total da OS atualizado para R${novo_valor_total:.2f}")

def calcular_valor_total_os(cursor, os_id):
    """Calcula o valor total de uma OS somando produtos e serviços."""
    total_produtos = 0.0
    cursor.execute("SELECT quantidade, preco_unitario FROM itens_os_produtos WHERE os_id = ?", (os_id,))
    produtos = cursor.fetchall()
    for p in produtos:
        total_produtos += p['quantidade'] * p['preco_unitario']

    total_servicos = 0.0
    cursor.execute("SELECT preco_unitario FROM itens_os_servicos WHERE os_id = ?", (os_id,))
    servicos = cursor.fetchall()
    for s in servicos:
        total_servicos += s['preco_unitario']

    return total_produtos + total_servicos

# --- Função Principal para Testar este Módulo ---

def main():
    """Função principal para demonstrar as funcionalidades do módulo de Ordem de Serviço."""
    conn, cursor = conectar_bd()

    if conn and cursor:
        criar_tabelas_os(cursor)

        while True:
            print("\n--- Menu Ordem de Serviço ---")
            print("1. Abrir Nova OS")
            print("2. Listar OSs")
            print("3. Visualizar Detalhes da OS")
            print("4. Atualizar Status da OS")
            print("5. Adicionar Produtos/Serviços à OS (Manualmente)") # Isso seria feito normalmente quando a OS for para "Serviço pronto"
            print("0. Sair")

            opcao = input("Escolha uma opção: ").strip()

            if opcao == '1':
                abrir_os(cursor, conn)
            elif opcao == '2':
                listar_oss(cursor)
            elif opcao == '3':
                os_id = input("Digite o ID da OS para visualizar: ").strip()
                if os_id.isdigit():
                    visualizar_detalhes_os(cursor, int(os_id))
                else:
                    print("ID inválido. Digite um número.")
            elif opcao == '4':
                os_id = input("Digite o ID da OS para atualizar status: ").strip()
                if os_id.isdigit():
                    atualizar_status_os(cursor, conn, int(os_id))
                else:
                    print("ID inválido. Digite um número.")
            elif opcao == '5':
                os_id = input("Digite o ID da OS para adicionar itens: ").strip()
                if os_id.isdigit():
                    adicionar_itens_os(cursor, conn, int(os_id))
                else:
                    print("ID inválido. Digite um número.")
            elif opcao == '0':
                print("Saindo do módulo de Ordem de Serviço.")
                break
            else:
                print("Opção inválida. Por favor, tente novamente.")

        fechar_bd(conn)

if __name__ == "__main__":
    main()