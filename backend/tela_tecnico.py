import sqlite3
# Importamos as funções necessárias do nosso módulo de Ordem de Serviço
from ordem_servico import conectar_bd, fechar_bd, listar_oss, visualizar_detalhes_os, atualizar_status_os
from db_utils import conectar_bd, fechar_bd
def tela_do_tecnico():
    """
    Função principal que simula a interface da Tela do Técnico.
    Permite visualizar e gerenciar as OSs sob a perspectiva do técnico.
    """
    conn, cursor = conectar_bd()

    if conn and cursor:
        while True:
            print("\n--- Tela do Técnico ---")
            print("1. Visualizar Minhas OSs (Todas)") # Por enquanto, todas as OSs
            print("2. Visualizar Detalhes de uma OS")
            print("3. Atualizar Status de uma OS")
            print("0. Sair da Tela do Técnico")

            opcao = input("Escolha uma opção: ").strip()

            if opcao == '1':
                print("\n--- Listando Ordens de Serviço ---")
                # Filtra as OSs que estariam "na bancada" ou "em testes" ou "aguardando aprovação/peças"
                # Por simplicidade inicial, listaremos todas. No futuro, podemos filtrar por técnico.
                listar_oss(cursor)
                
            elif opcao == '2':
                os_id_str = input("Digite o ID da OS para visualizar detalhes: ").strip()
                if os_id_str.isdigit():
                    os_id = int(os_id_str)
                    visualizar_detalhes_os(cursor, os_id)
                else:
                    print("ID inválido. Por favor, digite um número.")

            elif opcao == '3':
                os_id_str = input("Digite o ID da OS para atualizar status: ").strip()
                if os_id_str.isdigit():
                    os_id = int(os_id_str)
                    
                    # Para garantir a restrição, o técnico só pode mudar para certos status
                    # Precisamos buscar o status atual primeiro para aplicar a lógica
                    cursor.execute("SELECT status FROM ordens_servico WHERE id = ?", (os_id,))
                    os_info = cursor.fetchone()

                    if not os_info:
                        print(f"OS nº {os_id} não encontrada.")
                    else:
                        status_atual = os_info['status']
                        print(f"Status atual da OS {os_id}: {status_atual}")

                        # Lógica para permitir apenas certos status para o técnico
                        print("\nOpções de status para o técnico:")
                        status_permitidos_tecnico = []

                        if status_atual == "Na bancada":
                            status_permitidos_tecnico = ["Em testes", "Serviço concluído", "Aguardando peças"]
                        elif status_atual == "Em testes":
                             status_permitidos_tecnico = ["Serviço concluído", "Na bancada"] # Pode voltar para bancada para mais trabalho
                        elif status_atual == "Aguardando peças":
                            status_permitidos_tecnico = ["Na bancada", "Abandonado"] # Se as peças demorarem muito
                        elif status_atual == "Aguardando aprovação":
                             status_permitidos_tecnico = ["Abandonado"] # Técnico pode registrar abandono se o cliente não aprovar
                        # Outros status podem ter opções diferentes, ou nenhuma opção de mudança pelo técnico

                        if not status_permitidos_tecnico:
                            print("Nenhuma alteração de status disponível para o técnico neste status atual.")
                        else:
                            # Adiciona a opção de manter o status atual
                            status_permitidos_tecnico.insert(0, status_atual) 
                            
                            for i, status in enumerate(status_permitidos_tecnico):
                                print(f"{i+1}. {status}")
                            
                            while True:
                                try:
                                    escolha = int(input("Digite o número do novo status: ").strip())
                                    if 1 <= escolha <= len(status_permitidos_tecnico):
                                        novo_status = status_permitidos_tecnico[escolha - 1]
                                        # Chama a função de atualização de status do módulo de OS
                                        atualizar_status_os(cursor, conn, os_id) # A função já pedirá o novo status internamente
                                        break
                                    else:
                                        print("Opção inválida. Digite um número da lista.")
                                except ValueError:
                                    print("Entrada inválida. Digite um número.")
                else:
                    print("ID inválido. Por favor, digite um número.")

            elif opcao == '0':
                print("Saindo da Tela do Técnico.")
                break
            else:
                print("Opção inválida. Por favor, tente novamente.")
        fechar_bd(conn)

if __name__ == "__main__":
    tela_do_tecnico()