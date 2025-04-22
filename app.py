import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
import os

# Configuração da página
st.set_page_config(page_title="Sistema Imobiliário", layout="wide")

# Configuração do banco de dados
DB_NAME = "imobiliaria.db"

def criar_tabelas():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabela de compradores
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS compradores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cpf TEXT NOT NULL,
        rg TEXT,
        data_nascimento TEXT,
        estado_civil TEXT,
        profissao TEXT,
        email TEXT NOT NULL,
        telefone TEXT NOT NULL,
        cep TEXT,
        logradouro TEXT,
        numero TEXT,
        complemento TEXT,
        bairro TEXT,
        cidade TEXT,
        estado TEXT,
        tipo_imovel TEXT,
        localizacao TEXT,
        faixa_preco TEXT,
        qtd_quartos TEXT,
        qtd_banheiros TEXT,
        qtd_vagas TEXT,
        finalidade TEXT,
        forma_pagamento TEXT,
        data_cadastro TEXT
    )
    ''')
    
    # Tabela de vendedores
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vendedores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cpf_cnpj TEXT NOT NULL,
        rg TEXT,
        data_nascimento TEXT,
        email TEXT NOT NULL,
        telefone TEXT NOT NULL,
        cep TEXT,
        logradouro TEXT,
        numero TEXT,
        complemento TEXT,
        bairro TEXT,
        cidade TEXT,
        estado TEXT,
        tipo_imovel TEXT NOT NULL,
        valor_venda REAL NOT NULL,
        cep_imovel TEXT NOT NULL,
        logradouro_imovel TEXT NOT NULL,
        numero_imovel TEXT NOT NULL,
        complemento_imovel TEXT,
        bairro_imovel TEXT NOT NULL,
        cidade_imovel TEXT NOT NULL,
        estado_imovel TEXT NOT NULL,
        area_construida REAL,
        area_total REAL,
        quartos_imovel TEXT,
        data_cadastro TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

# Criar tabelas se não existirem
criar_tabelas()

# Funções auxiliares
def formatar_data_ptbr(data):
    """Formata datetime para string dd/mm/yyyy"""
    if pd.isna(data) or data == "" or data is None:
        return ""
    if isinstance(data, str):
        try:
            # Se já estiver no formato brasileiro, retorna como está
            if re.match(r'\d{2}/\d{2}/\d{4}', data):
                return data
            # Tenta converter de formato ISO (YYYY-MM-DD)
            return datetime.strptime(data, '%Y-%m-%d').strftime('%d/%m/%Y')
        except:
            return data
    return data.strftime('%d/%m/%Y')

def parse_date(date_str):
    """Converte string de data no formato dd/mm/yyyy para objeto date"""
    try:
        return datetime.strptime(date_str, '%d/%m/%Y').date()
    except:
        return None

# Funções de banco de dados
def carregar_compradores():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql('SELECT * FROM compradores', conn)
    conn.close()
    return df

def carregar_vendedores():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql('SELECT * FROM vendedores', conn)
    conn.close()
    return df

def salvar_comprador(comprador):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO compradores (
        nome, cpf, rg, data_nascimento, estado_civil, profissao,
        email, telefone, cep, logradouro, numero, complemento,
        bairro, cidade, estado, tipo_imovel, localizacao,
        faixa_preco, qtd_quartos, qtd_banheiros, qtd_vagas,
        finalidade, forma_pagamento, data_cadastro
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        comprador['nome'], comprador['cpf'], comprador['rg'], comprador['data_nascimento'],
        comprador['estado_civil'], comprador['profissao'], comprador['email'],
        comprador['telefone'], comprador['cep'], comprador['logradouro'],
        comprador['numero'], comprador['complemento'], comprador['bairro'],
        comprador['cidade'], comprador['estado'], comprador['tipo_imovel'],
        comprador['localizacao'], comprador['faixa_preco'], comprador['qtd_quartos'],
        comprador['qtd_banheiros'], comprador['qtd_vagas'], comprador['finalidade'],
        comprador['forma_pagamento'], comprador['data_cadastro']
    ))
    
    conn.commit()
    conn.close()

def salvar_vendedor(vendedor):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO vendedores (
        nome, cpf_cnpj, rg, data_nascimento, email, telefone,
        cep, logradouro, numero, complemento, bairro, cidade,
        estado, tipo_imovel, valor_venda, cep_imovel,
        logradouro_imovel, numero_imovel, complemento_imovel,
        bairro_imovel, cidade_imovel, estado_imovel, area_construida,
        area_total, quartos_imovel, data_cadastro
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        vendedor['nome'], vendedor['cpf_cnpj'], vendedor['rg'], vendedor['data_nascimento'],
        vendedor['email'], vendedor['telefone'], vendedor['cep'], vendedor['logradouro'],
        vendedor['numero'], vendedor['complemento'], vendedor['bairro'], vendedor['cidade'],
        vendedor['estado'], vendedor['tipo_imovel'], vendedor['valor_venda'],
        vendedor['cep_imovel'], vendedor['logradouro_imovel'], vendedor['numero_imovel'],
        vendedor['complemento_imovel'], vendedor['bairro_imovel'], vendedor['cidade_imovel'],
        vendedor['estado_imovel'], vendedor['area_construida'], vendedor['area_total'],
        vendedor['quartos_imovel'], vendedor['data_cadastro']
    ))
    
    conn.commit()
    conn.close()

def atualizar_comprador(id_comprador, novos_dados):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
    UPDATE compradores SET
        nome = ?, cpf = ?, rg = ?, data_nascimento = ?, estado_civil = ?, profissao = ?,
        email = ?, telefone = ?, cep = ?, logradouro = ?, numero = ?, complemento = ?,
        bairro = ?, cidade = ?, estado = ?, tipo_imovel = ?, localizacao = ?,
        faixa_preco = ?, qtd_quartos = ?, qtd_banheiros = ?, qtd_vagas = ?,
        finalidade = ?, forma_pagamento = ?
    WHERE id = ?
    ''', (
        novos_dados['nome'], novos_dados['cpf'], novos_dados['rg'], novos_dados['data_nascimento'],
        novos_dados['estado_civil'], novos_dados['profissao'], novos_dados['email'],
        novos_dados['telefone'], novos_dados['cep'], novos_dados['logradouro'],
        novos_dados['numero'], novos_dados['complemento'], novos_dados['bairro'],
        novos_dados['cidade'], novos_dados['estado'], novos_dados['tipo_imovel'],
        novos_dados['localizacao'], novos_dados['faixa_preco'], novos_dados['qtd_quartos'],
        novos_dados['qtd_banheiros'], novos_dados['qtd_vagas'], novos_dados['finalidade'],
        novos_dados['forma_pagamento'], id_comprador
    ))
    
    conn.commit()
    conn.close()

