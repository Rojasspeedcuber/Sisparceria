"""
Módulo de gerenciamento do banco de dados SQLite.
Contém funções para criar, inserir, buscar e exportar dados de propostas de parceria.
"""

import sqlite3
from datetime import datetime
from typing import Optional
import os

# Caminho do banco de dados
DATABASE_PATH = "parcerias.db"


def get_connection() -> sqlite3.Connection:
    """
    Cria e retorna uma conexão com o banco de dados SQLite.
    Utiliza Row factory para acesso por nome de coluna.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database() -> None:
    """
    Inicializa o banco de dados criando a tabela de propostas caso não exista.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS propostas_parceria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpf_cnpj TEXT NOT NULL,
                razao_social TEXT NOT NULL,
                rua TEXT NOT NULL,
                numero TEXT NOT NULL,
                complemento TEXT,
                cep TEXT NOT NULL,
                ponto_referencia TEXT,
                telefone TEXT NOT NULL,
                email TEXT NOT NULL,
                nome_contato TEXT NOT NULL,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def inserir_proposta(
    cpf_cnpj: str,
    razao_social: str,
    rua: str,
    numero: str,
    complemento: str,
    cep: str,
    ponto_referencia: str,
    telefone: str,
    email: str,
    nome_contato: str
) -> bool:
    """
    Insere uma nova proposta de parceria no banco de dados.

    Args:
        cpf_cnpj: CPF ou CNPJ da empresa
        razao_social: Razão social da empresa
        rua: Nome da rua
        numero: Número do endereço
        complemento: Complemento do endereço
        cep: CEP do endereço
        ponto_referencia: Ponto de referência
        telefone: Telefone de contato
        email: E-mail de contato
        nome_contato: Nome da pessoa de contato

    Returns:
        True se inserido com sucesso, False caso contrário
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO propostas_parceria (
                    cpf_cnpj, razao_social, rua, numero, complemento,
                    cep, ponto_referencia, telefone, email, nome_contato,
                    data_cadastro
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cpf_cnpj, razao_social, rua, numero, complemento,
                cep, ponto_referencia, telefone, email, nome_contato,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            conn.commit()
            return True
    except sqlite3.Error as e:
        print(f"Erro ao inserir proposta: {e}")
        return False


def listar_propostas(ordem: str = "desc") -> list:
    """
    Lista todas as propostas cadastradas ordenadas por data.

    Args:
        ordem: 'asc' para crescente, 'desc' para decrescente

    Returns:
        Lista de dicionários com os dados das propostas
    """
    ordem_sql = "DESC" if ordem.lower() == "desc" else "ASC"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT * FROM propostas_parceria
            ORDER BY data_cadastro {ordem_sql}
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def buscar_propostas(termo: str, campo: str = "razao_social") -> list:
    """
    Busca propostas por razão social ou CPF/CNPJ.

    Args:
        termo: Termo de busca
        campo: 'razao_social' ou 'cpf_cnpj'

    Returns:
        Lista de dicionários com os dados das propostas encontradas
    """
    campo_busca = "razao_social" if campo == "razao_social" else "cpf_cnpj"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT * FROM propostas_parceria
            WHERE {campo_busca} LIKE ?
            ORDER BY data_cadastro DESC
        """, (f"%{termo}%",))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def contar_registros() -> int:
    """
    Retorna a quantidade total de registros no banco de dados.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM propostas_parceria")
        return cursor.fetchone()[0]


def exportar_csv() -> str:
    """
    Exporta todos os registros para formato CSV.

    Returns:
        String no formato CSV
    """
    propostas = listar_propostas()

    if not propostas:
        return ""

    # Cabeçalho
    colunas = [
        "ID", "CPF/CNPJ", "Razão Social", "Rua", "Número",
        "Complemento", "CEP", "Ponto de Referência",
        "Telefone", "E-mail", "Nome do Contato", "Data de Cadastro"
    ]

    linhas = [";".join(colunas)]

    # Dados
    for p in propostas:
        linha = [
            str(p.get("id", "")),
            p.get("cpf_cnpj", ""),
            p.get("razao_social", ""),
            p.get("rua", ""),
            p.get("numero", ""),
            p.get("complemento", "") or "",
            p.get("cep", ""),
            p.get("ponto_referencia", "") or "",
            p.get("telefone", ""),
            p.get("email", ""),
            p.get("nome_contato", ""),
            p.get("data_cadastro", "")
        ]
        linhas.append(";".join(linha))

    return "\n".join(linhas)


def verificar_cpf_cnpj_existe(cpf_cnpj: str) -> bool:
    """
    Verifica se já existe um registro com o CPF/CNPJ informado.

    Args:
        cpf_cnpj: CPF ou CNPJ a ser verificado

    Returns:
        True se existe, False caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM propostas_parceria WHERE cpf_cnpj = ?",
            (cpf_cnpj,)
        )
        return cursor.fetchone()[0] > 0
