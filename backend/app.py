# backend/app.py
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from db_utils import conectar_bd, fechar_bd
# Importe suas funções existentes do back-end
from modulo_clientes import (
    conectar_bd, fechar_bd, criar_tabela_clientes,
    listar_clientes, buscar_cliente # Manter estas para uso nas APIs
)
from ordem_servico import (
    criar_tabelas_os, # Para garantir que as tabelas de OS são criadas
    listar_oss, visualizar_detalhes_os, # Funções de leitura
    registrar_historico_status, gerar_mensagem_status, # Funções utilitárias
    calcular_valor_total_os # Para recalcular o valor na atualização de status
)
from produtos_servicos import (
    criar_tabelas_produtos_servicos, # Para garantir que as tabelas de produtos/serviços são criadas
    cadastrar_produto, listar_produtos, atualizar_produto, excluir_produto,
    cadastrar_servico, listar_servicos, atualizar_servico, excluir_servico
)

#@app.route('/api/checklist_perguntas', methods=['GET'])
def get_checklist_perguntas():
    """
    API para retornar perguntas de checklist baseadas no tipo de equipamento.
    Exemplo: GET /api/checklist_perguntas?tipo_equipamento=Notebook
    """
    tipo_equipamento = request.args.get('tipo_equipamento')
    
    if not tipo_equipamento:
        return jsonify({"message": "O parâmetro 'tipo_equipamento' é obrigatório."}), 400

    perguntas = []
    # Lógica replicada/adaptada da função 'realizar_checklist' de ordem_servico.py
    # para ser usada aqui como uma API que retorna as perguntas.

    if "notebook" in tipo_equipamento.lower():
        perguntas = [
            {"pergunta": "Notebook acompanha a fonte de alimentação?", "tipo": "select", "opcoes": ["Sim", "Não"]},
            {"pergunta": "Notebook liga?", "tipo": "select", "opcoes": ["Sim", "Não"]},
            {"pergunta": "Se liga, tem imagem?", "tipo": "select", "opcoes": ["Sim", "Não", "Não se aplica"]},
            {"pergunta": "Se liga, teclado funciona?", "tipo": "select", "opcoes": ["Sim", "Não", "Não se aplica"]},
            {"pergunta": "Se liga, periféricos (USB, áudio) OK?", "tipo": "select", "opcoes": ["Sim", "Não", "Não se aplica"]},
            {"pergunta": "Avarias visíveis (campo aberto)", "tipo": "textarea"} # Campo aberto final
        ]
    elif "impressora" in tipo_equipamento.lower():
        perguntas = [
            {"pergunta": "Impressora liga?", "tipo": "select", "opcoes": ["Sim", "Não"]},
            {"pergunta": "Puxa papel?", "tipo": "select", "opcoes": ["Sim", "Não"]},
            {"pergunta": "Imprime colorido?", "tipo": "select", "opcoes": ["Sim", "Não", "Não se aplica"]},
            {"pergunta": "Conexões (USB/Rede) OK?", "tipo": "select", "opcoes": ["Sim", "Não", "Não se aplica"]},
            {"pergunta": "Avarias visíveis (campo aberto)", "tipo": "textarea"}
        ]
    else: # Checklist genérico para outros tipos ou se não houver um específico
        perguntas = [
            {"pergunta": f"{tipo_equipamento} liga?", "tipo": "select", "opcoes": ["Sim", "Não"]},
            {"pergunta": "Há avarias visíveis?", "tipo": "select", "opcoes": ["Sim", "Não"]},
            {"pergunta": "Acessórios acompanham?", "tipo": "text"}, # Campo de texto livre para quais acessórios
            {"pergunta": "Avarias visíveis (campo aberto)", "tipo": "textarea"}
        ]
    
    return jsonify(perguntas), 200

app = Flask(__name__)
CORS(app) # Habilita o CORS para todas as rotas, permitindo acesso do frontend

# --- Rotas da API para Módulo de Clientes ---

@app.route('/api/clientes', methods=['GET'])
def get_clientes():
    """
    API para listar todos os clientes ou buscar clientes por termo.
    Exemplo: GET /api/clientes ou GET /api/clientes?busca=termo
    """
    conn, cursor = conectar_bd()
    if not conn:
        return jsonify({"message": "Erro ao conectar ao banco de dados"}), 500

    termo_busca = request.args.get('busca') # Pega o parâmetro 'busca' da URL
    
    try:
        if termo_busca:
            clientes = buscar_cliente(cursor, termo_busca)
        else:
            clientes = listar_clientes(cursor)
        
        # Converte os objetos Row do SQLite para dicionários para jsonify
        clientes_list = [dict(cliente) for cliente in clientes]
        return jsonify(clientes_list), 200
    except sqlite3.Error as e:
        print(f"Erro ao listar clientes via API: {e}")
        return jsonify({"message": f"Erro interno ao buscar clientes: {e}"}), 500
    finally:
        fechar_bd(conn)

