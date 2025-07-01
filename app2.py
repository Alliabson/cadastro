import streamlit as st
import requests
from fpdf import FPDF
import base64
import pandas as pd
import socket
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import datetime # Importado para tratamento de datas
import re # Importado para tratamento de strings e validações

# Inicializa as variáveis de estado da sessão do Streamlit,
# garantindo que elas existam antes de serem acessadas para evitar KeyError.
# Isso é crucial para campos que são preenchidos por busca de CEP.
if "comprador_cep_pf" not in st.session_state:
    st.session_state.comprador_cep_pf = ""
if "comprador_end_residencial_pf" not in st.session_state:
    st.session_state.comprador_end_residencial_pf = ""
if "comprador_bairro_pf" not in st.session_state:
    st.session_state.comprador_bairro_pf = ""
if "comprador_cidade_pf" not in st.session_state:
    st.session_state.comprador_cidade_pf = ""
if "comprador_estado_pf" not in st.session_state:
    st.session_state.comprador_estado_pf = ""
if "comprador_numero_pf" not in st.session_state:
    st.session_state.comprador_numero_pf = ""

if "conjuge_cep_pf" not in st.session_state:
    st.session_state.conjuge_cep_pf = ""
if "conjuge_end_residencial_pf" not in st.session_state:
    st.session_state.conjuge_end_residencial_pf = ""
if "conjuge_bairro_pf" not in st.session_state:
    st.session_state.conjuge_bairro_pf = ""
if "conjuge_cidade_pf" not in st.session_state:
    st.session_state.conjuge_cidade_pf = ""
if "conjuge_estado_pf" not in st.session_state:
    st.session_state.conjuge_estado_pf = ""
if "conjuge_numero_pf" not in st.session_state:
    st.session_state.conjuge_numero_pf = ""

if "comprador_cep_pj" not in st.session_state:
    st.session_state.comprador_cep_pj = ""
if "comprador_end_residencial_comercial_pj" not in st.session_state:
    st.session_state.comprador_end_residencial_comercial_pj = ""
if "comprador_bairro_pj" not in st.session_state:
    st.session_state.comprador_bairro_pj = ""
if "comprador_cidade_pj" not in st.session_state:
    st.session_state.comprador_cidade_pj = ""
if "comprador_estado_pj" not in st.session_state:
    st.session_state.comprador_estado_pj = ""
if "comprador_numero_pj" not in st.session_state:
    st.session_state.comprador_numero_pj = ""

if "representante_cep_pj" not in st.session_state:
    st.session_state.representante_cep_pj = ""
if "representante_end_residencial_pj" not in st.session_state:
    st.session_state.representante_end_residencial_pj = ""
if "representante_bairro_pj" not in st.session_state:
    st.session_state.representante_bairro_pj = ""
if "representante_cidade_pj" not in st.session_state:
    st.session_state.representante_cidade_pj = ""
if "representante_estado_pj" not in st.session_state:
    st.session_state.representante_estado_pj = ""
if "representante_numero_pj" not in st.session_state:
    st.session_state.representante_numero_pj = ""

if "conjuge_cep_pj" not in st.session_state:
    st.session_state.conjuge_cep_pj = ""
if "conjuge_end_residencial_pj" not in st.session_state:
    st.session_state.conjuge_end_residencial_pj = ""
if "conjuge_bairro_pj" not in st.session_state:
    st.session_state.conjuge_bairro_pj = ""
if "conjuge_cidade_pj" not in st.session_state:
    st.session_state.conjuge_cidade_pj = ""
if "conjuge_estado_pj" not in st.session_state:
    st.session_state.conjuge_estado_pj = ""
if "conjuge_numero_pj" not in st.session_state:
    st.session_state.conjuge_numero_pj = ""

# Adicionado para pessoas vinculadas
if "endereco_pessoa_pj" not in st.session_state:
    st.session_state.endereco_pessoa_pj = ""
if "bairro_pessoa_pj" not in st.session_state:
    st.session_state.bairro_pessoa_pj = ""
if "cidade_pessoa_pj" not in st.session_state:
    st.session_state.cidade_pessoa_pj = ""
if "estado_pessoa_pj" not in st.session_state:
    st.session_state.estado_pessoa_pj = ""

# Adicionado para dependentes PF
if "dependentes_pf_temp" not in st.session_state:
    st.session_state.dependentes_pf_temp = []

# Adicionado para dependentes PJ
if "dependentes_pj_temp" not in st.session_state:
    st.session_state.dependentes_pj_temp = []

# Inicialização dos novos campos da proposta
if "proposta_valor_imovel" not in st.session_state:
    st.session_state.proposta_valor_imovel = ""
if "proposta_forma_pagamento_imovel" not in st.session_state:
    st.session_state.proposta_forma_pagamento_imovel = ""
if "proposta_valor_honorarios" not in st.session_state:
    st.session_state.proposta_valor_honorarios = ""
if "proposta_forma_pagamento_honorarios" not in st.session_state:
    st.session_state.proposta_forma_pagamento_honorarios = ""
if "proposta_conta_bancaria" not in st.session_state:
    st.session_state.proposta_conta_bancaria = ""
if "proposta_valor_ir" not in st.session_state:
    st.session_state.proposta_valor_ir = ""
if "proposta_valor_escritura" not in st.session_state: # Corrigido: era 'proposta_escritura'
    st.session_state.proposta_valor_escritura = ""
if "proposta_observacoes" not in st.session_state:
    st.session_state.proposta_observacoes = ""
if "proposta_corretor_angariador" not in st.session_state:
    st.session_state.proposta_corretor_angariador = ""
if "proposta_corretor_vendedor" not in st.session_state:
    st.session_state.proposta_corretor_vendedor = ""
if "proposta_data_negociacao" not in st.session_state:
    st.session_state.proposta_data_negociacao = datetime.date.today() # Valor padrão para data

# Configuração de sessão com retry para requisições HTTP
session = requests.Session()
retry = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# Lista de regimes de bens do casamento
REGIMES_DE_BENS = [
    "", # Opção vazia inicial
    "Comunhão Universal de Bens",
    "Comunhão Parcial de Bens",
    "Separação Total de Bens",
    "Separação Obrigatória de Bens",
    "Participação Final nos Aquestos",
]

def _buscar_cep_viacep(cep):
    """
    Busca informações de endereço a partir de um CEP usando a API ViaCEP.
    Retorna um dicionário com os dados do endereço e uma mensagem de erro (ou None).
    """
    url = f"https://viacep.com.br/ws/{cep}/json/"
    try:
        response = session.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if "erro" not in data:
            return data, None
        else:
            return None, f"CEP não encontrado na ViaCEP: {cep}"
    except requests.exceptions.Timeout:
        return None, "Tempo de conexão esgotado com ViaCEP."
    except requests.exceptions.ConnectionError:
        return None, "Não foi possível conectar ao servidor ViaCEP."
    except requests.exceptions.RequestException as e:
        return None, f"Erro na ViaCEP: {str(e)}"

def _buscar_cep_brasilapi(cep):
    """
    Busca informações de endereço a partir de um CEP usando a API Brasil API.
    Retorna um dicionário com os dados do endereço e uma mensagem de erro (ou None).
    """
    url = f"https://brasilapi.com.br/api/cep/v1/{cep}"
    try:
        response = session.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return {
            'logradouro': data.get('street', ''),
            'bairro': data.get('neighborhood', ''),
            'localidade': data.get('city', ''),
            'uf': data.get('state', '')
        }, None
    except requests.exceptions.Timeout:
        return None, "Tempo de conexão esgotado com Brasil API."
    except requests.exceptions.ConnectionError:
        return None, "Não foi possível conectar ao servidor Brasil API."
    except requests.exceptions.RequestException as e:
        return None, f"Erro na Brasil API: {str(e)}"

def _buscar_cep_postmon(cep):
    """
    Busca informações de endereço a partir de um CEP usando a API Postmon.
    Retorna um dicionário com os dados do endereço e uma mensagem de erro (ou None).
    """
    url = f"https://api.postmon.com.br/v1/cep/{cep}"
    try:
        response = session.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return {
            'logradouro': data.get('logradouro', ''),
            'bairro': data.get('bairro', ''),
            'localidade': data.get('cidade', ''),
            'uf': data.get('estado', '')
        }, None
    except requests.exceptions.Timeout:
        return None, "Tempo de conexão esgotado com Postmon."
    except requests.exceptions.ConnectionError:
        return None, "Não foi possível conectar ao servidor Postmon."
    except requests.exceptions.RequestException as e:
        return None, f"Erro na Postmon: {str(e)}"

def buscar_cep(cep):
    """
    Tenta buscar informações de endereço usando múltiplas APIs de CEP em cascata.
    Retorna um dicionário com os dados do endereço e uma mensagem de erro (ou None).
    """
    if not cep:
        return None, "Por favor, insira um CEP para buscar."
        
    cep_limpo = cep.replace("-", "").replace(".", "").strip()
    if len(cep_limpo) != 8 or not cep_limpo.isdigit():
        return None, "CEP inválido. Por favor, insira 8 dígitos numéricos."

    # Tentar ViaCEP primeiro
    endereco_info, error_msg = _buscar_cep_viacep(cep_limpo)
    if endereco_info:
        return endereco_info, None
    else:
        st.warning(f"ViaCEP falhou: {error_msg}. Tentando Brasil API...")
        
        # Tentar Brasil API como fallback
        endereco_info, error_msg = _buscar_cep_brasilapi(cep_limpo)
        if endereco_info:
            return endereco_info, None
        else:
            st.warning(f"Brasil API falhou: {error_msg}. Tentando Postmon...")
            
            # Tentar Postmon como último fallback
            endereco_info, error_msg = _buscar_cep_postmon(cep_limpo)
            if endereco_info:
                return endereco_info, None
            else:
                return None, f"Todas as APIs de CEP falharam: {error_msg}"


def sanitize_text(text):
    """
    Substitui caracteres Unicode problemáticos (como o en dash '\u2013')
    por equivalentes ASCII para evitar erros de codificação no FPDF.
    Também remove caracteres que não são compatíveis com latin-1 (como emojis).
    """
    if isinstance(text, str):
        # Substitui o "en dash" pelo hífen
        text = text.replace('\u2013', '-')
        # Substitui o "em dash" por hífen duplo
        text = text.replace('\u2014', '--')
        # Substitui aspas simples direitas
        text = text.replace('\u2019', "'")
        # Substitui aspas duplas esquerdas
        text = text.replace('\u201C', '"')
        # Substitui aspas duplas direitas
        text = text.replace('\u201D', '"')
        # Remove caracteres que não podem ser codificados em latin-1 (incluindo a maioria dos emojis)
        text = text.encode('latin-1', 'ignore').decode('latin-1')
        text = text.strip() # Remove espaços em branco do início e fim
    return text

def _on_cep_search_callback(tipo_campo: str, cep_key: str):
    """Callback para botões de busca de CEP."""
    cep_value = st.session_state[cep_key] # Pega o valor do CEP do session_state
    if cep_value:
        endereco_info, error_msg = buscar_cep(cep_value)
        if endereco_info:
            mapping = {
                'pf': {
                    'logradouro': 'comprador_end_residencial_pf',
                    'bairro': 'comprador_bairro_pf',
                    'localidade': 'comprador_cidade_pf',
                    'uf': 'comprador_estado_pf',
                },
                'conjuge_pf': {
                    'logradouro': 'conjuge_end_residencial_pf',
                    'bairro': 'conjuge_bairro_pf',
                    'localidade': 'conjuge_cidade_pf',
                    'uf': 'conjuge_estado_pf',
                },
                'empresa_pj': {
                    'logradouro': 'comprador_end_residencial_comercial_pj',
                    'bairro': 'comprador_bairro_pj',
                    'localidade': 'comprador_cidade_pj',
                    'uf': 'comprador_estado_pj',
                },
                'administrador_pj': {
                    'logradouro': 'representante_end_residencial_pj',
                    'bairro': 'representante_bairro_pj',
                    'localidade': 'representante_cidade_pj',
                    'uf': 'representante_estado_pj',
                },
                'conjuge_pj': {
                    'logradouro': 'conjuge_end_residencial_pj',
                    'bairro': 'conjuge_bairro_pj',
                    'localidade': 'conjuge_cidade_pj',
                    'uf': 'conjuge_estado_pj',
                },
                'pessoa_pj': { # Para pessoas vinculadas (não diretamente ligadas a um campo de formulário visível que o usuário preenche o CEP)
                    'logradouro': 'endereco_pessoa_pj',
                    'bairro': 'bairro_pessoa_pj',
                    'localidade': 'cidade_pessoa_pj',
                    'uf': 'estado_pessoa_pj'
                }
            }
            target_keys = mapping.get(tipo_campo)
            if target_keys:
                for campo_origem, session_key in target_keys.items():
                    try:
                        # Preenche os campos de endereço no session_state
                        st.session_state[session_key] = endereco_info.get(campo_origem, '')
                    except Exception as e:
                        st.warning(f"Erro ao definir o valor de {session_key}: {str(e)}")
                st.success("Endereço preenchido!")
            else:
                st.error("Tipo de campo de endereço desconhecido.")
        elif error_msg:
            st.error(error_msg)
    else:
        st.warning("Por favor, digite um CEP para buscar.")
    # Não é necessário st.rerun() aqui, o próprio clique do botão (dentro ou fora do form)
    # já aciona um rerun do Streamlit, que renderizará os campos com os novos valores.


