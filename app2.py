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
if "comprador_end_residencial_pf" not in st.session_state:
    st.session_state.comprador_end_residencial_pf = ""
if "comprador_bairro_pf" not in st.session_state:
    st.session_state.comprador_bairro_pf = ""
if "comprador_cidade_pf" not in st.session_state:
    st.session_state.comprador_cidade_pf = ""
if "comprador_estado_pf" not in st.session_state:
    st.session_state.comprador_estado_pf = ""

if "conjuge_end_residencial_pf" not in st.session_state:
    st.session_state.conjuge_end_residencial_pf = ""
if "conjuge_bairro_pf" not in st.session_state:
    st.session_state.conjuge_bairro_pf = ""
if "conjuge_cidade_pf" not in st.session_state:
    st.session_state.conjuge_cidade_pf = ""
if "conjuge_estado_pf" not in st.session_state:
    st.session_state.conjuge_estado_pf = ""

if "comprador_end_residencial_comercial_pj" not in st.session_state:
    st.session_state.comprador_end_residencial_comercial_pj = ""
if "comprador_bairro_pj" not in st.session_state:
    st.session_state.comprador_bairro_pj = ""
if "comprador_cidade_pj" not in st.session_state:
    st.session_state.comprador_cidade_pj = ""
if "comprador_estado_pj" not in st.session_state:
    st.session_state.comprador_estado_pj = ""

if "representante_end_residencial_pj" not in st.session_state:
    st.session_state.representante_end_residencial_pj = ""
if "representante_bairro_pj" not in st.session_state:
    st.session_state.representante_bairro_pj = ""
if "representante_cidade_pj" not in st.session_state:
    st.session_state.representante_cidade_pj = ""
if "representante_estado_pj" not in st.session_state:
    st.session_state.representante_estado_pj = ""

if "conjuge_end_residencial_pj" not in st.session_state:
    st.session_state.conjuge_end_residencial_pj = ""
if "conjuge_bairro_pj" not in st.session_state:
    st.session_state.conjuge_bairro_pj = ""
if "conjuge_cidade_pj" not in st.session_state:
    st.session_state.conjuge_cidade_pj = ""
if "conjuge_estado_pj" not in st.session_state:
    st.session_state.conjuge_estado_pj = ""

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

def preencher_endereco(tipo_campo: str, cep_value: str) -> str:
    """
    Busca informações de endereço a partir de um CEP e preenche o st.session_state.
    Retorna uma mensagem de erro se houver, ou None se bem-sucedido.
    """
    endereco_info, error_msg = buscar_cep(cep_value)

    if endereco_info:
        # Mapeamento de 'tipo_campo' para as chaves corretas no session_state
        mapping = {
            'pf': {
                'logradouro': 'comprador_end_residencial_pf',
                'bairro': 'comprador_bairro_pf',
                'localidade': 'comprador_cidade_pf', # Usar 'localidade' ou 'city' dependendo da API
                'uf': 'comprador_estado_pf' # Usar 'uf' ou 'state' dependendo da API
            },
            'conjuge_pf': {
                'logradouro': 'conjuge_end_residencial_pf',
                'bairro': 'conjuge_bairro_pf',
                'localidade': 'conjuge_cidade_pf',
                'uf': 'conjuge_estado_pf'
            },
            'empresa_pj': {
                'logradouro': 'comprador_end_residencial_comercial_pj',
                'bairro': 'comprador_bairro_pj',
                'localidade': 'comprador_cidade_pj',
                'uf': 'comprador_estado_pj'
            },
            'administrador_pj': {
                'logradouro': 'representante_end_residencial_pj',
                'bairro': 'representante_bairro_pj',
                'localidade': 'representante_cidade_pj',
                'uf': 'representante_estado_pj'
            },
            'conjuge_pj': {
                'logradouro': 'conjuge_end_residencial_pj',
                'bairro': 'conjuge_bairro_pj',
                'localidade': 'conjuge_cidade_pj',
                'uf': 'conjuge_estado_pj'
            },
            'pessoa_pj': { # Para pessoas vinculadas
                'logradouro': 'endereco_pessoa_pj',
                'bairro': 'bairro_pessoa_pj',
                'localidade': 'cidade_pessoa_pj',
                'uf': 'estado_pessoa_pj'
            }
        }

        target_keys = mapping.get(tipo_campo)
        if target_keys:
            for campo_origem, session_key in target_keys.items():
                st.session_state[session_key] = endereco_info.get(campo_origem, '')
            return None # Sem erro
        else:
            return "Tipo de campo de endereço desconhecido."
    else:
        return error_msg # Retorna a mensagem de erro da função buscar_cep

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
        return f"{telefone[:2]}-{telefone[2:7]}-{telefone[7:]}"
    elif len(telefone) == 10: # Telefone fixo ou celular sem 9º dígito
        return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
    return telefone # Retorna sem formatação se não corresponder aos padrões