@app.route('/api/clientes', methods=['POST'])
def add_cliente():
    """
    API para cadastrar um novo cliente.
    Espera um JSON no corpo da requisição com os dados do cliente.
    """
    conn, cursor = conectar_bd()
    if not conn:
        return jsonify({"message": "Erro ao conectar ao banco de dados"}), 500

    data = request.get_json() # Pega o JSON enviado pelo frontend

    if not data:
        fechar_bd(conn)
        return jsonify({"message": "Dados do cliente são obrigatórios"}), 400
    
    tipo_pessoa = data.get('tipo_pessoa')
    whatsapp = data.get('whatsapp')

    if not tipo_pessoa or tipo_pessoa not in ['PF', 'PJ']:
        fechar_bd(conn)
        return jsonify({"message": "Tipo de pessoa inválido (deve ser 'PF' ou 'PJ')"}), 400
    if not whatsapp:
        fechar_bd(conn)
        return jsonify({"message": "WhatsApp é obrigatório"}), 400

    try:
        if tipo_pessoa == 'PF':
            nome = data.get('nome')
            cpf = data.get('cpf')
            data_nascimento = data.get('data_nascimento')
            if not (nome and cpf and data_nascimento):
                fechar_bd(conn)
                return jsonify({"message": "Nome, CPF e Data de Nascimento são obrigatórios para PF"}), 400
            
            cursor.execute("""
                INSERT INTO clientes (tipo_pessoa, nome, cpf, data_nascimento, whatsapp)
                VALUES (?, ?, ?, ?, ?)
            """, (tipo_pessoa, nome, cpf, data_nascimento, whatsapp))
            conn.commit()
            cliente_id = cursor.lastrowid
            fechar_bd(conn)
            return jsonify({"message": "Cliente PF cadastrado com sucesso!", "id": cliente_id}), 201

        elif tipo_pessoa == 'PJ':
            razao_social = data.get('razao_social')
            cnpj = data.get('cnpj')
            responsavel = data.get('responsavel')
            if not (razao_social and cnpj and responsavel):
                fechar_bd(conn)
                return jsonify({"message": "Razão Social, CNPJ e Responsável são obrigatórios para PJ"}), 400
            
            cursor.execute("""
                INSERT INTO clientes (tipo_pessoa, razao_social, cnpj, responsavel, whatsapp)
                VALUES (?, ?, ?, ?, ?)
            """, (tipo_pessoa, razao_social, cnpj, responsavel, whatsapp))
            conn.commit()
            cliente_id = cursor.lastrowid
            fechar_bd(conn)
            return jsonify({"message": "Cliente PJ cadastrado com sucesso!", "id": cliente_id}), 201

    except sqlite3.IntegrityError as e:
        fechar_bd(conn)
        if "UNIQUE constraint failed: clientes.cpf" in str(e):
            return jsonify({"message": "Erro: CPF já cadastrado."}), 409
        elif "UNIQUE constraint failed: clientes.cnpj" in str(e):
            return jsonify({"message": "Erro: CNPJ já cadastrado."}), 409
        return jsonify({"message": f"Erro de integridade do banco de dados: {e}"}), 400
    except sqlite3.Error as e:
        fechar_bd(conn)
        return jsonify({"message": f"Erro ao cadastrar cliente: {e}"}), 500

# --- Rotas da API para Módulo de Ordens de Serviço ---

@app.route('/api/ordens_servico', methods=['GET'])
def get_ordens_servico():
    """
    API para listar todas as Ordens de Serviço.
    Pode aceitar filtros por status ou cliente_id.
    Exemplo: GET /api/ordens_servico ou GET /api/ordens_servico?status=Em%20aberto&cliente_id=1
    """
    conn, cursor = conectar_bd()
    if not conn:
        return jsonify({"message": "Erro ao conectar ao banco de dados"}), 500

    status = request.args.get('status')
    cliente_id_str = request.args.get('cliente_id')
    cliente_id = int(cliente_id_str) if cliente_id_str and cliente_id_str.isdigit() else None

    try:
        oss = listar_oss(cursor, status=status, cliente_id=cliente_id)
        os_list = [dict(os_item) for os_item in oss]
        return jsonify(os_list), 200
    except sqlite3.Error as e:
        print(f"Erro ao listar OSs via API: {e}")
        return jsonify({"message": f"Erro interno ao buscar ordens de serviço: {e}"}), 500
    finally:
        fechar_bd(conn)

