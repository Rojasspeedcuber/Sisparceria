"""
Aplicação Web para Cadastro de Propostas de Parceria Empresarial.
Interface moderna desenvolvida com Streamlit.
"""

import streamlit as st
import re
from datetime import datetime
import database as db

# Configuração da página
st.set_page_config(
    page_title="Sistema de Parcerias",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para melhorar a aparência
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A5F;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2C5282;
        border-bottom: 2px solid #E2E8F0;
        padding-bottom: 0.5rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #F7FAFC;
        border-radius: 10px;
        padding: 1rem;
        border-left: 4px solid #3182CE;
    }
    .success-message {
        background-color: #C6F6D5;
        color: #22543D;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #38A169;
    }
    .error-message {
        background-color: #FED7D7;
        color: #822727;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #E53E3E;
    }
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# FUNÇÕES DE VALIDAÇÃO
# ============================================================================

def validar_cpf(cpf: str) -> bool:
    """
    Valida se o CPF é válido usando o algoritmo de verificação.
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)

    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False

    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False

    # Calcula o primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    if int(cpf[9]) != digito1:
        return False

    # Calcula o segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    return int(cpf[10]) == digito2


def validar_cnpj(cnpj: str) -> bool:
    """
    Valida se o CNPJ é válido usando o algoritmo de verificação.
    """
    # Remove caracteres não numéricos
    cnpj = re.sub(r'[^0-9]', '', cnpj)

    # Verifica se tem 14 dígitos
    if len(cnpj) != 14:
        return False

    # Verifica se todos os dígitos são iguais
    if cnpj == cnpj[0] * 14:
        return False

    # Calcula o primeiro dígito verificador
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * pesos1[i] for i in range(12))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    if int(cnpj[12]) != digito1:
        return False

    # Calcula o segundo dígito verificador
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * pesos2[i] for i in range(13))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    return int(cnpj[13]) == digito2


def validar_cpf_cnpj(documento: str) -> tuple[bool, str]:
    """
    Valida se o documento é um CPF ou CNPJ válido.

    Returns:
        Tupla (é_válido, mensagem_erro)
    """
    # Remove caracteres não numéricos
    doc_limpo = re.sub(r'[^0-9]', '', documento)

    if not doc_limpo:
        return False, "CPF/CNPJ é obrigatório"

    if len(doc_limpo) == 11:
        if validar_cpf(doc_limpo):
            return True, ""
        return False, "CPF inválido"

    if len(doc_limpo) == 14:
        if validar_cnpj(doc_limpo):
            return True, ""
        return False, "CNPJ inválido"

    return False, "Documento deve ter 11 dígitos (CPF) ou 14 dígitos (CNPJ)"


def validar_email(email: str) -> tuple[bool, str]:
    """
    Valida se o e-mail tem formato válido.
    """
    if not email:
        return False, "E-mail é obrigatório"

    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(padrao, email):
        return True, ""
    return False, "E-mail inválido"


def validar_telefone(telefone: str) -> tuple[bool, str]:
    """
    Valida se o telefone tem formato válido.
    Aceita formatos: (XX) XXXXX-XXXX, (XX) XXXX-XXXX, XXXXXXXXXXX
    """
    if not telefone:
        return False, "Telefone é obrigatório"

    # Remove caracteres não numéricos
    tel_limpo = re.sub(r'[^0-9]', '', telefone)

    if len(tel_limpo) < 10 or len(tel_limpo) > 11:
        return False, "Telefone deve ter 10 ou 11 dígitos"

    return True, ""


def validar_cep(cep: str) -> tuple[bool, str]:
    """
    Valida se o CEP tem formato válido.
    """
    if not cep:
        return False, "CEP é obrigatório"

    # Remove caracteres não numéricos
    cep_limpo = re.sub(r'[^0-9]', '', cep)

    if len(cep_limpo) != 8:
        return False, "CEP deve ter 8 dígitos"

    return True, ""


def validar_campos_obrigatorios(dados: dict) -> list[str]:
    """
    Valida se todos os campos obrigatórios estão preenchidos.

    Returns:
        Lista de mensagens de erro
    """
    erros = []

    campos_obrigatorios = {
        'cpf_cnpj': 'CPF/CNPJ',
        'razao_social': 'Razão Social',
        'rua': 'Rua',
        'numero': 'Número',
        'cep': 'CEP',
        'telefone': 'Telefone',
        'email': 'E-mail',
        'nome_contato': 'Nome do Contato'
    }

    for campo, nome in campos_obrigatorios.items():
        if not dados.get(campo, '').strip():
            erros.append(f"O campo '{nome}' é obrigatório")

    return erros


def formatar_cpf_cnpj(documento: str) -> str:
    """
    Formata CPF ou CNPJ para exibição.
    """
    doc_limpo = re.sub(r'[^0-9]', '', documento)

    if len(doc_limpo) == 11:
        return f"{doc_limpo[:3]}.{doc_limpo[3:6]}.{doc_limpo[6:9]}-{doc_limpo[9:]}"

    if len(doc_limpo) == 14:
        return f"{doc_limpo[:2]}.{doc_limpo[2:5]}.{doc_limpo[5:8]}/{doc_limpo[8:12]}-{doc_limpo[12:]}"

    return documento


def limpar_documento(documento: str) -> str:
    """
    Remove formatação do documento para armazenamento.
    """
    return re.sub(r'[^0-9]', '', documento)


# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

# Inicializa o banco de dados
db.init_database()

# Inicializa estado da sessão para limpar formulário
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

if 'form_key' not in st.session_state:
    st.session_state.form_key = 0


# ============================================================================
# INTERFACE - SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("### 📋 Menu")

    pagina = st.radio(
        "Navegação",
        ["Novo Cadastro", "Consultar Registros"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Indicador de quantidade de registros
    total_registros = db.contar_registros()
    st.metric(
        label="Total de Registros",
        value=total_registros,
        delta=None
    )

    st.markdown("---")

    st.markdown("### ℹ️ Sobre")
    st.markdown("""
    **Sistema de Parcerias**

    Aplicação para cadastro e
    gerenciamento de propostas
    de parceria empresarial.

    Versão 1.0
    """)


# ============================================================================
# PÁGINA - NOVO CADASTRO
# ============================================================================

if pagina == "Novo Cadastro":
    # Cabeçalho
    st.markdown('<h1 class="main-header">🤝 Sistema de Parcerias</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Cadastro de Propostas de Parceria Empresarial</p>', unsafe_allow_html=True)

    # Formulário de cadastro
    with st.form(key=f"form_parceria_{st.session_state.form_key}"):

        # Seção: Dados da Empresa
        st.markdown('<p class="section-header">🏢 Dados da Empresa</p>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            cpf_cnpj = st.text_input(
                "CPF ou CNPJ *",
                placeholder="Digite apenas números",
                help="Informe o CPF (11 dígitos) ou CNPJ (14 dígitos)"
            )

        with col2:
            razao_social = st.text_input(
                "Razão Social *",
                placeholder="Nome da empresa",
                help="Nome oficial da empresa"
            )

        # Seção: Endereço
        st.markdown('<p class="section-header">📍 Endereço</p>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns([3, 1, 2])

        with col1:
            rua = st.text_input(
                "Rua *",
                placeholder="Nome da rua/avenida"
            )

        with col2:
            numero = st.text_input(
                "Número *",
                placeholder="Nº"
            )

        with col3:
            complemento = st.text_input(
                "Complemento",
                placeholder="Apto, sala, etc."
            )

        col1, col2 = st.columns(2)

        with col1:
            cep = st.text_input(
                "CEP *",
                placeholder="00000-000",
                help="CEP com 8 dígitos"
            )

        with col2:
            ponto_referencia = st.text_input(
                "Ponto de Referência",
                placeholder="Próximo a..."
            )

        # Seção: Contato
        st.markdown('<p class="section-header">📞 Contato</p>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            telefone = st.text_input(
                "Telefone *",
                placeholder="(00) 00000-0000",
                help="Telefone com DDD"
            )

        with col2:
            email = st.text_input(
                "E-mail *",
                placeholder="email@empresa.com"
            )

        with col3:
            nome_contato = st.text_input(
                "Nome do Contato *",
                placeholder="Pessoa responsável"
            )

        st.markdown("---")

        # Botão de envio
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button(
                "✅ Cadastrar Proposta",
                use_container_width=True,
                type="primary"
            )

    # Processamento do formulário
    if submitted:
        # Coleta os dados
        dados = {
            'cpf_cnpj': cpf_cnpj,
            'razao_social': razao_social,
            'rua': rua,
            'numero': numero,
            'complemento': complemento,
            'cep': cep,
            'ponto_referencia': ponto_referencia,
            'telefone': telefone,
            'email': email,
            'nome_contato': nome_contato
        }

        # Lista de erros
        erros = []

        # Validação de campos obrigatórios
        erros.extend(validar_campos_obrigatorios(dados))

        # Validações específicas (apenas se o campo foi preenchido)
        if cpf_cnpj.strip():
            valido, msg = validar_cpf_cnpj(cpf_cnpj)
            if not valido:
                erros.append(msg)

        if email.strip():
            valido, msg = validar_email(email)
            if not valido:
                erros.append(msg)

        if telefone.strip():
            valido, msg = validar_telefone(telefone)
            if not valido:
                erros.append(msg)

        if cep.strip():
            valido, msg = validar_cep(cep)
            if not valido:
                erros.append(msg)

        # Exibe erros ou salva
        if erros:
            st.error("**Por favor, corrija os seguintes erros:**")
            for erro in erros:
                st.warning(f"• {erro}")
        else:
            # Limpa o documento antes de salvar
            cpf_cnpj_limpo = limpar_documento(cpf_cnpj)

            # Verifica se já existe
            if db.verificar_cpf_cnpj_existe(cpf_cnpj_limpo):
                st.warning("⚠️ Já existe uma proposta cadastrada com este CPF/CNPJ.")
            else:
                # Tenta inserir no banco
                sucesso = db.inserir_proposta(
                    cpf_cnpj=cpf_cnpj_limpo,
                    razao_social=razao_social.strip(),
                    rua=rua.strip(),
                    numero=numero.strip(),
                    complemento=complemento.strip(),
                    cep=limpar_documento(cep),
                    ponto_referencia=ponto_referencia.strip(),
                    telefone=limpar_documento(telefone),
                    email=email.strip().lower(),
                    nome_contato=nome_contato.strip()
                )

                if sucesso:
                    st.success("✅ Proposta cadastrada com sucesso!")
                    st.balloons()
                    # Incrementa a key do formulário para limpar os campos
                    st.session_state.form_key += 1
                    st.rerun()
                else:
                    st.error("❌ Erro ao cadastrar proposta. Tente novamente.")


# ============================================================================
# PÁGINA - CONSULTAR REGISTROS
# ============================================================================

elif pagina == "Consultar Registros":
    # Cabeçalho
    st.markdown('<h1 class="main-header">📋 Consulta de Propostas</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Visualize e gerencie as propostas cadastradas</p>', unsafe_allow_html=True)

    # Filtros e busca
    st.markdown('<p class="section-header">🔍 Busca e Filtros</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        termo_busca = st.text_input(
            "Buscar",
            placeholder="Digite para buscar...",
            label_visibility="collapsed"
        )

    with col2:
        campo_busca = st.selectbox(
            "Buscar por",
            ["Razão Social", "CPF/CNPJ"],
            label_visibility="collapsed"
        )

    with col3:
        ordem = st.selectbox(
            "Ordenar por",
            ["Mais recentes", "Mais antigos"],
            label_visibility="collapsed"
        )

    # Busca ou lista os registros
    if termo_busca:
        campo = "razao_social" if campo_busca == "Razão Social" else "cpf_cnpj"
        propostas = db.buscar_propostas(termo_busca, campo)
    else:
        ordem_db = "desc" if ordem == "Mais recentes" else "asc"
        propostas = db.listar_propostas(ordem_db)

    # Exibe resultados
    st.markdown("---")

    if propostas:
        st.markdown(f"**{len(propostas)} registro(s) encontrado(s)**")

        # Botão de exportação
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            csv_data = db.exportar_csv()
            if csv_data:
                st.download_button(
                    label="📥 Exportar CSV",
                    data=csv_data,
                    file_name=f"propostas_parceria_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

        st.markdown("")

        # Tabela de resultados
        for proposta in propostas:
            with st.expander(
                f"🏢 {proposta['razao_social']} - {formatar_cpf_cnpj(proposta['cpf_cnpj'])}",
                expanded=False
            ):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Dados da Empresa**")
                    st.write(f"**CPF/CNPJ:** {formatar_cpf_cnpj(proposta['cpf_cnpj'])}")
                    st.write(f"**Razão Social:** {proposta['razao_social']}")

                    st.markdown("**Endereço**")
                    endereco = f"{proposta['rua']}, {proposta['numero']}"
                    if proposta['complemento']:
                        endereco += f" - {proposta['complemento']}"
                    st.write(f"**Logradouro:** {endereco}")

                    cep_formatado = proposta['cep']
                    if len(cep_formatado) == 8:
                        cep_formatado = f"{cep_formatado[:5]}-{cep_formatado[5:]}"
                    st.write(f"**CEP:** {cep_formatado}")

                    if proposta['ponto_referencia']:
                        st.write(f"**Referência:** {proposta['ponto_referencia']}")

                with col2:
                    st.markdown("**Contato**")
                    st.write(f"**Nome:** {proposta['nome_contato']}")

                    telefone = proposta['telefone']
                    if len(telefone) == 11:
                        telefone = f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
                    elif len(telefone) == 10:
                        telefone = f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
                    st.write(f"**Telefone:** {telefone}")

                    st.write(f"**E-mail:** {proposta['email']}")

                    st.markdown("**Cadastro**")
                    st.write(f"**Data:** {proposta['data_cadastro']}")
                    st.write(f"**ID:** #{proposta['id']}")

    else:
        st.info("📭 Nenhuma proposta encontrada.")

        if termo_busca:
            st.markdown("*Tente buscar com outros termos ou verifique a ortografia.*")
        else:
            st.markdown("*Cadastre sua primeira proposta no menu 'Novo Cadastro'.*")