def gerar_pdf_pf(dados, dependentes=None):
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
        # Campos do comprador
        fields_comprador = [
            ("Nome Completo", "comprador_nome_pf"),
            ("Profissão", "comprador_profissao_pf"),
            ("Nacionalidade", "comprador_nacionalidade_pf"),
            ("Fone Residencial", "comprador_fone_residencial_pf"),
            ("Fone Comercial", "comprador_fone_comercial_pf"),
            ("Celular", "comprador_celular_pf"),
            ("E-mail", "comprador_email_pf"),
            ("Endereço Residencial", "comprador_end_residencial_pf", "comprador_numero_pf"),
            ("Bairro", "comprador_bairro_pf"),
            ("Cidade/Estado", "comprador_cidade_pf", "comprador_estado_pf"),
            ("CEP", "comprador_cep_pf"),
            ("Estado Civil", "comprador_estado_civil_pf"),
            ("Regime de Bens", "comprador_regime_bens_pf"),
            ("União Estável", "comprador_uniao_estavel_pf")
        ]
        for field_info in fields_comprador:
            label = field_info[0]
            if len(field_info) == 2:
                value = dados.get(field_info[1], '')
                if value and sanitize_text(value):
                    # Aplica formatação de telefone se o campo for de telefone
                    if "fone" in field_info[1] or "celular" in field_info[1]:
                        value = formatar_telefone(value)
                    elif "cpf" in field_info[1]:
                        value = formatar_cpf(value)
                    pdf.cell(0, 6, f"{sanitize_text(label)}: {sanitize_text(value)}", 0, 1)
            elif len(field_info) == 3: # Special case for address and city/state
                if label == "Endereço Residencial":
                    endereco = dados.get(field_info[1], '')
                    numero = dados.get(field_info[2], '')
                    if endereco and sanitize_text(endereco):
                        pdf.cell(0, 6, f"{sanitize_text(label)}: {sanitize_text(endereco)}, Nº {sanitize_text(numero)}", 0, 1)
                elif label == "Cidade/Estado":
                    cidade = dados.get(field_info[1], '')
                    estado = dados.get(field_info[2], '')
                    if cidade and estado and sanitize_text(cidade) and sanitize_text(estado):
                         pdf.cell(0, 6, f"{sanitize_text(label)}: {sanitize_text(cidade)}/{sanitize_text(estado)}", 0, 1)

        pdf.ln(3) # Reduzido de 5 para 3
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, sanitize_text("Condição de Convivência:"), 0, 1) # Reduzido de 7 para 6
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 4.5, sanitize_text("Declara conviver em união estável - Apresentar comprovante de estado civil de cada um e a declaração de convivência em união estável com as assinaturas reconhecidas em Cartório."), 0, "L") # Reduzido de 5 para 4.5
        pdf.ln(3) # Reduzido de 5 para 3

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, sanitize_text("Dados do CÔNJUGE/SÓCIO(A)"), 0, 1, "L")
        pdf.set_font("Helvetica", "", 10)
        # Campos do cônjuge/sócio
        fields_conjuge_pf = [
            ("Nome Completo Cônjuge/Sócio(a)", "conjuge_nome_pf"),
            ("Profissão Cônjuge/Sócio(a)", "conjuge_profissao_pf"),
            ("Nacionalidade Cônjuge/Sócio(a)", "conjuge_nacionalidade_pf"),
            ("Fone Residencial Cônjuge/Sócio(a)", "conjuge_fone_residencial_pf"),
            ("Fone Comercial Cônjuge/Sócio(a)", "conjuge_fone_comercial_pf"),
            ("Celular", "conjuge_celular_pf"),
            ("E-mail", "conjuge_email_pf"),
            ("Endereço Residencial", "conjuge_end_residencial_pf", "conjuge_numero_pf"),
            ("Bairro", "conjuge_bairro_pf"),
            ("Cidade/Estado", "conjuge_cidade_pf", "conjuge_estado_pf"),
            ("CEP", "conjuge_cep_pf")
        ]
        for field_info in fields_conjuge_pf:
            label = field_info[0]
            if len(field_info) == 2:
                value = dados.get(field_info[1], '')
                if value and sanitize_text(value):
                    # Aplica formatação de telefone se o campo for de telefone
                    if "fone" in field_info[1] or "celular" in field_info[1]:
                        value = formatar_telefone(value)
                    elif "cpf" in field_info[1]:
                        value = formatar_cpf(value)
                    pdf.cell(0, 6, f"{sanitize_text(label)}: {sanitize_text(value)}", 0, 1)
            elif len(field_info) == 3: # Special case for address and city/state
                if label == "Endereço Residencial":
                    endereco = dados.get(field_info[1], '')
                    numero = dados.get(field_info[2], '')
                    if endereco and sanitize_text(endereco):
                        pdf.cell(0, 6, f"{sanitize_text(label)}: {sanitize_text(endereco)}, Nº {sanitize_text(numero)}", 0, 1)
                elif label == "Cidade/Estado":
                    cidade = dados.get(field_info[1], '')
                    estado = dados.get(field_info[2], '')
                    if cidade and estado and sanitize_text(cidade) and sanitize_text(estado):
                        pdf.cell(0, 6, f"{sanitize_text(label)}: {sanitize_text(cidade)}/{sanitize_text(estado)}", 0, 1)
        pdf.ln(3) # Reduzido de 5 para 3

        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, sanitize_text("DOCUMENTOS NECESSÁRIOS:"), 0, 1) # Reduzido de 7 para 6
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 4.5, sanitize_text("CNH; RG e CPF; Comprovante do Estado Civil, Comprovante de Endereço, Comprovante de Renda, CND da Prefeitura e Nada Consta do Condomínio ou Associação."), 0, "L") # Reduzido de 5 para 4.5
        pdf.ln(1) # Reduzido de 5 para 3
        # Campo adicional para condômino indicado
        condomino_indicado = dados.get('condomino_indicado_pf', '')
        if condomino_indicado and sanitize_text(condomino_indicado):
            pdf.ln(1)
            pdf.set_font("Helvetica", "B", 10)
            pdf.multi_cell(0, 6, sanitize_text("No caso de Condomínio ou Loteamento Fechado, quando a cessão for emitida para sócio(a)(s), não casados entre si e nem conviventes é necessário indicar qual dos dois será o(a) condômino(a):"), 0, 'L')
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 6, f"Indique aqui quem será o(a) condômino(a): {sanitize_text(condomino_indicado)}", 0, 1)
            pdf.ln(3)


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

        # Imobiliária Celeste
        pdf.cell(0, 0, "_" * 50, 0, 1, 'C') # Linha para assinatura
        pdf.ln(3) # Reduzido de 5 para 3
        pdf.cell(0, 4, sanitize_text("Imobiliária Celeste"), 0, 1, 'C') # Reduzido de 5 para 4
        
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