@app.route('/api/ordens_servico', methods=['POST'])
def add_ordem_servico():
    """
    API para abrir uma nova Ordem de Serviço.
    Espera um JSON no corpo da requisição com os dados da OS e do checklist.
    """
    conn, cursor = conectar_bd()
    if not conn:
        return jsonify({"message": "Erro ao conectar ao banco de dados"}), 500

    data = request.get_json()
    if not data:
        fechar_bd(conn)
        return jsonify({"message": "Dados da Ordem de Serviço são obrigatórios"}), 400

    cliente_id = data.get('cliente_id')
    tipo_equipamento = data.get('tipo_equipamento')
    descricao_problema = data.get('descricao_problema')
    checklist_respostas = data.get('checklist') # Espera uma lista de {'pergunta': '...', 'resposta': '...'}

    if not cliente_id or not tipo_equipamento:
        fechar_bd(conn)
        return jsonify({"message": "ID do cliente e Tipo de Equipamento são obrigatórios."}), 400
    
    cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
    cliente_selecionado = cursor.fetchone()
    if not cliente_selecionado:
        fechar_bd(conn)
        return jsonify({"message": f"Cliente com ID {cliente_id} não encontrado."}), 404

    data_abertura = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_inicial = "Em aberto"

    try:
        cursor.execute("""
            INSERT INTO ordens_servico (cliente_id, tipo_equipamento, descricao_problema, data_abertura, status)
            VALUES (?, ?, ?, ?, ?)
        """, (cliente_id, tipo_equipamento, descricao_problema, data_abertura, status_inicial))
        os_id = cursor.lastrowid
        conn.commit()

        registrar_historico_status(cursor, conn, os_id, None, status_inicial)

        if checklist_respostas:
            for item in checklist_respostas:
                pergunta = item.get('pergunta')
                resposta = item.get('resposta')
                if pergunta and resposta:
                    cursor.execute("""
                        INSERT INTO checklist_os (os_id, pergunta, resposta)
                        VALUES (?, ?, ?)
                    """, (os_id, pergunta, resposta))
            conn.commit()

        fechar_bd(conn)
        return jsonify({
            "message": f"Ordem de Serviço nº {os_id} aberta com sucesso!",
            "os_id": os_id,
            "cliente_whatsapp": cliente_selecionado['whatsapp'],
            "mensagem_automatica": gerar_mensagem_status({'id': os_id, 'tipo_equipamento': tipo_equipamento, 'valor_total': 0.0}, dict(cliente_selecionado), status_inicial)
        }), 201

    except sqlite3.Error as e:
        fechar_bd(conn)
        print(f"Erro ao abrir OS via API: {e}")
        return jsonify({"message": f"Erro interno ao abrir Ordem de Serviço: {e}"}), 500

@app.route('/api/ordens_servico/<int:os_id>', methods=['GET'])
def get_detalhes_os(os_id):
    """
    API para visualizar detalhes de uma OS específica.
    Exemplo: GET /api/ordens_servico/1
    """
    conn, cursor = conectar_bd()
    if not conn:
        return jsonify({"message": "Erro ao conectar ao banco de dados"}), 500

    try:
        os_info = visualizar_detalhes_os(cursor, os_id)
        
        if not os_info:
            return jsonify({"message": f"OS nº {os_id} não encontrada."}), 404

        os_dict = dict(os_info)

        cursor.execute("SELECT pergunta, resposta FROM checklist_os WHERE os_id = ?", (os_id,))
        checklist = [dict(item) for item in cursor.fetchall()]

        cursor.execute("""
            SELECT ip.quantidade, ip.preco_unitario, p.nome AS produto_nome
            FROM itens_os_produtos ip
            JOIN produtos p ON ip.produto_id = p.id
            WHERE ip.os_id = ?
        """, (os_id,))
        produtos_os = [dict(item) for item in cursor.fetchall()]

        cursor.execute("""
            SELECT isv.preco_unitario, s.nome AS servico_nome
            FROM itens_os_servicos isv
            JOIN servicos s ON isv.servico_id = s.id
            WHERE isv.os_id = ?
        """, (os_id,))
        servicos_os = [dict(item) for item in cursor.fetchall()]
        
        cursor.execute("SELECT status_anterior, status_novo, data_mudanca FROM historico_status_os WHERE os_id = ? ORDER BY data_mudanca", (os_id,))
        historico = [dict(item) for item in cursor.fetchall()]


        os_dict['checklist'] = checklist
        os_dict['produtos_utilizados'] = produtos_os
        os_dict['servicos_realizados'] = servicos_os
        os_dict['historico_status'] = historico

        return jsonify(os_dict), 200
    except sqlite3.Error as e:
        print(f"Erro ao obter detalhes da OS via API: {e}")
        return jsonify({"message": f"Erro interno ao buscar detalhes da Ordem de Serviço: {e}"}), 500
    finally:
        fechar_bd(conn)

