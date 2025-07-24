antes de tudo: eu nao me considero nenhum tipo de desenvolvedor, só identifico problrmas, vejo uma solução usando automação ou codigo, e a parte suja de escrever os grosso do codigo eu deixo isso pra I.A, sempre tem uns erros aqui e ali, mas é só saber ler que isso eu mesmo resolvo, de resto tem umas partes comentadas no codigo(era pra ter apagado, mas acabei subindo assim mesmo , foda-se)

# PROJETO ASSISTENCIA TECNICA - SoftGateE ai, beleza? Esse aqui é o repo do Projeto Assistencia Tecnica, a ferramenta **incrivel** q fiz pra gerenciar uma assistencia tecnica, feita com Python e SQLite no back-end e um front-end web (q ta sendo feito, mas ja funciona o basico!).

**Link do Repositório:** [https://github.com/EmanoelTech/softgate.git](https://github.com/EmanoelTech/softgate.git)

## Como fazer essa parada rodar? (Passo a passo pra nao se perder)

### 1. O q vc precisa ter na maquina

Pra rodar isso aqui, vc vai precisar ter instalado:

* **Python 3.x:** (Tipo, 3.8 pra cima, pra nao dar pepino)
* **pip:** (Pra instalar as paradas do Python)

### 2. Baixando as coisas (Dependencias)

Primeiro, clone esse repo ai pro seu pc:

```bash
git clone [https://github.com/EmanoelTech/softgate.git](https://github.com/EmanoelTech/softgate.git)
cd softgate/PROJETO_ASSISTENCIA
Ai, entra na pasta backend e instala as bibliotecas q o Python precisa:

Bash

cd backend
pip install Flask Flask-Cors
importante: se der erro de ModuleNotFoundError lembra q pode ser alguma dessas faltando, ja aconteceu comigo, isso ai é normal
3.ligando o motor (Backend - API Flask)
Esse é o coraçao do bagulho, Vc precisa rodar o servidor Flask pra q o front-end consiga conversar com o banco de dados

Dentro da pasta backend, manda o comando:

python app.py

Se aparecer umas mensagens tipo * Running on http://127.0.0.1:5000 e umas de "Tabela X verificada/criada", ta tudo certo! Deixa esse terminal aberto, ele tem q tar rodando pra parada funcionar

4. Abrindo a Interface (Frontend Web)
Agora q o back-end ta ligado, eh so abrir o navegador!

Vai na pasta frontend do projeto e abre o arquivo index.html direto no seu navegador preferido (Chrome, Firefox, Edge, etc.). Eh so dar dois cliques nele ou arrastar pro navegador.

ATENCAO! Se a interface nao carregar ou ficar em "carregando...", faz um hard refresh no navegador, As vezes o cache atrapalha

no Chrome/Firefox/Edge: Ctrl + Shift + R (Windows/Linux) ou Cmd + Shift + R (Mac).

5. O q ja ta funcionando? (Funcionalidades Principais)
A interface pode nao ser a mais bonita do mundo (ainda to aprendendo front-end, paciencia!), mas o grosso ja ta la:

Gerenciar Clientes:
Ver a lista de todos os clientes cadastrados.
Cadastrar cliente novo (PF ou PJ, com os campos certos).
(Por enquanto, atualizar e excluir sao so pelo console do backend ou direto no banco, mas a API ja ta la, eh so integrar no front depois).
Gerenciar Ordens de Serviço (OS):
Ver a lista de todas as OSs abertas.
Abrir uma OS nova (escolhe o cliente, descreve o problema, faz o checklist inicial)
Ver os detalhes completos de uma OS (checklist, produtos/serviços usados, historico de status)
Atualizar o status da OS (o tecnico consegue mudar o status e adicionar observacoes/garantia)

6. O q vem por ai? (Proximos Passos)
A ideia eh adicionar mais coisas, tipo:
CRUD completo de Produtos e Serviços no front: Pra poder cadastrar, listar, editar e apagar produtos e serviços direto pela interface.
Tela de Pagamento da OS: Pra registrar os pagamentos, aplicar desconto e tal.
Deixar o layout lindao e responsivo de vdd: Fazer umas telas mais organizadas, com menu de navegacao (aquele "hamburguer" pro celular) e um visual mais maneiro.
Qualquer duvida, problema ou se quiser dar uma maozinha no front, manda um "issue" ou "pull request" ai!

Tecnologias Usadas:

Backend: Python 3.x, Flask, SQLite3

Frontend: HTML5, CSS3, JavaScript