def gerar_pdf_pj(dados, dependentes=None):
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
        # Campos do comprador PJ
        fields_comprador_pj = [
            ("Razão Social", "comprador_razao_social_pj"),
            ("Nome Fantasia", "comprador_nome_fantasia_pj"),
            ("Inscrição Estadual", "comprador_inscricao_estadual_pj"),
            ("Fone Residencial", "comprador_fone_residencial_pj"),
            ("Fone Comercial", "comprador_fone_comercial_pj"),
            ("Celular", "comprador_celular_pj"),
            ("E-mail", "comprador_email_pj"),
            ("Endereço Residencial/Comercial", "comprador_end_residencial_comercial_pj", "comprador_numero_pj"),
            ("Bairro", "comprador_bairro_pj"),
            ("Cidade/Estado", "comprador_cidade_pj", "comprador_estado_pj"),
            ("CEP", "comprador_cep_pj")
        ]
        for field_info in fields_comprador_pj:
            label = field_info[0]
            if len(field_info) == 2:
                value = dados.get(field_info[1], '')
                if value and sanitize_text(value):
                    # Aplica formatação de telefone se o campo for de telefone
                    if "fone" in field_info[1] or "celular" in field_info[1]:
                        value = formatar_telefone(value)
                    elif "cnpj" in field_info[1]:
                        value = formatar_cnpj(value)
                    pdf.cell(0, 6, f"{sanitize_text(label)}: {sanitize_text(value)}", 0, 1)
            elif len(field_info) == 3: # Special case for address and city/state
                if label == "Endereço Residencial/Comercial":
                    endereco = dados.get(field_info[1], '')
                    numero = dados.get(field_info[2], '')
                    if endereco and sanitize_text(endereco):
                        pdf.cell(0, 6, f"{sanitize_text(label)}: {sanitize_text(endereco)}, Nº {sanitize_text(numero)}", 0, 1)
                elif label == "Cidade/Estado":
                    cidade = dados.get(field_info[1], '')
                    estado = dados.get(field_info[2], '')
                    if cidade and estado and sanitize_text(cidade) and sanitize_text(estado):
                        pdf.cell(0, 6, f"{sanitize_text(label)}: {sanitize_text(cidade)}/{sanitize_text(estado)}", 0, 1)
        pdf.ln(3) # Reduzido de 5 para 3

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, sanitize_text("Dados do REPRESENTANTE"), 0, 1, "L")
        pdf.set_font("Helvetica", "", 10)
        # Campos do representante
        fields_representante_pj = [
            ("Nome Completo Representante", "representante_nome_pj"),
            ("Profissão Representante", "representante_profissao_pj"),
            ("Nacionalidade Representante", "representante_nacionalidade_pj"),
            ("Fone Residencial Representante", "representante_fone_residencial_pj"),
            ("Fone Comercial Representante", "representante_fone_comercial_pj"),
            ("Celular", "representante_celular_pj"),
            ("E-mail", "representante_email_pj"),
            ("Endereço Residencial", "representante_end_residencial_pj", "representante_numero_pj"),
            ("Bairro", "representante_bairro_pj"),
            ("Cidade/Estado", "representante_cidade_pj", "representante_estado_pj"),
            ("CEP", "representante_cep_pj")
        ]
        for field_info in fields_representante_pj:
            label = field_info[0]
            if len(field_info) == 2:
                value = dados.get(field_info[1], '')
                if value and sanitize_text(value):
                    # Aplica formatação de telefone se o campo for de telefone
                    if "fone" in field_info[1] or "celular" in field_info[1]:
                        value = formatar_telefone(value)
                    elif "cpf" in field_info[1]:
                        value = formatar_cpf(value)
                    pdf.cell(0, 6, f"{sanitize_text(label)}: {sanitize_text(value)}", 0, 1)
            elif len(field_info) == 3: # Special case for address and city/state
                if label == "Endereço Residencial":
                    endereco = dados.get(field_info[1], '')
                    numero = dados.get(field_info[2], '')
                    if endereco and sanitize_text(endereco):
                        pdf.cell(0, 6, f"{sanitize_text(label)}: {sanitize_text(endereco)}, Nº {sanitize_text(numero)}", 0, 1)
                elif label == "Cidade/Estado":
                    cidade = dados.get(field_info[1], '')
                    estado = dados.get(field_info[2], '')
                    if cidade and estado and sanitize_text(cidade) and sanitize_text(estado):
                        pdf.cell(0, 6, f"{sanitize_text(label)}: {sanitize_text(cidade)}/{sanitize_text(estado)}", 0, 1)
        pdf.ln(3) # Reduzido de 5 para 3

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, sanitize_text("Dados do CÔNJUGE/SÓCIO(A)"), 0, 1, "L")
        pdf.set_font("Helvetica", "", 10)
        # Campos do cônjuge/sócio PJ
        fields_conjuge_pj = [
            ("Nome Completo Cônjuge/Sócio(a) PJ", "conjuge_nome_pj"),
            ("Profissão Cônjuge/Sócio(a) PJ", "conjuge_profissao_pj"),
            ("Nacionalidade Cônjuge/Sócio(a) PJ", "conjuge_nacionalidade_pj"),
            ("Fone Residencial Cônjuge/Sócio(a) PJ", "conjuge_fone_residencial_pj"),
            ("Fone Comercial Cônjuge/Sócio(a) PJ", "conjuge_fone_comercial_pj"),
            ("Celular", "conjuge_celular_pj"),
            ("E-mail", "conjuge_email_pj"),
            ("Endereço Residencial", "conjuge_end_residencial_pj", "conjuge_numero_pj"),
            ("Bairro", "conjuge_bairro_pj"),
            ("Cidade/Estado", "conjuge_cidade_pj", "conjuge_estado_pj"),
            ("CEP", "conjuge_cep_pj")
        ]
        for field_info in fields_conjuge_pj:
            label = field_info[0]
            if len(field_info) == 2:
                value = dados.get(field_info[1], '')
                if value and sanitize_text(value):
                    # Aplica formatação de telefone se o campo for de telefone
                    if "fone" in field_info[1] or "celular" in field_info[1]:
                        value = formatar_telefone(value)
                    elif "cpf" in field_info[1]:
                        value = formatar_cpf(value)
                    pdf.cell(0, 6, f"{sanitize_text(label)}: {sanitize_text(value)}", 0, 1)
            elif len(field_info) == 3: # Special case for address and city/state
                if label == "Endereço Residencial":
                    endereco = dados.get(field_info[1], '')
                    numero = dados.get(field_info[2], '')
                    if endereco and sanitize_text(endereco):
                        pdf.cell(0, 6, f"{sanitize_text(label)}: {sanitize_text(endereco)}, Nº {sanitize_text(numero)}", 0, 1)
                elif label == "Cidade/Estado":
                    cidade = dados.get(field_info[1], '')
                    estado = dados.get(field_info[2], '')
                    if cidade and estado and sanitize_text(cidade) and sanitize_text(estado):
                        pdf.cell(0, 6, f"{sanitize_text(label)}: {sanitize_text(cidade)}/{sanitize_text(estado)}", 0, 1)
        pdf.ln(3) # Reduzido de 5 para 3
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, sanitize_text("DOCUMENTOS NECESSÁRIOS:"), 0, 1) # Reduzido de 7 para 6
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 4.5, sanitize_text("DA EMPRESA: CONTRATO SOCIAL E ALTERAÇÕES, COMPROVANTE DE ENDEREÇO, DECLARAÇÃO DE FATURAMENTO;"), 0, "L") # Reduzido de 5 para 4.5
        pdf.multi_cell(0, 4.5, sanitize_text("DOS SÓCIOS E SEUS CÔNJUGES: CNH; RG e CPF, Comprovante do Estado Civil, Comprovante de Endereço, Comprovante de Renda, CND da Prefeitura e Nada Consta do Condomínio ou Associação."), 0, "L") # Reduzido de 5 para 4.5
        pdf.ln(1) # Reduzido de 5 para 3
        # Campo adicional para condômino indicado
        condomino_indicado = dados.get('condomino_indicado_pj', '')
        if condomino_indicado and sanitize_text(condomino_indicado):
            pdf.ln(1)
            pdf.set_font("Helvetica", "B", 10)
            pdf.multi_cell(0, 6, sanitize_text("No caso de Condomínio ou Loteamento Fechado, quando a empresa possuir mais de um(a) sócio(a) não casados entre si e nem conviventes, é necessário indicar qual do(a)(s) sócio(a)(s) será o(a) condômino(a):"), 0, 'L')
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 6, f"Indique aqui quem será o(a) condômino(a): {sanitize_text(condomino_indicado)}", 0, 1)
            pdf.ln(3)

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

        # Imobiliária Celeste
        pdf.cell(0, 0, "_" * 50, 0, 1, 'C') # Linha para assinatura
        pdf.ln(3) # Reduzido de 5 para 3
        pdf.cell(0, 4, sanitize_text("Imobiliária Celeste"), 0, 1, 'C') # Reduzido de 5 para 4

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