def formatar_cpf(cpf: str) -> str:
    """Formata o CPF como 000.000.000-00."""
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf

def formatar_cnpj(cnpj: str) -> str:
    """Formata o CNPJ como 00.000.000/0000-00."""
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    if len(cnpj) == 14:
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    return cnpj

def formatar_telefone(telefone: str) -> str:
    """
    Formata o telefone celular como 00-99999-0000 e telefone fixo como 00 0000-0000.
    """
    telefone = re.sub(r'[^0-9]', '', telefone)
    if len(telefone) == 11 and telefone[2] == '9': # Celular com 9º dígito
        return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}" # Adicionado parênteses para DDD
    elif len(telefone) == 10: # Telefone fixo ou celular sem 9º dígito
        return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
    return telefone # Retorna sem formatação se não corresponder aos padrões


def gerar_pdf_pf(dados, dependentes=None, dados_proposta=None):
    """
    Gera um arquivo PDF com os dados da Ficha Cadastral de Pessoa Física.
    """
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Usando fontes padrão do FPDF que suportam caracteres acentuados
        pdf.set_font('Helvetica', '', 10)
        
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, sanitize_text("Ficha Cadastral Pessoa Física - Cessão e Transferência de Direitos"), 0, 1, "C")
        pdf.ln(8) # Reduzido de 10 para 8

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, sanitize_text("Dados do Empreendimento e Imobiliária"), 0, 1, "L")
        pdf.set_font("Helvetica", "", 10)
        # Campos do empreendimento
        for key_suffix in ["empreendimento", "corretor", "imobiliaria", "qd", "lt", "ativo", "quitado"]:
            key = f"{key_suffix}_pf"
            value = dados.get(key, '')
            if value and sanitize_text(value):
                pdf.cell(0, 6, f"{sanitize_text(key_suffix.replace('_', ' ').title())}: {sanitize_text(str(value))}", 0, 1) # Reduzido de 7 para 6
        pdf.ln(3) # Reduzido de 5 para 3

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, sanitize_text("Dados do COMPRADOR(A)"), 0, 1, "L")
        pdf.set_font("Helvetica", "", 10)
        
        # Nome Completo, Profissão
        nome_comprador = dados.get('comprador_nome_pf', '')
        profissao_comprador = dados.get('comprador_profissao_pf', '')
        if nome_comprador or profissao_comprador:
            pdf.cell(95, 6, f"Nome Completo: {sanitize_text(nome_comprador)}", 0, 0)
            pdf.cell(0, 6, f"Profissão: {sanitize_text(profissao_comprador)}", 0, 1)

        # Nacionalidade
        nacionalidade_comprador = dados.get('comprador_nacionalidade_pf', '')
        if nacionalidade_comprador:
            pdf.cell(0, 6, f"Nacionalidade: {sanitize_text(nacionalidade_comprador)}", 0, 1)

        # Fone Residencial, Fone Comercial
        fone_residencial_comprador = dados.get('comprador_fone_residencial_pf', '')
        fone_comercial_comprador = dados.get('comprador_fone_comercial_pf', '')
        if fone_residencial_comprador or fone_comercial_comprador:
            pdf.cell(95, 6, f"Fone Residencial: {sanitize_text(formatar_telefone(fone_residencial_comprador))}", 0, 0)
            pdf.cell(0, 6, f"Fone Comercial: {sanitize_text(formatar_telefone(fone_comercial_comprador))}", 0, 1)

        # Celular, E-mail
        celular_comprador = dados.get('comprador_celular_pf', '')
        email_comprador = dados.get('comprador_email_pf', '')
        if celular_comprador or email_comprador:
            pdf.cell(95, 6, f"Celular: {sanitize_text(formatar_telefone(celular_comprador))}", 0, 0)
            pdf.cell(0, 6, f"E-mail: {sanitize_text(email_comprador)}", 0, 1)

        # Endereço Residencial, Número
        endereco_res_comprador = dados.get('comprador_end_residencial_pf', '')
        numero_comprador = dados.get('comprador_numero_pf', '')
        if endereco_res_comprador:
            endereco_linha = f"Endereço Residencial: {sanitize_text(endereco_res_comprador)}"
            if numero_comprador:
                endereco_linha += f", Nº {sanitize_text(numero_comprador)}"
            pdf.cell(0, 6, endereco_linha, 0, 1)

        # Bairro, Cidade/Estado, CEP
        bairro_comprador = dados.get('comprador_bairro_pf', '')
        cidade_comprador = dados.get('comprador_cidade_pf', '')
        estado_comprador = dados.get('comprador_estado_pf', '')
        cep_comprador = dados.get('comprador_cep_pf', '')

        if bairro_comprador or cidade_comprador or estado_comprador or cep_comprador:
            if bairro_comprador:
                pdf.cell(95, 6, f"Bairro: {sanitize_text(bairro_comprador)}", 0, 0)
            if cidade_comprador and estado_comprador:
                pdf.cell(0, 6, f"Cidade/Estado: {sanitize_text(cidade_comprador)}/{sanitize_text(estado_comprador)}", 0, 1)
            elif bairro_comprador: # If only bairro and no city/state, force line break after bairro
                pdf.ln(6) 
            
            if cep_comprador:
                pdf.cell(0, 6, f"CEP: {sanitize_text(cep_comprador)}", 0, 1)

        # Estado Civil, Regime de Bens
        estado_civil_comprador = dados.get('comprador_estado_civil_pf', '')
        regime_bens_comprador = dados.get('comprador_regime_bens_pf', '')
        if estado_civil_comprador or regime_bens_comprador:
            pdf.cell(95, 6, f"Estado Civil: {sanitize_text(estado_civil_comprador)}", 0, 0)
            pdf.cell(0, 6, f"Regime de Bens: {sanitize_text(regime_bens_comprador)}", 0, 1)

        # União Estável
        uniao_estavel_comprador = dados.get('comprador_uniao_estavel_pf', '')
        if uniao_estavel_comprador:
            pdf.cell(0, 6, f"União Estável: {sanitize_text(uniao_estavel_comprador)}", 0, 1)

        pdf.ln(3) # Reduzido de 5 para 3
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, sanitize_text("Condição de Convivência:"), 0, 1) # Reduzido de 7 para 6
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 4.5, sanitize_text("Declara conviver em união estável - Apresentar comprovante de estado civil de cada um e a declaração de convivência em união estável com as assinaturas reconhecidas em Cartório."), 0, "L") # Reduzido de 5 para 4.5
        pdf.ln(3) # Reduzido de 5 para 3

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, sanitize_text("Dados do CÔNJUGE/SÓCIO(A)"), 0, 1, "L")
        pdf.set_font("Helvetica", "", 10)
        
        # Nome Completo Cônjuge/Sócio(a), Profissão Cônjuge/Sócio(a)
        nome_conjuge = dados.get('conjuge_nome_pf', '')
        profissao_conjuge = dados.get('conjuge_profissao_pf', '')
        if nome_conjuge or profissao_conjuge:
            pdf.cell(95, 6, f"Nome Completo Cônjuge/Sócio(a): {sanitize_text(nome_conjuge)}", 0, 0)
            pdf.cell(0, 6, f"Profissão Cônjuge/Sócio(a): {sanitize_text(profissao_conjuge)}", 0, 1)

        # Nacionalidade Cônjuge/Sócio(a)
        nacionalidade_conjuge = dados.get('conjuge_nacionalidade_pf', '')
        if nacionalidade_conjuge:
            pdf.cell(0, 6, f"Nacionalidade Cônjuge/Sócio(a): {sanitize_text(nacionalidade_conjuge)}", 0, 1)

        # Fone Residencial Cônjuge/Sócio(a), Fone Comercial Cônjuge/Sócio(a)
        fone_residencial_conjuge = dados.get('conjuge_fone_residencial_pf', '')
        fone_comercial_conjuge = dados.get('conjuge_fone_comercial_pf', '')
        if fone_residencial_conjuge or fone_comercial_conjuge:
            pdf.cell(95, 6, f"Fone Residencial: {sanitize_text(formatar_telefone(fone_residencial_conjuge))}", 0, 0)
            pdf.cell(0, 6, f"Fone Comercial: {sanitize_text(formatar_telefone(fone_comercial_conjuge))}", 0, 1)

        # Celular Cônjuge/Sócio(a), E-mail Cônjuge/Sócio(a)
        celular_conjuge = dados.get('conjuge_celular_pf', '')
        email_conjuge = dados.get('conjuge_email_pf', '')
        if celular_conjuge or email_conjuge:
            pdf.cell(95, 6, f"Celular: {sanitize_text(formatar_telefone(celular_conjuge))}", 0, 0)
            pdf.cell(0, 6, f"E-mail: {sanitize_text(email_conjuge)}", 0, 1)

        # Endereço Residencial Cônjuge/Sócio(a), Número Cônjuge/Sócio(a)
        endereco_res_conjuge = dados.get('conjuge_end_residencial_pf', '')
        numero_conjuge = dados.get('conjuge_numero_pf', '')
        if endereco_res_conjuge:
            endereco_linha_conjuge = f"Endereço Residencial: {sanitize_text(endereco_res_conjuge)}"
            if numero_conjuge:
                endereco_linha_conjuge += f", Nº {sanitize_text(numero_conjuge)}"
            pdf.cell(0, 6, endereco_linha_conjuge, 0, 1)
        
        # Bairro Cônjuge/Sócio(a), Cidade/Estado Cônjuge/Sócio(a), CEP Cônjuge/Sócio(a)
        bairro_conjuge = dados.get('conjuge_bairro_pf', '')
        cidade_conjuge = dados.get('conjuge_cidade_pf', '')
        estado_conjuge = dados.get('conjuge_estado_pf', '')
        cep_conjuge = dados.get('conjuge_cep_pf', '')

        if bairro_conjuge or cidade_conjuge or estado_conjuge or cep_conjuge:
            if bairro_conjuge:
                pdf.cell(95, 6, f"Bairro: {sanitize_text(bairro_conjuge)}", 0, 0)
            if cidade_conjuge and estado_conjuge:
                pdf.cell(0, 6, f"Cidade/Estado: {sanitize_text(cidade_conjuge)}/{sanitize_text(estado_conjuge)}", 0, 1)
            elif bairro_conjuge: # If only bairro and no city/state, force line break after bairro
                pdf.ln(6) 
            
            if cep_conjuge:
                pdf.cell(0, 6, f"CEP: {sanitize_text(cep_conjuge)}", 0, 1)
        
        pdf.ln(3) # Reduzido de 5 para 3

        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, sanitize_text("DOCUMENTOS NECESSÁRIOS:"), 0, 1) # Reduzido de 7 para 6
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 4.5, sanitize_text("CNH; RG e CPF; Comprovante do Estado Civil, Comprovante de Endereço, Comprovante de Renda, CND da Prefeitura e Nada Consta do Condomínio ou Associação."), 0, "L") # Reduzido de 5 para 4.5
        pdf.ln(3) # Reduzido de 5 para 3

        # Campo adicional para condômino indicado
        condomino_indicado = dados.get('condomino_indicado_pf', '')
        if condomino_indicado and sanitize_text(condomino_indicado):
            pdf.ln(5)
            pdf.set_font("Helvetica", "B", 10)
            pdf.multi_cell(0, 6, sanitize_text("No caso de Condomínio ou Loteamento Fechado, quando a cessão for emitida para sócio(a)(s), não casados entre si e nem conviventes é necessário indicar qual dos dois será o(a) condômino(a):"), 0, 'L')
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 6, f"Indique aqui quem será o(a) condômino(a): {sanitize_text(condomino_indicado)}", 0, 1)
            pdf.ln(3)

        # Inserir Dados da Proposta em uma nova página, se houver
        if dados_proposta:
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, sanitize_text("Dados da Proposta"), 0, 1, "C")
            pdf.ln(5)
            pdf.set_font("Helvetica", "", 10)

            # Valor do imóvel e Forma de pagamento (imóvel)
            valor_imovel = dados_proposta.get('valor_imovel', '')
            forma_pagamento_imovel = dados_proposta.get('forma_pagamento_imovel', '')
            if valor_imovel or forma_pagamento_imovel:
                pdf.cell(80, 6, f"Valor do imóvel: {sanitize_text(valor_imovel)}", 0, 0) # Adjusted width
                # Usar multi_cell para forma de pagamento para permitir quebra de linha
                pdf.multi_cell(110, 6, f"Forma de pagamento (Imóvel): {sanitize_text(forma_pagamento_imovel)}", 0, "L") 

            # Valor dos honorários e Forma de pagamento (honorários)
            valor_honorarios = dados_proposta.get('valor_honorarios', '')
            forma_pagamento_honorarios = dados_proposta.get('forma_pagamento_honorarios', '')
            if valor_honorarios or forma_pagamento_honorarios:
                pdf.cell(80, 6, f"Valor dos honorários: {sanitize_text(valor_honorarios)}", 0, 0) # Adjusted width
                # Usar multi_cell para forma de pagamento para permitir quebra de linha
                pdf.multi_cell(110, 6, f"Forma de pagamento (Honorários): {sanitize_text(forma_pagamento_honorarios)}", 0, "L") 

            # Conta Bancária para transferência
            conta_bancaria = dados_proposta.get('conta_bancaria', '')
            if conta_bancaria:
                pdf.cell(0, 6, f"Conta Bancária para transferência: {sanitize_text(conta_bancaria)}", 0, 1)

            # Valor para declaração de imposto de renda
            valor_ir = dados_proposta.get('valor_ir', '')
            if valor_ir:
                pdf.cell(0, 6, f"Valor para declaração de imposto de renda: {sanitize_text(valor_ir)}", 0, 1)
            
            # Valor para escritura
            valor_escritura = dados_proposta.get('valor_escritura', '')
            if valor_escritura:
                pdf.cell(0, 6, f"Valor para escritura: {sanitize_text(valor_escritura)}", 0, 1)

            # Observações
            observacoes_proposta = dados_proposta.get('observacoes', '')
            if observacoes_proposta:
                pdf.multi_cell(0, 6, f"Observações: {sanitize_text(observacoes_proposta)}", 0, "L")
            
            # Corretor(a) angariador e Corretor(a) vendedor(a)
            corretor_angariador = dados_proposta.get('corretor_angariador', '')
            corretor_vendedor = dados_proposta.get('corretor_vendedor', '')
            if corretor_angariador or corretor_vendedor:
                pdf.cell(95, 6, f"Corretor(a) angariador: {sanitize_text(corretor_angariador)}", 0, 0)
                pdf.cell(0, 6, f"Corretor(a) vendedor(a): {sanitize_text(corretor_vendedor)}", 0, 1)

            # Data da negociação
            data_negociacao = dados_proposta.get('data_negociacao', '')
            if data_negociacao:
                pdf.cell(0, 6, f"Data da negociação: {sanitize_text(str(data_negociacao))}", 0, 1)

            pdf.ln(5) # Espaço após dados da proposta


        # Adiciona a seção de data e assinaturas
        pdf.ln(7) # Ajustado espaçamento
        today = datetime.date.today()
        month_names = {
            1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril", 5: "maio", 6: "junho",
            7: "julho", 8: "agosto", 9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
        }
        
        # Cidade/Estado,___ de _________de __________
        current_city_state = f"{sanitize_text(dados.get('comprador_cidade_pf', ''))}/{sanitize_text(dados.get('comprador_estado_pf', ''))}"
        pdf.cell(0, 6, f"{current_city_state}, {today.day} de {month_names[today.month]} de {today.year}", 0, 1, 'C') # Reduzido de 7 para 6
        pdf.ln(7) # Ajustado espaçamento

        # Assinatura do(a) Comprador(a)
        pdf.cell(0, 0, "_" * 50, 0, 1, 'C') # Linha para assinatura
        pdf.ln(3) # Reduzido de 5 para 3
        pdf.cell(0, 4, sanitize_text("Assinatura do(a) Comprador(a)"), 0, 1, 'C') # Reduzido de 5 para 4
        pdf.ln(7) # Ajustado espaçamento

        # Autorizado em:__________/______/__________
        pdf.cell(0, 6, f"Autorizado em: {today.strftime('%d/%m/%Y')}", 0, 1, 'C') # Reduzido de 7 para 6
        pdf.ln(7) # Ajustado espaçamento

        # Sistema Imobiliário
        pdf.cell(0, 0, "_" * 50, 0, 1, 'C') # Linha para assinatura
        pdf.ln(3) # Reduzido de 5 para 3
        pdf.cell(0, 4, sanitize_text("Sistema Imobiliário"), 0, 1, 'C') # Reduzido de 5 para 4
        
        # Inserir dependentes em uma nova página, se houver
        if dependentes:
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, sanitize_text("LISTAGEM DE DEPENDENTES"), 0, 1, "C")
            pdf.ln(5)

            pdf.set_font("Helvetica", "", 10)
            for i, dep in enumerate(dependentes):
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(0, 6, f"DEPENDENTE {i+1}:", 0, 1, "L")
                pdf.set_font("Helvetica", "", 9)
                pdf.cell(0, 5, f"Nome: {sanitize_text(dep.get('nome', ''))}", 0, 1)
                pdf.cell(0, 5, f"CPF: {sanitize_text(formatar_cpf(dep.get('cpf', '')))}", 0, 1)
                pdf.cell(0, 5, f"Telefone Comercial: {sanitize_text(formatar_telefone(dep.get('telefone_comercial', '')))}", 0, 1)
                pdf.cell(0, 5, f"Celular: {sanitize_text(formatar_telefone(dep.get('celular', '')))}", 0, 1)
                pdf.cell(0, 5, f"E-mail: {sanitize_text(dep.get('email', ''))}", 0, 1)
                pdf.cell(0, 5, f"Grau de Parentesco: {sanitize_text(dep.get('grau_parentesco', ''))}", 0, 1)
                pdf.ln(3) # Espaço entre dependentes
        
        # Adicionada codificação para 'latin-1'
        pdf_output = pdf.output(dest='S').encode('latin-1')
        b64_pdf = base64.b64encode(pdf_output).decode('utf-8')
        return b64_pdf
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {str(e)}")
        return None