@app.route('/api/ordens_servico/<int:os_id>/status', methods=['PUT'])
def update_os_status(os_id):
    """
    API para atualizar o status de uma OS.
    Espera um JSON com {'novo_status': '...', 'observacoes_tecnico': '...', 'garantia': '...'}.
    """
    conn, cursor = conectar_bd()
    if not conn:
        return jsonify({"message": "Erro ao conectar ao banco de dados"}), 500

    data = request.get_json()
    novo_status = data.get('novo_status')
    observacoes_tecnico = data.get('observacoes_tecnico')
    garantia = data.get('garantia')
    
    if not novo_status:
        fechar_bd(conn)
        return jsonify({"message": "Novo status é obrigatório."}), 400

    cursor.execute("SELECT status, valor_total, tipo_equipamento, cliente_id, data_conclusao, observacoes_tecnico, garantia FROM ordens_servico WHERE id = ?", (os_id,))
    os_atual = cursor.fetchone()

    if not os_atual:
        fechar_bd(conn)
        return jsonify({"message": f"OS nº {os_id} não encontrada."}), 404
    
    cursor.execute("SELECT * FROM clientes WHERE id = ?", (os_atual['cliente_id'],))
    cliente_info = cursor.fetchone()

    status_anterior = os_atual['status']
    data_conclusao = os_atual['data_conclusao'] # Manter o existente, ou None

    current_obs_tecnico = os_atual['observacoes_tecnico'] if os_atual['observacoes_tecnico'] else None
    current_garantia = os_atual['garantia'] if os_atual['garantia'] else None
    current_valor_total = os_atual['valor_total'] if os_atual['valor_total'] is not None else 0.0

    # Atualiza observações se fornecidas, caso contrário, mantém as existentes ou None
    # Se observacoes_tecnico for uma string vazia, defina como None para o banco de dados.
    obs_to_save = observacoes_tecnico if observacoes_tecnico is not None and observacoes_tecnico != "" else current_obs_tecnico
    
    # Faz o mesmo para garantia
    garantia_to_save = garantia if garantia is not None and garantia != "" else current_garantia
    
    # Lógica para data_conclusao e valor_total ao mudar para "Serviço concluído" ou "Serviço pronto"
    if novo_status in ["Serviço concluído", "Serviço pronto"]:
        if not data_conclusao: # Apenas define a data se ainda não foi definida
            data_conclusao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Recalcula o valor total, importante se itens foram adicionados/removidos
        current_valor_total = calcular_valor_total_os(cursor, os_id)
    
    # Se o status anterior era 'Serviço pronto' e o novo é 'Aguardando pagamento' ou 'Finalizando',
    # e o valor total ainda não foi calculado ou é 0, recalcula.
    # Isso é uma redundância, pois o serviço pronto já deve ter calculado,
    # mas garante que o valor_total esteja correto.
    if status_anterior == 'Serviço pronto' and novo_status in ['Aguardando pagamento', 'Finalizando'] and current_valor_total <= 0.0:
        current_valor_total = calcular_valor_total_os(cursor, os_id)


    try:
        cursor.execute("""
            UPDATE ordens_servico
            SET status = ?, observacoes_tecnico = ?, garantia = ?, data_conclusao = ?, valor_total = ?
            WHERE id = ?
        """, (novo_status, obs_to_save, garantia_to_save, data_conclusao, current_valor_total, os_id))
        conn.commit()

        registrar_historico_status(cursor, conn, os_id, status_anterior, novo_status)

        os_info_para_msg = {
            'id': os_id,
            'tipo_equipamento': os_atual['tipo_equipamento'],
            'valor_total': current_valor_total # Passa o valor_total atualizado
        }
        mensagem_automatica = gerar_mensagem_status(os_info_para_msg, dict(cliente_info), novo_status)

        fechar_bd(conn)
        return jsonify({
            "message": f"Status da OS nº {os_id} atualizado para '{novo_status}'!",
            "new_status": novo_status,
            "mensagem_automatica": mensagem_automatica
        }), 200

    except sqlite3.Error as e:
        fechar_bd(conn)
        print(f"Erro ao atualizar status da OS: {e}")
        return jsonify({"message": f"Erro interno ao atualizar status da OS: {e}"}), 500


# --- APIs para Gerenciamento de Itens da OS (Produtos e Serviços) ---
# Estas APIs são para adicionar produtos/serviços já existentes a UMA OS.
# As APIs para CRUD dos PRODUTOS e SERVIÇOS em si estão logo abaixo.
@app.route('/api/ordens_servico/<int:os_id>/itens/produtos', methods=['POST'])
def add_item_os_produto(os_id):
    """
    API para adicionar um produto a uma OS.
    Espera um JSON com {'produto_id': int, 'quantidade': int}.
    """
    conn, cursor = conectar_bd()
    if not conn:
        return jsonify({"message": "Erro ao conectar ao banco de dados"}), 500

    data = request.get_json()
    produto_id = data.get('produto_id')
    quantidade = data.get('quantidade')

    if not produto_id or not quantidade or quantidade <= 0:
        fechar_bd(conn)
        return jsonify({"message": "ID do produto e quantidade válida são obrigatórios."}), 400

    try:
        # Verifica se a OS existe
        cursor.execute("SELECT id FROM ordens_servico WHERE id = ?", (os_id,))
        if not cursor.fetchone():
            fechar_bd(conn)
            return jsonify({"message": f"OS nº {os_id} não encontrada."}), 404

        # Busca informações do produto
        cursor.execute("SELECT nome, preco, estoque FROM produtos WHERE id = ?", (produto_id,))
        produto = cursor.fetchone()
        if not produto:
            fechar_bd(conn)
            return jsonify({"message": f"Produto com ID {produto_id} não encontrado."}), 404
        
        if quantidade > produto['estoque']:
            fechar_bd(conn)
            return jsonify({"message": f"Estoque insuficiente para {produto['nome']}. Disponível: {produto['estoque']}"}), 400

        preco_unitario = produto['preco']

        cursor.execute("""
            INSERT INTO itens_os_produtos (os_id, produto_id, quantidade, preco_unitario)
            VALUES (?, ?, ?, ?)
        """, (os_id, produto_id, quantidade, preco_unitario))
        
        # Atualiza estoque
        cursor.execute("UPDATE produtos SET estoque = estoque - ? WHERE id = ?", (quantidade, produto_id))
        conn.commit()

        # Recalcula e atualiza o valor total da OS
        novo_valor_total = calcular_valor_total_os(cursor, os_id)
        cursor.execute("UPDATE ordens_servico SET valor_total = ? WHERE id = ?", (novo_valor_total, os_id))
        conn.commit()

        fechar_bd(conn)
        return jsonify({"message": f"{quantidade}x '{produto['nome']}' adicionado à OS nº {os_id}. Novo valor total: R${novo_valor_total:.2f}"}), 201
    except sqlite3.Error as e:
        fechar_bd(conn)
        print(f"Erro ao adicionar produto à OS via API: {e}")
        return jsonify({"message": f"Erro interno ao adicionar produto à OS: {e}"}), 500