st.title("Ficha Cadastral - Imobiliária Celeste")
st.markdown("Selecione o tipo de cadastro e preencha as informações.")

# Seleção do tipo de ficha
ficha_tipo = st.radio("Selecione o tipo de ficha:", ("Pessoa Física", "Pessoa Jurídica"))

# --- Callback functions for adding dependents ---
def add_dependent_pf_callback():
    # Verifica se os campos obrigatórios estão preenchidos antes de adicionar
    if st.session_state.get("dep_nome_pf") and st.session_state.get("dep_cpf_pf"):
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
        st.warning("Nome e CPF do dependente são obrigatórios para adicionar.")

def add_dependent_pj_callback():
    # Verifica se os campos obrigatórios estão preenchidos antes de adicionar
    if st.session_state.get("dep_nome_pj") and st.session_state.get("dep_cpf_pj"):
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
        st.warning("Nome e CPF do dependente são obrigatórios para adicionar.")

if ficha_tipo == "Pessoa Física":
    st.header("Ficha Cadastral Pessoa Física")

    # Início do formulário principal
    with st.form("form_pf"): 
        st.subheader("Dados do Empreendimento e Imobiliária")
        col1, col2 = st.columns(2)
        with col1:
            empreendimento_pf = st.text_input("Empreendimento", key="empreendimento_pf")
            corretor_pf = st.text_input("Corretor(a)", key="corretor_pf")
            qd_pf = st.text_input("QD", key="qd_pf")
        with col2:
            imobiliaria_pf = st.text_input("Imobiliária", key="imobiliaria_pf")
            lt_pf = st.text_input("LT", key="lt_pf")
            st.markdown("<br>", unsafe_allow_html=True)
            ativo_pf = st.checkbox("Ativo", key="ativo_pf")
            quitado_pf = st.checkbox("Quitado", key="quitado_pf")

        st.subheader("Dados do COMPRADOR(A)")
        col1, col2 = st.columns(2)
        with col1:
            comprador_nome_pf = st.text_input("Nome Completo", key="comprador_nome_pf")
            comprador_profissao_pf = st.text_input("Profissão", key="comprador_profissao_pf")
            comprador_fone_residencial_pf = st.text_input("Fone Residencial", key="comprador_fone_residencial_pf")
            comprador_celular_pf = st.text_input("Celular", key="comprador_celular_pf")
            
            # Estado Civil e Regime de Bens
            col_ec, col_rb = st.columns(2)
            with col_ec:
                comprador_estado_civil_pf = st.selectbox("Estado Civil", ["", "Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)"], key="comprador_estado_civil_pf")
            
            with col_rb:
                comprador_regime_bens_pf = st.selectbox("Regime de Bens", REGIMES_DE_BENS, key="comprador_regime_bens_pf")

            st.markdown("**Condição de Convivência:**")
            comprador_uniao_estavel_pf = st.checkbox("( ) Declara conviver em união estável", key="comprador_uniao_estavel_pf")
            st.markdown("– Apresentar comprovante de estado civil de cada um e a declaração de convivência em união estável com as assinaturas reconhecidas em Cartório.")
            
            comprador_cep_pf = st.text_input("CEP", help="Digite o CEP e pressione Enter para buscar o endereço.", key="comprador_cep_pf")
            
            if st.form_submit_button("Buscar Endereço Comprador"):
                if comprador_cep_pf:
                    error_msg = preencher_endereco('pf', comprador_cep_pf)
                    if error_msg:
                        st.error(error_msg)
                    else:
                        st.success("Endereço do comprador preenchido!")
                        st.rerun() # Força a atualização dos campos na UI
                else:
                    st.warning("Por favor, digite um CEP para buscar.")

        with col2:
            comprador_nacionalidade_pf = st.text_input("Nacionalidade", key="comprador_nacionalidade_pf")
            comprador_email_pf = st.text_input("E-mail", key="comprador_email_pf")
            comprador_fone_comercial_pf = st.text_input("Fone Comercial", key="comprador_fone_comercial_pf")

        # Campos preenchidos automaticamente após a busca do CEP
        # Usando 'value' para refletir o session_state e 'key' para o controle do widget
        comprador_end_residencial_pf = st.text_input("Endereço Residencial", value=st.session_state.get("comprador_end_residencial_pf", ""), key="comprador_end_residencial_pf")
        comprador_numero_pf = st.text_input("Número", value=st.session_state.get("comprador_numero_pf", ""), key="comprador_numero_pf")
        comprador_bairro_pf = st.text_input("Bairro", value=st.session_state.get("comprador_bairro_pf", ""), key="comprador_bairro_pf")
        comprador_cidade_pf = st.text_input("Cidade", value=st.session_state.get("comprador_cidade_pf", ""), key="comprador_cidade_pf")
        comprador_estado_pf = st.text_input("Estado", value=st.session_state.get("comprador_estado_pf", ""), key="comprador_estado_pf")

        st.subheader("Dados do CÔNJUGE/SÓCIO(A)")
        col1, col2 = st.columns(2)
        with col1:
            conjuge_nome_pf = st.text_input("Nome Completo Cônjuge/Sócio(a)", key="conjuge_nome_pf")
            conjuge_profissao_pf = st.text_input("Profissão Cônjuge/Sócio(a)", key="conjuge_profissao_pf")
            conjuge_fone_residencial_pf = st.text_input("Fone Residencial Cônjuge/Sócio(a)", key="conjuge_fone_residencial_pf")
            conjuge_celular_pf = st.text_input("Celular Cônjuge/Sócio(a)", key="conjuge_celular_pf")
            conjuge_cep_pf = st.text_input("CEP Cônjuge/Sócio(a)", help="Digite o CEP e pressione Enter para buscar o endereço.", key="conjuge_cep_pf")

            if st.form_submit_button("Buscar Endereço Cônjuge/Sócio(a)"):
                if conjuge_cep_pf:
                    error_msg = preencher_endereco('conjuge_pf', conjuge_cep_pf)
                    if error_msg:
                        st.error(error_msg)
                    else:
                        st.success("Endereço do cônjuge preenchido!")
                        st.rerun() # Força a atualização dos campos na UI
                else:
                    st.warning("Por favor, digite um CEP para buscar.")

        with col2:
            conjuge_nacionalidade_pf = st.text_input("Nacionalidade Cônjuge/Sócio(a)", key="conjuge_nacionalidade_pf")
            conjuge_email_pf = st.text_input("E-mail Cônjuge/Sócio(a)", key="conjuge_email_pf")
            conjuge_fone_comercial_pf = st.text_input("Fone Comercial Cônjuge/Sócio(a)", key="conjuge_fone_comercial_pf")

        # Campos preenchidos automaticamente após a busca do CEP
        conjuge_end_residencial_pf = st.text_input("Endereço Residencial Cônjuge/Sócio(a)", value=st.session_state.get("conjuge_end_residencial_pf", ""), key="conjuge_end_residencial_pf")
        conjuge_numero_pf = st.text_input("Número Cônjuge/Sócio(a)", value=st.session_state.get("conjuge_numero_pf", ""), key="conjuge_numero_pf")
        conjuge_bairro_pf = st.text_input("Bairro Cônjuge/Sócio(a)", value=st.session_state.get("conjuge_bairro_pf", ""), key="conjuge_bairro_pf")
        conjuge_cidade_pf = st.text_input("Cidade Cônjuge/Sócio(a)", value=st.session_state.get("conjuge_cidade_pf", ""), key="conjuge_cidade_pf")
        conjuge_estado_pf = st.text_input("Estado Cônjuge/Sócio(a)", value=st.session_state.get("conjuge_estado_pf", ""), key="conjuge_estado_pf")

        st.markdown("---")
        st.markdown("**DOCUMENTOS NECESSÁRIOS:**")
        st.markdown("- CNH; RG e CPF; Comprovante do Estado Civil, Comprovante de Endereço, Comprovante de Renda, CND da Prefeitura e Nada Consta do Condomínio ou Associação.")
        st.markdown("---")

        st.write("No caso de Condomínio ou Loteamento Fechado, quando a cessão for emitida para sócio(a)(s), não casados entre si e nem conviventes é necessário indicar qual dos dois será o(a) condômino(a):")
        condomino_indicado_pf = st.text_input("Indique aqui quem será o(a) condômino(a)", key="condomino_indicado_pf")

        # Botões de ação do formulário principal (permanecem dentro do st.form)
        col1, col2 = st.columns(2)
        with col1:
            submitted_pf = st.form_submit_button("Gerar Ficha de Pessoa Física")
        with col2:
            imprimir_pf = st.form_submit_button("Imprimir Formulário")

    # Seção para Dependentes (FORA DO st.form para Pessoa Física)
    st.subheader("Dependentes")
    incluir_dependentes_pf = st.checkbox("Incluir Dependentes", key="incluir_dependentes_pf_checkbox") # Renomeado key para evitar conflito

    if incluir_dependentes_pf:
        with st.container(border=True): # Use um container para agrupar visualmente
            st.markdown("**Adicionar Novo Dependente:**")
            dep_nome_pf = st.text_input("Nome Completo do Dependente", value=st.session_state.get("dep_nome_pf", ""), key="dep_nome_pf")
            dep_cpf_pf = st.text_input("CPF do Dependente", value=st.session_state.get("dep_cpf_pf", ""), key="dep_cpf_pf")
            dep_tel_comercial_pf = st.text_input("Telefone Comercial do Dependente", value=st.session_state.get("dep_tel_comercial_pf", ""), key="dep_tel_comercial_pf")
            dep_celular_pf = st.text_input("Celular do Dependente", value=st.session_state.get("dep_celular_pf", ""), key="dep_celular_pf")
            dep_email_pf = st.text_input("E-mail do Dependente", value=st.session_state.get("dep_email_pf", ""), key="dep_email_pf")
            dep_grau_parentesco_pf = st.text_input("Grau de Parentesco", value=st.session_state.get("dep_grau_parentesco_pf", ""), key="dep_grau_parentesco_pf")

            # Botão de adicionar dependente com callback
            st.button("Adicionar Dependente", key="add_dep_pf_button_out_form", on_click=add_dependent_pf_callback)
        
        # Exibe dependentes adicionados (se houver)
        if st.session_state.dependentes_pf_temp:
            st.markdown("---")
            st.markdown("**Dependentes Adicionados:**")
            df_dependentes_pf = pd.DataFrame(st.session_state.dependentes_pf_temp)
            st.dataframe(df_dependentes_pf)

            clear_dep_pf_button = st.button("Limpar Dependentes", key="clear_dep_pf_button_out_form") # Nova key
            if clear_dep_pf_button:
                st.session_state.dependentes_pf_temp = []
                st.success("Dependentes limpos.")
                st.rerun()

        # Lógica de processamento após a submissão do formulário PF
        # Esta lógica agora é chamada APÓS o `with st.form("form_pf"):`
        if submitted_pf: 
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
                "comprador_end_residencial_pf": comprador_end_residencial_pf.strip(),
                "comprador_numero_pf": comprador_numero_pf.strip(),
                "comprador_bairro_pf": comprador_bairro_pf.strip(),
                "comprador_cidade_pf": comprador_cidade_pf.strip(),
                "comprador_estado_pf": comprador_estado_pf.strip(),
                "comprador_cep_pf": comprador_cep_pf.strip(),
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
                "conjuge_end_residencial_pf": conjuge_end_residencial_pf.strip(),
                "conjuge_numero_pf": conjuge_numero_pf.strip(),
                "conjuge_bairro_pf": conjuge_bairro_pf.strip(),
                "conjuge_cidade_pf": conjuge_cidade_pf.strip(),
                "conjuge_estado_pf": conjuge_estado_pf.strip(),
                "conjuge_cep_pf": conjuge_cep_pf.strip(),
                "condomino_indicado_pf": condomino_indicado_pf.strip(),
            }
            
            pdf_b64_pf = gerar_pdf_pf(dados_pf, st.session_state.dependentes_pf_temp if incluir_dependentes_pf else None)
            if pdf_b64_pf:
                href = f'<a href="data:application/pdf;base64,{pdf_b64_pf}" download="Ficha_Cadastral_Pessoa_Fisica.pdf">Clique aqui para baixar a Ficha Cadastral de Pessoa Física</a>'
                st.markdown(href, unsafe_allow_html=True)


