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

def verificar_conexao_internet(host="8.8.8.8", port=53, timeout=3):
    """Verifica se há conexão com a internet"""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

def buscar_cep(cep):
    """
    Busca informações de endereço a partir de um CEP usando a API ViaCEP.
    Retorna um dicionário com os dados do endereço e uma mensagem de erro (ou None).
    """
    if not cep:
        return None, "Por favor, insira um CEP para buscar."
        
    cep = cep.replace("-", "").replace(".", "").strip()  # Limpa o CEP
    if len(cep) != 8 or not cep.isdigit():
        return None, "CEP inválido. Por favor, insira 8 dígitos numéricos."

    # Verifica conexão com a internet antes de tentar
    if not verificar_conexao_internet():
        return None, "Sem conexão com a internet. Verifique sua rede."

    url = f"https://viacep.com.br/ws/{cep}/json/"
    
    try:
        response = session.get(url, timeout=5)
        response.raise_for_status()  # Levanta erro para códigos 4xx/5xx
        
        data = response.json()
        
        if "erro" not in data:
            return data, None
        else:
            return None, f"CEP não encontrado: {cep}"
            
    except requests.exceptions.Timeout:
        return None, "Tempo de conexão esgotado. Servidor pode estar indisponível."
    except requests.exceptions.ConnectionError:
        return None, "Não foi possível conectar ao servidor. Verifique sua conexão com a internet."
    except requests.exceptions.RequestException as e:
        return None, f"Erro ao buscar CEP: {str(e)}"