@app.route('/api/ordens_servico/<int:os_id>/itens/servicos', methods=['POST'])
def add_item_os_servico(os_id):
    """
    API para adicionar um serviço a uma OS.
    Espera um JSON com {'servico_id': int}.
    """
    conn, cursor = conectar_bd()
    if not conn:
        return jsonify({"message": "Erro ao conectar ao banco de dados"}), 500

    data = request.get_json()
    servico_id = data.get('servico_id')

    if not servico_id:
        fechar_bd(conn)
        return jsonify({"message": "ID do serviço é obrigatório."}), 400

    try:
        # Verifica se a OS existe
        cursor.execute("SELECT id FROM ordens_servico WHERE id = ?", (os_id,))
        if not cursor.fetchone():
            fechar_bd(conn)
            return jsonify({"message": f"OS nº {os_id} não encontrada."}), 404

        # Busca informações do serviço
        cursor.execute("SELECT nome, preco FROM servicos WHERE id = ?", (servico_id,))
        servico = cursor.fetchone()
        if not servico:
            fechar_bd(conn)
            return jsonify({"message": f"Serviço com ID {servico_id} não encontrado."}), 404
        
        preco_unitario = servico['preco']

        cursor.execute("""
            INSERT INTO itens_os_servicos (os_id, servico_id, preco_unitario)
            VALUES (?, ?, ?)
        """, (os_id, servico_id, preco_unitario))
        conn.commit()

        # Recalcula e atualiza o valor total da OS
        novo_valor_total = calcular_valor_total_os(cursor, os_id)
        cursor.execute("UPDATE ordens_servico SET valor_total = ? WHERE id = ?", (novo_valor_total, os_id))
        conn.commit()

        fechar_bd(conn)
        return jsonify({"message": f"Serviço '{servico['nome']}' adicionado à OS nº {os_id}. Novo valor total: R${novo_valor_total:.2f}"}), 201
    except sqlite3.Error as e:
        fechar_bd(conn)
        print(f"Erro ao adicionar serviço à OS via API: {e}")
        return jsonify({"message": f"Erro interno ao adicionar serviço à OS: {e}"}), 500
    finally:
        fechar_bd(conn)

# --- Rotas da API para Módulo de Produtos ---
# Estas são para gerenciar os produtos como catálogo, não para adicionar a OS.

@app.route('/api/produtos', methods=['GET'])
def get_produtos():
    """API para listar todos os produtos."""
    conn, cursor = conectar_bd()
    if not conn:
        return jsonify({"message": "Erro ao conectar ao banco de dados"}), 500
    try:
        produtos = listar_produtos(cursor) # Sua função listar_produtos já retorna a lista
        produtos_list = [dict(p) for p in produtos]
        return jsonify(produtos_list), 200
    except sqlite3.Error as e:
        print(f"Erro ao listar produtos via API: {e}")
        return jsonify({"message": f"Erro interno ao buscar produtos: {e}"}), 500
    finally:
        fechar_bd(conn)

