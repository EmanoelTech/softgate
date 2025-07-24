// frontend/js/main.js

const API_BASE_URL = 'http://127.0.0.1:5000/api'; // URL base do seu servidor Flask

document.addEventListener('DOMContentLoaded', () => {
    // --- Elementos HTML para Clientes ---
    const tipoPessoaSelect = document.getElementById('tipoPessoa');
    const camposPF = document.getElementById('camposPF');
    const camposPJ = document.getElementById('camposPJ');
    const formCadastroCliente = document.getElementById('form-cadastro-cliente');
    const clientesContainer = document.getElementById('clientes-container');
    const btnRecarregarClientes = document.getElementById('btn-recarregar-clientes');
    const mensagemFeedback = document.getElementById('mensagem-feedback');

    // --- Elementos HTML para Ordens de Serviço ---
    const ossContainer = document.getElementById('oss-container');
    const btnRecarregarOSs = document.getElementById('btn-recarregar-oss');
    const formAbrirOS = document.getElementById('form-abrir-os');
    const mensagemFeedbackOS = document.getElementById('mensagem-feedback-os');
    
    // Mapeamento de seções para facilitar a alternância de visibilidade
    const secoes = {
        listaClientes: document.getElementById('lista-clientes'),
        cadastroCliente: document.getElementById('cadastro-cliente'),
        listaOSs: document.getElementById('lista-oss'),
        aberturaOS: document.getElementById('abertura-os'),
        detalhesOS: document.getElementById('detalhes-os'),
        // Novas seções para Produtos e Serviços
        listaProdutos: document.getElementById('lista-produtos'),
        formProduto: document.getElementById('form-produto'),
        listaServicos: document.getElementById('lista-servicos'),
        formServico: document.getElementById('form-servico')
    };

    // Detalhes da OS e atualização de status
    const osIdDetalheSpan = document.getElementById('os-id-detalhe');
    const osDetalhesConteudoDiv = document.getElementById('os-detalhes-conteudo');
    const novoStatusOSSelect = document.getElementById('novoStatusOS');
    const obsTecnicoOSInput = document.getElementById('obsTecnicoOS');
    const garantiaOSInput = document.getElementById('garantiaOS');
    const btnAtualizarStatusOS = document.getElementById('btn-atualizar-status-os');
    const btnVoltarOSList = document.getElementById('btn-voltar-os-list');
    const mensagemFeedbackStatusOS = document.getElementById('mensagem-feedback-status-os');

    // --- Novos Elementos HTML para Produtos ---
    const produtosContainer = document.getElementById('produtos-container');
    const btnRecarregarProdutos = document.getElementById('btn-recarregar-produtos');
    const formCadastroProduto = document.getElementById('form-cadastro-produto');
    const produtoIdInput = document.getElementById('produtoId');
    const nomeProdutoInput = document.getElementById('nomeProduto');
    const descricaoProdutoInput = document.getElementById('descricaoProduto');
    const precoProdutoInput = document.getElementById('precoProduto');
    const estoqueProdutoInput = document.getElementById('estoqueProduto');
    const btnSalvarProduto = document.getElementById('btn-salvar-produto');
    const btnCancelarProduto = document.getElementById('btn-cancelar-produto');
    const mensagemFeedbackProduto = document.getElementById('mensagem-feedback-produto');

    // --- Novos Elementos HTML para Serviços ---
    const servicosContainer = document.getElementById('servicos-container');
    const btnRecarregarServicos = document.getElementById('btn-recarregar-servicos');
    const formCadastroServico = document.getElementById('form-cadastro-servico');
    const servicoIdInput = document.getElementById('servicoId');
    const nomeServicoInput = document.getElementById('nomeServico');
    const descricaoServicoInput = document.getElementById('descricaoServico');
    const precoServicoInput = document.getElementById('precoServico');
    const btnSalvarServico = document.getElementById('btn-salvar-servico');
    const btnCancelarServico = document.getElementById('btn-cancelar-servico');
    const mensagemFeedbackServico = document.getElementById('mensagem-feedback-servico');


    let currentOsId = null; // Variável para armazenar o ID da OS sendo visualizada/editada


    // --- Funções Auxiliares Comuns ---

    // Função para exibir mensagens de feedback (generalizada para reuso)
    function showFeedback(message, type = 'success', element = mensagemFeedback) {
        if (element) {
            element.textContent = message;
            element.className = `feedback-message ${type}`;
            setTimeout(() => {
                element.textContent = '';
                element.className = 'feedback-message';
            }, 5000); // Mensagem some após 5 segundos
        }
    }

    // Função para ocultar todas as seções e mostrar apenas uma específica
    function showSection(sectionToShow) {
        Object.values(secoes).forEach(section => {
            if (section) { 
                section.classList.add('hidden');
            }
        });
        if (sectionToShow) { 
            sectionToShow.classList.remove('hidden');
        }
    }

    // --- Funções para Clientes ---

    // Função para exibir/ocultar campos PF/PJ no formulário de cadastro de cliente
    if (tipoPessoaSelect) {
        tipoPessoaSelect.addEventListener('change', () => {
            if (tipoPessoaSelect.value === 'PF') {
                if (camposPF) camposPF.classList.remove('hidden');
                if (camposPJ) camposPJ.classList.add('hidden');
                
                if (document.getElementById('nomePF')) document.getElementById('nomePF').setAttribute('required', 'required');
                if (document.getElementById('cpfPF')) document.getElementById('cpfPF').setAttribute('required', 'required');
                if (document.getElementById('dataNascimentoPF')) document.getElementById('dataNascimentoPF').setAttribute('required', 'required');

                if (document.getElementById('razaoSocialPJ')) document.getElementById('razaoSocialPJ').removeAttribute('required');
                if (document.getElementById('cnpjPJ')) document.getElementById('cnpjPJ').removeAttribute('required');
                if (document.getElementById('responsavelPJ')) document.getElementById('responsavelPJ').removeAttribute('required');

            } else if (tipoPessoaSelect.value === 'PJ') {
                if (camposPJ) camposPJ.classList.remove('hidden');
                if (camposPF) camposPF.classList.add('hidden');
                
                if (document.getElementById('razaoSocialPJ')) document.getElementById('razaoSocialPJ').setAttribute('required', 'required');
                if (document.getElementById('cnpjPJ')) document.getElementById('cnpjPJ').setAttribute('required', 'required');
                if (document.getElementById('responsavelPJ')) document.getElementById('responsavelPJ').setAttribute('required', 'required');

                if (document.getElementById('nomePF')) document.getElementById('nomePF').removeAttribute('required');
                if (document.getElementById('cpfPF')) document.getElementById('cpfPF').removeAttribute('required');
                if (document.getElementById('dataNascimentoPF')) document.getElementById('dataNascimentoPF').removeAttribute('required');

            } else {
                if (camposPF) camposPF.classList.add('hidden');
                if (camposPJ) camposPJ.classList.add('hidden');
                
                if (document.getElementById('nomePF')) document.getElementById('nomePF').removeAttribute('required');
                if (document.getElementById('cpfPF')) document.getElementById('cpfPF').removeAttribute('required');
                if (document.getElementById('dataNascimentoPF')) document.getElementById('dataNascimentoPF').removeAttribute('required');
                if (document.getElementById('razaoSocialPJ')) document.getElementById('razaoSocialPJ').removeAttribute('required');
                if (document.getElementById('cnpjPJ')) document.getElementById('cnpjPJ').removeAttribute('required');
                if (document.getElementById('responsavelPJ')) document.getElementById('responsavelPJ').removeAttribute('required');
            }
        });
    }

    // Função para carregar clientes da API
    async function carregarClientes() {
        if (!clientesContainer) { 
            console.error("Element 'clientes-container' not found.");
            return;
        }
        clientesContainer.innerHTML = '<p>Carregando clientes...</p>';
        try {
            const response = await fetch(`${API_BASE_URL}/clientes`);
            const clientes = await response.json();

            clientesContainer.innerHTML = ''; // Limpa o "Carregando..."
            if (clientes.length === 0) {
                clientesContainer.innerHTML = '<p>Nenhum cliente cadastrado ainda.</p>';
                return;
            }

            clientes.forEach(cliente => {
                const clienteCard = document.createElement('div');
                clienteCard.classList.add('cliente-card');
                
                let detalhes = '';
                if (cliente.tipo_pessoa === 'PF') {
                    detalhes = `<strong>Nome:</strong> ${cliente.nome}<br>
                                <strong>CPF:</strong> ${cliente.cpf}<br>
                                <strong>Nascimento:</strong> ${cliente.data_nascimento}<br>`;
                } else if (cliente.tipo_pessoa === 'PJ') {
                    detalhes = `<strong>Razão Social:</strong> ${cliente.razao_social}<br>
                                <strong>CNPJ:</strong> ${cliente.cnpj}<br>
                                <strong>Responsável:</strong> ${cliente.responsavel}<br>`;
                }

                clienteCard.innerHTML = `
                    <h3>ID: ${cliente.id} | Tipo: ${cliente.tipo_pessoa}</h3>
                    <p>
                        ${detalhes}
                        <strong>WhatsApp:</strong> ${cliente.whatsapp}
                    </p>
                `;
                clientesContainer.appendChild(clienteCard);
            });
        } catch (error) {
            console.error('Erro ao carregar clientes:', error);
            if (clientesContainer) { 
                clientesContainer.innerHTML = '<p class="feedback-message error">Erro ao carregar clientes. Verifique o servidor.</p>';
            }
        }
    }

    // Evento para submissão do formulário de cadastro de cliente
    if (formCadastroCliente) { 
        formCadastroCliente.addEventListener('submit', async (event) => {
            event.preventDefault(); // Impede o recarregamento da página

            const formData = new FormData(formCadastroCliente);
            const data = {};
            for (const [key, value] of formData.entries()) {
                const element = formCadastroCliente.elements[key];
                if ((element && !element.closest('.hidden')) || key === 'tipo_pessoa' || key === 'whatsapp') {
                    data[key] = value;
                }
            }
            
            if (data.tipo_pessoa === 'PF') {
                delete data.razao_social;
                delete data.cnpj;
                delete data.responsavel;
            } else if (data.tipo_pessoa === 'PJ') {
                delete data.nome;
                delete data.cpf;
                delete data.data_nascimento;
            } else {
                showFeedback('Por favor, selecione o tipo de pessoa (PF/PJ).', 'error');
                return;
            }

            try {
                const response = await fetch(`${API_BASE_URL}/clientes`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (response.ok) { 
                    showFeedback(result.message, 'success');
                    formCadastroCliente.reset(); 
                    if (tipoPessoaSelect) tipoPessoaSelect.value = ''; 
                    if (camposPF) camposPF.classList.add('hidden'); 
                    if (camposPJ) camposPJ.classList.add('hidden');
                    carregarClientes(); 
                } else { 
                    showFeedback(`Erro: ${result.message}`, 'error');
                }
            } catch (error) {
                console.error('Erro ao cadastrar cliente:', error);
                showFeedback('Erro ao conectar com o servidor para cadastrar cliente.', 'error');
            }
        });
    }


    // --- Funções para Ordens de Serviço ---

    // Função para carregar Ordens de Serviço da API
    async function carregarOSs() {
        if (!ossContainer) { 
            console.error("Element 'oss-container' not found.");
            return;
        }
        ossContainer.innerHTML = '<p>Carregando Ordens de Serviço...</p>';
        try {
            const response = await fetch(`${API_BASE_URL}/ordens_servico`);
            const oss = await response.json();

            ossContainer.innerHTML = '';
            if (oss.length === 0) {
                ossContainer.innerHTML = '<p>Nenhuma Ordem de Serviço cadastrada ainda.</p>';
                return;
            }

            oss.forEach(os => {
                const osCard = document.createElement('div');
                osCard.classList.add('os-card');
                osCard.dataset.osId = os.id; // Armazena o ID da OS no elemento para cliques

                const clienteNomeExibicao = os.tipo_pessoa === 'PF' ? os.cliente_nome : os.cliente_razao_social;
                const statusClass = os.status.toLowerCase().replace(/ /g, '-'); 

                osCard.innerHTML = `
                    <h3>OS ID: ${os.id} | Cliente: ${clienteNomeExibicao}</h3>
                    <p>
                        <strong>Equipamento:</strong> ${os.tipo_equipamento}<br>
                        <strong>Problema:</strong> ${os.descricao_problema || 'N/A'}<br>
                        <strong>Abertura:</strong> ${os.data_abertura ? os.data_abertura.substring(0, 10) : 'N/A'}<br>
                        <strong>Status:</strong> <span class="status-tag ${statusClass}">${os.status}</span>
                    </p>
                `;
                ossContainer.appendChild(osCard);

                // Adiciona evento de clique para visualizar detalhes
                osCard.addEventListener('click', () => {
                    visualizarDetalhesOS(os.id);
                });
            });
        } catch (error) {
            console.error('Erro ao carregar Ordens de Serviço:', error);
            if (ossContainer) { 
                ossContainer.innerHTML = '<p class="feedback-message error">Erro ao carregar Ordens de Serviço. Verifique o servidor.</p>';
            }
        }
    }

    // Função para visualizar detalhes de uma OS específica
    async function visualizarDetalhesOS(osId) {
        currentOsId = osId; 
        if (secoes.detalhesOS) showSection(secoes.detalhesOS); 

        if (osIdDetalheSpan) osIdDetalheSpan.textContent = osId;
        if (osDetalhesConteudoDiv) osDetalhesConteudoDiv.innerHTML = '<p>Carregando detalhes da OS...</p>';
        if (mensagemFeedbackStatusOS) mensagemFeedbackStatusOS.textContent = ''; 
        if (novoStatusOSSelect) novoStatusOSSelect.value = ''; 
        if (obsTecnicoOSInput) obsTecnicoOSInput.value = '';
        if (garantiaOSInput) garantiaOSInput.value = '';

        try {
            const response = await fetch(`${API_BASE_URL}/ordens_servico/${osId}`);
            const os = await response.json();

            if (!response.ok) {
                if (osDetalhesConteudoDiv) osDetalhesConteudoDiv.innerHTML = `<p class="feedback-message error">${os.message || 'Erro ao carregar detalhes da OS.'}</p>`;
                return;
            }

            let clienteDisplay = os.tipo_pessoa === 'PF' 
                               ? `${os.cliente_nome} (PF)` 
                               : `${os.cliente_razao_social} (PJ)`;

            let checklistHtml = os.checklist.length > 0 ? '<ul>' : '<p>Nenhum item de checklist registrado.</p>';
            os.checklist.forEach(item => {
                checklistHtml += `<li><strong>${item.pergunta}:</strong> ${item.resposta}</li>`;
            });
            if (os.checklist.length > 0) checklistHtml += '</ul>';

            let produtosHtml = os.produtos_utilizados.length > 0 ? '<ul>' : '<p>Nenhum produto utilizado.</p>';
            os.produtos_utilizados.forEach(item => {
                produtosHtml += `<li>${item.quantidade}x ${item.produto_nome} (R$${item.preco_unitario.toFixed(2)})</li>`;
            });
            if (os.produtos_utilizados.length > 0) produtosHtml += '</ul>';

            let servicosHtml = os.servicos_realizados.length > 0 ? '<ul>' : '<p>Nenhum serviço realizado.</p>';
            os.servicos_realizados.forEach(item => {
                servicosHtml += `<li>${item.servico_nome} (R$${item.preco_unitario.toFixed(2)})</li>`;
            });
            if (os.servicos_realizados.length > 0) servicosHtml += '</ul>';

            let historicoHtml = os.historico_status.length > 0 ? '<ul>' : '<p>Nenhum histórico de status.</p>';
            os.historico_status.forEach(item => {
                historicoHtml += `<li>${item.data_mudanca.substring(0, 19)}: De "${item.status_anterior || 'N/A'}" para "${item.status_novo}"</li>`;
            });
            if (os.historico_status.length > 0) historicoHtml += '</ul>';


            if (osDetalhesConteudoDiv) { 
                osDetalhesConteudoDiv.innerHTML = `
                    <p><strong>Cliente:</strong> ${clienteDisplay} - WhatsApp: ${os.whatsapp}</p>
                    <p><strong>Equipamento:</strong> ${os.tipo_equipamento}</p>
                    <p><strong>Problema Reportado:</strong> ${os.descricao_problema || 'N/A'}</p>
                    <p><strong>Data de Abertura:</strong> ${os.data_abertura ? os.data_abertura.substring(0, 19) : 'N/A'}</p>
                    <p><strong>Status Atual:</strong> <span class="status-tag ${os.status.toLowerCase().replace(/ /g, '-')}">${os.status}</span></p>
                    <p><strong>Observações do Técnico:</strong> ${os.observacoes_tecnico || 'N/A'}</p>
                    <p><strong>Valor Total:</strong> R$${os.valor_total ? os.valor_total.toFixed(2) : '0.00'}</p>
                    <p><strong>Garantia:</strong> ${os.garantia || 'N/A'}</p>
                    <p><strong>Data de Conclusão:</strong> ${os.data_conclusao ? os.data_conclusao.substring(0, 19) : 'N/A'}</p>

                    <h3>Checklist</h3>
                    ${checklistHtml}

                    <h3>Produtos Utilizados</h3>
                    ${produtosHtml}

                    <h3>Serviços Realizados</h3>
                    ${servicosHtml}

                    <h3>Histórico de Status</h3>
                    ${historicoHtml}
                `;
            }

            if (novoStatusOSSelect) novoStatusOSSelect.value = os.status;
            if (obsTecnicoOSInput) obsTecnicoOSInput.value = os.observacoes_tecnico || '';
            if (garantiaOSInput) garantiaOSInput.value = os.garantia || '';

        } catch (error) {
            console.error('Erro ao carregar detalhes da OS:', error);
            if (osDetalhesConteudoDiv) { 
                osDetalhesConteudoDiv.innerHTML = '<p class="feedback-message error">Erro ao carregar detalhes da OS.</p>';
            }
        }
    }

    // Evento para submissão do formulário de abertura de OS
    if (formAbrirOS) { 
        formAbrirOS.addEventListener('submit', async (event) => {
            event.preventDefault();

            const formData = new FormData(formAbrirOS);
            const data = {};
            for (const [key, value] of formData.entries()) {
                data[key] = value;
            }

            data.cliente_id = parseInt(data.cliente_id);
            if (isNaN(data.cliente_id)) {
                showFeedback('ID do Cliente deve ser um número válido.', 'error', mensagemFeedbackOS);
                return;
            }

            const checklist = [];
            const checklistInputs = document.querySelectorAll('#checklist-container input, #checklist-container select, #checklist-container textarea');
            checklistInputs.forEach(input => {
                const label = input.previousElementSibling; 
                if (label && label.tagName === 'LABEL') {
                    const perguntaTexto = label.textContent.trim().replace(/\s*\(.*\)\s*$/, ''); 
                    const respostaTexto = input.value.trim();
                    if (perguntaTexto && respostaTexto) {
                        checklist.push({ pergunta: perguntaTexto, resposta: respostaTexto });
                    }
                }
            });
            
            data.checklist = checklist;

            try {
                const response = await fetch(`${API_BASE_URL}/ordens_servico`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (response.ok) {
                    showFeedback(result.message, 'success', mensagemFeedbackOS);
                    formAbrirOS.reset();
                    carregarOSs(); 
                } else {
                    showFeedback(`Erro: ${result.message}`, 'error', mensagemFeedbackOS);
                }
            } catch (error) {
                console.error('Erro ao abrir OS:', error);
                showFeedback('Erro ao conectar com o servidor para abrir OS.', 'error', mensagemFeedbackOS);
            }
        });
    }

    // Evento para atualizar status da OS
    if (btnAtualizarStatusOS) { 
        btnAtualizarStatusOS.addEventListener('click', async () => {
            if (!currentOsId) {
                showFeedback('Nenhuma OS selecionada para atualizar o status.', 'error', mensagemFeedbackStatusOS);
                return;
            }

            const novoStatus = novoStatusOSSelect ? novoStatusOSSelect.value : '';
            const obsTecnico = obsTecnicoOSInput ? obsTecnicoOSInput.value : '';
            const garantia = garantiaOSInput ? garantiaOSInput.value : '';

            if (!novoStatus) {
                showFeedback('Selecione um novo status.', 'error', mensagemFeedbackStatusOS);
                return;
            }

            const data = {
                novo_status: novoStatus,
                observacoes_tecnico: obsTecnico,
                garantia: garantia
            };

            try {
                const response = await fetch(`${API_BASE_URL}/ordens_servico/${currentOsId}/status`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (response.ok) {
                    showFeedback(result.message, 'success', mensagemFeedbackStatusOS);
                    visualizarDetalhesOS(currentOsId);
                    console.log("Mensagem Automática:", result.mensagem_automatica); 
                } else {
                    showFeedback(`Erro: ${result.message}`, 'error', mensagemFeedbackStatusOS);
                }
            } catch (error) {
                console.error('Erro ao atualizar status da OS:', error);
                showFeedback('Erro ao conectar com o servidor para atualizar status da OS.', 'error', mensagemFeedbackStatusOS);
            }
        });
    }

    // Evento para o botão de voltar da tela de detalhes da OS
    if (btnVoltarOSList) { 
        btnVoltarOSList.addEventListener('click', () => {
            Object.values(secoes).forEach(section => section.classList.remove('hidden'));
            if (secoes.detalhesOS) secoes.detalhesOS.classList.add('hidden'); 
            carregarOSs(); 
        });
    }


    // --- Funções para Produtos (CRUD) ---

    async function carregarProdutos() {
        if (!produtosContainer) return;
        produtosContainer.innerHTML = '<p>Carregando produtos...</p>';
        try {
            const response = await fetch(`${API_BASE_URL}/produtos`);
            const produtos = await response.json();

            produtosContainer.innerHTML = '';
            if (produtos.length === 0) {
                produtosContainer.innerHTML = '<p>Nenhum produto cadastrado ainda.</p>';
                return;
            }

            produtos.forEach(produto => {
                const produtoCard = document.createElement('div');
                produtoCard.classList.add('produto-card');
                produtoCard.innerHTML = `
                    <div class="info">
                        <h3>ID: ${produto.id} | ${produto.nome}</h3>
                        <p>Descrição: ${produto.descricao || 'N/A'}</p>
                        <p>Preço: R$${produto.preco.toFixed(2)} | Estoque: ${produto.estoque}</p>
                    </div>
                    <div class="actions">
                        <button class="btn-edit" data-id="${produto.id}" data-type="produto">Editar</button>
                        <button class="btn-delete" data-id="${produto.id}" data-type="produto">Excluir</button>
                    </div>
                `;
                produtosContainer.appendChild(produtoCard);
            });

            // Adiciona event listeners para botões de edição/exclusão
            document.querySelectorAll('.btn-edit[data-type="produto"]').forEach(button => {
                button.addEventListener('click', (e) => editarProduto(e.target.dataset.id));
            });
            document.querySelectorAll('.btn-delete[data-type="produto"]').forEach(button => {
                button.addEventListener('click', (e) => excluirProduto(e.target.dataset.id));
            });

        } catch (error) {
            console.error('Erro ao carregar produtos:', error);
            if (produtosContainer) produtosContainer.innerHTML = '<p class="feedback-message error">Erro ao carregar produtos. Verifique o servidor.</p>';
        }
    }

    async function cadastrarOuAtualizarProduto() {
        const id = produtoIdInput ? produtoIdInput.value : '';
        const nome = nomeProdutoInput ? nomeProdutoInput.value : '';
        const descricao = descricaoProdutoInput ? descricaoProdutoInput.value : '';
        const preco = precoProdutoInput ? parseFloat(precoProdutoInput.value) : 0;
        const estoque = estoqueProdutoInput ? parseInt(estoqueProdutoInput.value) : 0;

        if (!nome || isNaN(preco) || preco < 0 || isNaN(estoque) || estoque < 0) {
            showFeedback('Preencha todos os campos obrigatórios e válidos para o produto.', 'error', mensagemFeedbackProduto);
            return;
        }

        const data = { nome, descricao, preco, estoque };
        let url = `${API_BASE_URL}/produtos`;
        let method = 'POST';

        if (id) { // Se tem ID, é uma atualização
            url = `${API_BASE_URL}/produtos/${id}`;
            method = 'PUT';
        }

        try {
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();

            if (response.ok) {
                showFeedback(result.message, 'success', mensagemFeedbackProduto);
                resetFormProduto(); // Limpa o formulário e reverte para cadastro
                carregarProdutos(); // Recarrega a lista
            } else {
                showFeedback(`Erro: ${result.message}`, 'error', mensagemFeedbackProduto);
            }
        } catch (error) {
            console.error('Erro ao salvar produto:', error);
            showFeedback('Erro ao conectar com o servidor para salvar produto.', 'error', mensagemFeedbackProduto);
        }
    }

    async function editarProduto(id) {
        // Busca o produto para preencher o formulário
        try {
            const response = await fetch(`${API_BASE_URL}/produtos`); // Busca todos e encontra pelo ID
            const produtos = await response.json();
            const produto = produtos.find(p => p.id == id); // Usa == para comparar string com number

            if (produto) {
                if (produtoIdInput) produtoIdInput.value = produto.id;
                if (nomeProdutoInput) nomeProdutoInput.value = produto.nome;
                if (descricaoProdutoInput) descricaoProdutoInput.value = produto.descricao || '';
                if (precoProdutoInput) precoProdutoInput.value = produto.preco;
                if (estoqueProdutoInput) estoqueProdutoInput.value = produto.estoque;
                
                if (btnSalvarProduto) btnSalvarProduto.textContent = 'Atualizar Produto';
                if (btnCancelarProduto) btnCancelarProduto.classList.remove('hidden');
                
                // Opcional: rolar para o formulário
                if (secoes.formProduto) secoes.formProduto.scrollIntoView({ behavior: 'smooth' });
                // Ou mostrar apenas o formulário
                // showSection(secoes.formProduto); 

            } else {
                showFeedback('Produto não encontrado para edição.', 'error', mensagemFeedbackProduto);
            }
        } catch (error) {
            console.error('Erro ao carregar produto para edição:', error);
            showFeedback('Erro ao carregar produto para edição.', 'error', mensagemFeedbackProduto);
        }
    }

    async function excluirProduto(id) {
        if (!confirm(`Tem certeza que deseja excluir o produto ID ${id}?`)) {
            return;
        }
        try {
            const response = await fetch(`${API_BASE_URL}/produtos/${id}`, {
                method: 'DELETE'
            });
            const result = await response.json();

            if (response.ok) {
                showFeedback(result.message, 'success', mensagemFeedbackProduto);
                carregarProdutos();
            } else {
                showFeedback(`Erro: ${result.message}`, 'error', mensagemFeedbackProduto);
            }
        } catch (error) {
            console.error('Erro ao excluir produto:', error);
            showFeedback('Erro ao conectar com o servidor para excluir produto.', 'error', mensagemFeedbackProduto);
        }
    }

    function resetFormProduto() {
        if (formCadastroProduto) formCadastroProduto.reset();
        if (produtoIdInput) produtoIdInput.value = '';
        if (btnSalvarProduto) btnSalvarProduto.textContent = 'Cadastrar Produto';
        if (btnCancelarProduto) btnCancelarProduto.classList.add('hidden');
        if (mensagemFeedbackProduto) mensagemFeedbackProduto.textContent = '';
        if (mensagemFeedbackProduto) mensagemFeedbackProduto.className = 'feedback-message';
    }


    // --- Funções para Serviços (CRUD) ---

    async function carregarServicos() {
        if (!servicosContainer) return;
        servicosContainer.innerHTML = '<p>Carregando serviços...</p>';
        try {
            const response = await fetch(`${API_BASE_URL}/servicos`);
            const servicos = await response.json();

            servicosContainer.innerHTML = '';
            if (servicos.length === 0) {
                servicosContainer.innerHTML = '<p>Nenhum serviço cadastrado ainda.</p>';
                return;
            }

            servicos.forEach(servico => {
                const servicoCard = document.createElement('div');
                servicoCard.classList.add('servico-card');
                servicoCard.innerHTML = `
                    <div class="info">
                        <h3>ID: ${servico.id} | ${servico.nome}</h3>
                        <p>Descrição: ${servico.descricao || 'N/A'}</p>
                        <p>Preço: R$${servico.preco.toFixed(2)}</p>
                    </div>
                    <div class="actions">
                        <button class="btn-edit" data-id="${servico.id}" data-type="servico">Editar</button>
                        <button class="btn-delete" data-id="${servico.id}" data-type="servico">Excluir</button>
                    </div>
                `;
                servicosContainer.appendChild(servicoCard);
            });

            // Adiciona event listeners para botões de edição/exclusão
            document.querySelectorAll('.btn-edit[data-type="servico"]').forEach(button => {
                button.addEventListener('click', (e) => editarServico(e.target.dataset.id));
            });
            document.querySelectorAll('.btn-delete[data-type="servico"]').forEach(button => {
                button.addEventListener('click', (e) => excluirServico(e.target.dataset.id));
            });

        } catch (error) {
            console.error('Erro ao carregar serviços:', error);
            if (servicosContainer) servicosContainer.innerHTML = '<p class="feedback-message error">Erro ao carregar serviços. Verifique o servidor.</p>';
        }
    }

    async function cadastrarOuAtualizarServico() {
        const id = servicoIdInput ? servicoIdInput.value : '';
        const nome = nomeServicoInput ? nomeServicoInput.value : '';
        const descricao = descricaoServicoInput ? descricaoServicoInput.value : '';
        const preco = precoServicoInput ? parseFloat(precoServicoInput.value) : 0;

        if (!nome || isNaN(preco) || preco < 0) {
            showFeedback('Preencha todos os campos obrigatórios e válidos para o serviço.', 'error', mensagemFeedbackServico);
            return;
        }

        const data = { nome, descricao, preco };
        let url = `${API_BASE_URL}/servicos`;
        let method = 'POST';

        if (id) { // Se tem ID, é uma atualização
            url = `${API_BASE_URL}/servicos/${id}`;
            method = 'PUT';
        }

        try {
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();

            if (response.ok) {
                showFeedback(result.message, 'success', mensagemFeedbackServico);
                resetFormServico(); // Limpa o formulário e reverte para cadastro
                carregarServicos(); // Recarrega a lista
            } else {
                showFeedback(`Erro: ${result.message}`, 'error', mensagemFeedbackServico);
            }
        } catch (error) {
            console.error('Erro ao salvar serviço:', error);
            showFeedback('Erro ao conectar com o servidor para salvar serviço.', 'error', mensagemFeedbackServico);
        }
    }

    async function editarServico(id) {
        // Busca o serviço para preencher o formulário
        try {
            const response = await fetch(`${API_BASE_URL}/servicos`); // Busca todos e encontra pelo ID
            const servicos = await response.json();
            const servico = servicos.find(s => s.id == id);

            if (servico) {
                if (servicoIdInput) servicoIdInput.value = servico.id;
                if (nomeServicoInput) nomeServicoInput.value = servico.nome;
                if (descricaoServicoInput) descricaoServicoInput.value = servico.descricao || '';
                if (precoServicoInput) precoServicoInput.value = servico.preco;
                
                if (btnSalvarServico) btnSalvarServico.textContent = 'Atualizar Serviço';
                if (btnCancelarServico) btnCancelarServico.classList.remove('hidden');

                if (secoes.formServico) secoes.formServico.scrollIntoView({ behavior: 'smooth' });
            } else {
                showFeedback('Serviço não encontrado para edição.', 'error', mensagemFeedbackServico);
            }
        } catch (error) {
            console.error('Erro ao carregar serviço para edição:', error);
            showFeedback('Erro ao carregar serviço para edição.', 'error', mensagemFeedbackServico);
        }
    }

    async function excluirServico(id) {
        if (!confirm(`Tem certeza que deseja excluir o serviço ID ${id}?`)) {
            return;
        }
        try {
            const response = await fetch(`${API_BASE_URL}/servicos/${id}`, {
                method: 'DELETE'
            });
            const result = await response.json();

            if (response.ok) {
                showFeedback(result.message, 'success', mensagemFeedbackServico);
                carregarServicos();
            } else {
                showFeedback(`Erro: ${result.message}`, 'error', mensagemFeedbackServico);
            }
        } catch (error) {
            console.error('Erro ao excluir serviço:', error);
            showFeedback('Erro ao conectar com o servidor para excluir serviço.', 'error', mensagemFeedbackServico);
        }
    }

    function resetFormServico() {
        if (formCadastroServico) formCadastroServico.reset();
        if (servicoIdInput) servicoIdInput.value = '';
        if (btnSalvarServico) btnSalvarServico.textContent = 'Cadastrar Serviço';
        if (btnCancelarServico) btnCancelarServico.classList.add('hidden');
        if (mensagemFeedbackServico) mensagemFeedbackServico.textContent = '';
        if (mensagemFeedbackServico) mensagemFeedbackServico.className = 'feedback-message';
    }


    // --- Eventos de Carregamento Inicial e Botões ---
    if (btnRecarregarClientes) btnRecarregarClientes.addEventListener('click', carregarClientes);
    if (btnRecarregarOSs) btnRecarregarOSs.addEventListener('click', carregarOSs);
    if (btnRecarregarProdutos) btnRecarregarProdutos.addEventListener('click', carregarProdutos);
    if (btnRecarregarServicos) btnRecarregarServicos.addEventListener('click', carregarServicos);


    // Eventos de Formulário (Submit e Cancelar)
    if (formCadastroProduto) formCadastroProduto.addEventListener('submit', async (e) => { e.preventDefault(); cadastrarOuAtualizarProduto(); });
    if (btnCancelarProduto) btnCancelarProduto.addEventListener('click', resetFormProduto);

    if (formCadastroServico) formCadastroServico.addEventListener('submit', async (e) => { e.preventDefault(); cadastrarOuAtualizarServico(); });
    if (btnCancelarServico) btnCancelarServico.addEventListener('click', resetFormServico);


    // Carregar dados ao iniciar a página
    carregarClientes();
    carregarOSs();
    carregarProdutos();
    carregarServicos();
});