def sanitize_text(text):
    """
    Substitui caracteres Unicode problemáticos (como o en dash '\u2013')
    por equivalentes ASCII para evitar erros de codificação no FPDF.
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
        # Adicione mais substituições se outros caracteres causarem problemas
        text = text.strip() # Remove espaços em branco do início e fim
    return text

def gerar_pdf_pf(dados):
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
        pdf.ln(10)

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, sanitize_text("Dados do Empreendimento e Imobiliária"), 0, 1, "L")
        pdf.set_font("Helvetica", "", 10)
        for key, value in dados.items():
            if key in ["empreendimento_pf", "corretor_pf", "imobiliaria_pf", "qd_pf", "lt_pf", "ativo_pf", "quitado_pf"]:
                pdf.cell(0, 7, f"{sanitize_text(key.replace('_pf', '').replace('_', ' ').title())}: {sanitize_text(str(value))}", 0, 1) # Convert value to string before sanitizing
        pdf.ln(5)

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, sanitize_text("Dados do COMPRADOR(A)"), 0, 1, "L")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, f"Nome Completo: {sanitize_text(dados.get('comprador_nome_pf', ''))}", 0, 1)
        pdf.cell(0, 7, f"Profissão: {sanitize_text(dados.get('comprador_profissao_pf', ''))}", 0, 1)
        pdf.cell(0, 7, f"Nacionalidade: {sanitize_text(dados.get('comprador_nacionalidade_pf', ''))}", 0, 1)
        pdf.cell(0, 7, f"Fone Residencial: {sanitize_text(dados.get('comprador_fone_residencial_pf', ''))}", 0, 1)
        pdf.cell(0, 7, f"Fone Comercial: {sanitize_text(dados.get('comprador_fone_comercial_pf', ''))}", 0, 1)
        pdf.cell(0, 7, f"Celular: {sanitize_text(dados.get('comprador_celular_pf', ''))}", 0, 1)
        pdf.cell(0, 7, f"E-mail: {sanitize_text(dados.get('comprador_email_pf', ''))}", 0, 1)
        
        pdf.cell(0, 7, f"Endereço Residencial: {sanitize_text(dados.get('comprador_end_residencial_pf', ''))}, Nº {sanitize_text(dados.get('comprador_numero_pf', ''))}", 0, 1)
        pdf.cell(0, 7, f"Bairro: {sanitize_text(dados.get('comprador_bairro_pf', ''))}", 0, 1)
        pdf.cell(0, 7, f"Cidade/Estado: {sanitize_text(dados.get('comprador_cidade_pf', ''))}/{sanitize_text(dados.get('comprador_estado_pf', ''))}", 0, 1)
        pdf.cell(0, 7, f"CEP: {sanitize_text(dados.get('comprador_cep_pf', ''))}", 0, 1)
        pdf.cell(0, 7, f"Estado Civil: {sanitize_text(dados.get('comprador_estado_civil_pf', ''))}", 0, 1)
        # O campo 'Data do Casamento' foi removido conforme sua solicitação.
        pdf.cell(0, 7, f"Regime de Bens: {sanitize_text(dados.get('comprador_regime_bens_pf', ''))}", 0, 1)
        pdf.cell(0, 7, f"União Estável: {sanitize_text(dados.get('comprador_uniao_estavel_pf', ''))}", 0, 1)
        pdf.ln(5)
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, sanitize_text("Condição de Convivência:"), 0, 1)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, sanitize_text("Declara conviver em união estável - Apresentar comprovante de estado civil de cada um e a declaração de convivência em união estável com as assinaturas reconhecidas em Cartório."), 0, "L")
        pdf.ln(5)

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, sanitize_text("Dados do CÔNJUGE/SÓCIO(A)"), 0, 1, "L")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, f"Nome Completo Cônjuge/Sócio(a): {sanitize_text(dados.get('conjuge_nome_pf', ''))}", 0, 1)
        pdf.cell(0, 7, f"Profissão Cônjuge/Sócio(a): {sanitize_text(dados.get('conjuge_profissao_pf', ''))}", 0, 1)
        pdf.cell(0, 7, f"Nacionalidade Cônjuge/Sócio(a): {sanitize_text(dados.get('conjuge_nacionalidade_pf', ''))}", 0, 1)
        pdf.cell(0, 7, f"Fone Residencial Cônjuge/Sócio(a): {sanitize_text(dados.get('conjuge_fone_residencial_pf', ''))}", 0, 1)
        pdf.cell(0, 7, f"Fone Comercial Cônjuge/Sócio(a): {sanitize_text(dados.get('conjuge_fone_comercial_pf', ''))}", 0, 1)
        pdf.cell(0, 7, f"Celular Cônjuge/Sócio(a): {sanitize_text(dados.get('conjuge_celular_pf', ''))}", 0, 1)
        pdf.cell(0, 7, f"E-mail Cônjuge/Sócio(a): {sanitize_text(dados.get('conjuge_email_pf', ''))}", 0, 1)

        pdf.cell(0, 7, f"Endereço Residencial: {sanitize_text(dados.get('conjuge_end_residencial_pf', ''))}, Nº {sanitize_text(dados.get('conjuge_numero_pf', ''))}", 0, 1)
        pdf.cell(0, 7, f"Bairro: {sanitize_text(dados.get('conjuge_bairro_pf', ''))}", 0, 1)
        pdf.cell(0, 7, f"Cidade/Estado: {sanitize_text(dados.get('conjuge_cidade_pf', ''))}/{sanitize_text(dados.get('conjuge_estado_pf', ''))}", 0, 1)
        pdf.cell(0, 7, f"CEP: {sanitize_text(dados.get('conjuge_cep_pf', ''))}", 0, 1)
        pdf.ln(5)

        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, sanitize_text("DOCUMENTOS NECESSÁRIOS:"), 0, 1)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, sanitize_text("CNH; RG e CPF; Comprovante do Estado Civil, Comprovante de Endereço, Comprovante de Renda, CND da Prefeitura e Nada Consta do Condomínio ou Associação."), 0, "L")
        pdf.ln(5)

        # Adiciona a seção de data e assinaturas
        pdf.ln(10)
        today = datetime.date.today()
        month_names = {
            1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril", 5: "maio", 6: "junho",
            7: "julho", 8: "agosto", 9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
        }
        
        # Cidade/Estado,___ de _________de __________
        current_city_state = f"{sanitize_text(dados.get('comprador_cidade_pf', ''))}/{sanitize_text(dados.get('comprador_estado_pf', ''))}"
        pdf.cell(0, 7, f"{current_city_state}, {today.day} de {month_names[today.month]} de {today.year}", 0, 1, 'C')
        pdf.ln(10) # Espaço antes da linha de assinatura

        # Assinatura do(a) Comprador(a)
        pdf.cell(0, 0, "_" * 50, 0, 1, 'C') # Linha para assinatura
        pdf.ln(5)
        pdf.cell(0, 5, sanitize_text("Assinatura do(a) Comprador(a)"), 0, 1, 'C')
        pdf.ln(10)

        # Autorizado em:__________/______/__________
        pdf.cell(0, 7, f"Autorizado em: {today.strftime('%d/%m/%Y')}", 0, 1, 'C')
        pdf.ln(10)

        # Imobiliária Celeste
        pdf.cell(0, 0, "_" * 50, 0, 1, 'C') # Linha para assinatura
        pdf.ln(5)
        pdf.cell(0, 5, sanitize_text("Imobiliária Celeste"), 0, 1, 'C')
        
        # Adicionada codificação para 'latin-1'
        pdf_output = pdf.output(dest='S').encode('latin-1')
        b64_pdf = base64.b64encode(pdf_output).decode('utf-8')
        return b64_pdf
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {str(e)}")
        return None

def gerar_pdf_pj(dados):
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
        pdf.ln(10)

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, sanitize_text("Dados do Empreendimento e Imobiliária"), 0, 1, "L")
        pdf.set_font("Helvetica", "", 10)
        for key, value in dados.items():
            if key in ["empreendimento_pj", "corretor_pj", "imobiliaria_pj", "qd_pj", "lt_pj", "ativo_pj", "quitado_pj"]:
                pdf.cell(0, 7, f"{sanitize_text(key.replace('_pj', '').replace('_', ' ').title())}: {sanitize_text(str(value))}", 0, 1) # Convert value to string before sanitizing
        pdf.ln(5)

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, sanitize_text("Dados do COMPRADOR(A)"), 0, 1, "L")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, f"Razão Social: {sanitize_text(dados.get('comprador_razao_social_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"Nome Fantasia: {sanitize_text(dados.get('comprador_nome_fantasia_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"Inscrição Estadual: {sanitize_text(dados.get('comprador_inscricao_estadual_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"Fone Residencial: {sanitize_text(dados.get('comprador_fone_residencial_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"Fone Comercial: {sanitize_text(dados.get('comprador_fone_comercial_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"Celular: {sanitize_text(dados.get('comprador_celular_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"E-mail: {sanitize_text(dados.get('comprador_email_pj', ''))}", 0, 1)

        pdf.cell(0, 7, f"Endereço Residencial/Comercial: {sanitize_text(dados.get('comprador_end_residencial_comercial_pj', ''))}, Nº {sanitize_text(dados.get('comprador_numero_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"Bairro: {sanitize_text(dados.get('comprador_bairro_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"Cidade/Estado: {sanitize_text(dados.get('comprador_cidade_pj', ''))}/{sanitize_text(dados.get('comprador_estado_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"CEP: {sanitize_text(dados.get('comprador_cep_pj', ''))}", 0, 1)
        pdf.ln(5)

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, sanitize_text("Dados do REPRESENTANTE"), 0, 1, "L")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, f"Nome Completo Representante: {sanitize_text(dados.get('representante_nome_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"Profissão Representante: {sanitize_text(dados.get('representante_profissao_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"Nacionalidade Representante: {sanitize_text(dados.get('representante_nacionalidade_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"Fone Residencial Representante: {sanitize_text(dados.get('representante_fone_residencial_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"Fone Comercial Representante: {sanitize_text(dados.get('representante_fone_comercial_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"Celular Representante: {sanitize_text(dados.get('representante_celular_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"E-mail Representante: {sanitize_text(dados.get('representante_email_pj', ''))}", 0, 1)
        
        pdf.cell(0, 7, f"Endereço Residencial: {sanitize_text(dados.get('representante_end_residencial_pj', ''))}, Nº {sanitize_text(dados.get('representante_numero_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"Bairro: {sanitize_text(dados.get('representante_bairro_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"Cidade/Estado: {sanitize_text(dados.get('representante_cidade_pj', ''))}/{sanitize_text(dados.get('representante_estado_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"CEP: {sanitize_text(dados.get('representante_cep_pj', ''))}", 0, 1)
        pdf.ln(5)

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, sanitize_text("Dados do CÔNJUGE/SÓCIO(A)"), 0, 1, "L")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, f"Nome Completo Cônjuge/Sócio(a) PJ: {sanitize_text(dados.get('conjuge_nome_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"Profissão Cônjuge/Sócio(a) PJ: {sanitize_text(dados.get('conjuge_profissao_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"Nacionalidade Cônjuge/Sócio(a) PJ: {sanitize_text(dados.get('conjuge_nacionalidade_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"Fone Residencial Cônjuge/Sócio(a) PJ: {sanitize_text(dados.get('conjuge_fone_residencial_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"Fone Comercial Cônjuge/Sócio(a) PJ: {sanitize_text(dados.get('conjuge_fone_comercial_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"Celular Cônjuge/Sócio(a) PJ: {sanitize_text(dados.get('conjuge_celular_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"E-mail Cônjuge/Sócio(a) PJ: {sanitize_text(dados.get('conjuge_email_pj', ''))}", 0, 1)
        
        pdf.cell(0, 7, f"Endereço Residencial: {sanitize_text(dados.get('conjuge_end_residencial_pj', ''))}, Nº {sanitize_text(dados.get('conjuge_numero_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"Bairro: {sanitize_text(dados.get('conjuge_bairro_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"Cidade/Estado: {sanitize_text(dados.get('conjuge_cidade_pj', ''))}/{sanitize_text(dados.get('conjuge_estado_pj', ''))}", 0, 1)
        pdf.cell(0, 7, f"CEP: {sanitize_text(dados.get('conjuge_cep_pj', ''))}", 0, 1)
        pdf.ln(5)
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, sanitize_text("DOCUMENTOS NECESSÁRIOS:"), 0, 1)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, sanitize_text("DA EMPRESA: CONTRATO SOCIAL E ALTERAÇÕES, COMPROVANTE DE ENDEREÇO, DECLARAÇÃO DE FATURAMENTO;"), 0, "L")
        pdf.multi_cell(0, 5, sanitize_text("DOS SÓCIOS E SEUS CÔNJUGES: CNH; RG e CPF, Comprovante do Estado Civil, Comprovante de Endereço, Comprovante de Renda, CND da Prefeitura e Nada Consta do Condomínio ou Associação."), 0, "L")
        pdf.ln(5)

        # Adiciona a seção de data e assinaturas
        pdf.ln(10)
        today = datetime.date.today()
        month_names = {
            1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril", 5: "maio", 6: "junho",
            7: "julho", 8: "agosto", 9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
        }
        
        # Cidade/Estado,___ de _________de __________
        current_city_state = f"{sanitize_text(dados.get('comprador_cidade_pj', ''))}/{sanitize_text(dados.get('comprador_estado_pj', ''))}"
        pdf.cell(0, 7, f"{current_city_state}, {today.day} de {month_names[today.month]} de {today.year}", 0, 1, 'C')
        pdf.ln(10) # Espaço antes da linha de assinatura

        # Assinatura do(a) Comprador(a) / Representante Legal (para PJ)
        pdf.cell(0, 0, "_" * 50, 0, 1, 'C') # Linha para assinatura
        pdf.ln(5)
        # Para PJ, o ideal seria "Assinatura do(a) Representante Legal" ou similar.
        # Mantendo "Assinatura do(a) Comprador(a)" conforme solicitado genericamente.
        pdf.cell(0, 5, sanitize_text("Assinatura do(a) Comprador(a)"), 0, 1, 'C') 
        pdf.ln(10)

        # Autorizado em:__________/______/__________
        pdf.cell(0, 7, f"Autorizado em: {today.strftime('%d/%m/%Y')}", 0, 1, 'C')
        pdf.ln(10)

        # Imobiliária Celeste
        pdf.cell(0, 0, "_" * 50, 0, 1, 'C') # Linha para assinatura
        pdf.ln(5)
        pdf.cell(0, 5, sanitize_text("Imobiliária Celeste"), 0, 1, 'C')

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

if ficha_tipo == "Pessoa Física":
    st.header("Ficha Cadastral Pessoa Física")

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

            # O campo 'Data do Casamento' e sua lógica foram removidos daqui.
            
            st.markdown("**Condição de Convivência:**")
            comprador_uniao_estavel_pf = st.checkbox("( ) Declara conviver em união estável", key="comprador_uniao_estavel_pf")
            st.markdown("– Apresentar comprovante de estado civil de cada um e a declaração de convivência em união estável com as assinaturas reconhecidas em Cartório.")
            
            comprador_cep_pf = st.text_input("CEP", help="Digite o CEP e pressione Enter para buscar o endereço.", key="comprador_cep_pf")
            
            if st.form_submit_button("Buscar Endereço Comprador"):
                if comprador_cep_pf:
                    endereco_comprador, error_msg = buscar_cep(comprador_cep_pf)
                    if endereco_comprador:
                        st.session_state.comprador_end_residencial_pf = endereco_comprador.get("logradouro", "")
                        st.session_state.comprador_bairro_pf = endereco_comprador.get("bairro", "")
                        st.session_state.comprador_cidade_pf = endereco_comprador.get("localidade", "")
                        st.session_state.comprador_estado_pf = endereco_comprador.get("uf", "")
                        st.success("Endereço do comprador preenchido!")
                    elif error_msg:
                        st.error(error_msg) # Exibe a mensagem de erro específica
                else:
                    st.warning("Por favor, digite um CEP para buscar.")

        with col2:
            comprador_nacionalidade_pf = st.text_input("Nacionalidade", key="comprador_nacionalidade_pf")
            comprador_email_pf = st.text_input("E-mail", key="comprador_email_pf")
            comprador_fone_comercial_pf = st.text_input("Fone Comercial", key="comprador_fone_comercial_pf")

        # Campos preenchidos automaticamente após a busca do CEP (chaves atualizadas para evitar conflitos)
        comprador_end_residencial_pf_val = st.text_input("Endereço Residencial", value=st.session_state.get("comprador_end_residencial_pf", ""), key="comprador_end_residencial_pf_display")
        comprador_numero_pf = st.text_input("Número", key="comprador_numero_pf")
        comprador_bairro_pf_val = st.text_input("Bairro", value=st.session_state.get("comprador_bairro_pf", ""), key="comprador_bairro_pf_display")
        comprador_cidade_pf_val = st.text_input("Cidade", value=st.session_state.get("comprador_cidade_pf", ""), key="comprador_cidade_pf_display")
        comprador_estado_pf_val = st.text_input("Estado", value=st.session_state.get("comprador_estado_pf", ""), key="comprador_estado_pf_display")

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
                    endereco_conjuge, error_msg = buscar_cep(conjuge_cep_pf)
                    if endereco_conjuge:
                        st.session_state.conjuge_end_residencial_pf = endereco_conjuge.get("logradouro", "")
                        st.session_state.conjuge_bairro_pf = endereco_conjuge.get("bairro", "")
                        st.session_state.conjuge_cidade_pf = endereco_conjuge.get("localidade", "")
                        st.session_state.conjuge_estado_pf = endereco_conjuge.get("uf", "")
                        st.success("Endereço do cônjuge preenchido!")
                    elif error_msg:
                        st.error(error_msg) # Exibe a mensagem de erro específica
                else:
                    st.warning("Por favor, digite um CEP para buscar.")

        with col2:
            conjuge_nacionalidade_pf = st.text_input("Nacionalidade Cônjuge/Sócio(a)", key="conjuge_nacionalidade_pf")
            conjuge_email_pf = st.text_input("E-mail Cônjuge/Sócio(a)", key="conjuge_email_pf")
            conjuge_fone_comercial_pf = st.text_input("Fone Comercial Cônjuge/Sócio(a)", key="conjuge_fone_comercial_pf")

        # Campos preenchidos automaticamente após a busca do CEP (chaves atualizadas para evitar conflitos)
        conjuge_end_residencial_pf_val = st.text_input("Endereço Residencial Cônjuge/Sócio(a)", value=st.session_state.get("conjuge_end_residencial_pf", ""), key="conjuge_end_residencial_pf_display")
        conjuge_numero_pf = st.text_input("Número Cônjuge/Sócio(a)", key="conjuge_numero_pf")
        conjuge_bairro_pf_val = st.text_input("Bairro Cônjuge/Sócio(a)", value=st.session_state.get("conjuge_bairro_pf", ""), key="conjuge_bairro_pf_display")
        conjuge_cidade_pf_val = st.text_input("Cidade Cônjuge/Sócio(a)", value=st.session_state.get("conjuge_cidade_pf", ""), key="conjuge_cidade_pf_display")
        conjuge_estado_pf_val = st.text_input("Estado Cônjuge/Sócio(a)", value=st.session_state.get("conjuge_estado_pf", ""), key="conjuge_estado_pf_display")

        st.markdown("---")
        st.markdown("**DOCUMENTOS NECESSÁRIOS:**")
        st.markdown("- CNH; RG e CPF; Comprovante do Estado Civil, Comprovante de Endereço, Comprovante de Renda, CND da Prefeitura e Nada Consta do Condomínio ou Associação.")
        st.markdown("---")

        st.write("📌 No caso de Condomínio ou Loteamento Fechado, quando a cessão for emitida para sócio(a)(s), não casados entre si e nem conviventes é necessário indicar qual dos dois será o(a) condômino(a): 📌")
        condomino_indicado_pf = st.text_input("➡️ Indique aqui quem será o(a) condômino(a)", key="condomino_indicado_pf")

        submitted_pf = st.form_submit_button("Gerar Ficha de Pessoa Física")
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
                "comprador_end_residencial_pf": comprador_end_residencial_pf_val.strip(),
                "comprador_numero_pf": comprador_numero_pf.strip(),
                "comprador_bairro_pf": comprador_bairro_pf_val.strip(),
                "comprador_cidade_pf": comprador_cidade_pf_val.strip(),
                "comprador_estado_pf": comprador_estado_pf_val.strip(),
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
                "conjuge_end_residencial_pf": conjuge_end_residencial_pf_val.strip(),
                "conjuge_numero_pf": conjuge_numero_pf.strip(),
                "conjuge_bairro_pf": conjuge_bairro_pf_val.strip(),
                "conjuge_cidade_pf": conjuge_cidade_pf_val.strip(),
                "conjuge_estado_pf": conjuge_estado_pf_val.strip(),
                "conjuge_cep_pf": conjuge_cep_pf.strip(),
                "condomino_indicado_pf": condomino_indicado_pf.strip(),
            }
            
            pdf_b64_pf = gerar_pdf_pf(dados_pf)
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
                    endereco_comprador_pj, error_msg = buscar_cep(comprador_cep_pj)
                    if endereco_comprador_pj:
                        st.session_state.comprador_end_residencial_comercial_pj = endereco_comprador_pj.get("logradouro", "")
                        st.session_state.comprador_bairro_pj = endereco_comprador_pj.get("bairro", "")
                        st.session_state.comprador_cidade_pj = endereco_comprador_pj.get("localidade", "")
                        st.session_state.comprador_estado_pj = endereco_comprador_pj.get("uf", "")
                        st.success("Endereço do comprador PJ preenchido!")
                    elif error_msg:
                        st.error(error_msg) # Exibe a mensagem de erro específica
                else:
                    st.warning("Por favor, digite um CEP para buscar.")

        with col2:
            comprador_nome_fantasia_pj = st.text_input("Nome Fantasia", key="comprador_nome_fantasia_pj")
            comprador_inscricao_estadual_pj = st.text_input("Inscrição Estadual", key="comprador_inscricao_estadual_pj")
            comprador_fone_comercial_pj = st.text_input("Fone Comercial", key="comprador_fone_comercial_pj")
            comprador_email_pj = st.text_input("E-mail", key="comprador_email_pj")

        comprador_end_residencial_comercial_pj_val = st.text_input("Endereço Residencial/Comercial", value=st.session_state.get("comprador_end_residencial_comercial_pj", ""), key="comprador_end_residencial_comercial_pj_display")
        comprador_numero_pj = st.text_input("Número", key="comprador_numero_pj")
        comprador_bairro_pj_val = st.text_input("Bairro", value=st.session_state.get("comprador_bairro_pj", ""), key="comprador_bairro_pj_display")
        comprador_cidade_pj_val = st.text_input("Cidade", value=st.session_state.get("comprador_cidade_pj", ""), key="comprador_cidade_pj_display")
        comprador_estado_pj_val = st.text_input("Estado", value=st.session_state.get("comprador_estado_pj", ""), key="comprador_estado_pj_display")

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
                    endereco_representante, error_msg = buscar_cep(representante_cep_pj)
                    if endereco_representante:
                        st.session_state.representante_end_residencial_pj = endereco_representante.get("logradouro", "")
                        st.session_state.representante_bairro_pj = endereco_representante.get("bairro", "")
                        st.session_state.representante_cidade_pj = endereco_representante.get("localidade", "")
                        st.session_state.representante_estado_pj = endereco_representante.get("uf", "")
                        st.success("Endereço do representante preenchido!")
                    elif error_msg:
                        st.error(error_msg) # Exibe a mensagem de erro específica
                else:
                    st.warning("Por favor, digite um CEP para buscar.")

        with col2:
            representante_nacionalidade_pj = st.text_input("Nacionalidade Representante", key="representante_nacionalidade_pj")
            representante_email_pj = st.text_input("E-mail Representante", key="representante_email_pj")
            representante_fone_comercial_pj = st.text_input("Fone Comercial Representante", key="representante_fone_comercial_pj")
        
        representante_end_residencial_pj_val = st.text_input("Endereço Residencial Representante", value=st.session_state.get("representante_end_residencial_pj", ""), key="representante_end_residencial_pj_display")
        representante_numero_pj = st.text_input("Número Representante", key="representante_numero_pj")
        representante_bairro_pj_val = st.text_input("Bairro Representante", value=st.session_state.get("representante_bairro_pj", ""), key="representante_bairro_pj_display")
        representante_cidade_pj_val = st.text_input("Cidade Representante", value=st.session_state.get("representante_cidade_pj", ""), key="representante_cidade_pj_display")
        representante_estado_pj_val = st.text_input("Estado Representante", value=st.session_state.get("representante_estado_pj", ""), key="representante_estado_pj_display")

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
                    endereco_conjuge_pj, error_msg = buscar_cep(conjuge_cep_pj)
                    if endereco_conjuge_pj:
                        st.session_state.conjuge_end_residencial_pj = endereco_conjuge_pj.get("logradouro", "")
                        st.session_state.conjuge_bairro_pj = endereco_conjuge_pj.get("bairro", "")
                        st.session_state.conjuge_cidade_pj = endereco_conjuge_pj.get("localidade", "")
                        st.session_state.conjuge_estado_pj = endereco_conjuge_pj.get("uf", "")
                        st.success("Endereço do cônjuge/sócio PJ preenchido!")
                    elif error_msg:
                        st.error(error_msg) # Exibe a mensagem de erro específica
                else:
                    st.warning("Por favor, digite um CEP para buscar.")

        with col2:
            conjuge_nacionalidade_pj = st.text_input("Nacionalidade Cônjuge/Sócio(a) PJ", key="conjuge_nacionalidade_pj")
            conjuge_email_pj = st.text_input("E-mail Cônjuge/Sócio(a) PJ", key="conjuge_email_pj")
            conjuge_fone_comercial_pj = st.text_input("Fone Comercial Cônjuge/Sócio(a) PJ", key="conjuge_fone_comercial_pj")

        conjuge_end_residencial_pj_val = st.text_input("Endereço Residencial Cônjuge/Sócio(a) PJ", value=st.session_state.get("conjuge_end_residencial_pj", ""), key="conjuge_end_residencial_pj_display")
        conjuge_numero_pj = st.text_input("Número Cônjuge/Sócio(a) PJ", key="conjuge_numero_pj")
        conjuge_bairro_pj_val = st.text_input("Bairro Cônjuge/Sócio(a) PJ", value=st.session_state.get("conjuge_bairro_pj", ""), key="conjuge_bairro_pj_display")
        conjuge_cidade_pj_val = st.text_input("Cidade Cônjuge/Sócio(a) PJ", value=st.session_state.get("conjuge_cidade_pj", ""), key="conjuge_cidade_pj_display")
        conjuge_estado_pj_val = st.text_input("Estado Cônjuge/Sócio(a) PJ", value=st.session_state.get("conjuge_estado_pj", ""), key="conjuge_estado_pj_display")

        st.markdown("---")
        st.markdown("**DOCUMENTOS NECESSÁRIOS:**")
        st.markdown("- **DA EMPRESA:** CONTRATO SOCIAL E ALTERAÇÕES, COMPROVANTE DE ENDEREÇO, DECLARAÇÃO DE FATURAMENTO;")
        st.markdown("- **DOS SÓCIOS E SEUS CÔNJUGES:** CNH; RG e CPF, Comprovante do Estado Civil, Comprovante de Endereço, Comprovante de Renda, CND da Prefeitura e Nada Consta do Condomínio ou Associação.")
        st.markdown("---")

        st.write("📌 No caso de Condomínio ou Loteamento Fechado, quando a empresa possuir mais de um(a) sócio(a) não casados entre si e nem conviventes, é necessário indicar qual do(a)(s) sócio(a)(s) será o(a) condômino(a): 📌")
        condomino_indicado_pj = st.text_input("➡️ Indique aqui quem será o(a) condômino(a)", key="condomino_indicado_pj")

        submitted_pj = st.form_submit_button("Gerar Ficha de Pessoa Jurídica")
        if submitted_pj:
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
                "comprador_end_residencial_comercial_pj": comprador_end_residencial_comercial_pj_val.strip(),
                "comprador_numero_pj": comprador_numero_pj.strip(),
                "comprador_bairro_pj": comprador_bairro_pj_val.strip(),
                "comprador_cidade_pj": comprador_cidade_pj_val.strip(),
                "comprador_estado_pj": comprador_estado_pj_val.strip(),
                "comprador_cep_pj": comprador_cep_pj.strip(),
                "representante_nome_pj": representante_nome_pj.strip(),
                "representante_profissao_pj": representante_profissao_pj.strip(),
                "representante_nacionalidade_pj": representante_nacionalidade_pj.strip(),
                "representante_fone_residencial_pj": representante_fone_residencial_pj.strip(),
                "representante_fone_comercial_pj": representante_fone_comercial_pj.strip(),
                "representante_celular_pj": representante_celular_pj.strip(),
                "representante_email_pj": representante_email_pj.strip(),
                "representante_end_residencial_pj": representante_end_residencial_pj_val.strip(),
                "representante_numero_pj": representante_numero_pj.strip(),
                "representante_bairro_pj": representante_bairro_pj_val.strip(),
                "representante_cidade_pj": representante_cidade_pj_val.strip(),
                "representante_estado_pj": representante_estado_pj_val.strip(),
                "representante_cep_pj": representante_cep_pj.strip(),
                "conjuge_nome_pj": conjuge_nome_pj.strip(),
                "conjuge_profissao_pj": conjuge_profissao_pj.strip(),
                "conjuge_nacionalidade_pj": conjuge_nacionalidade_pj.strip(),
                "conjuge_fone_residencial_pj": conjuge_fone_residencial_pj.strip(),
                "conjuge_fone_comercial_pj": conjuge_fone_comercial_pj.strip(),
                "conjuge_celular_pj": conjuge_celular_pj.strip(),
                "conjuge_email_pj": conjuge_email_pj.strip(),
                "conjuge_end_residencial_pj": conjuge_end_residencial_pj_val.strip(),
                "conjuge_numero_pj": conjuge_numero_pj.strip(),
                "conjuge_bairro_pj": conjuge_bairro_pj_val.strip(),
                "conjuge_cidade_pj": conjuge_cidade_pj_val.strip(),
                "conjuge_estado_pj": conjuge_estado_pj_val.strip(),
                "conjuge_cep_pj": conjuge_cep_pj.strip(),
                "condomino_indicado_pj": condomino_indicado_pj.strip(),
            }
            
            pdf_b64_pj = gerar_pdf_pj(dados_pj)
            if pdf_b64_pj:
                href = f'<a href="data:application/pdf;base64,{pdf_b64_pj}" download="Ficha_Cadastral_Pessoa_Juridica.pdf">Clique aqui para baixar a Ficha Cadastral de Pessoa Jurídica</a>'
                st.markdown(href, unsafe_allow_html=True)