@app.route('/api/produtos', methods=['POST'])
def add_produto():
    """API para cadastrar um novo produto."""
    conn, cursor = conectar_bd()
    if not conn:
        return jsonify({"message": "Erro ao conectar ao banco de dados"}), 500
    data = request.get_json()
    if not data:
        return jsonify({"message": "Dados do produto são obrigatórios"}), 400

    nome = data.get('nome')
    descricao = data.get('descricao')
    preco = data.get('preco')
    estoque = data.get('estoque')

    if not nome or preco is None or estoque is None:
        return jsonify({"message": "Nome, preço e estoque são obrigatórios."}), 400
    if not isinstance(preco, (int, float)) or preco < 0:
        return jsonify({"message": "Preço inválido."}), 400
    if not isinstance(estoque, int) or estoque < 0:
        return jsonify({"message": "Estoque inválido."}), 400
    
    try:
        # A função cadastrar_produto original interage via console.
        # Estamos reimplementando a lógica aqui para interagir com a API.
        cursor.execute("""
            INSERT INTO produtos (nome, descricao, preco, estoque)
            VALUES (?, ?, ?, ?)
        """, (nome, descricao, preco, estoque))
        conn.commit()
        produto_id = cursor.lastrowid
        return jsonify({"message": f"Produto '{nome}' cadastrado com sucesso!", "id": produto_id}), 201
    except sqlite3.IntegrityError:
        return jsonify({"message": f"Erro: Produto com nome '{nome}' já existe."}), 409
    except sqlite3.Error as e:
        print(f"Erro ao cadastrar produto via API: {e}")
        return jsonify({"message": f"Erro interno ao cadastrar produto: {e}"}), 500
    finally:
        fechar_bd(conn)

@app.route('/api/produtos/<int:produto_id>', methods=['PUT'])
def update_produto(produto_id):
    """API para atualizar um produto existente."""
    conn, cursor = conectar_bd()
    if not conn:
        return jsonify({"message": "Erro ao conectar ao banco de dados"}), 500
    data = request.get_json()
    if not data:
        return jsonify({"message": "Dados para atualização são obrigatórios"}), 400

    cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
    produto_existente = cursor.fetchone()
    if not produto_existente:
        return jsonify({"message": f"Produto com ID {produto_id} não encontrado."}), 404

    nome = data.get('nome', produto_existente['nome'])
    descricao = data.get('descricao', produto_existente['descricao'])
    preco = data.get('preco', produto_existente['preco'])
    estoque = data.get('estoque', produto_existente['estoque'])

    if preco is not None and (not isinstance(preco, (int, float)) or preco < 0):
        return jsonify({"message": "Preço inválido."}), 400
    if estoque is not None and (not isinstance(estoque, int) or estoque < 0):
        return jsonify({"message": "Estoque inválido."}), 400
    
    try:
        cursor.execute("""
            UPDATE produtos
            SET nome = ?, descricao = ?, preco = ?, estoque = ?
            WHERE id = ?
        """, (nome, descricao, preco, estoque, produto_id))
        conn.commit()
        return jsonify({"message": f"Produto '{nome}' (ID: {produto_id}) atualizado com sucesso!"}), 200
    except sqlite3.IntegrityError:
        return jsonify({"message": f"Erro: Produto com nome '{nome}' já existe."}), 409
    except sqlite3.Error as e:
        print(f"Erro ao atualizar produto via API: {e}")
        return jsonify({"message": f"Erro interno ao atualizar produto: {e}"}), 500
    finally:
        fechar_bd(conn)

@app.route('/api/produtos/<int:produto_id>', methods=['DELETE'])
def delete_produto(produto_id):
    """API para excluir um produto."""
    conn, cursor = conectar_bd()
    if not conn:
        return jsonify({"message": "Erro ao conectar ao banco de dados"}), 500
    try:
        cursor.execute("SELECT id, nome FROM produtos WHERE id = ?", (produto_id,))
        produto_existente = cursor.fetchone()
        if not produto_existente:
            return jsonify({"message": f"Produto com ID {produto_id} não encontrado."}), 404
        
        cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        conn.commit()
        return jsonify({"message": f"Produto '{produto_existente['nome']}' (ID: {produto_id}) excluído com sucesso!"}), 200
    except sqlite3.Error as e:
        print(f"Erro ao excluir produto via API: {e}")
        return jsonify({"message": f"Erro interno ao excluir produto: {e}"}), 500
    finally:
        fechar_bd(conn)

# --- Rotas da API para Módulo de Serviços ---
# Estas são para gerenciar os serviços como catálogo, não para adicionar a OS.

@app.route('/api/servicos', methods=['GET'])
def get_servicos():
    """API para listar todos os serviços."""
    conn, cursor = conectar_bd()
    if not conn:
        return jsonify({"message": "Erro ao conectar ao banco de dados"}), 500
    try:
        servicos = listar_servicos(cursor) # Sua função listar_servicos já retorna a lista
        servicos_list = [dict(s) for s in servicos]
        return jsonify(servicos_list), 200
    except sqlite3.Error as e:
        print(f"Erro ao listar serviços via API: {e}")
        return jsonify({"message": f"Erro interno ao buscar serviços: {e}"}), 500
    finally:
        fechar_bd(conn)