def gerar_pdf_pj(dados, dependentes=None, dados_proposta=None):
    """
    Gera um arquivo PDF com os dados da Ficha Cadastral de Pessoa Jurídica.
    """
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Usando fontes padrão do FPDF que suportam caracteres acentuados
        pdf.set_font('Helvetica', '', 10)
        
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, sanitize_text("Ficha Cadastral Pessoa Jurídica - Cessão e Transferência de Direitos"), 0, 1, "C")
        pdf.ln(8) # Reduzido de 10 para 8

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, sanitize_text("Dados do Empreendimento e Imobiliária"), 0, 1, "L")
        pdf.set_font("Helvetica", "", 10)
        # Campos do empreendimento
        for key_suffix in ["empreendimento", "corretor", "imobiliaria", "qd", "lt", "ativo", "quitado"]:
            key = f"{key_suffix}_pj"
            value = dados.get(key, '')
            if value and sanitize_text(value):
                pdf.cell(0, 6, f"{sanitize_text(key_suffix.replace('_', ' ').title())}: {sanitize_text(str(value))}", 0, 1) # Reduzido de 7 para 6
        pdf.ln(3) # Reduzido de 5 para 3

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, sanitize_text("Dados do COMPRADOR(A)"), 0, 1, "L")
        pdf.set_font("Helvetica", "", 10)
        
        # Razão Social, Nome Fantasia
        razao_social_comprador_pj = dados.get('comprador_razao_social_pj', '')
        nome_fantasia_comprador_pj = dados.get('comprador_nome_fantasia_pj', '')
        if razao_social_comprador_pj or nome_fantasia_comprador_pj:
            pdf.cell(95, 6, f"Razão Social: {sanitize_text(razao_social_comprador_pj)}", 0, 0)
            pdf.cell(0, 6, f"Nome Fantasia: {sanitize_text(nome_fantasia_comprador_pj)}", 0, 1)
        
        # Inscrição Estadual
        inscricao_estadual_comprador_pj = dados.get('comprador_inscricao_estadual_pj', '')
        if inscricao_estadual_comprador_pj:
            pdf.cell(0, 6, f"Inscrição Estadual: {sanitize_text(inscricao_estadual_comprador_pj)}", 0, 1)

        # Fone Residencial, Fone Comercial
        fone_residencial_comprador_pj = dados.get('comprador_fone_residencial_pj', '')
        fone_comercial_comprador_pj = dados.get('comprador_fone_comercial_pj', '')
        if fone_residencial_comprador_pj or fone_comercial_comprador_pj:
            pdf.cell(95, 6, f"Fone Residencial: {sanitize_text(formatar_telefone(fone_residencial_comprador_pj))}", 0, 0)
            pdf.cell(0, 6, f"Fone Comercial: {sanitize_text(formatar_telefone(fone_comercial_comprador_pj))}", 0, 1)

        # Celular, E-mail
        celular_comprador_pj = dados.get('comprador_celular_pj', '')
        email_comprador_pj = dados.get('comprador_email_pj', '')
        if celular_comprador_pj or email_comprador_pj:
            pdf.cell(95, 6, f"Celular: {sanitize_text(formatar_telefone(celular_comprador_pj))}", 0, 0)
            pdf.cell(0, 6, f"E-mail: {sanitize_text(email_comprador_pj)}", 0, 1)

        # Endereço Residencial/Comercial, Número
        endereco_res_comercial_comprador_pj = dados.get('comprador_end_residencial_comercial_pj', '')
        numero_comprador_pj = dados.get('comprador_numero_pj', '')
        if endereco_res_comercial_comprador_pj:
            endereco_linha_pj = f"Endereço Residencial/Comercial: {sanitize_text(endereco_res_comercial_comprador_pj)}"
            if numero_comprador_pj:
                endereco_linha_pj += f", Nº {sanitize_text(numero_comprador_pj)}"
            pdf.cell(0, 6, endereco_linha_pj, 0, 1)

        # Bairro, Cidade/Estado, CEP
        bairro_comprador_pj = dados.get('comprador_bairro_pj', '')
        cidade_comprador_pj = dados.get('comprador_cidade_pj', '')
        estado_comprador_pj = dados.get('comprador_estado_pj', '')
        cep_comprador_pj = dados.get('comprador_cep_pj', '')

        if bairro_comprador_pj or cidade_comprador_pj or estado_comprador_pj or cep_comprador_pj:
            if bairro_comprador_pj:
                pdf.cell(95, 6, f"Bairro: {sanitize_text(bairro_comprador_pj)}", 0, 0)
            if cidade_comprador_pj and estado_comprador_pj:
                pdf.cell(0, 6, f"Cidade/Estado: {sanitize_text(cidade_comprador_pj)}/{sanitize_text(estado_comprador_pj)}", 0, 1)
            elif bairro_comprador_pj: # If only bairro and no city/state, force line break after bairro
                pdf.ln(6)
            
            if cep_comprador_pj:
                pdf.cell(0, 6, f"CEP: {sanitize_text(cep_comprador_pj)}", 0, 1)
        
        pdf.ln(3) # Reduzido de 5 para 3

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, sanitize_text("Dados do REPRESENTANTE"), 0, 1, "L")
        pdf.set_font("Helvetica", "", 10)

        # Nome Completo Representante, Profissão Representante
        nome_representante = dados.get('representante_nome_pj', '')
        profissao_representante = dados.get('representante_profissao_pj', '')
        if nome_representante or profissao_representante:
            pdf.cell(95, 6, f"Nome Completo Representante: {sanitize_text(nome_representante)}", 0, 0)
            pdf.cell(0, 6, f"Profissão Representante: {sanitize_text(profissao_representante)}", 0, 1)

        # Nacionalidade Representante
        nacionalidade_representante = dados.get('representante_nacionalidade_pj', '')
        if nacionalidade_representante:
            pdf.cell(0, 6, f"Nacionalidade Representante: {sanitize_text(nacionalidade_representante)}", 0, 1)

        # Fone Residencial Representante, Fone Comercial Representante
        fone_residencial_representante = dados.get('representante_fone_residencial_pj', '')
        fone_comercial_representante = dados.get('representante_fone_comercial_pj', '')
        if fone_residencial_representante or fone_comercial_representante:
            pdf.cell(95, 6, f"Fone Residencial: {sanitize_text(formatar_telefone(fone_residencial_representante))}", 0, 0)
            pdf.cell(0, 6, f"Fone Comercial: {sanitize_text(formatar_telefone(fone_comercial_representante))}", 0, 1)

        # Celular Representante, E-mail Representante
        celular_representante = dados.get('representante_celular_pj', '')
        email_representante = dados.get('representante_email_pj', '')
        if celular_representante or email_representante:
            pdf.cell(95, 6, f"Celular: {sanitize_text(formatar_telefone(celular_representante))}", 0, 0)
            pdf.cell(0, 6, f"E-mail: {sanitize_text(email_representante)}", 0, 1)

        # Endereço Residencial Representante, Número Representante
        endereco_res_representante = dados.get('representante_end_residencial_pj', '')
        numero_representante = dados.get('representante_numero_pj', '')
        if endereco_res_representante:
            endereco_linha_rep = f"Endereço Residencial: {sanitize_text(endereco_res_representante)}"
            if numero_representante:
                endereco_linha_rep += f", Nº {sanitize_text(numero_representante)}"
            pdf.cell(0, 6, endereco_linha_rep, 0, 1)

        # Bairro Representante, Cidade/Estado Representante, CEP Representante
        bairro_representante = dados.get('representante_bairro_pj', '')
        cidade_representante = dados.get('representante_cidade_pj', '')
        estado_representante = dados.get('representante_estado_pj', '')
        cep_representante = dados.get('representante_cep_pj', '')

        if bairro_representante or cidade_representante or estado_representante or cep_representante:
            if bairro_representante:
                pdf.cell(95, 6, f"Bairro: {sanitize_text(bairro_representante)}", 0, 0)
            if cidade_representante and estado_representante:
                pdf.cell(0, 6, f"Cidade/Estado: {sanitize_text(cidade_representante)}/{sanitize_text(estado_representante)}", 0, 1)
            elif bairro_representante: # If only bairro and no city/state, force line break after bairro
                pdf.ln(6)
            
            if cep_representante:
                pdf.cell(0, 6, f"CEP: {sanitize_text(cep_representante)}", 0, 1)
        
        pdf.ln(3) # Reduzido de 5 para 3
        
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, sanitize_text("Dados do CÔNJUGE/SÓCIO(A)"), 0, 1, "L")
        pdf.set_font("Helvetica", "", 10)

        # Nome Completo Cônjuge/Sócio(a) PJ, Profissão Cônjuge/Sócio(a) PJ
        nome_conjuge_pj = dados.get('conjuge_nome_pj', '')
        profissao_conjuge_pj = dados.get('conjuge_profissao_pj', '')
        if nome_conjuge_pj or profissao_conjuge_pj:
            pdf.cell(95, 6, f"Nome Completo Cônjuge/Sócio(a) PJ: {sanitize_text(nome_conjuge_pj)}", 0, 0)
            pdf.cell(0, 6, f"Profissão Cônjuge/Sócio(a) PJ: {sanitize_text(profissao_conjuge_pj)}", 0, 1)

        # Nacionalidade Cônjuge/Sócio(a) PJ
        nacionalidade_conjuge_pj = dados.get('conjuge_nacionalidade_pj', '')
        if nacionalidade_conjuge_pj:
            pdf.cell(0, 6, f"Nacionalidade Cônjuge/Sócio(a) PJ: {sanitize_text(nacionalidade_conjuge_pj)}", 0, 1)

        # Fone Residencial Cônjuge/Sócio(a) PJ, Fone Comercial Cônjuge/Sócio(a) PJ
        fone_residencial_conjuge_pj = dados.get('conjuge_fone_residencial_pj', '')
        fone_comercial_conjuge_pj = dados.get('conjuge_fone_comercial_pj', '')
        if fone_residencial_conjuge_pj or fone_comercial_conjuge_pj:
            pdf.cell(95, 6, f"Fone Residencial: {sanitize_text(formatar_telefone(fone_residencial_conjuge_pj))}", 0, 0)
            pdf.cell(0, 6, f"Fone Comercial: {sanitize_text(formatar_telefone(fone_comercial_conjuge_pj))}", 0, 1)

        # Celular Cônjuge/Sócio(a) PJ, E-mail Cônjuge/Sócio(a) PJ
        celular_conjuge_pj = dados.get('conjuge_celular_pj', '')
        email_conjuge_pj = dados.get('conjuge_email_pj', '')
        if celular_conjuge_pj or email_conjuge_pj:
            pdf.cell(95, 6, f"Celular: {sanitize_text(formatar_telefone(celular_conjuge_pj))}", 0, 0)
            pdf.cell(0, 6, f"E-mail: {sanitize_text(email_conjuge_pj)}", 0, 1)

        # Endereço Residencial Cônjuge/Sócio(a) PJ, Número Cônjuge/Sócio(a) PJ
        endereco_res_conjuge_pj = dados.get('conjuge_end_residencial_pj', '')
        numero_conjuge_pj = dados.get('conjuge_numero_pj', '')
        if endereco_res_conjuge_pj:
            endereco_linha_conjuge_pj = f"Endereço Residencial: {sanitize_text(endereco_res_conjuge_pj)}"
            if numero_conjuge_pj:
                endereco_linha_conjuge_pj += f", Nº {sanitize_text(numero_conjuge_pj)}"
            pdf.cell(0, 6, endereco_linha_conjuge_pj, 0, 1)

        # Bairro Cônjuge/Sócio(a) PJ, Cidade/Estado Cônjuge/Sócio(a) PJ, CEP Cônjuge/Sócio(a) PJ
        bairro_conjuge_pj = dados.get('conjuge_bairro_pj', '')
        cidade_conjuge_pj = dados.get('conjuge_cidade_pj', '')
        estado_conjuge_pj = dados.get('conjuge_estado_pj', '')
        cep_conjuge_pj = dados.get('conjuge_cep_pj', '')

        if bairro_conjuge_pj or cidade_conjuge_pj or estado_conjuge_pj or cep_conjuge_pj:
            if bairro_conjuge_pj:
                pdf.cell(95, 6, f"Bairro: {sanitize_text(bairro_conjuge_pj)}", 0, 0)
            if cidade_conjuge_pj and estado_conjuge_pj:
                pdf.cell(0, 6, f"Cidade/Estado: {sanitize_text(cidade_conjuge_pj)}/{sanitize_text(estado_conjuge_pj)}", 0, 1)
            elif bairro_conjuge_pj: # If only bairro and no city/state, force line break after bairro
                pdf.ln(6)
            
            if cep_conjuge_pj:
                pdf.cell(0, 6, f"CEP: {sanitize_text(cep_conjuge_pj)}", 0, 1)
        
        pdf.ln(3) # Reduzido de 5 para 3
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, sanitize_text("DOCUMENTOS NECESSÁRIOS:"), 0, 1) # Reduzido de 7 para 6
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 4.5, sanitize_text("DA EMPRESA: CONTRATO SOCIAL E ALTERAÇÕES, COMPROVANTE DE ENDEREÇO, DECLARAÇÃO DE FATURAMENTO;"), 0, "L") # Reduzido de 5 para 4.5
        pdf.multi_cell(0, 4.5, sanitize_text("DOS SÓCIOS E SEUS CÔNJUGES: CNH; RG e CPF, Comprovante do Estado Civil, Comprovante de Endereço, Comprovante de Renda, CND da Prefeitura e Nada Consta do Condomínio ou Associação."), 0, "L") # Reduzido de 5 para 4.5
        pdf.ln(3) # Reduzido de 5 para 3

        # Campo adicional para condômino indicado
        condomino_indicado = dados.get('condomino_indicado_pj', '')
        if condomino_indicado and sanitize_text(condomino_indicado):
            pdf.ln(5)
            pdf.set_font("Helvetica", "B", 10)
            pdf.multi_cell(0, 6, sanitize_text("No caso de Condomínio ou Loteamento Fechado, quando a empresa possuir mais de um(a) sócio(a) não casados entre si e nem conviventes, é necessário indicar qual do(a)(s) sócio(a)(s) será o(a) condômino(a):"), 0, 'L')
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 6, f"Indique aqui quem será o(a) condômino(a): {sanitize_text(condomino_indicado)}", 0, 1)
            pdf.ln(3)

        # Inserir Dados da Proposta em uma nova página, se houver
        if dados_proposta:
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, sanitize_text("Dados da Proposta"), 0, 1, "C")
            pdf.ln(5)
            pdf.set_font("Helvetica", "", 10)

            # Valor do imóvel e Forma de pagamento (imóvel)
            valor_imovel = dados_proposta.get('valor_imovel', '')
            forma_pagamento_imovel = dados_proposta.get('forma_pagamento_imovel', '')
            if valor_imovel or forma_pagamento_imovel:
                pdf.cell(80, 6, f"Valor do imóvel: {sanitize_text(valor_imovel)}", 0, 0) # Adjusted width
                # Usar multi_cell para forma de pagamento para permitir quebra de linha
                pdf.multi_cell(110, 6, f"Forma de pagamento (Imóvel): {sanitize_text(forma_pagamento_imovel)}", 0, "L") 

            # Valor dos honorários e Forma de pagamento (honorários)
            valor_honorarios = dados_proposta.get('valor_honorarios', '')
            forma_pagamento_honorarios = dados_proposta.get('forma_pagamento_honorarios', '')
            if valor_honorarios or forma_pagamento_honorarios:
                pdf.cell(80, 6, f"Valor dos honorários: {sanitize_text(valor_honorarios)}", 0, 0) # Adjusted width
                # Usar multi_cell para forma de pagamento para permitir quebra de linha
                pdf.multi_cell(110, 6, f"Forma de pagamento (Honorários): {sanitize_text(forma_pagamento_honorarios)}", 0, "L") 

            # Conta Bancária para transferência
            conta_bancaria = dados_proposta.get('conta_bancaria', '')
            if conta_bancaria:
                pdf.cell(0, 6, f"Conta Bancária para transferência: {sanitize_text(conta_bancaria)}", 0, 1)

            # Valor para declaração de imposto de renda
            valor_ir = dados_proposta.get('valor_ir', '')
            if valor_ir:
                pdf.cell(0, 6, f"Valor para declaração de imposto de renda: {sanitize_text(valor_ir)}", 0, 1)
            
            # Valor para escritura
            valor_escritura = dados_proposta.get('valor_escritura', '')
            if valor_escritura:
                pdf.cell(0, 6, f"Valor para escritura: {sanitize_text(valor_escritura)}", 0, 1)

            # Observações
            observacoes_proposta = dados_proposta.get('observacoes', '')
            if observacoes_proposta:
                pdf.multi_cell(0, 6, f"Observações: {sanitize_text(observacoes_proposta)}", 0, "L")
            
            # Corretor(a) angariador e Corretor(a) vendedor(a)
            corretor_angariador = dados_proposta.get('corretor_angariador', '')
            corretor_vendedor = dados_proposta.get('corretor_vendedor', '')
            if corretor_angariador or corretor_vendedor:
                pdf.cell(95, 6, f"Corretor(a) angariador: {sanitize_text(corretor_angariador)}", 0, 0)
                pdf.cell(0, 6, f"Corretor(a) vendedor(a): {sanitize_text(corretor_vendedor)}", 0, 1)

            # Data da negociação
            data_negociacao = dados_proposta.get('data_negociacao', '')
            if data_negociacao:
                pdf.cell(0, 6, f"Data da negociação: {sanitize_text(str(data_negociacao))}", 0, 1)

            pdf.ln(5) # Espaço após dados da proposta

        # Adiciona a seção de data e assinaturas
        pdf.ln(7) # Ajustado espaçamento
        today = datetime.date.today()
        month_names = {
            1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril", 5: "maio", 6: "junho",
            7: "julho", 8: "agosto", 9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
        }
        
        # Cidade/Estado,___ de _________de __________
        current_city_state = f"{sanitize_text(dados.get('comprador_cidade_pj', ''))}/{sanitize_text(dados.get('comprador_estado_pj', ''))}"
        pdf.cell(0, 6, f"{current_city_state}, {today.day} de {month_names[today.month]} de {today.year}", 0, 1, 'C') # Reduzido de 7 para 6
        pdf.ln(7) # Ajustado espaçamento

        # Assinatura do(a) Comprador(a) / Representante Legal (para PJ)
        pdf.cell(0, 0, "_" * 50, 0, 1, 'C') # Linha para assinatura
        pdf.ln(3) # Reduzido de 5 para 3
        # Para PJ, o ideal seria "Assinatura do(a) Representante Legal" ou similar.
        # Mantendo "Assinatura do(a) Comprador(a)" conforme solicitado genericamente.
        pdf.cell(0, 4, sanitize_text("Assinatura do(a) Comprador(a)"), 0, 1, 'C') # Reduzido de 5 para 4
        pdf.ln(7) # Ajustado espaçamento

        # Autorizado em:__________/______/__________
        pdf.cell(0, 6, f"Autorizado em: {today.strftime('%d/%m/%Y')}", 0, 1, 'C') # Reduzido de 7 para 6
        pdf.ln(7) # Ajustado espaçamento

        # Sistema Imobiliário
        pdf.cell(0, 0, "_" * 50, 0, 1, 'C') # Linha para assinatura
        pdf.ln(3) # Reduzido de 5 para 3
        pdf.cell(0, 4, sanitize_text("Sistema Imobiliário"), 0, 1, 'C') # Reduzido de 5 para 4

        # Inserir dependentes em uma nova página, se houver
        if dependentes:
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, sanitize_text("LISTAGEM DE DEPENDENTES"), 0, 1, "C")
            pdf.ln(5)

            pdf.set_font("Helvetica", "", 10)
            for i, dep in enumerate(dependentes):
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(0, 6, f"DEPENDENTE {i+1}:", 0, 1, "L")
                pdf.set_font("Helvetica", "", 9)
                pdf.cell(0, 5, f"Nome: {sanitize_text(dep.get('nome', ''))}", 0, 1)
                pdf.cell(0, 5, f"CPF: {sanitize_text(formatar_cpf(dep.get('cpf', '')))}", 0, 1)
                pdf.cell(0, 5, f"Telefone Comercial: {sanitize_text(formatar_telefone(dep.get('telefone_comercial', '')))}", 0, 1)
                pdf.cell(0, 5, f"Celular: {sanitize_text(formatar_telefone(dep.get('celular', '')))}", 0, 1)
                pdf.cell(0, 5, f"E-mail: {sanitize_text(dep.get('email', ''))}", 0, 1)
                pdf.cell(0, 5, f"Grau de Parentesco: {sanitize_text(dep.get('grau_parentesco', ''))}", 0, 1)
                pdf.ln(3) # Espaço entre dependentes
        
        # Adicionada codificação para 'latin-1'
        pdf_output = pdf.output(dest='S').encode('latin-1')
        b64_pdf = base64.b64encode(pdf_output).decode('utf-8')
        return b64_pdf
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {str(e)}")
        return None

