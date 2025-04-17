import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Sistema Imobiliário", layout="wide")

# Dados em memória (em produção, substituir por banco de dados)
if 'compradores' not in st.session_state:
    st.session_state.compradores = pd.DataFrame(columns=[
        'nome', 'cpf', 'rg', 'data_nascimento', 'estado_civil', 'profissao',
        'email', 'telefone', 'cep', 'logradouro', 'numero', 'complemento',
        'bairro', 'cidade', 'estado', 'tipo_imovel', 'localizacao',
        'faixa_preco', 'qtd_quartos', 'qtd_banheiros', 'qtd_vagas',
        'finalidade', 'forma_pagamento', 'data_cadastro'
    ])

if 'vendedores' not in st.session_state:
    st.session_state.vendedores = pd.DataFrame(columns=[
        'nome', 'cpf_cnpj', 'rg', 'data_nascimento', 'email', 'telefone',
        'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade',
        'estado', 'tipo_imovel', 'valor_venda', 'cep_imovel',
        'logradouro_imovel', 'numero_imovel', 'complemento_imovel',
        'bairro_imovel', 'cidade_imovel', 'estado_imovel', 'area_construida',
        'area_total', 'quartos_imovel', 'data_cadastro'
    ])

# Funções auxiliares
def formatar_telefone(telefone):
    if len(telefone) == 11:
        return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
    return telefone