@app.route('/api/servicos', methods=['POST'])
def add_servico():
    """API para cadastrar um novo serviço."""
    conn, cursor = conectar_bd()
    if not conn:
        return jsonify({"message": "Erro ao conectar ao banco de dados"}), 500
    data = request.get_json()
    if not data:
        return jsonify({"message": "Dados do serviço são obrigatórios"}), 400

    nome = data.get('nome')
    descricao = data.get('descricao')
    preco = data.get('preco')

    if not nome or preco is None:
        return jsonify({"message": "Nome e preço são obrigatórios."}), 400
    if not isinstance(preco, (int, float)) or preco < 0:
        return jsonify({"message": "Preço inválido."}), 400
    
    try:
        cursor.execute("""
            INSERT INTO servicos (nome, descricao, preco)
            VALUES (?, ?, ?)
        """, (nome, descricao, preco))
        conn.commit()
        servico_id = cursor.lastrowid
        return jsonify({"message": f"Serviço '{nome}' cadastrado com sucesso!", "id": servico_id}), 201
    except sqlite3.IntegrityError:
        return jsonify({"message": f"Erro: Serviço com nome '{nome}' já existe."}), 409
    except sqlite3.Error as e:
        print(f"Erro ao cadastrar serviço via API: {e}")
        return jsonify({"message": f"Erro interno ao cadastrar serviço: {e}"}), 500
    finally:
        fechar_bd(conn)

@app.route('/api/servicos/<int:servico_id>', methods=['PUT'])
def update_servico(servico_id):
    """API para atualizar um serviço existente."""
    conn, cursor = conectar_bd()
    if not conn:
        return jsonify({"message": "Erro ao conectar ao banco de dados"}), 500
    data = request.get_json()
    if not data:
        return jsonify({"message": "Dados para atualização são obrigatórios"}), 400

    cursor.execute("SELECT * FROM servicos WHERE id = ?", (servico_id,))
    servico_existente = cursor.fetchone()
    if not servico_existente:
        return jsonify({"message": f"Serviço com ID {servico_id} não encontrado."}), 404

    nome = data.get('nome', servico_existente['nome'])
    descricao = data.get('descricao', servico_existente['descricao'])
    preco = data.get('preco', servico_existente['preco'])

    if preco is not None and (not isinstance(preco, (int, float)) or preco < 0):
        return jsonify({"message": "Preço inválido."}), 400
    
    try:
        cursor.execute("""
            UPDATE servicos
            SET nome = ?, descricao = ?, preco = ?
            WHERE id = ?
        """, (nome, descricao, preco, servico_id))
        conn.commit()
        return jsonify({"message": f"Serviço '{nome}' (ID: {servico_id}) atualizado com sucesso!"}), 200
    except sqlite3.IntegrityError:
        return jsonify({"message": f"Erro: Serviço com nome '{nome}' já existe."}), 409
    except sqlite3.Error as e:
        print(f"Erro ao atualizar serviço via API: {e}")
        return jsonify({"message": f"Erro interno ao atualizar serviço: {e}"}), 500
    finally:
        fechar_bd(conn)

@app.route('/api/servicos/<int:servico_id>', methods=['DELETE'])
def delete_servico(servico_id):
    """API para excluir um serviço."""
    conn, cursor = conectar_bd()
    if not conn:
        return jsonify({"message": "Erro ao conectar ao banco de dados"}), 500
    try:
        cursor.execute("SELECT id, nome FROM servicos WHERE id = ?", (servico_id,))
        servico_existente = cursor.fetchone()
        if not servico_existente:
            return jsonify({"message": f"Serviço com ID {servico_id} não encontrado."}), 404
        
        cursor.execute("DELETE FROM servicos WHERE id = ?", (servico_id,))
        conn.commit()
        return jsonify({"message": f"Serviço '{servico_existente['nome']}' (ID: {servico_id}) excluído com sucesso!"}), 200
    except sqlite3.Error as e:
        print(f"Erro ao excluir serviço via API: {e}")
        return jsonify({"message": f"Erro interno ao excluir serviço: {e}"}), 500
    finally:
        fechar_bd(conn)


# --- APIs de Listagem para Produtos e Serviços para Adicionar na OS (para dropdowns/buscas) ---
# Essas são endpoints auxiliares que retornam listas simples de produtos/serviços para seletores.

@app.route('/api/lista_produtos', methods=['GET'])
def get_lista_produtos_simples():
    """API para listar produtos com ID, nome e preço (para dropdowns em OS)."""
    conn, cursor = conectar_bd()
    if not conn:
        return jsonify({"message": "Erro ao conectar ao banco de dados"}), 500
    try:
        cursor.execute("SELECT id, nome, preco, estoque FROM produtos ORDER BY nome")
        produtos = cursor.fetchall()
        produtos_list = [dict(p) for p in produtos]
        return jsonify(produtos_list), 200
    except sqlite3.Error as e:
        print(f"Erro ao listar produtos simples via API: {e}")
        return jsonify({"message": f"Erro interno ao buscar produtos: {e}"}), 500
    finally:
        fechar_bd(conn)