# Configuração da página Streamlit
st.set_page_config(layout="wide", page_title="Ficha Cadastral")

st.title("Ficha Cadastral - Sistema Imobiliário")
st.markdown("Selecione o tipo de cadastro e preencha as informações.")

# Seleção do tipo de ficha
ficha_tipo = st.radio("Selecione o tipo de ficha:", ("Pessoa Física", "Pessoa Jurídica"))

# --- Callback functions for adding dependents ---
def add_dependent_pf_callback():
    # Verifica se o nome do dependente está preenchido (CPF não é mais obrigatório)
    if st.session_state.get("dep_nome_pf"):
        st.session_state.dependentes_pf_temp.append({
            "nome": st.session_state.dep_nome_pf,
            "cpf": st.session_state.dep_cpf_pf,
            "telefone_comercial": st.session_state.dep_tel_comercial_pf,
            "celular": st.session_state.dep_celular_pf,
            "email": st.session_state.dep_email_pf,
            "grau_parentesco": st.session_state.dep_grau_parentesco_pf,
        })
        # Limpa os campos de entrada do dependente no session_state para que a UI seja atualizada
        st.session_state.dep_nome_pf = ""
        st.session_state.dep_cpf_pf = ""
        st.session_state.dep_tel_comercial_pf = ""
        st.session_state.dep_celular_pf = ""
        st.session_state.dep_email_pf = ""
        st.session_state.dep_grau_parentesco_pf = ""
        st.success("Dependente adicionado! Submeta o formulário principal para salvá-lo no PDF.")
    else:
        st.warning("O nome do dependente é obrigatório para adicionar.")