elif ficha_tipo == "Pessoa Jurídica":
    st.header("Ficha Cadastral Pessoa Jurídica")

    with st.form("form_pj"):
        st.subheader("Dados do Empreendimento e Imobiliária")
        col1, col2 = st.columns(2)
        with col1:
            empreendimento_pj = st.text_input("Empreendimento", key="empreendimento_pj")
            corretor_pj = st.text_input("Corretor(a)", key="corretor_pj")
            qd_pj = st.text_input("QD", key="qd_pj")
        with col2:
            imobiliaria_pj = st.text_input("Imobiliária", key="imobiliaria_pj")
            lt_pj = st.text_input("LT", key="lt_pj")
            st.markdown("<br>", unsafe_allow_html=True)
            ativo_pj = st.checkbox("Ativo", key="ativo_pj")
            quitado_pj = st.checkbox("Quitado", key="quitado_pj")

        st.subheader("Dados do COMPRADOR(A)")
        col1, col2 = st.columns(2)
        with col1:
            comprador_razao_social_pj = st.text_input("Razão Social", key="comprador_razao_social_pj")
            comprador_fone_residencial_pj = st.text_input("Fone Residencial", key="comprador_fone_residencial_pj")
            comprador_celular_pj = st.text_input("Celular", key="comprador_celular_pj")
            comprador_cep_pj = st.text_input("CEP", help="Digite o CEP e pressione Enter para buscar o endereço.", key="comprador_cep_pj")
            
            if st.form_submit_button("Buscar Endereço Comprador PJ"):
                if comprador_cep_pj:
                    error_msg = preencher_endereco('empresa_pj', comprador_cep_pj)
                    if error_msg:
                        st.error(error_msg)
                    else:
                        st.success("Endereço do comprador PJ preenchido!")
                        st.rerun()
                else:
                    st.warning("Por favor, digite um CEP para buscar.")

        with col2:
            comprador_nome_fantasia_pj = st.text_input("Nome Fantasia", key="comprador_nome_fantasia_pj")
            comprador_inscricao_estadual_pj = st.text_input("Inscrição Estadual", key="comprador_inscricao_estadual_pj")
            comprador_fone_comercial_pj = st.text_input("Fone Comercial", key="comprador_fone_comercial_pj")
            comprador_email_pj = st.text_input("E-mail", key="comprador_email_pj")

        comprador_end_residencial_comercial_pj = st.text_input("Endereço Residencial/Comercial", value=st.session_state.get("comprador_end_residencial_comercial_pj", ""), key="comprador_end_residencial_comercial_pj")
        comprador_numero_pj = st.text_input("Número", value=st.session_state.get("comprador_numero_pj", ""), key="comprador_numero_pj")
        comprador_bairro_pj = st.text_input("Bairro", value=st.session_state.get("comprador_bairro_pj", ""), key="comprador_bairro_pj")
        comprador_cidade_pj = st.text_input("Cidade", value=st.session_state.get("comprador_cidade_pj", ""), key="comprador_cidade_pj")
        comprador_estado_pj = st.text_input("Estado", value=st.session_state.get("comprador_estado_pj", ""), key="comprador_estado_pj")

        st.subheader("Dados do REPRESENTANTE")
        col1, col2 = st.columns(2)
        with col1:
            representante_nome_pj = st.text_input("Nome Completo Representante", key="representante_nome_pj")
            representante_profissao_pj = st.text_input("Profissão Representante", key="representante_profissao_pj")
            representante_fone_residencial_pj = st.text_input("Fone Residencial Representante", key="representante_fone_residencial_pj")
            representante_celular_pj = st.text_input("Celular Representante", key="representante_celular_pj")
            representante_cep_pj = st.text_input("CEP Representante", help="Digite o CEP e pressione Enter para buscar o endereço.", key="representante_cep_pj")
            
            if st.form_submit_button("Buscar Endereço Representante"):
                if representante_cep_pj:
                    error_msg = preencher_endereco('administrador_pj', representante_cep_pj)
                    if error_msg:
                        st.error(error_msg)
                    else:
                        st.success("Endereço do representante preenchido!")
                        st.rerun()
                else:
                    st.warning("Por favor, digite um CEP para buscar.")

        with col2:
            representante_nacionalidade_pj = st.text_input("Nacionalidade Representante", key="representante_nacionalidade_pj")
            representante_email_pj = st.text_input("E-mail Representante", key="representante_email_pj")
            representante_fone_comercial_pj = st.text_input("Fone Comercial Representante", key="representante_fone_comercial_pj")
        
        representante_end_residencial_pj = st.text_input("Endereço Residencial Representante", value=st.session_state.get("representante_end_residencial_pj", ""), key="representante_end_residencial_pj")
        representante_numero_pj = st.text_input("Número Representante", value=st.session_state.get("representante_numero_pj", ""), key="representante_numero_pj")
        representante_bairro_pj = st.text_input("Bairro Representante", value=st.session_state.get("representante_bairro_pj", ""), key="representante_bairro_pj")
        representante_cidade_pj = st.text_input("Cidade Representante", value=st.session_state.get("representante_cidade_pj", ""), key="representante_cidade_pj")
        representante_estado_pj = st.text_input("Estado Representante", value=st.session_state.get("representante_estado_pj", ""), key="representante_estado_pj")

        st.subheader("Dados do CÔNJUGE/SÓCIO(A)")
        col1, col2 = st.columns(2)
        with col1:
            conjuge_nome_pj = st.text_input("Nome Completo Cônjuge/Sócio(a) PJ", key="conjuge_nome_pj")
            conjuge_profissao_pj = st.text_input("Profissão Cônjuge/Sócio(a) PJ", key="conjuge_profissao_pj")
            conjuge_fone_residencial_pj = st.text_input("Fone Residencial Cônjuge/Sócio(a) PJ", key="conjuge_fone_residencial_pj")
            conjuge_celular_pj = st.text_input("Celular Cônjuge/Sócio(a) PJ", key="conjuge_celular_pj")
            conjuge_cep_pj = st.text_input("CEP Cônjuge/Sócio(a) PJ", help="Digite o CEP e pressione Enter para buscar o endereço.", key="conjuge_cep_pj")
            
            if st.form_submit_button("Buscar Endereço Cônjuge/Sócio(a) PJ"):
                if conjuge_cep_pj:
                    error_msg = preencher_endereco('conjuge_pj', conjuge_cep_pj)
                    if error_msg:
                        st.error(error_msg)
                    else:
                        st.success("Endereço do cônjuge/sócio PJ preenchido!")
                        st.rerun()
                else:
                    st.warning("Por favor, digite um CEP para buscar.")

        with col2:
            conjuge_nacionalidade_pj = st.text_input("Nacionalidade Cônjuge/Sócio(a) PJ", key="conjuge_nacionalidade_pj")
            conjuge_email_pj = st.text_input("E-mail Cônjuge/Sócio(a) PJ", key="conjuge_email_pj")
            conjuge_fone_comercial_pj = st.text_input("Fone Comercial Cônjuge/Sócio(a) PJ", key="conjuge_fone_comercial_pj")

        conjuge_end_residencial_pj = st.text_input("Endereço Residencial Cônjuge/Sócio(a) PJ", value=st.session_state.get("conjuge_end_residencial_pj", ""), key="conjuge_end_residencial_pj")
        conjuge_numero_pj = st.text_input("Número Cônjuge/Sócio(a) PJ", value=st.session_state.get("conjuge_numero_pj", ""), key="conjuge_numero_pj")
        conjuge_bairro_pj = st.text_input("Bairro Cônjuge/Sócio(a) PJ", value=st.session_state.get("conjuge_bairro_pj", ""), key="conjuge_bairro_pj")
        conjuge_cidade_pj = st.text_input("Cidade Cônjuge/Sócio(a) PJ", value=st.session_state.get("conjuge_cidade_pj", ""), key="conjuge_cidade_pj")
        conjuge_estado_pj = st.text_input("Estado Cônjuge/Sócio(a) PJ", value=st.session_state.get("conjuge_estado_pj", ""), key="conjuge_estado_pj")

        st.markdown("---")
        st.markdown("**DOCUMENTOS NECESSÁRIOS:**")
        st.markdown("- **DA EMPRESA:** CONTRATO SOCIAL E ALTERAÇÕES, COMPROVANTE DE ENDEREÇO, DECLARAÇÃO DE FATURAMENTO;")
        st.markdown("- **DOS SÓCIOS E SEUS CÔNJUGES:** CNH; RG e CPF, Comprovante do Estado Civil, Comprovante de Endereço, Comprovante de Renda, CND da Prefeitura e Nada Consta do Condomínio ou Associação.")
        st.markdown("---")

        st.write("No caso de Condomínio ou Loteamento Fechado, quando a empresa possuir mais de um(a) sócio(a) não casados entre si e nem conviventes, é necessário indicar qual do(a)(s) sócio(a)(s) será o(a) condômino(a):")
        condomino_indicado_pj = st.text_input("Indique aqui quem será o(a) condômino(a)", key="condomino_indicado_pj")

        # Botões de ação do formulário principal
        submitted_pj = st.form_submit_button("Gerar Ficha de Pessoa Jurídica")
        imprimir_pj = st.form_submit_button("Imprimir Formulário")

    # Seção para Dependentes PJ (FORA DO st.form)
    st.subheader("Dependentes (Pessoa Jurídica)")
    incluir_dependentes_pj = st.checkbox("Incluir Dependentes para PJ", key="incluir_dependentes_pj_checkbox") # Renomeado key

    if incluir_dependentes_pj:
        with st.container(border=True): # Use um container para agrupar visualmente
            st.markdown("**Adicionar Novo Dependente para PJ:**")
            dep_nome_pj = st.text_input("Nome Completo do Dependente (PJ)", value=st.session_state.get("dep_nome_pj", ""), key="dep_nome_pj")
            dep_cpf_pj = st.text_input("CPF do Dependente (PJ)", value=st.session_state.get("dep_cpf_pj", ""), key="dep_cpf_pj")
            dep_tel_comercial_pj = st.text_input("Telefone Comercial do Dependente (PJ)", value=st.session_state.get("dep_tel_comercial_pj", ""), key="dep_tel_comercial_pj")
            dep_celular_pj = st.text_input("Celular do Dependente (PJ)", value=st.session_state.get("dep_celular_pj", ""), key="dep_celular_pj")
            dep_email_pj = st.text_input("E-mail do Dependente (PJ)", value=st.session_state.get("dep_email_pj", ""), key="dep_email_pj")
            dep_grau_parentesco_pj = st.text_input("Grau de Parentesco (PJ)", value=st.session_state.get("dep_grau_parentesco_pj", ""), key="dep_grau_parentesco_pj")

            st.button("Adicionar Dependente (PJ)", key="add_dep_pj_button_out_form", on_click=add_dependent_pj_callback) # Nova key
            
            if st.session_state.dependentes_pj_temp:
                st.markdown("---")
                st.markdown("**Dependentes Adicionados (PJ):**")
                df_dependentes_pj = pd.DataFrame(st.session_state.dependentes_pj_temp)
                st.dataframe(df_dependentes_pj)

                clear_dep_pj_button = st.button("Limpar Dependentes (PJ)", key="clear_dep_pj_button_out_form") # Nova key
                if clear_dep_pj_button:
                    st.session_state.dependentes_pj_temp = []
                    st.success("Dependentes limpos para PJ.")
                    st.rerun()

    # Lógica de processamento após a submissão do formulário (agora fora do st.form)
    # submitted_pf e submitted_pj são as variáveis do st.form_submit_button dos forms principais.
    # Esta lógica precisa estar no nível superior ou ser chamada após o formulário.
    if submitted_pf: # submitted_pf é a variável do st.form_submit_button do form principal
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
            "comprador_end_residencial_pf": comprador_end_residencial_pf.strip(),
            "comprador_numero_pf": comprador_numero_pf.strip(),
            "comprador_bairro_pf": comprador_bairro_pf.strip(),
            "comprador_cidade_pf": comprador_cidade_pf.strip(),
            "comprador_estado_pf": comprador_estado_pf.strip(),
            "comprador_cep_pf": comprador_cep_pf.strip(),
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
            "conjuge_end_residencial_pf": conjuge_end_residencial_pf.strip(),
            "conjuge_numero_pf": conjuge_numero_pf.strip(),
            "conjuge_bairro_pf": conjuge_bairro_pf.strip(),
            "conjuge_cidade_pf": conjuge_cidade_pf.strip(),
            "conjuge_estado_pf": conjuge_estado_pf.strip(),
            "conjuge_cep_pf": conjuge_cep_pf.strip(),
            "condomino_indicado_pf": condomino_indicado_pf.strip(),
        }
        
        pdf_b64_pf = gerar_pdf_pf(dados_pf, st.session_state.dependentes_pf_temp if incluir_dependentes_pf else None)
        if pdf_b64_pf:
            href = f'<a href="data:application/pdf;base64,{pdf_b64_pf}" download="Ficha_Cadastral_Pessoa_Fisica.pdf">Clique aqui para baixar a Ficha Cadastral de Pessoa Física</a>'
            st.markdown(href, unsafe_allow_html=True)


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
            "comprador_end_residencial_comercial_pj": comprador_end_residencial_comercial_pj.strip(),
            "comprador_numero_pj": comprador_numero_pj.strip(),
            "comprador_bairro_pj": comprador_bairro_pj.strip(),
            "comprador_cidade_pj": comprador_cidade_pj.strip(),
            "comprador_estado_pj": comprador_estado_pj.strip(),
            "comprador_cep_pj": comprador_cep_pj.strip(),
            "representante_nome_pj": representante_nome_pj.strip(),
            "representante_profissao_pj": representante_profissao_pj.strip(),
            "representante_nacionalidade_pj": representante_nacionalidade_pj.strip(),
            "representante_fone_residencial_pj": representante_fone_residencial_pj.strip(),
            "representante_fone_comercial_pj": representante_fone_comercial_pj.strip(),
            "representante_celular_pj": representante_celular_pj.strip(),
            "representante_email_pj": representante_email_pj.strip(),
            "representante_end_residencial_pj": representante_end_residencial_pj.strip(),
            "representante_numero_pj": representante_numero_pj.strip(),
            "representante_bairro_pj": representante_bairro_pj.strip(),
            "representante_cidade_pj": representante_cidade_pj.strip(),
            "representante_estado_pj": representante_estado_pj.strip(),
            "representante_cep_pj": representante_cep_pj.strip(),
            "conjuge_nome_pj": conjuge_nome_pj.strip(),
            "conjuge_profissao_pj": conjuge_profissao_pj.strip(),
            "conjuge_nacionalidade_pj": conjuge_nacionalidade_pj.strip(),
            "conjuge_fone_residencial_pj": conjuge_fone_residencial_pj.strip(),
            "conjuge_fone_comercial_pj": conjuge_fone_comercial_pj.strip(),
            "conjuge_celular_pj": conjuge_celular_pj.strip(),
            "conjuge_email_pj": conjuge_email_pj.strip(),
            "conjuge_end_residencial_pj": conjuge_end_residencial_pj.strip(),
            "conjuge_numero_pj": conjuge_numero_pj.strip(),
            "conjuge_bairro_pj": conjuge_bairro_pj.strip(),
            "conjuge_cidade_pj": conjuge_cidade_pj.strip(),
            "conjuge_estado_pj": conjuge_estado_pj.strip(),
            "conjuge_cep_pj": conjuge_cep_pj.strip(),
            "condomino_indicado_pj": condomino_indicado_pj.strip(),
        }
        
        pdf_b64_pj = gerar_pdf_pj(dados_pj, st.session_state.dependentes_pj_temp if incluir_dependentes_pj else None)
        if pdf_b64_pj:
            href = f'<a href="data:application/pdf;base64,{pdf_b64_pj}" download="Ficha_Cadastral_Pessoa_Juridica.pdf">Clique aqui para baixar a Ficha Cadastral de Pessoa Jurídica</a>'
            st.markdown(href, unsafe_allow_html=True)