def atualizar_vendedor(id_vendedor, novos_dados):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
    UPDATE vendedores SET
        nome = ?, cpf_cnpj = ?, rg = ?, data_nascimento = ?, email = ?, telefone = ?,
        cep = ?, logradouro = ?, numero = ?, complemento = ?, bairro = ?, cidade = ?,
        estado = ?, tipo_imovel = ?, valor_venda = ?, cep_imovel = ?,
        logradouro_imovel = ?, numero_imovel = ?, complemento_imovel = ?,
        bairro_imovel = ?, cidade_imovel = ?, estado_imovel = ?, area_construida = ?,
        area_total = ?, quartos_imovel = ?
    WHERE id = ?
    ''', (
        novos_dados['nome'], novos_dados['cpf_cnpj'], novos_dados['rg'], novos_dados['data_nascimento'],
        novos_dados['email'], novos_dados['telefone'], novos_dados['cep'], novos_dados['logradouro'],
        novos_dados['numero'], novos_dados['complemento'], novos_dados['bairro'], novos_dados['cidade'],
        novos_dados['estado'], novos_dados['tipo_imovel'], novos_dados['valor_venda'],
        novos_dados['cep_imovel'], novos_dados['logradouro_imovel'], novos_dados['numero_imovel'],
        novos_dados['complemento_imovel'], novos_dados['bairro_imovel'], novos_dados['cidade_imovel'],
        novos_dados['estado_imovel'], novos_dados['area_construida'], novos_dados['area_total'],
        novos_dados['quartos_imovel'], id_vendedor
    ))
    
    conn.commit()
    conn.close()

def deletar_comprador(id_comprador):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM compradores WHERE id = ?', (id_comprador,))
    
    conn.commit()
    conn.close()

def deletar_vendedor(id_vendedor):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM vendedores WHERE id = ?', (id_vendedor,))
    
    conn.commit()
    conn.close()

# Carregar dados iniciais
if 'compradores' not in st.session_state:
    st.session_state.compradores = carregar_compradores()

if 'vendedores' not in st.session_state:
    st.session_state.vendedores = carregar_vendedores()

# Interface principal
st.title("Sistema de Cadastro Imobiliário")

# Abas
tab1, tab2, tab3 = st.tabs([
    "Cadastro de Compradores", 
    "Cadastro de Vendedores", 
    "Consulta de Registros"
])

with tab1:
    st.header("Cadastro de Compradores")
    
    # Verifica se está em modo de edição
    if 'editando_comprador' in st.session_state:
        with st.form("form_edicao_comprador"):
            st.subheader(f"Editando Comprador: {st.session_state.editando_comprador['nome']}")
            
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome Completo *", value=st.session_state.editando_comprador['nome'])
                cpf = st.text_input("CPF *", value=st.session_state.editando_comprador['cpf'], 
                                  help="Formato: 000.000.000-00")
                rg = st.text_input("RG", value=st.session_state.editando_comprador['rg'])
                data_nascimento = st.text_input("Data de Nascimento (dd/mm/aaaa)", 
                                              value=formatar_data_ptbr(st.session_state.editando_comprador['data_nascimento']))
            
            with col2:
                estado_civil = st.selectbox("Estado Civil", 
                                         ["", "Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)", "Outro"],
                                         index=["", "Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)", "Outro"].index(
                                             st.session_state.editando_comprador['estado_civil']))
                profissao = st.text_input("Profissão", value=st.session_state.editando_comprador['profissao'])
                email = st.text_input("E-mail *", value=st.session_state.editando_comprador['email'])
                telefone = st.text_input("Telefone *", value=st.session_state.editando_comprador['telefone'],
                                       help="Formato: (00) 00000-0000")
            
            st.subheader("Endereço")
            col1, col2 = st.columns(2)
            with col1:
                cep = st.text_input("CEP", value=st.session_state.editando_comprador['cep'],
                                   help="Formato: 00000-000")
                logradouro = st.text_input("Logradouro", value=st.session_state.editando_comprador['logradouro'])
                numero = st.text_input("Número", value=st.session_state.editando_comprador['numero'])
            
            with col2:
                complemento = st.text_input("Complemento", value=st.session_state.editando_comprador['complemento'])
                bairro = st.text_input("Bairro", value=st.session_state.editando_comprador['bairro'])
                cidade = st.text_input("Cidade", value=st.session_state.editando_comprador['cidade'])
            
            estado = st.selectbox("Estado", 
                                ["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", 
                                 "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"],
                                index=["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", 
                                      "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"].index(
                                          st.session_state.editando_comprador['estado']))
            
            st.subheader("Preferências de Compra")
            col1, col2 = st.columns(2)
            with col1:
                tipo_imovel = st.selectbox("Tipo de Imóvel", 
                                         ["", "Casa", "Apartamento", "Terreno", "Comercial", "Rural", "Outro"],
                                         index=["", "Casa", "Apartamento", "Terreno", "Comercial", "Rural", "Outro"].index(
                                             st.session_state.editando_comprador['tipo_imovel']))
                localizacao = st.text_input("Localização Desejada", 
                                         value=st.session_state.editando_comprador['localizacao'],
                                         placeholder="Bairro, Cidade, Estado")
                faixa_preco = st.selectbox("Faixa de Preço", 
                                         ["", "Até R$ 100.000", "R$ 100.000 a R$ 250.000",
                                          "R$ 250.000 a R$ 500.000", "R$ 500.000 a R$ 1.000.000",
                                          "Acima de R$ 1.000.000"],
                                         index=["", "Até R$ 100.000", "R$ 100.000 a R$ 250.000",
                                               "R$ 250.000 a R$ 500.000", "R$ 500.000 a R$ 1.000.000",
                                               "Acima de R$ 1.000.000"].index(
                                                   st.session_state.editando_comprador['faixa_preco']))
            
            with col2:
                qtd_quartos = st.selectbox("Número de Quartos", 
                                         ["", "1", "2", "3", "4", "5 ou mais"],
                                         index=["", "1", "2", "3", "4", "5 ou mais"].index(
                                             st.session_state.editando_comprador['qtd_quartos']))
                qtd_banheiros = st.selectbox("Número de Banheiros", 
                                           ["", "1", "2", "3", "4 ou mais"],
                                           index=["", "1", "2", "3", "4 ou mais"].index(
                                               st.session_state.editando_comprador['qtd_banheiros']))
                qtd_vagas = st.selectbox("Número de Vagas", 
                                       ["", "0", "1", "2", "3 ou mais"],
                                       index=["", "0", "1", "2", "3 ou mais"].index(
                                           st.session_state.editando_comprador['qtd_vagas']))
            
            col1, col2 = st.columns(2)
            with col1:
                finalidade = st.selectbox("Finalidade", 
                                        ["", "Residencial", "Investimento", "Comercial"],
                                        index=["", "Residencial", "Investimento", "Comercial"].index(
                                            st.session_state.editando_comprador['finalidade']))
            with col2:
                forma_pagamento = st.selectbox("Forma de Pagamento", 
                                             ["", "À Vista", "Financiamento", "Consórcio", "Permuta"],
                                             index=["", "À Vista", "Financiamento", "Consórcio", "Permuta"].index(
                                                 st.session_state.editando_comprador['forma_pagamento']))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.form_submit_button("Salvar Alterações"):
                    dados_atualizados = {
                        'nome': nome,
                        'cpf': cpf,
                        'rg': rg,
                        'data_nascimento': data_nascimento,
                        'estado_civil': estado_civil,
                        'profissao': profissao,
                        'email': email,
                        'telefone': telefone,
                        'cep': cep,
                        'logradouro': logradouro,
                        'numero': numero,
                        'complemento': complemento,
                        'bairro': bairro,
                        'cidade': cidade,
                        'estado': estado,
                        'tipo_imovel': tipo_imovel,
                        'localizacao': localizacao,
                        'faixa_preco': faixa_preco,
                        'qtd_quartos': qtd_quartos,
                        'qtd_banheiros': qtd_banheiros,
                        'qtd_vagas': qtd_vagas,
                        'finalidade': finalidade,
                        'forma_pagamento': forma_pagamento
                    }
                    atualizar_comprador(st.session_state.id_edicao, dados_atualizados)
                    st.session_state.compradores = carregar_compradores()
                    del st.session_state.editando_comprador
                    del st.session_state.id_edicao
                    st.success("Comprador atualizado com sucesso!")
                    st.rerun()
            
            with col2:
                if st.form_submit_button("Cancelar Edição"):
                    del st.session_state.editando_comprador
                    del st.session_state.id_edicao
                    st.rerun()
            
            with col3:
                if st.form_submit_button("Excluir Comprador"):
                    deletar_comprador(st.session_state.id_edicao)
                    st.session_state.compradores = carregar_compradores()
                    del st.session_state.editando_comprador
                    del st.session_state.id_edicao
                    st.success("Comprador removido com sucesso!")
                    st.rerun()
    
    else:
        with st.form("form_comprador"):
            st.subheader("Informações Pessoais")
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome Completo *", key="nome_comprador")
                cpf = st.text_input("CPF *", key="cpf_comprador", help="Formato: 000.000.000-00")
                rg = st.text_input("RG", key="rg_comprador")
                data_nascimento = st.text_input("Data de Nascimento (dd/mm/aaaa)", key="data_nasc_comprador")
            
            with col2:
                estado_civil = st.selectbox("Estado Civil", 
                                          ["", "Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)", "Outro"],
                                          key="estado_civil_comprador")
                profissao = st.text_input("Profissão", key="profissao_comprador")
                email = st.text_input("E-mail *", key="email_comprador")
                telefone = st.text_input("Telefone *", key="telefone_comprador", help="Formato: (00) 00000-0000")
            
            st.subheader("Endereço")
            col1, col2 = st.columns(2)
            with col1:
                cep = st.text_input("CEP", key="cep_comprador", help="Formato: 00000-000")
                logradouro = st.text_input("Logradouro", key="logradouro_comprador")
                numero = st.text_input("Número", key="numero_comprador")
            
            with col2:
                complemento = st.text_input("Complemento", key="complemento_comprador")
                bairro = st.text_input("Bairro", key="bairro_comprador")
                cidade = st.text_input("Cidade", key="cidade_comprador")
            
            estado = st.selectbox("Estado", 
                                ["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", 
                                 "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"],
                                key="estado_comprador")
            
            st.subheader("Preferências de Compra")
            col1, col2 = st.columns(2)
            with col1:
                tipo_imovel = st.selectbox("Tipo de Imóvel", 
                                          ["", "Casa", "Apartamento", "Terreno", "Comercial", "Rural", "Outro"],
                                          key="tipo_imovel_comprador")
                localizacao = st.text_input("Localização Desejada", 
                                          key="localizacao_comprador",
                                          placeholder="Bairro, Cidade, Estado")
                faixa_preco = st.selectbox("Faixa de Preço", 
                                         ["", "Até R$ 100.000", "R$ 100.000 a R$ 250.000",
                                          "R$ 250.000 a R$ 500.000", "R$ 500.000 a R$ 1.000.000",
                                          "Acima de R$ 1.000.000"],
                                         key="faixa_preco_comprador")
            
            with col2:
                qtd_quartos = st.selectbox("Número de Quartos", 
                                         ["", "1", "2", "3", "4", "5 ou mais"],
                                         key="qtd_quartos_comprador")
                qtd_banheiros = st.selectbox("Número de Banheiros", 
                                           ["", "1", "2", "3", "4 ou mais"],
                                           key="qtd_banheiros_comprador")
                qtd_vagas = st.selectbox("Número de Vagas", 
                                       ["", "0", "1", "2", "3 ou mais"],
                                       key="qtd_vagas_comprador")
            
            col1, col2 = st.columns(2)
            with col1:
                finalidade = st.selectbox("Finalidade", 
                                        ["", "Residencial", "Investimento", "Comercial"],
                                        key="finalidade_comprador")
            with col2:
                forma_pagamento = st.selectbox("Forma de Pagamento", 
                                             ["", "À Vista", "Financiamento", "Consórcio", "Permuta"],
                                             key="forma_pagamento_comprador")
            
            submitted = st.form_submit_button("Cadastrar Comprador")
            
            if submitted:
                if not nome or not cpf or not email or not telefone:
                    st.error("Por favor, preencha os campos obrigatórios (*)")
                else:
                    novo_comprador = {
                        'nome': nome,
                        'cpf': cpf,
                        'rg': rg,
                        'data_nascimento': data_nascimento,
                        'estado_civil': estado_civil,
                        'profissao': profissao,
                        'email': email,
                        'telefone': telefone,
                        'cep': cep,
                        'logradouro': logradouro,
                        'numero': numero,
                        'complemento': complemento,
                        'bairro': bairro,
                        'cidade': cidade,
                        'estado': estado,
                        'tipo_imovel': tipo_imovel,
                        'localizacao': localizacao,
                        'faixa_preco': faixa_preco,
                        'qtd_quartos': qtd_quartos,
                        'qtd_banheiros': qtd_banheiros,
                        'qtd_vagas': qtd_vagas,
                        'finalidade': finalidade,
                        'forma_pagamento': forma_pagamento,
                        'data_cadastro': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                    }
                    
                    salvar_comprador(novo_comprador)
                    st.session_state.compradores = carregar_compradores()
                    st.success("Comprador cadastrado com sucesso!")

with tab2:
    st.header("Cadastro de Vendedores")
    
    # Verifica se está em modo de edição
    if 'editando_vendedor' in st.session_state:
        with st.form("form_edicao_vendedor"):
            st.subheader(f"Editando Vendedor: {st.session_state.editando_vendedor['nome']}")
            
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome Completo *", value=st.session_state.editando_vendedor['nome'])
                cpf_cnpj = st.text_input("CPF / CNPJ *", value=st.session_state.editando_vendedor['cpf_cnpj'])
                rg = st.text_input("RG", value=st.session_state.editando_vendedor['rg'])
            
            with col2:
                data_nascimento = st.text_input("Data de Nascimento (dd/mm/aaaa)", 
                                              value=formatar_data_ptbr(st.session_state.editando_vendedor['data_nascimento']))
                email = st.text_input("E-mail *", value=st.session_state.editando_vendedor['email'])
                telefone = st.text_input("Telefone *", value=st.session_state.editando_vendedor['telefone'],
                                        help="Formato: (00) 00000-0000")
            
            st.subheader("Endereço de Correspondência")
            col1, col2 = st.columns(2)
            with col1:
                cep = st.text_input("CEP", value=st.session_state.editando_vendedor['cep'],
                                   help="Formato: 00000-000")
                logradouro = st.text_input("Logradouro", value=st.session_state.editando_vendedor['logradouro'])
                numero = st.text_input("Número", value=st.session_state.editando_vendedor['numero'])
            
            with col2:
                complemento = st.text_input("Complemento", value=st.session_state.editando_vendedor['complemento'])
                bairro = st.text_input("Bairro", value=st.session_state.editando_vendedor['bairro'])
                cidade = st.text_input("Cidade", value=st.session_state.editando_vendedor['cidade'])
            
            estado = st.selectbox("Estado", 
                                ["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", 
                                 "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"],
                                index=["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", 
                                      "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"].index(
                                          st.session_state.editando_vendedor['estado']))
            
            st.subheader("Informações do Imóvel")
            col1, col2 = st.columns(2)
            with col1:
                tipo_imovel = st.selectbox("Tipo de Imóvel *", 
                                         ["", "Casa", "Apartamento", "Terreno", "Comercial", "Rural", "Outro"],
                                         index=["", "Casa", "Apartamento", "Terreno", "Comercial", "Rural", "Outro"].index(
                                             st.session_state.editando_vendedor['tipo_imovel']))
                valor_venda = st.number_input("Valor de Venda (R$) *", 
                                            min_value=0.0, step=0.01,
                                            value=float(st.session_state.editando_vendedor['valor_venda']))
            
            with col2:
                area_construida = st.number_input("Área Construída (m²)", 
                                               min_value=0.0, step=0.01,
                                               value=float(st.session_state.editando_vendedor['area_construida']) 
                                               if pd.notna(st.session_state.editando_vendedor['area_construida']) else None)
                area_total = st.number_input("Área Total (m²)", 
                                           min_value=0.0, step=0.01,
                                           value=float(st.session_state.editando_vendedor['area_total']) 
                                           if pd.notna(st.session_state.editando_vendedor['area_total']) else None)
            
            st.subheader("Endereço do Imóvel")
            col1, col2 = st.columns(2)
            with col1:
                cep_imovel = st.text_input("CEP *", value=st.session_state.editando_vendedor['cep_imovel'],
                                          help="Formato: 00000-000")
                logradouro_imovel = st.text_input("Logradouro *", value=st.session_state.editando_vendedor['logradouro_imovel'])
                numero_imovel = st.text_input("Número *", value=st.session_state.editando_vendedor['numero_imovel'])
            
            with col2:
                complemento_imovel = st.text_input("Complemento", value=st.session_state.editando_vendedor['complemento_imovel'])
                bairro_imovel = st.text_input("Bairro *", value=st.session_state.editando_vendedor['bairro_imovel'])
                cidade_imovel = st.text_input("Cidade *", value=st.session_state.editando_vendedor['cidade_imovel'])
            
            estado_imovel = st.selectbox("Estado *", 
                                       ["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", 
                                        "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"],
                                       index=["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", 
                                             "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"].index(
                                                 st.session_state.editando_vendedor['estado_imovel']))
            
            quartos_imovel = st.selectbox("Número de Quartos", 
                                        ["", "1", "2", "3", "4", "5 ou mais"],
                                        index=["", "1", "2", "3", "4", "5 ou mais"].index(
                                            st.session_state.editando_vendedor['quartos_imovel']))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.form_submit_button("Salvar Alterações"):
                    dados_atualizados = {
                        'nome': nome,
                        'cpf_cnpj': cpf_cnpj,
                        'rg': rg,
                        'data_nascimento': data_nascimento,
                        'email': email,
                        'telefone': telefone,
                        'cep': cep,
                        'logradouro': logradouro,
                        'numero': numero,
                        'complemento': complemento,
                        'bairro': bairro,
                        'cidade': cidade,
                        'estado': estado,
                        'tipo_imovel': tipo_imovel,
                        'valor_venda': valor_venda,
                        'cep_imovel': cep_imovel,
                        'logradouro_imovel': logradouro_imovel,
                        'numero_imovel': numero_imovel,
                        'complemento_imovel': complemento_imovel,
                        'bairro_imovel': bairro_imovel,
                        'cidade_imovel': cidade_imovel,
                        'estado_imovel': estado_imovel,
                        'area_construida': area_construida,
                        'area_total': area_total,
                        'quartos_imovel': quartos_imovel
                    }
                    atualizar_vendedor(st.session_state.id_edicao, dados_atualizados)
                    st.session_state.vendedores = carregar_vendedores()
                    del st.session_state.editando_vendedor
                    del st.session_state.id_edicao
                    st.success("Vendedor atualizado com sucesso!")
                    st.rerun()
            
            with col2:
                if st.form_submit_button("Cancelar Edição"):
                    del st.session_state.editando_vendedor
                    del st.session_state.id_edicao
                    st.rerun()
            
            with col3:
                if st.form_submit_button("Excluir Vendedor"):
                    deletar_vendedor(st.session_state.id_edicao)
                    st.session_state.vendedores = carregar_vendedores()
                    del st.session_state.editando_vendedor
                    del st.session_state.id_edicao
                    st.success("Vendedor removido com sucesso!")
                    st.rerun()
    
    else:
        with st.form("form_vendedor"):
            st.subheader("Informações Pessoais do Vendedor")
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome Completo *", key="nome_vendedor")
                cpf_cnpj = st.text_input("CPF / CNPJ *", key="cpf_cnpj_vendedor")
                rg = st.text_input("RG", key="rg_vendedor")
            
            with col2:
                data_nascimento = st.text_input("Data de Nascimento (dd/mm/aaaa)", key="data_nasc_vendedor")
                email = st.text_input("E-mail *", key="email_vendedor")
                telefone = st.text_input("Telefone *", key="telefone_vendedor", help="Formato: (00) 00000-0000")
            
            st.subheader("Endereço de Correspondência")
            col1, col2 = st.columns(2)
            with col1:
                cep = st.text_input("CEP", key="cep_vendedor", help="Formato: 00000-000")
                logradouro = st.text_input("Logradouro", key="logradouro_vendedor")
                numero = st.text_input("Número", key="numero_vendedor")
            
            with col2:
                complemento = st.text_input("Complemento", key="complemento_vendedor")
                bairro = st.text_input("Bairro", key="bairro_vendedor")
                cidade = st.text_input("Cidade", key="cidade_vendedor")
            
            estado = st.selectbox("Estado", 
                                ["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", 
                                 "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"],
                                key="estado_vendedor")
            
            st.subheader("Informações do Imóvel")
            col1, col2 = st.columns(2)
            with col1:
                tipo_imovel = st.selectbox("Tipo de Imóvel *", 
                                         ["", "Casa", "Apartamento", "Terreno", "Comercial", "Rural", "Outro"],
                                         key="tipo_imovel_venda")
                valor_venda = st.number_input("Valor de Venda (R$) *", 
                                            min_value=0.0, step=0.01,
                                            key="valor_venda")
            
            with col2:
                area_construida = st.number_input("Área Construída (m²)", 
                                               min_value=0.0, step=0.01,
                                               key="area_construida")
                area_total = st.number_input("Área Total (m²)", 
                                           min_value=0.0, step=0.01,
                                           key="area_total")
            
            st.subheader("Endereço do Imóvel")
            col1, col2 = st.columns(2)
            with col1:
                cep_imovel = st.text_input("CEP *", key="cep_imovel", help="Formato: 00000-000")
                logradouro_imovel = st.text_input("Logradouro *", key="logradouro_imovel")
                numero_imovel = st.text_input("Número *", key="numero_imovel")
            
            with col2:
                complemento_imovel = st.text_input("Complemento", key="complemento_imovel")
                bairro_imovel = st.text_input("Bairro *", key="bairro_imovel")
                cidade_imovel = st.text_input("Cidade *", key="cidade_imovel")
            
            estado_imovel = st.selectbox("Estado *", 
                                       ["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", 
                                        "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"],
                                       key="estado_imovel")
            
            quartos_imovel = st.selectbox("Número de Quartos", 
                                        ["", "1", "2", "3", "4", "5 ou mais"],
                                        key="quartos_imovel")
            
            submitted = st.form_submit_button("Cadastrar Vendedor")
            
            if submitted:
                if (not nome or not cpf_cnpj or not email or not telefone or not tipo_imovel or 
                    not valor_venda or not cep_imovel or not logradouro_imovel or not numero_imovel or
                    not bairro_imovel or not cidade_imovel or not estado_imovel):
                    st.error("Por favor, preencha os campos obrigatórios (*)")
                else:
                    novo_vendedor = {
                        'nome': nome,
                        'cpf_cnpj': cpf_cnpj,
                        'rg': rg,
                        'data_nascimento': data_nascimento,
                        'email': email,
                        'telefone': telefone,
                        'cep': cep,
                        'logradouro': logradouro,
                        'numero': numero,
                        'complemento': complemento,
                        'bairro': bairro,
                        'cidade': cidade,
                        'estado': estado,
                        'tipo_imovel': tipo_imovel,
                        'valor_venda': valor_venda,
                        'cep_imovel': cep_imovel,
                        'logradouro_imovel': logradouro_imovel,
                        'numero_imovel': numero_imovel,
                        'complemento_imovel': complemento_imovel,
                        'bairro_imovel': bairro_imovel,
                        'cidade_imovel': cidade_imovel,
                        'estado_imovel': estado_imovel,
                        'area_construida': area_construida,
                        'area_total': area_total,
                        'quartos_imovel': quartos_imovel,
                        'data_cadastro': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                    }
                    
                    salvar_vendedor(novo_vendedor)
                    st.session_state.vendedores = carregar_vendedores()
                    st.success("Vendedor cadastrado com sucesso!")

with tab3:
    st.header("Consulta de Registros")
    
    tipo_consulta = st.radio("Tipo de Consulta", 
                            ["Compradores", "Vendedores"], 
                            horizontal=True)
    
    if tipo_consulta == "Compradores":
        df = st.session_state.compradores.copy()
    else:
        df = st.session_state.vendedores.copy()
    
    if not df.empty:
        # Filtros
        col1, col2 = st.columns(2)
        
        with col1:
            filtro_nome = st.text_input("Filtrar por nome")
        
        with col2:
            filtro_tipo = st.selectbox("Filtrar por tipo de imóvel", 
                                     ["Todos"] + list(df['tipo_imovel'].dropna().unique()))
        
        # Aplicar filtros
        if filtro_nome:
            df = df[df['nome'].str.contains(filtro_nome, case=False, na=False)]
        
        if filtro_tipo != "Todos":
            df = df[df['tipo_imovel'] == filtro_tipo]
        
        # Formatar datas antes de exibir
        df_formatado = df.copy()
        for col in df_formatado.columns:
            if 'data' in col.lower():
                df_formatado[col] = df_formatado[col].apply(formatar_data_ptbr)
        
        # Mostrar tabela
        st.dataframe(df_formatado)
        
        # Seleção de registro para edição/exclusão
        if not df.empty:
            registros = df.to_dict('records')
            options = [f"{i+1} - {r['nome']} ({r.get('cpf', r.get('cpf_cnpj', ''))})" 
                      for i, r in enumerate(registros)]
            
            selected = st.selectbox("Selecione um registro para ação:", ["Selecione..."] + options)
            
            if selected != "Selecione...":
                index_selected = options.index(selected)
                registro_selecionado = registros[index_selected]
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Editar Registro"):
                        if tipo_consulta == "Compradores":
                            st.session_state.editando_comprador = registro_selecionado
                        else:
                            st.session_state.editando_vendedor = registro_selecionado
                        st.session_state.id_edicao = registro_selecionado['id']
                        st.rerun()
                
                with col2:
                    if st.button("Excluir Registro"):
                        if tipo_consulta == "Compradores":
                            deletar_comprador(registro_selecionado['id'])
                            st.session_state.compradores = carregar_compradores()
                        else:
                            deletar_vendedor(registro_selecionado['id'])
                            st.session_state.vendedores = carregar_vendedores()
                        st.success("Registro removido com sucesso!")
                        st.rerun()
        
        # Opções de exportação
        st.download_button(
            label="Exportar para CSV",
            data=df_formatado.to_csv(index=False, sep=';').encode('utf-8'),
            file_name=f"{tipo_consulta.lower()}_{datetime.now().strftime('%d%m%Y')}.csv",
            mime='text/csv'
        )
    else:
        st.warning("Nenhum registro encontrado.")