def add_dependent_pj_callback():
    # Verifica se o nome do dependente está preenchido (CPF não é mais obrigatório)
    if st.session_state.get("dep_nome_pj"):
        st.session_state.dependentes_pj_temp.append({
            "nome": st.session_state.dep_nome_pj,
            "cpf": st.session_state.dep_cpf_pj,
            "telefone_comercial": st.session_state.dep_tel_comercial_pj,
            "celular": st.session_state.dep_celular_pj,
            "email": st.session_state.dep_email_pj,
            "grau_parentesco": st.session_state.dep_grau_parentesco_pj,
        })
        # Limpa os campos de entrada do dependente no session_state para que a UI seja atualizada
        st.session_state.dep_nome_pj = ""
        st.session_state.dep_cpf_pj = ""
        st.session_state.dep_tel_comercial_pj = ""
        st.session_state.dep_celular_pj = ""
        st.session_state.dep_email_pj = ""
        st.session_state.dep_grau_parentesco_pj = ""
        st.success("Dependente adicionado para PJ! Submeta o formulário principal para salvá-lo no PDF.")
    else:
        st.warning("O nome do dependente é obrigatório para adicionar.")

# Inicializa submitted_pf e submitted_pj fora dos formulários
submitted_pf = False
submitted_pj = False