def formatar_cpf(cpf):
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf

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
    
    with st.form("form_comprador"):
        st.subheader("Informações Pessoais")
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome Completo *", key="nome_comprador")
            cpf = st.text_input("CPF *", key="cpf_comprador", 
                              help="Formato: 000.000.000-00")
            rg = st.text_input("RG", key="rg_comprador")
            data_nascimento = st.date_input("Data de Nascimento", 
                                          key="data_nasc_comprador")
        
        with col2:
            estado_civil = st.selectbox("Estado Civil", 
                                       ["", "Solteiro(a)", "Casado(a)", 
                                        "Divorciado(a)", "Viúvo(a)", "Outro"],
                                       key="estado_civil_comprador")
            profissao = st.text_input("Profissão", key="profissao_comprador")
            email = st.text_input("E-mail *", key="email_comprador")
            telefone = st.text_input("Telefone *", key="telefone_comprador",
                                   help="Formato: (00) 00000-0000")
        
        st.subheader("Endereço")
        col1, col2 = st.columns(2)
        
        with col1:
            cep = st.text_input("CEP", key="cep_comprador",
                               help="Formato: 00000-000")
            logradouro = st.text_input("Logradouro", key="logradouro_comprador")
            numero = st.text_input("Número", key="numero_comprador")
        
        with col2:
            complemento = st.text_input("Complemento", key="complemento_comprador")
            bairro = st.text_input("Bairro", key="bairro_comprador")
            cidade = st.text_input("Cidade", key="cidade_comprador")
        
        estado = st.selectbox("Estado", 
                            ["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", 
                             "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", 
                             "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"],
                            key="estado_comprador")
        
        st.subheader("Preferências de Compra")
        col1, col2 = st.columns(2)
        
        with col1:
            tipo_imovel = st.selectbox("Tipo de Imóvel", 
                                      ["", "Casa", "Apartamento", "Terreno", 
                                       "Comercial", "Rural", "Outro"],
                                      key="tipo_imovel_comprador")
            localizacao = st.text_input("Localização Desejada", 
                                      key="localizacao_comprador",
                                      placeholder="Bairro, Cidade, Estado")
            faixa_preco = st.selectbox("Faixa de Preço", 
                                     ["", "Até R$ 100.000", 
                                      "R$ 100.000 a R$ 250.000",
                                      "R$ 250.000 a R$ 500.000",
                                      "R$ 500.000 a R$ 1.000.000",
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
                                         ["", "À Vista", "Financiamento", 
                                          "Consórcio", "Permuta"],
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
                    'data_cadastro': datetime.now()
                }
                
                st.session_state.compradores = st.session_state.compradores.append(
                    novo_comprador, ignore_index=True
                )
                st.success("Comprador cadastrado com sucesso!")

with tab2:
    st.header("Cadastro de Vendedores")
    
    with st.form("form_vendedor"):
        st.subheader("Informações Pessoais do Vendedor")
        col1, col2 = st.columns(2)
        
        with col1:
            nome_vendedor = st.text_input("Nome Completo *", key="nome_vendedor")
            cpf_cnpj = st.text_input("CPF / CNPJ *", key="cpf_cnpj_vendedor")
            rg_vendedor = st.text_input("RG", key="rg_vendedor")
        
        with col2:
            data_nascimento_vendedor = st.date_input("Data de Nascimento", 
                                                   key="data_nasc_vendedor")
            email_vendedor = st.text_input("E-mail *", key="email_vendedor")
            telefone_vendedor = st.text_input("Telefone *", key="telefone_vendedor",
                                            help="Formato: (00) 00000-0000")
        
        st.subheader("Endereço de Correspondência")
        col1, col2 = st.columns(2)
        
        with col1:
            cep_vendedor = st.text_input("CEP", key="cep_vendedor",
                                       help="Formato: 00000-000")
            logradouro_vendedor = st.text_input("Logradouro", key="logradouro_vendedor")
            numero_vendedor = st.text_input("Número", key="numero_vendedor")
        
        with col2:
            complemento_vendedor = st.text_input("Complemento", key="complemento_vendedor")
            bairro_vendedor = st.text_input("Bairro", key="bairro_vendedor")
            cidade_vendedor = st.text_input("Cidade", key="cidade_vendedor")
        
        estado_vendedor = st.selectbox("Estado", 
                                     ["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", 
                                      "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", 
                                      "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"],
                                     key="estado_vendedor")
        
        st.subheader("Informações do Imóvel")
        col1, col2 = st.columns(2)
        
        with col1:
            tipo_imovel_venda = st.selectbox("Tipo de Imóvel *", 
                                            ["", "Casa", "Apartamento", "Terreno", 
                                             "Comercial", "Rural", "Outro"],
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
            cep_imovel = st.text_input("CEP *", key="cep_imovel",
                                     help="Formato: 00000-000")
            logradouro_imovel = st.text_input("Logradouro *", key="logradouro_imovel")
            numero_imovel = st.text_input("Número *", key="numero_imovel")
        
        with col2:
            complemento_imovel = st.text_input("Complemento", key="complemento_imovel")
            bairro_imovel = st.text_input("Bairro *", key="bairro_imovel")
            cidade_imovel = st.text_input("Cidade *", key="cidade_imovel")
        
        estado_imovel = st.selectbox("Estado *", 
                                   ["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", 
                                    "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", 
                                    "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"],
                                   key="estado_imovel")
        
        quartos_imovel = st.selectbox("Número de Quartos", 
                                    ["", "1", "2", "3", "4", "5 ou mais"],
                                    key="quartos_imovel")
        
        submitted = st.form_submit_button("Cadastrar Vendedor")
        
        if submitted:
            if (not nome_vendedor or not cpf_cnpj or not email_vendedor or 
                not telefone_vendedor or not tipo_imovel_venda or not valor_venda or
                not cep_imovel or not logradouro_imovel or not numero_imovel or
                not bairro_imovel or not cidade_imovel or not estado_imovel):
                st.error("Por favor, preencha os campos obrigatórios (*)")
            else:
                novo_vendedor = {
                    'nome': nome_vendedor,
                    'cpf_cnpj': cpf_cnpj,
                    'rg': rg_vendedor,
                    'data_nascimento': data_nascimento_vendedor,
                    'email': email_vendedor,
                    'telefone': telefone_vendedor,
                    'cep': cep_vendedor,
                    'logradouro': logradouro_vendedor,
                    'numero': numero_vendedor,
                    'complemento': complemento_vendedor,
                    'bairro': bairro_vendedor,
                    'cidade': cidade_vendedor,
                    'estado': estado_vendedor,
                    'tipo_imovel': tipo_imovel_venda,
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
                    'data_cadastro': datetime.now()
                }
                
                st.session_state.vendedores = st.session_state.vendedores.append(
                    novo_vendedor, ignore_index=True
                )
                st.success("Vendedor cadastrado com sucesso!")

with tab3:
    st.header("Consulta de Registros")
    
    tipo_consulta = st.radio("Tipo de Consulta", 
                            ["Compradores", "Vendedores"], 
                            horizontal=True)
    
    if tipo_consulta == "Compradores":
        df = st.session_state.compradores
    else:
        df = st.session_state.vendedores
    
    if not df.empty:
        # Filtros
        col1, col2 = st.columns(2)
        
        with col1:
            filtro_nome = st.text_input("Filtrar por nome")
        
        with col2:
            if tipo_consulta == "Compradores":
                filtro_tipo = st.selectbox("Filtrar por tipo de imóvel", 
                                          ["Todos"] + list(df['tipo_imovel'].unique()))
            else:
                filtro_tipo = st.selectbox("Filtrar por tipo de imóvel", 
                                          ["Todos"] + list(df['tipo_imovel'].unique()))
        
        # Aplicar filtros
        if filtro_nome:
            df = df[df['nome'].str.contains(filtro_nome, case=False, na=False)]
        
        if filtro_tipo != "Todos":
            df = df[df['tipo_imovel'] == filtro_tipo]
        
        # Mostrar tabela
        st.dataframe(df)
        
        # Opções de exportação
        st.download_button(
            label="Exportar para CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name=f"{tipo_consulta.lower()}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv'
        )
    else:
        st.warning("Nenhum registro encontrado.")