@app.route('/api/lista_servicos', methods=['GET'])
def get_lista_servicos_simples():
    """API para listar serviços com ID, nome e preço (para dropdowns em OS)."""
    conn, cursor = conectar_bd()
    if not conn:
        return jsonify({"message": "Erro ao conectar ao banco de dados"}), 500
    try:
        cursor.execute("SELECT id, nome, preco FROM servicos ORDER BY nome")
        servicos = cursor.fetchall()
        servicos_list = [dict(s) for s in servicos]
        return jsonify(servicos_list), 200
    except sqlite3.Error as e:
        print(f"Erro ao listar serviços simples via API: {e}")
        return jsonify({"message": f"Erro interno ao buscar serviços: {e}"}), 500
    finally:
        fechar_bd(conn)


# --- APIs para Módulo de Pagamento ---
# Já incluídas anteriormente, mas aqui para o contexto completo.

@app.route('/api/ordens_servico/<int:os_id>/pagamento', methods=['PUT'])
def process_pagamento_os(os_id):
    """
    API para registrar o pagamento de uma Ordem de Serviço.
    Espera um JSON com:
    {
        "desconto": float,
        "forma_pagamento": "Dinheiro" | "PIX" | "Cartão de Débito" | "Cartão de Crédito",
        "parcelamento": "À vista" | "Nx" (ex: "3x")
    }
    """
    conn, cursor = conectar_bd()
    if not conn:
        return jsonify({"message": "Erro ao conectar ao banco de dados"}), 500

    data = request.get_json()
    desconto = data.get('desconto', 0.0)
    forma_pagamento = data.get('forma_pagamento')
    parcelamento = data.get('parcelamento', 'À vista')

    if not forma_pagamento:
        fechar_bd(conn)
        return jsonify({"message": "Forma de pagamento é obrigatória."}), 400

    cursor.execute("SELECT status, valor_total, tipo_equipamento, cliente_id FROM ordens_servico WHERE id = ?", (os_id,))
    os_info = cursor.fetchone()

    if not os_info:
        fechar_bd(conn)
        return jsonify({"message": f"OS nº {os_id} não encontrada."}), 404
    
    if os_info['status'] not in ("Serviço pronto", "Aguardando pagamento"):
        fechar_bd(conn)
        return jsonify({"message": f"Erro: OS nº {os_id} está com status '{os_info['status']}'. O pagamento só pode ser registrado para OSs com status 'Serviço pronto' ou 'Aguardando pagamento'."}), 400
    
    valor_atual = os_info['valor_total'] if os_info['valor_total'] is not None else 0.0

    if not (0 <= desconto <= valor_atual):
        fechar_bd(conn)
        return jsonify({"message": "Valor de desconto inválido ou excede o valor total da OS."}), 400

    valor_final = valor_atual - desconto
    data_pagamento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("SELECT * FROM clientes WHERE id = ?", (os_info['cliente_id'],))
    cliente_info = cursor.fetchone()

    try:
        status_anterior = os_info['status']
        novo_status_final = "Finalizando"

        if status_anterior == "Serviço pronto":
            cursor.execute("UPDATE ordens_servico SET status = ? WHERE id = ?", ("Aguardando pagamento", os_id))
            conn.commit()
            registrar_historico_status(cursor, conn, os_id, status_anterior, "Aguardando pagamento")
            
            msg_aguardando = gerar_mensagem_status({'id': os_id, 'tipo_equipamento': os_info['tipo_equipamento'], 'valor_total': valor_final}, dict(cliente_info), "Aguardando pagamento")
            print(f"DEBUG: Mensagem Aguardando Pagamento: {msg_aguardando}")


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

        registrar_historico_status(cursor, conn, os_id, status_anterior, novo_status_final)
        
        mensagem_final = gerar_mensagem_status({'id': os_id, 'tipo_equipamento': os_info['tipo_equipamento'], 'valor_total': valor_final}, dict(cliente_info), novo_status_final)

        fechar_bd(conn)
        return jsonify({
            "message": f"Pagamento da OS nº {os_id} registrado com sucesso! Status final: '{novo_status_final}'.",
            "valor_final": f"R${valor_final:.2f}",
            "forma_pagamento": forma_pagamento,
            "parcelamento": parcelamento,
            "data_pagamento": data_pagamento,
            "mensagem_automatica": mensagem_final
        }), 200

    except sqlite3.Error as e:
        fechar_bd(conn)
        print(f"Erro ao registrar pagamento via API: {e}")
        return jsonify({"message": f"Erro interno ao registrar pagamento: {e}"}), 500


# --- Inicialização do Banco de Dados ---
# Garante que as tabelas sejam criadas quando o app iniciar
with app.app_context():
    conn, cursor = conectar_bd()
    if conn and cursor:
        criar_tabela_clientes(cursor)
        criar_tabelas_os(cursor)
        criar_tabelas_produtos_servicos(cursor) # Garante que as tabelas de produtos e serviços são criadas
        conn.commit()
        fechar_bd(conn)
    else:
        print("Aviso: Não foi possível conectar ao banco de dados na inicialização para criar tabelas.")


# --- Execução do Aplicativo ---
if __name__ == '__main__':
    app.run(debug=True)