if ficha_tipo == "Pessoa Física":
    st.header("Ficha Cadastral Pessoa Física")

    # Início do formulário principal
    with st.form("form_pf"):	
        st.subheader("Dados do Empreendimento e Imobiliária")
        
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            empreendimento_pf = st.text_input("Empreendimento", key="empreendimento_pf")
        with col2:
            qd_pf = st.text_input("QD", key="qd_pf")
        with col3:
            lt_pf = st.text_input("LT", key="lt_pf")

        col_corr_imob = st.columns([1, 1])
        with col_corr_imob[0]:
            corretor_pf = st.text_input("Corretor(a)", key="corretor_pf")
        with col_corr_imob[1]:
            imobiliaria_pf = st.text_input("Imobiliária", key="imobiliaria_pf")
        
        col_ativo_quit = st.columns([1,1])
        with col_ativo_quit[0]:
            ativo_pf = st.checkbox("Ativo", key="ativo_pf")
        with col_ativo_quit[1]:
            quitado_pf = st.checkbox("Quitado", key="quitado_pf")

        st.subheader("Dados do COMPRADOR(A)") 
        
        col_nome_prof_nasc = st.columns([2,1,1])
        with col_nome_prof_nasc[0]:
            comprador_nome_pf = st.text_input("Nome Completo", key="comprador_nome_pf")
        with col_nome_prof_nasc[1]:
            comprador_profissao_pf = st.text_input("Profissão", key="comprador_profissao_pf")
        with col_nome_prof_nasc[2]:
            comprador_nacionalidade_pf = st.text_input("Nacionalidade", key="comprador_nacionalidade_pf")

        col_fones_email = st.columns([1,1,1,1])
        with col_fones_email[0]:
            comprador_fone_residencial_pf = st.text_input("Fone Residencial", key="comprador_fone_residencial_pf")
        with col_fones_email[1]:
            comprador_fone_comercial_pf = st.text_input("Fone Comercial", key="comprador_fone_comercial_pf")
        with col_fones_email[2]:
            comprador_celular_pf = st.text_input("Celular", key="comprador_celular_pf")
        with col_fones_email[3]:
            comprador_email_pf = st.text_input("E-mail", key="comprador_email_pf")

        # CEP E ENDEREÇO DO COMPRADOR - AGORA DENTRO DO FORMULÁRIO COM on_click
        col_cep_comp, col_btn_comp = st.columns([0.7, 0.3])
        with col_cep_comp:
            comprador_cep_pf = st.text_input("CEP", help="Digite o CEP e clique 'Buscar Endereço' para preencher.", key="comprador_cep_pf", value=st.session_state.comprador_cep_pf)
        with col_btn_comp:
            st.form_submit_button("Buscar Endereço Comprador", on_click=_on_cep_search_callback, args=('pf', 'comprador_cep_pf'))

        col_end_num_bairro = st.columns([2,1,1])
        with col_end_num_bairro[0]:
            comprador_end_residencial_pf = st.text_input("Endereço Residencial", value=st.session_state.comprador_end_residencial_pf, key="comprador_end_residencial_pf")
        with col_end_num_bairro[1]:
            comprador_numero_pf = st.text_input("Número", value=st.session_state.comprador_numero_pf, key="comprador_numero_pf")
        with col_end_num_bairro[2]:
            comprador_bairro_pf = st.text_input("Bairro", value=st.session_state.comprador_bairro_pf, key="comprador_bairro_pf")
        
        col_cidade_estado = st.columns([2,1])
        with col_cidade_estado[0]:
            comprador_cidade_pf = st.text_input("Cidade", value=st.session_state.comprador_cidade_pf, key="comprador_cidade_pf")
        with col_cidade_estado[1]:
            comprador_estado_pf = st.text_input("Estado", value=st.session_state.comprador_estado_pf, key="comprador_estado_pf")

        st.markdown("---") # Separador visual


        col_estado_civil_regime = st.columns([1,1])
        with col_estado_civil_regime[0]:
            comprador_estado_civil_pf = st.selectbox("Estado Civil", ["", "Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)"], key="comprador_estado_civil_pf")
        with col_estado_civil_regime[1]:
            comprador_regime_bens_pf = st.selectbox("Regime de Bens", REGIMES_DE_BENS, key="comprador_regime_bens_pf")

        st.markdown("**Condição de Convivência:**")
        comprador_uniao_estavel_pf = st.checkbox("( ) Declara conviver em união estável", key="comprador_uniao_estavel_pf")
        st.markdown("– Apresentar comprovante de estado civil de cada um e a declaração de convivência em união estável com as assinaturas reconhecidas em Cartório.")
        
        st.subheader("Dados do CÔNJUGE/SÓCIO(A)") # New subheader for fields still in form
        col_conjuge_nome_prof_nasc = st.columns([2,1,1])
        with col_conjuge_nome_prof_nasc[0]:
            conjuge_nome_pf = st.text_input("Nome Completo Cônjuge/Sócio(a)", key="conjuge_nome_pf")
        with col_conjuge_nome_prof_nasc[1]:
            conjuge_profissao_pf = st.text_input("Profissão", key="conjuge_profissao_pf")
        with col_conjuge_nome_prof_nasc[2]:
            conjuge_nacionalidade_pf = st.text_input("Nacionalidade", key="conjuge_nacionalidade_pf")

        col_conjuge_fones_email = st.columns([1,1,1,1])
        with col_conjuge_fones_email[0]:
            conjuge_fone_residencial_pf = st.text_input("Fone Residencial Cônjuge/Sócio(a)", key="conjuge_fone_residencial_pf")
        with col_conjuge_fones_email[1]:
            conjuge_fone_comercial_pf = st.text_input("Fone Comercial Cônjuge/Sócio(a)", key="conjuge_fone_comercial_pf")
        with col_conjuge_fones_email[2]:
            conjuge_celular_pf = st.text_input("Celular", key="conjuge_celular_pf")
        with col_conjuge_fones_email[3]:
            conjuge_email_pf = st.text_input("E-mail", key="conjuge_email_pf")

        # CEP E ENDEREÇO DO CÔNJUGE - AGORA DENTRO DO FORMULÁRIO COM on_click
        col_conjuge_cep, col_btn_conj = st.columns([0.7, 0.3])
        with col_conjuge_cep:
            conjuge_cep_pf = st.text_input("CEP do Cônjuge/Sócio(a)", help="Digite o CEP e clique 'Buscar Endereço' para preencher.", key="conjuge_cep_pf", value=st.session_state.conjuge_cep_pf)
        with col_btn_conj:
            st.form_submit_button("Buscar Endereço Cônjuge/Sócio(a)", on_click=_on_cep_search_callback, args=('conjuge_pf', 'conjuge_cep_pf'))

        col_conjuge_end_num_bairro = st.columns([2,1,1])
        with col_conjuge_end_num_bairro[0]:
            conjuge_end_residencial_pf = st.text_input("Endereço Residencial Cônjuge/Sócio(a)", value=st.session_state.conjuge_end_residencial_pf, key="conjuge_end_residencial_pf")
        with col_conjuge_end_num_bairro[1]:
            conjuge_numero_pf = st.text_input("Número", value=st.session_state.conjuge_numero_pf, key="conjuge_numero_pf")
        with col_conjuge_end_num_bairro[2]:
            conjuge_bairro_pf = st.text_input("Bairro", value=st.session_state.conjuge_bairro_pf, key="conjuge_bairro_pf")

        col_conjuge_cidade_estado = st.columns([2,1])
        with col_conjuge_cidade_estado[0]:
            conjuge_cidade_pf = st.text_input("Cidade", value=st.session_state.conjuge_cidade_pf, key="conjuge_cidade_pf")
        with col_conjuge_cidade_estado[1]:
            conjuge_estado_pf = st.text_input("Estado", value=st.session_state.conjuge_estado_pf, key="conjuge_estado_pf")

        st.markdown("---")
        st.markdown("**DOCUMENTOS NECESSÁRIOS:**")
        st.markdown("- CNH; RG e CPF; Comprovante do Estado Civil, Comprovante de Endereço, Comprovante de Renda, CND da Prefeitura e Nada Consta do Condomínio ou Associação.")
        st.markdown("---")

        st.write("No caso de Condomínio ou Loteamento Fechado, quando a cessão for emitida para sócio(a)(s), não casados entre si e nem conviventes é necessário indicar qual dos dois será o(a) condômino(a):")
        condomino_indicado_pf = st.text_input("Indique aqui quem será o(a) condômino(a)", key="condomino_indicado_pf")

        # Botões de ação do formulário principal (permanecem dentro do st.form)
        col1_form_pf, col2_form_pf = st.columns(2)
        with col1_form_pf:
            submitted_pf = st.form_submit_button("Gerar Ficha de Pessoa Física")
        # Removed "Imprimir Formulário" st.form_submit_button here

    # Section for Dados da Proposta (Optional, controlled by checkbox)
    st.subheader("Dados da Proposta")
    incluir_dados_proposta_pf = st.checkbox("Incluir Dados da Proposta", key="incluir_dados_proposta_pf_checkbox")

    dados_proposta_pf = None # Initialize outside the if block

    if incluir_dados_proposta_pf:
        with st.container(border=True):
            col_val_imovel_fp = st.columns(2)
            with col_val_imovel_fp[0]:
                valor_imovel_pf = st.text_input("Valor do imóvel", value=st.session_state.get("proposta_valor_imovel", ""), key="proposta_valor_imovel")
            with col_val_imovel_fp[1]:
                forma_pagamento_imovel_pf = st.text_input("Forma de pagamento (Imóvel)", value=st.session_state.get("proposta_forma_pagamento_imovel", ""), key="proposta_forma_pagamento_imovel")

            col_val_honorarios_fp = st.columns(2)
            with col_val_honorarios_fp[0]:
                valor_honorarios_pf = st.text_input("Valor dos honorários", value=st.session_state.get("proposta_valor_honorarios", ""), key="proposta_valor_honorarios")
            with col_val_honorarios_fp[1]:
                forma_pagamento_honorarios_pf = st.text_input("Forma de pagamento (Honorários)", value=st.session_state.get("proposta_forma_pagamento_honorarios", ""), key="proposta_forma_pagamento_honorarios")

            conta_bancaria_pf = st.text_input("Conta Bancária para transferência", value=st.session_state.get("proposta_conta_bancaria", ""), key="proposta_conta_bancaria")
            valor_ir_pf = st.text_input("Valor para declaração de imposto de renda", value=st.session_state.get("proposta_valor_ir", ""), key="proposta_valor_ir")
            valor_escritura_pf = st.text_input("Valor para escritura", value=st.session_state.get("proposta_valor_escritura", ""), key="proposta_valor_escritura")
            observacoes_proposta_pf = st.text_area("Observações", value=st.session_state.get("proposta_observacoes", ""), key="proposta_observacoes")

            col_corretores = st.columns(2)
            with col_corretores[0]:
                corretor_angariador_pf = st.text_input("Corretor(a) angariador", value=st.session_state.get("proposta_corretor_angariador", ""), key="proposta_corretor_angariador")
            with col_corretores[1]:
                corretor_vendedor_pf = st.text_input("Corretor(a) vendedor(a)", value=st.session_state.get("proposta_corretor_vendedor", ""), key="proposta_corretor_vendedor")
            
            data_negociacao_pf = st.date_input("Data da negociação", value=st.session_state.get("proposta_data_negociacao", datetime.date.today()), key="proposta_data_negociacao")
            
            dados_proposta_pf = {
                "valor_imovel": valor_imovel_pf.strip(),
                "forma_pagamento_imovel": forma_pagamento_imovel_pf.strip(),
                "valor_honorarios": valor_honorarios_pf.strip(),
                "forma_pagamento_honorarios": forma_pagamento_honorarios_pf.strip(),
                "conta_bancaria": conta_bancaria_pf.strip(),
                "valor_ir": valor_ir_pf.strip(),
                "valor_escritura": valor_escritura_pf.strip(),
                "observacoes": observacoes_proposta_pf.strip(),
                "corretor_angariador": corretor_angariador_pf.strip(),
                "corretor_vendedor": corretor_vendedor_pf.strip(),
                "data_negociacao": data_negociacao_pf,
            }


    # Seção para Dependentes (FORA DO st.form para Pessoa Física)
    st.subheader("Dependentes")
    incluir_dependentes_pf = st.checkbox("Incluir Dependentes", key="incluir_dependentes_pf_checkbox")

    if incluir_dependentes_pf:
        with st.container(border=True):
            st.markdown("**Adicionar Novo Dependente:**")
            dep_nome_pf = st.text_input("Nome Completo do Dependente", value=st.session_state.get("dep_nome_pf", ""), key="dep_nome_pf")
            dep_cpf_pf = st.text_input("CPF do Dependente", value=st.session_state.get("dep_cpf_pf", ""), key="dep_cpf_pf")
            dep_tel_comercial_pf = st.text_input("Telefone Comercial do Dependente", value=st.session_state.get("dep_tel_comercial_pf", ""), key="dep_tel_comercial_pf")
            dep_celular_pf = st.text_input("Celular do Dependente", value=st.session_state.get("dep_celular_pf", ""), key="dep_celular_pf")
            dep_email_pf = st.text_input("E-mail do Dependente", value=st.session_state.get("dep_email_pf", ""), key="dep_email_pf")
            dep_grau_parentesco_pf = st.text_input("Grau de Parentesco", value=st.session_state.get("dep_grau_parentesco_pf", ""), key="dep_grau_parentesco_pf")

            st.button("Adicionar Dependente", key="add_dep_pf_button_out_form", on_click=add_dependent_pf_callback)
        
        if st.session_state.dependentes_pf_temp:
            st.markdown("---")
            st.markdown("**Dependentes Adicionados:**")
            df_dependentes_pf = pd.DataFrame(st.session_state.dependentes_pf_temp)
            st.dataframe(df_dependentes_pf)

            clear_dep_pf_button = st.button("Limpar Dependentes", key="clear_dep_pf_button_out_form")
            if clear_dep_pf_button:
                st.session_state.dependentes_pf_temp = []
                st.success("Dependentes limpos.")
                st.rerun()

    # Lógica de processamento após a submissão do formulário PF
    if submitted_pf:
        # Data dictionary should now pull updated fields directly from session_state
        dados_pf = {
            "empreendimento_pf": empreendimento_pf.strip(),
            "corretor_pf": corretor_pf.strip(),
            "imobiliaria_pf": imobiliaria_pf.strip(),
            "qd_pf": qd_pf.strip(),
            "lt_pf": lt_pf.strip(),
            "ativo_pf": "Sim" if ativo_pf else "Não",
            "quitado_pf": "Sim" if quitado_pf else "Não",
            "comprador_nome_pf": comprador_nome_pf.strip(),
            "comprador_profissao_pf": comprador_profissao_pf.strip(),
            "comprador_nacionalidade_pf": comprador_nacionalidade_pf.strip(),
            "comprador_fone_residencial_pf": comprador_fone_residencial_pf.strip(),
            "comprador_fone_comercial_pf": comprador_fone_comercial_pf.strip(),
            "comprador_celular_pf": comprador_celular_pf.strip(),
            "comprador_email_pf": comprador_email_pf.strip(),
            "comprador_end_residencial_pf": st.session_state.comprador_end_residencial_pf.strip(), 
            "comprador_numero_pf": st.session_state.comprador_numero_pf.strip(), 
            "comprador_bairro_pf": st.session_state.comprador_bairro_pf.strip(), 
            "comprador_cidade_pf": st.session_state.comprador_cidade_pf.strip(), 
            "comprador_estado_pf": st.session_state.comprador_estado_pf.strip(), 
            "comprador_cep_pf": st.session_state.comprador_cep_pf.strip(), 
            "comprador_estado_civil_pf": comprador_estado_civil_pf.strip(),
            "comprador_regime_bens_pf": comprador_regime_bens_pf.strip(),
            "comprador_uniao_estavel_pf": "Sim" if comprador_uniao_estavel_pf else "Não",
            "conjuge_nome_pf": conjuge_nome_pf.strip(),
            "conjuge_profissao_pf": conjuge_profissao_pf.strip(),
            "conjuge_nacionalidade_pf": conjuge_nacionalidade_pf.strip(),
            "conjuge_fone_residencial_pf": conjuge_fone_residencial_pf.strip(),
            "conjuge_fone_comercial_pf": conjuge_fone_comercial_pf.strip(),
            "conjuge_celular_pf": conjuge_celular_pf.strip(),
            "conjuge_email_pf": conjuge_email_pf.strip(),
            "conjuge_end_residencial_pf": st.session_state.conjuge_end_residencial_pf.strip(), 
            "conjuge_numero_pf": st.session_state.conjuge_numero_pf.strip(), 
            "conjuge_bairro_pf": st.session_state.conjuge_bairro_pf.strip(), 
            "conjuge_cidade_pf": st.session_state.conjuge_cidade_pf.strip(), 
            "conjuge_estado_pf": st.session_state.conjuge_estado_pf.strip(), 
            "conjuge_cep_pf": st.session_state.conjuge_cep_pf.strip(), 
            "condomino_indicado_pf": condomino_indicado_pf.strip(),
        }
        
        pdf_b64_pf = gerar_pdf_pf(dados_pf, 
                                st.session_state.dependentes_pf_temp if incluir_dependentes_pf else None,
                                dados_proposta_pf if incluir_dados_proposta_pf else None)


        if pdf_b64_pf:
            # O link de download original pode ser mantido se preferir uma opção de texto
            # href = f'<a href="data:application/pdf;base64,{pdf_b64_pf}" download="Ficha_Cadastral_Pessoa_Fisica.pdf">Clique aqui para baixar a Ficha Cadastral de Pessoa Física</a>'
            # st.markdown(href, unsafe_allow_html=True)
            
            # Botão de download explícito (novo)
            st.download_button(
                label="Imprimir Formulário (PDF)", # Texto do botão
                data=base64.b64decode(pdf_b64_pf), # Dados do PDF decodificados
                file_name="Ficha_Cadastral_Pessoa_Fisica.pdf", # Nome do arquivo ao baixar
                mime="application/pdf", # Tipo MIME do arquivo
                key="download_pf_form" # Chave única para o botão
            )


