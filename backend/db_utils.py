# backend/db_utils.py
import sqlite3

def conectar_bd(nome_banco="assistencia_tecnica.db"):
    """
    Conecta ao banco de dados SQLite. Se o banco não existir, ele será criado.
    Retorna o objeto de conexão e o cursor.
    """
    conn = None
    try:
        conn = sqlite3.connect(nome_banco)
        conn.row_factory = sqlite3.Row # Permite acessar colunas por nome
        cursor = conn.cursor()
        return conn, cursor
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None, None

def fechar_bd(conn):
    """Fecha a conexão com o banco de dados."""
    if conn:
        conn.close()