elif ficha_tipo == "Pessoa Jurídica":
    st.header("Ficha Cadastral Pessoa Jurídica")

    with st.form("form_pj"):
        st.subheader("Dados do Empreendimento e Imobiliária")
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            empreendimento_pj = st.text_input("Empreendimento", key="empreendimento_pj")
        with col2:
            qd_pj = st.text_input("QD", key="qd_pj")
        with col3:
            lt_pj = st.text_input("LT", key="lt_pj")

        col_corr_imob_pj = st.columns([1, 1])
        with col_corr_imob_pj[0]:
            corretor_pj = st.text_input("Corretor(a)", key="corretor_pj")
        with col_corr_imob_pj[1]:
            imobiliaria_pj = st.text_input("Imobiliária", key="imobiliaria_pj")
        
        col_ativo_quit_pj = st.columns([1,1])
        with col_ativo_quit_pj[0]:
            ativo_pj = st.checkbox("Ativo", key="ativo_pj")
        with col_ativo_quit_pj[1]:
            quitado_pj = st.checkbox("Quitado", key="quitado_pj")

        st.subheader("Dados do COMPRADOR(A)") 
        col_razao_cnpj_email_pj = st.columns([2,1,1])
        with col_razao_cnpj_email_pj[0]:
            comprador_razao_social_pj = st.text_input("Razão Social", key="comprador_razao_social_pj")
        with col_razao_cnpj_email_pj[1]:
            comprador_nome_fantasia_pj = st.text_input("Nome Fantasia", key="comprador_nome_fantasia_pj")
        with col_razao_cnpj_email_pj[2]:
            comprador_inscricao_estadual_pj = st.text_input("Inscrição Estadual", key="comprador_inscricao_estadual_pj")

        col_fones_empresa_pj = st.columns([1,1,1,1])
        with col_fones_empresa_pj[0]:
            comprador_fone_residencial_pj = st.text_input("Fone Residencial", key="comprador_fone_residencial_pj")
        with col_fones_empresa_pj[1]:
            comprador_fone_comercial_pj = st.text_input("Fone Comercial", key="comprador_fone_comercial_pj")
        with col_fones_empresa_pj[2]:
            comprador_celular_pj = st.text_input("Celular", key="comprador_celular_pj")
        with col_fones_empresa_pj[3]:
            comprador_email_pj = st.text_input("E-mail", key="comprador_email_pj")

        # CEP E ENDEREÇO DA EMPRESA - AGORA DENTRO DO FORMULÁRIO COM on_click
        col_cep_comp_pj, col_btn_comp_pj = st.columns([0.7, 0.3])
        with col_cep_comp_pj:
            comprador_cep_pj = st.text_input("CEP da Empresa", help="Digite o CEP e clique 'Buscar Endereço' para preencher.", key="comprador_cep_pj", value=st.session_state.comprador_cep_pj)
        with col_btn_comp_pj:
            st.form_submit_button("Buscar Endereço Empresa", on_click=_on_cep_search_callback, args=('empresa_pj', 'comprador_cep_pj'))

        col_end_num_bairro_empresa_pj = st.columns([2,1,1])
        with col_end_num_bairro_empresa_pj[0]:
            comprador_end_residencial_comercial_pj = st.text_input("Endereço Residencial/Comercial", value=st.session_state.comprador_end_residencial_comercial_pj, key="comprador_end_residencial_comercial_pj")
        with col_end_num_bairro_empresa_pj[1]:
            comprador_numero_pj = st.text_input("Número", value=st.session_state.comprador_numero_pj, key="comprador_numero_pj")
        with col_end_num_bairro_empresa_pj[2]:
            comprador_bairro_pj = st.text_input("Bairro", value=st.session_state.comprador_bairro_pj, key="comprador_bairro_pj")
        
        col_cidade_estado_empresa_pj = st.columns([2,1])
        with col_cidade_estado_empresa_pj[0]:
            comprador_cidade_pj = st.text_input("Cidade", value=st.session_state.comprador_cidade_pj, key="comprador_cidade_pj")
        with col_cidade_estado_empresa_pj[1]:
            comprador_estado_pj = st.text_input("Estado", value=st.session_state.comprador_estado_pj, key="comprador_estado_pj")

        st.markdown("---") # Separador visual

        st.subheader("Dados do REPRESENTANTE") 
        col_rep_nome_prof_nasc = st.columns([2,1,1])
        with col_rep_nome_prof_nasc[0]:
            representante_nome_pj = st.text_input("Nome Completo Representante", key="representante_nome_pj")
        with col_rep_nome_prof_nasc[1]:
            representante_profissao_pj = st.text_input("Profissão", key="representante_profissao_pj")
        with col_rep_nome_prof_nasc[2]:
            representante_nacionalidade_pj = st.text_input("Nacionalidade", key="representante_nacionalidade_pj")
        
        col_rep_fones_email = st.columns([1,1,1,1])
        with col_rep_fones_email[0]:
            representante_fone_residencial_pj = st.text_input("Fone Residencial Representante", key="representante_fone_residencial_pj")
        with col_rep_fones_email[1]:
            representante_fone_comercial_pj = st.text_input("Fone Comercial Representante", key="representante_fone_comercial_pj")
        with col_rep_fones_email[2]:
            representante_celular_pj = st.text_input("Celular", key="representante_celular_pj")
        with col_rep_fones_email[3]:
            representante_email_pj = st.text_input("E-mail", key="representante_email_pj")

        # CEP E ENDEREÇO DO REPRESENTANTE - AGORA DENTRO DO FORMULÁRIO COM on_click
        col_cep_rep_pj, col_btn_rep_pj = st.columns([0.7, 0.3])
        with col_cep_rep_pj:
            representante_cep_pj = st.text_input("CEP do Representante", help="Digite o CEP e clique 'Buscar Endereço' para preencher.", key="representante_cep_pj", value=st.session_state.representante_cep_pj)
        with col_btn_rep_pj:
            st.form_submit_button("Buscar Endereço Representante", on_click=_on_cep_search_callback, args=('administrador_pj', 'representante_cep_pj'))

        col_rep_end_num_bairro = st.columns([2,1,1])
        with col_rep_end_num_bairro[0]:
            representante_end_residencial_pj = st.text_input("Endereço Residencial Representante", value=st.session_state.representante_end_residencial_pj, key="representante_end_residencial_pj")
        with col_rep_end_num_bairro[1]:
            representante_numero_pj = st.text_input("Número", value=st.session_state.representante_numero_pj, key="representante_numero_pj")
        with col_rep_end_num_bairro[2]:
            representante_bairro_pj = st.text_input("Bairro", value=st.session_state.representante_bairro_pj, key="representante_bairro_pj")

        col_rep_cidade_estado = st.columns([2,1])
        with col_rep_cidade_estado[0]:
            representante_cidade_pj = st.text_input("Cidade Representante", value=st.session_state.representante_cidade_pj, key="representante_cidade_pj")
        with col_rep_cidade_estado[1]:
            representante_estado_pj = st.text_input("Estado", value=st.session_state.representante_estado_pj, key="representante_estado_pj")

        st.markdown("---") # Separador visual
        
        st.subheader("Dados do CÔNJUGE/SÓCIO(A)") 
        col_conjuge_pj_nome_prof_nasc = st.columns([2,1,1])
        with col_conjuge_pj_nome_prof_nasc[0]:
            conjuge_nome_pj = st.text_input("Nome Completo Cônjuge/Sócio(a) PJ", key="conjuge_nome_pj")
        with col_conjuge_pj_nome_prof_nasc[1]:
            conjuge_profissao_pj = st.text_input("Profissão", key="conjuge_profissao_pj")
        with col_conjuge_pj_nome_prof_nasc[2]:
            conjuge_nacionalidade_pj = st.text_input("Nacionalidade", key="conjuge_nacionalidade_pj")

        col_conjuge_pj_fones_email = st.columns([1,1,1,1])
        with col_conjuge_pj_fones_email[0]:
            conjuge_fone_residencial_pj = st.text_input("Fone Residencial Cônjuge/Sócio(a) PJ", key="conjuge_fone_residencial_pj")
        with col_conjuge_pj_fones_email[1]:
            conjuge_fone_comercial_pj = st.text_input("Fone Comercial Cônjuge/Sócio(a) PJ", key="conjuge_fone_comercial_pj")
        with col_conjuge_pj_fones_email[2]:
            conjuge_celular_pj = st.text_input("Celular", key="conjuge_celular_pj")
        with col_conjuge_pj_fones_email[3]:
            conjuge_email_pj = st.text_input("E-mail", key="conjuge_email_pj")

        # CEP E ENDEREÇO DO CÔNJUGE PJ - AGORA DENTRO DO FORMULÁRIO COM on_click
        col_conjuge_cep_pj, col_btn_conj_pj = st.columns([0.7, 0.3])
        with col_conjuge_cep_pj:
            conjuge_cep_pj = st.text_input("CEP Cônjuge/Sócio(a) PJ", help="Digite o CEP e clique 'Buscar Endereço' para preencher.", key="conjuge_cep_pj", value=st.session_state.conjuge_cep_pj)
        with col_btn_conj_pj:
            st.form_submit_button("Buscar Endereço Cônjuge/Sócio(a) PJ", on_click=_on_cep_search_callback, args=('conjuge_pj', 'conjuge_cep_pj'))

        col_conjuge_pj_end_num_bairro = st.columns([2,1,1])
        with col_conjuge_pj_end_num_bairro[0]:
            conjuge_end_residencial_pj = st.text_input("Endereço Residencial Cônjuge/Sócio(a) PJ", value=st.session_state.conjuge_end_residencial_pj, key="conjuge_end_residencial_pj")
        with col_conjuge_pj_end_num_bairro[1]:
            conjuge_numero_pj = st.text_input("Número", value=st.session_state.conjuge_numero_pj, key="conjuge_numero_pj")
        with col_conjuge_pj_end_num_bairro[2]:
            conjuge_bairro_pj = st.text_input("Bairro", value=st.session_state.conjuge_bairro_pj, key="conjuge_bairro_pj")

        col_conjuge_pj_cidade_estado = st.columns([2,1])
        with col_conjuge_pj_cidade_estado[0]:
            conjuge_cidade_pj = st.text_input("Cidade", value=st.session_state.conjuge_cidade_pj, key="conjuge_cidade_pj")
        with col_conjuge_pj_cidade_estado[1]:
            conjuge_estado_pj = st.text_input("Estado", value=st.session_state.conjuge_estado_pj, key="conjuge_estado_pj")

        st.markdown("---")
        st.markdown("**DOCUMENTOS NECESSÁRIAS:**")
        st.markdown("- **DA EMPRESA:** CONTRATO SOCIAL E ALTERAÇÕES, COMPROVANTE DE ENDEREÇO, DECLARAÇÃO DE FATURAMENTO;")
        st.markdown("- **DOS SÓCIOS E SEUS CÔNJUGES:** CNH; RG e CPF, Comprovante do Estado Civil, Comprovante de Endereço, Comprovante de Renda, CND da Prefeitura e Nada Consta do Condomínio ou Associação.")
        st.markdown("---")

        st.write("No caso de Condomínio ou Loteamento Fechado, quando a empresa possuir mais de um(a) sócio(a) não casados entre si e nem conviventes, é necessário indicar qual do(a)(s) sócio(a)(s) será o(a) condômino(a):")
        condomino_indicado_pj = st.text_input("Indique aqui quem será o(a) condômino(a)", key="condomino_indicado_pj")

        # Botões de ação do formulário principal
        col1_form_pj, col2_form_pj = st.columns(2)
        with col1_form_pj:
            submitted_pj = st.form_submit_button("Gerar Ficha de Pessoa Jurídica")
        # Removed "Imprimir Formulário PJ" st.form_submit_button here

    # Section for Dados da Proposta (Optional, controlled by checkbox)
    st.subheader("Dados da Proposta")
    incluir_dados_proposta_pj = st.checkbox("Incluir Dados da Proposta para PJ", key="incluir_dados_proposta_pj_checkbox")

    dados_proposta_pj = None # Initialize outside the if block

    if incluir_dados_proposta_pj:
        with st.container(border=True):
            col_val_imovel_fp_pj = st.columns(2)
            with col_val_imovel_fp_pj[0]:
                valor_imovel_pj = st.text_input("Valor do imóvel (PJ)", value=st.session_state.get("proposta_valor_imovel", ""), key="proposta_valor_imovel_pj")
            with col_val_imovel_fp_pj[1]:
                forma_pagamento_imovel_pj = st.text_input("Forma de pagamento (Imóvel - PJ)", value=st.session_state.get("proposta_forma_pagamento_imovel", ""), key="proposta_forma_pagamento_imovel_pj")

            col_val_honorarios_fp_pj = st.columns(2)
            with col_val_honorarios_fp_pj[0]:
                valor_honorarios_pj = st.text_input("Valor dos honorários (PJ)", value=st.session_state.get("proposta_valor_honorarios", ""), key="proposta_valor_honorarios_pj")
            with col_val_honorarios_fp_pj[1]:
                forma_pagamento_honorarios_pj = st.text_input("Forma de pagamento (Honorários - PJ)", value=st.session_state.get("proposta_forma_pagamento_honorarios", ""), key="proposta_forma_pagamento_honorarios_pj")

            conta_bancaria_pj = st.text_input("Conta Bancária para transferência (PJ)", value=st.session_state.get("proposta_conta_bancaria", ""), key="proposta_conta_bancaria_pj")
            valor_ir_pj = st.text_input("Valor para declaração de imposto de renda (PJ)", value=st.session_state.get("proposta_valor_ir", ""), key="proposta_valor_ir_pj")
            valor_escritura_pj = st.text_input("Valor para escritura (PJ)", value=st.session_state.get("proposta_valor_escritura", ""), key="proposta_valor_escritura_pj")
            observacoes_proposta_pj = st.text_area("Observações (PJ)", value=st.session_state.get("proposta_observacoes", ""), key="proposta_observacoes_pj")

            col_corretores_pj = st.columns(2)
            with col_corretores_pj[0]:
                corretor_angariador_pj = st.text_input("Corretor(a) angariador (PJ)", value=st.session_state.get("proposta_corretor_angariador", ""), key="proposta_corretor_angariador_pj")
            with col_corretores_pj[1]:
                corretor_vendedor_pj = st.text_input("Corretor(a) vendedor(a) (PJ)", value=st.session_state.get("proposta_corretor_vendedor", ""), key="proposta_corretor_vendedor_pj")
            
            data_negociacao_pj = st.date_input("Data da negociação (PJ)", value=st.session_state.get("proposta_data_negociacao", datetime.date.today()), key="proposta_data_negociacao_pj")
            
            dados_proposta_pj = {
                "valor_imovel": valor_imovel_pj.strip(),
                "forma_pagamento_imovel": forma_pagamento_imovel_pj.strip(),
                "valor_honorarios": valor_honorarios_pj.strip(),
                "forma_pagamento_honorarios": forma_pagamento_honorarios_pj.strip(),
                "conta_bancaria": conta_bancaria_pj.strip(),
                "valor_ir": valor_ir_pj.strip(),
                "valor_escritura": valor_escritura_pj.strip(),
                "observacoes": observacoes_proposta_pj.strip(),
                "corretor_angariador": corretor_angariador_pj.strip(),
                "corretor_vendedor": corretor_vendedor_pj.strip(),
                "data_negociacao": data_negociacao_pj,
            }

    # Remaining sections remain outside the form
    st.subheader("Dependentes (Pessoa Jurídica)")
    incluir_dependentes_pj = st.checkbox("Incluir Dependentes para PJ", key="incluir_dependentes_pj_checkbox")

    if incluir_dependentes_pj:
        with st.container(border=True):
            st.markdown("**Adicionar Novo Dependente para PJ:**")
            dep_nome_pj = st.text_input("Nome Completo do Dependente (PJ)", value=st.session_state.get("dep_nome_pj", ""), key="dep_nome_pj")
            dep_cpf_pj = st.text_input("CPF do Dependente (PJ)", value=st.session_state.get("dep_cpf_pj", ""), key="dep_cpf_pj")
            dep_tel_comercial_pj = st.text_input("Telefone Comercial do Dependente (PJ)", value=st.session_state.get("dep_tel_comercial_pj", ""), key="dep_tel_comercial_pj")
            dep_celular_pj = st.text_input("Celular do Dependente (PJ)", value=st.session_state.get("dep_celular_pj", ""), key="dep_celular_pj")
            dep_email_pj = st.text_input("E-mail do Dependente (PJ)", value=st.session_state.get("dep_email_pj", ""), key="dep_email_pj")
            dep_grau_parentesco_pj = st.text_input("Grau de Parentesco (PJ)", value=st.session_state.get("dep_grau_parentesco_pj", ""), key="dep_grau_parentesco_pj")

            st.button("Adicionar Dependente (PJ)", key="add_dep_pj_button_out_form", on_click=add_dependent_pj_callback)
            
            if st.session_state.dependentes_pj_temp:
                st.markdown("---")
                st.markdown("**Dependentes Adicionados (PJ):**")
                df_dependentes_pj = pd.DataFrame(st.session_state.dependentes_pj_temp)
                st.dataframe(df_dependentes_pj)

                clear_dep_pj_button = st.button("Limpar Dependentes (PJ)", key="clear_dep_pj_button_out_form")
                if clear_dep_pj_button:
                    st.session_state.dependentes_pj_temp = []
                    st.success("Dependentes limpos para PJ.")
                    st.rerun()

    # Lógica de processamento após a submissão do formulário
    if submitted_pf:
        # Data dictionary should now pull updated fields directly from session_state
        dados_pf = {
            "empreendimento_pf": empreendimento_pf.strip(),
            "corretor_pf": corretor_pf.strip(),
            "imobiliaria_pf": imobiliaria_pf.strip(),
            "qd_pf": qd_pf.strip(),
            "lt_pf": lt_pf.strip(),
            "ativo_pf": "Sim" if ativo_pf else "Não",
            "quitado_pf": "Sim" if quitado_pf else "Não",
            "comprador_nome_pf": comprador_nome_pf.strip(),
            "comprador_profissao_pf": comprador_profissao_pf.strip(),
            "comprador_nacionalidade_pf": comprador_nacionalidade_pf.strip(),
            "comprador_fone_residencial_pf": comprador_fone_residencial_pf.strip(),
            "comprador_fone_comercial_pf": comprador_fone_comercial_pf.strip(),
            "comprador_celular_pf": comprador_celular_pf.strip(),
            "comprador_email_pf": comprador_email_pf.strip(),
            "comprador_end_residencial_pf": st.session_state.comprador_end_residencial_pf.strip(), 
            "comprador_numero_pf": st.session_state.comprador_numero_pf.strip(), 
            "comprador_bairro_pf": st.session_state.comprador_bairro_pf.strip(), 
            "comprador_cidade_pf": st.session_state.comprador_cidade_pf.strip(), 
            "comprador_estado_pf": st.session_state.comprador_estado_pf.strip(), 
            "comprador_cep_pf": st.session_state.comprador_cep_pf.strip(), 
            "comprador_estado_civil_pf": comprador_estado_civil_pf.strip(),
            "comprador_regime_bens_pf": comprador_regime_bens_pf.strip(),
            "comprador_uniao_estavel_pf": "Sim" if comprador_uniao_estavel_pf else "Não",
            "conjuge_nome_pf": conjuge_nome_pf.strip(),
            "conjuge_profissao_pf": conjuge_profissao_pf.strip(),
            "conjuge_nacionalidade_pf": conjuge_nacionalidade_pf.strip(),
            "conjuge_fone_residencial_pf": conjuge_fone_residencial_pf.strip(),
            "conjuge_fone_comercial_pf": conjuge_fone_comercial_pf.strip(),
            "conjuge_celular_pf": conjuge_celular_pf.strip(),
            "conjuge_email_pf": conjuge_email_pf.strip(),
            "conjuge_end_residencial_pf": st.session_state.conjuge_end_residencial_pf.strip(), 
            "conjuge_numero_pf": st.session_state.conjuge_numero_pf.strip(), 
            "conjuge_bairro_pf": st.session_state.conjuge_bairro_pf.strip(), 
            "conjuge_cidade_pf": st.session_state.conjuge_cidade_pf.strip(), 
            "conjuge_estado_pf": st.session_state.conjuge_estado_pf.strip(), 
            "conjuge_cep_pf": st.session_state.conjuge_cep_pf.strip(), 
            "condomino_indicado_pf": condomino_indicado_pf.strip(),
        }
        
        pdf_b64_pf = gerar_pdf_pf(dados_pf, 
                                st.session_state.dependentes_pf_temp if incluir_dependentes_pf else None,
                                dados_proposta_pf if incluir_dados_proposta_pf else None)


        if pdf_b64_pf:
            # O link de download original pode ser mantido se preferir uma opção de texto
            # href = f'<a href="data:application/pdf;base64,{pdf_b64_pf}" download="Ficha_Cadastral_Pessoa_Fisica.pdf">Clique aqui para baixar a Ficha Cadastral de Pessoa Física</a>'
            # st.markdown(href, unsafe_allow_html=True)
            
            # Botão de download explícito (novo)
            st.download_button(
                label="Imprimir Formulário (PDF)", # Texto do botão
                data=base64.b64decode(pdf_b64_pf), # Dados do PDF decodificados
                file_name="Ficha_Cadastral_Pessoa_Fisica.pdf", # Nome do arquivo ao baixar
                mime="application/pdf", # Tipo MIME do arquivo
                key="download_pf_form" # Chave única para o botão
            )


    if submitted_pj: # submitted_pj é a variável do st.form_submit_button do form principal
        dados_pj = {
            "empreendimento_pj": empreendimento_pj.strip(),
            "corretor_pj": corretor_pj.strip(),
            "imobiliaria_pj": imobiliaria_pj.strip(),
            "qd_pj": qd_pj.strip(),
            "lt_pj": lt_pj.strip(),
            "ativo_pj": "Sim" if ativo_pj else "Não",
            "quitado_pj": "Sim" if quitado_pj else "Não",
            "comprador_razao_social_pj": comprador_razao_social_pj.strip(),
            "comprador_nome_fantasia_pj": comprador_nome_fantasia_pj.strip(),
            "comprador_inscricao_estadual_pj": comprador_inscricao_estadual_pj.strip(),
            "comprador_fone_residencial_pj": comprador_fone_residencial_pj.strip(),
            "comprador_fone_comercial_pj": comprador_fone_comercial_pj.strip(),
            "comprador_celular_pj": comprador_celular_pj.strip(),
            "comprador_email_pj": comprador_email_pj.strip(),
            "comprador_end_residencial_comercial_pj": st.session_state.comprador_end_residencial_comercial_pj.strip(),
            "comprador_numero_pj": st.session_state.comprador_numero_pj.strip(),
            "comprador_bairro_pj": st.session_state.comprador_bairro_pj.strip(),
            "comprador_cidade_pj": st.session_state.comprador_cidade_pj.strip(),
            "comprador_estado_pj": st.session_state.comprador_estado_pj.strip(),
            "comprador_cep_pj": st.session_state.comprador_cep_pj.strip(),
            "representante_nome_pj": representante_nome_pj.strip(),
            "representante_profissao_pj": representante_profissao_pj.strip(),
            "representante_nacionalidade_pj": representante_nacionalidade_pj.strip(),
            "representante_fone_residencial_pj": representante_fone_residencial_pj.strip(),
            "representante_fone_comercial_pj": representante_fone_comercial_pj.strip(),
            "representante_celular_pj": representante_celular_pj.strip(),
            "representante_email_pj": representante_email_pj.strip(),
            "representante_end_residencial_pj": st.session_state.representante_end_residencial_pj.strip(),
            "representante_numero_pj": st.session_state.representante_numero_pj.strip(),
            "representante_bairro_pj": st.session_state.representante_bairro_pj.strip(),
            "representante_cidade_pj": st.session_state.representante_cidade_pj.strip(),
            "representante_estado_pj": st.session_state.representante_estado_pj.strip(),
            "representante_cep_pj": st.session_state.representante_cep_pj.strip(),
            "conjuge_nome_pj": conjuge_nome_pj.strip(),
            "conjuge_profissao_pj": conjuge_profissao_pj.strip(),
            "conjuge_nacionalidade_pj": conjuge_nacionalidade_pj.strip(),
            "conjuge_fone_residencial_pj": conjuge_fone_residencial_pj.strip(),
            "conjuge_fone_comercial_pj": conjuge_fone_comercial_pj.strip(),
            "conjuge_celular_pj": conjuge_celular_pj.strip(),
            "conjuge_email_pj": conjuge_email_pj.strip(),
            "conjuge_end_residencial_pj": st.session_state.conjuge_end_residencial_pj.strip(),
            "conjuge_numero_pj": st.session_state.conjuge_numero_pj.strip(),
            "conjuge_bairro_pj": st.session_state.conjuge_bairro_pj.strip(),
            "conjuge_cidade_pj": st.session_state.conjuge_cidade_pj.strip(),
            "conjuge_estado_pj": st.session_state.conjuge_estado_pj.strip(),
            "conjuge_cep_pj": st.session_state.conjuge_cep_pj.strip(),
            "condomino_indicado_pj": condomino_indicado_pj.strip(),
        }
        
        pdf_b64_pj = gerar_pdf_pj(dados_pj, 
                                st.session_state.dependentes_pj_temp if incluir_dependentes_pj else None,
                                dados_proposta_pj if incluir_dados_proposta_pj else None)

        if pdf_b64_pj:
            href = f'<a href="data:application/pdf;base64,{pdf_b64_pj}" download="Ficha_Cadastral_Pessoa_Juridica.pdf">Clique aqui para baixar a Ficha Cadastral de Pessoa Jurídica</a>'
            st.markdown(href, unsafe_allow_html=True)
            # Adicionado o botão de download explícito após a geração do PDF
            st.download_button(
                label="Imprimir Formulário PJ (PDF)", # Texto do botão
                data=base64.b64decode(pdf_b64_pj), # Dados do PDF decodificados
                file_name="Ficha_Cadastral_Pessoa_Juridica.pdf", # Nome do arquivo ao baixar
                mime="application/pdf", # Tipo MIME do arquivo
                key="download_pj_form" # Chave única para o botão
            )
