import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
import re
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# --- Configuração da página ---
st.set_page_config(page_title="Sistema Imobiliário", layout="wide")

# --- Configuração do banco de dados ---
DB_NAME = "imobiliaria.db"

def criar_tabelas():
    """Cria as tabelas no banco de dados SQLite se elas não existirem."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Tabela de compradores (Pessoa Física) - Baseada em 'Ficha Cadastral Cessão Pessoa Física.docx'
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS compradores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        empreendimento TEXT,
        qd TEXT,
        lt TEXT,
        ativo INTEGER, -- Alterado de BOOLEAN para INTEGER
        quitado INTEGER, -- Alterado de BOOLEAN para INTEGER
        corretor TEXT,
        imobiliaria TEXT,
        # COMPRADOR(A)
        nome_comprador TEXT NOT NULL,
        profissao_comprador TEXT,
        nacionalidade_comprador TEXT,
        fone_resid_comprador TEXT,
        fone_com_comprador TEXT,
        celular_comprador TEXT,
        email_comprador TEXT NOT NULL,
        end_residencial_comprador TEXT,
        bairro_comprador TEXT,
        cidade_comprador TEXT,
        estado_comprador TEXT,
        cep_comprador TEXT,
        estado_civil_comprador TEXT,
        data_casamento_comprador TEXT,
        regime_casamento_comprador TEXT,
        condicao_convivencia_comprador INTEGER, -- Alterado de BOOLEAN para INTEGER
        # CÔNJUGE/SÓCIO(A)
        nome_conjuge TEXT,
        profissao_conjuge TEXT,
        nacionalidade_conjuge TEXT,
        fone_resid_conjuge TEXT,
        fone_com_conjuge TEXT,
        celular_conjuge TEXT,
        email_conjuge TEXT,
        end_residencial_conjuge TEXT,
        bairro_conjuge TEXT,
        cidade_conjuge TEXT,
        estado_conjuge TEXT,
        cep_conjuge TEXT,
        cpf_conjuge TEXT,
        data_nascimento_conjuge TEXT,
        # Documentos Necessários (simplificado para texto, pode ser mais detalhado)
        documentos_necessarios TEXT,
        # Condomínio/Loteamento Fechado
        condomino_indicado TEXT,
        # Dados de cadastro
        data_cadastro TEXT
    )
    ''')

    # Tabela de vendedores (Pessoa Jurídica) - Baseada em 'Ficha Cadastral_Cessão_Pessoa Jurídica.docx'
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vendedores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        empreendimento TEXT,
        qd TEXT,
        lt TEXT,
        ativo INTEGER, -- Alterado de BOOLEAN para INTEGER
        quitado INTEGER, -- Alterado de BOOLEAN para INTEGER
        corretor TEXT,
        imobiliaria TEXT,
        # COMPRADOR(A) (neste caso, a empresa que está cedendo/transferindo)
        nome_comprador_pj TEXT NOT NULL, # Nome da empresa
        fone_resid_comprador_pj TEXT,
        fone_com_comprador_pj TEXT,
        celular_comprador_pj TEXT,
        email_comprador_pj TEXT NOT NULL,
        end_residencial_comercial_pj TEXT,
        bairro_comprador_pj TEXT,
        cidade_comprador_pj TEXT,
        estado_comprador_pj TEXT,
        cep_comprador_pj TEXT,
        # REPRESENTANTE
        nome_representante TEXT,
        profissao_representante TEXT,
        nacionalidade_representante TEXT,
        fone_resid_representante TEXT,
        fone_com_representante TEXT,
        celular_representante TEXT,
        email_representante TEXT,
        end_residencial_representante TEXT,
        bairro_representante TEXT,
        cidade_representante TEXT,
        estado_representante TEXT,
        cep_representante TEXT,
        # CÔNJUGE/SÓCIO(A)
        nome_socio TEXT,
        cpf_socio TEXT,
        data_nascimento_socio TEXT,
        profissao_socio TEXT,
        nacionalidade_socio TEXT,
        fone_resid_socio TEXT,
        fone_com_socio TEXT,
        celular_socio TEXT,
        email_socio TEXT,
        end_residencial_socio TEXT,
        bairro_socio TEXT,
        cidade_socio TEXT,
        estado_socio TEXT,
        cep_socio TEXT,
        # Documentos Necessários (simplificado para texto)
        documentos_empresa TEXT,
        documentos_socios TEXT,
        # Condomínio/Loteamento Fechado
        condomino_indicado_pj TEXT,
        # Dados de cadastro
        data_cadastro TEXT
    )
    ''')

    # Tabela para Dependentes - para ligar a Compradores ou Vendedores (Pessoa Física ou Jurídica)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS dependentes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_titular INTEGER NOT NULL,
        tipo_titular TEXT NOT NULL, -- 'comprador' ou 'vendedor'
        nome TEXT NOT NULL,
        cpf TEXT,
        email TEXT,
        fone_com TEXT,
        celular TEXT,
        fone_recado TEXT,
        grau_parentesco TEXT
    )
    ''')

    conn.commit()
    conn.close()

# Criar tabelas se não existirem
criar_tabelas()

# --- Funções auxiliares ---
def formatar_data_ptbr(data):
    """Formata datetime ou string YYYY-MM-DD para string dd/mm/yyyy."""
    if pd.isna(data) or data == "" or data is None:
        return ""
    if isinstance(data, str):
        # Se já estiver no formato brasileiro, retorna como está
        if re.match(r'\d{2}/\d{2}/\d{4}', data):
            return data
        try:
            # Tenta converter de formato ISO (YYYY-MM-DD)
            return datetime.strptime(data, '%Y-%m-%d').strftime('%d/%m/%Y')
        except ValueError:
            return data # Retorna a string original se não puder converter
    return data.strftime('%d/%m/%Y')

def parse_data_para_db(data_str):
    """Converte string de data no formato dd/mm/yyyy para YYYY-MM-DD para o banco de dados."""
    if not data_str:
        return None
    try:
        return datetime.strptime(data_str, '%d/%m/%Y').strftime('%Y-%m-%d')
    except ValueError:
        return data_str # Retorna a string original se for inválida ou já no formato ISO

# --- Funções de banco de dados ---
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

def carregar_dependentes(id_titular, tipo_titular):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql(f"SELECT * FROM dependentes WHERE id_titular = ? AND tipo_titular = ?", conn, params=(id_titular, tipo_titular))
    conn.close()
    return df

def salvar_comprador(comprador_data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO compradores (
        empreendimento, qd, lt, ativo, quitado, corretor, imobiliaria,
        nome_comprador, profissao_comprador, nacionalidade_comprador, fone_resid_comprador,
        fone_com_comprador, celular_comprador, email_comprador, end_residencial_comprador,
        bairro_comprador, cidade_comprador, estado_comprador, cep_comprador,
        estado_civil_comprador, data_casamento_comprador, regime_casamento_comprador,
        condicao_convivencia_comprador, nome_conjuge, profissao_conjuge,
        nacionalidade_conjuge, fone_resid_conjuge, fone_com_conjuge, celular_conjuge,
        email_conjuge, end_residencial_conjuge, bairro_conjuge, cidade_conjuge,
        estado_conjuge, cep_conjuge, cpf_conjuge, data_nascimento_conjuge,
        documentos_necessarios, condomino_indicado, data_cadastro
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        comprador_data['empreendimento'], comprador_data['qd'], comprador_data['lt'],
        comprador_data['ativo'], comprador_data['quitado'], comprador_data['corretor'],
        comprador_data['imobiliaria'], comprador_data['nome_comprador'],
        comprador_data['profissao_comprador'], comprador_data['nacionalidade_comprador'],
        comprador_data['fone_resid_comprador'], comprador_data['fone_com_comprador'],
        comprador_data['celular_comprador'], comprador_data['email_comprador'],
        comprador_data['end_residencial_comprador'], comprador_data['bairro_comprador'],
        comprador_data['cidade_comprador'], comprador_data['estado_comprador'],
        comprador_data['cep_comprador'], comprador_data['estado_civil_comprador'],
        parse_data_para_db(comprador_data['data_casamento_comprador']),
        comprador_data['regime_casamento_comprador'], comprador_data['condicao_convivencia_comprador'],
        comprador_data['nome_conjuge'], comprador_data['profissao_conjuge'],
        comprador_data['nacionalidade_conjuge'], comprador_data['fone_resid_conjuge'],
        comprador_data['fone_com_conjuge'], comprador_data['celular_conjuge'],
        comprador_data['email_conjuge'], comprador_data['end_residencial_conjuge'],
        comprador_data['bairro_conjuge'], comprador_data['cidade_conjuge'],
        comprador_data['estado_conjuge'], comprador_data['cep_conjuge'],
        comprador_data['cpf_conjuge'], parse_data_para_db(comprador_data['data_nascimento_conjuge']),
        comprador_data['documentos_necessarios'], comprador_data['condomino_indicado'],
        comprador_data['data_cadastro']
    ))
    comprador_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return comprador_id

def salvar_vendedor(vendedor_data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO vendedores (
        empreendimento, qd, lt, ativo, quitado, corretor, imobiliaria,
        nome_comprador_pj, fone_resid_comprador_pj, fone_com_comprador_pj,
        celular_comprador_pj, email_comprador_pj, end_residencial_comercial_pj,
        bairro_comprador_pj, cidade_comprador_pj, estado_comprador_pj,
        cep_comprador_pj, nome_representante, profissao_representante,
        nacionalidade_representante, fone_resid_representante, fone_com_representante,
        celular_representante, email_representante, end_residencial_representante,
        bairro_representante, cidade_representante, estado_representante,
        cep_representante, nome_socio, cpf_socio, data_nascimento_socio,
        profissao_socio, nacionalidade_socio, fone_resid_socio, fone_com_socio,
        celular_socio, email_socio, end_residencial_socio, bairro_socio,
        cidade_socio, estado_socio, cep_socio, documentos_empresa,
        documentos_socios, condomino_indicado_pj, data_cadastro
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        vendedor_data['empreendimento'], vendedor_data['qd'], vendedor_data['lt'],
        vendedor_data['ativo'], vendedor_data['quitado'], vendedor_data['corretor'],
        vendedor_data['imobiliaria'], vendedor_data['nome_comprador_pj'],
        vendedor_data['fone_resid_comprador_pj'], vendedor_data['fone_com_comprador_pj'],
        vendedor_data['celular_comprador_pj'], vendedor_data['email_comprador_pj'],
        vendedor_data['end_residencial_comercial_pj'], vendedor_data['bairro_comprador_pj'],
        vendedor_data['cidade_comprador_pj'], vendedor_data['estado_comprador_pj'],
        vendedor_data['cep_comprador_pj'], vendedor_data['nome_representante'],
        vendedor_data['profissao_representante'], vendedor_data['nacionalidade_representante'],
        vendedor_data['fone_resid_representante'], vendedor_data['fone_com_representante'],
        vendedor_data['celular_representante'], vendedor_data['email_representante'],
        vendedor_data['end_residencial_representante'], vendedor_data['bairro_representante'],
        vendedor_data['cidade_representante'], vendedor_data['estado_representante'],
        vendedor_data['cep_representante'], vendedor_data['nome_socio'],
        vendedor_data['cpf_socio'], parse_data_para_db(vendedor_data['data_nascimento_socio']),
        vendedor_data['profissao_socio'], vendedor_data['nacionalidade_socio'],
        vendedor_data['fone_resid_socio'], vendedor_data['fone_com_socio'],
        vendedor_data['celular_socio'], vendedor_data['email_socio'],
        vendedor_data['end_residencial_socio'], vendedor_data['bairro_socio'],
        vendedor_data['cidade_socio'], vendedor_data['estado_socio'],
        vendedor_data['cep_socio'], vendedor_data['documentos_empresa'],
        vendedor_data['documentos_socios'], vendedor_data['condomino_indicado_pj'],
        vendedor_data['data_cadastro']
    ))
    vendedor_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return vendedor_id

def salvar_dependente(dependente_data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO dependentes (
        id_titular, tipo_titular, nome, cpf, email, fone_com, celular, fone_recado, grau_parentesco
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        dependente_data['id_titular'], dependente_data['tipo_titular'], dependente_data['nome'],
        dependente_data['cpf'], dependente_data['email'], dependente_data['fone_com'],
        dependente_data['celular'], dependente_data['fone_recado'], dependente_data['grau_parentesco']
    ))
    conn.commit()
    conn.close()

def atualizar_comprador(id_comprador, novos_dados):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE compradores SET
        empreendimento = ?, qd = ?, lt = ?, ativo = ?, quitado = ?, corretor = ?, imobiliaria = ?,
        nome_comprador = ?, profissao_comprador = ?, nacionalidade_comprador = ?, fone_resid_comprador = ?,
        fone_com_comprador = ?, celular_comprador = ?, email_comprador = ?, end_residencial_comprador = ?,
        bairro_comprador = ?, cidade_comprador = ?, estado_comprador = ?, cep_comprador = ?,
        estado_civil_comprador = ?, data_casamento_comprador = ?, regime_casamento_comprador = ?,
        condicao_convivencia_comprador = ?, nome_conjuge = ?, profissao_conjuge = ?,
        nacionalidade_conjuge = ?, fone_resid_conjuge = ?, fone_com_conjuge = ?, celular_conjuge = ?,
        email_conjuge = ?, end_residencial_conjuge = ?, bairro_conjuge = ?, cidade_conjuge = ?,
        estado_conjuge = ?, cep_conjuge = ?, cpf_conjuge = ?, data_nascimento_conjuge = ?,
        documentos_necessarios = ?, condomino_indicado = ?
    WHERE id = ?
    ''', (
        novos_dados['empreendimento'], novos_dados['qd'], novos_dados['lt'],
        novos_dados['ativo'], novos_dados['quitado'], novos_dados['corretor'],
        novos_dados['imobiliaria'], novos_dados['nome_comprador'],
        novos_dados['profissao_comprador'], novos_dados['nacionalidade_comprador'],
        novos_dados['fone_resid_comprador'], novos_dados['fone_com_comprador'],
        novos_dados['celular_comprador'], novos_dados['email_comprador'],
        novos_dados['end_residencial_comprador'], novos_dados['bairro_comprador'],
        novos_dados['cidade_comprador'], novos_dados['estado_comprador'],
        novos_dados['cep_comprador'], novos_dados['estado_civil_comprador'],
        parse_data_para_db(novos_dados['data_casamento_comprador']),
        novos_dados['regime_casamento_comprador'], novos_dados['condicao_convivencia_comprador'],
        novos_dados['nome_conjuge'], novos_dados['profissao_conjuge'],
        novos_dados['nacionalidade_conjuge'], novos_dados['fone_resid_conjuge'],
        novos_dados['fone_com_conjuge'], novos_dados['celular_conjuge'],
        novos_dados['email_conjuge'], novos_dados['end_residencial_conjuge'],
        novos_dados['bairro_conjuge'], novos_dados['cidade_conjuge'],
        novos_dados['estado_conjuge'], novos_dados['cep_conjuge'],
        novos_dados['cpf_conjuge'], parse_data_para_db(novos_dados['data_nascimento_conjuge']),
        novos_dados['documentos_necessarios'], novos_dados['condomino_indicado'],
        id_comprador
    ))
    conn.commit()
    conn.close()

def atualizar_vendedor(id_vendedor, novos_dados):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE vendedores SET
        empreendimento = ?, qd = ?, lt = ?, ativo = ?, quitado = ?, corretor = ?, imobiliaria = ?,
        nome_comprador_pj = ?, fone_resid_comprador_pj = ?, fone_com_comprador_pj = ?,
        celular_comprador_pj = ?, email_comprador_pj = ?, end_residencial_comercial_pj = ?,
        bairro_comprador_pj = ?, cidade_comprador_pj = ?, estado_comprador_pj = ?,
        cep_comprador_pj = ?, nome_representante = ?, profissao_representante = ?,
        nacionalidade_representante = ?, fone_resid_representante = ?, fone_com_representante = ?,
        celular_representante = ?, email_representante = ?, end_residencial_representante = ?,
        bairro_representante = ?, cidade_representante = ?, estado_representante = ?,
        cep_representante = ?, nome_socio = ?, cpf_socio = ?, data_nascimento_socio = ?,
        profissao_socio = ?, nacionalidade_socio = ?, fone_resid_socio = ?, fone_com_socio = ?,
        celular_socio = ?, email_socio = ?, end_residencial_socio = ?, bairro_socio = ?,
        cidade_socio = ?, estado_socio = ?, cep_socio = ?, documentos_empresa = ?,
        documentos_socios = ?, condomino_indicado_pj = ?
    WHERE id = ?
    ''', (
        novos_dados['empreendimento'], novos_dados['qd'], novos_dados['lt'],
        novos_dados['ativo'], novos_dados['quitado'], novos_dados['corretor'],
        novos_dados['imobiliaria'], novos_dados['nome_comprador_pj'],
        novos_dados['fone_resid_comprador_pj'], novos_dados['fone_com_comprador_pj'],
        novos_dados['celular_comprador_pj'], novos_dados['email_comprador_pj'],
        novos_dados['end_residencial_comercial_pj'], novos_dados['bairro_comprador_pj'],
        novos_dados['cidade_comprador_pj'], novos_dados['estado_comprador_pj'],
        novos_dados['cep_comprador_pj'], novos_dados['nome_representante'],
        novos_dados['profissao_representante'], novos_dados['nacionalidade_representante'],
        novos_dados['fone_resid_representante'], novos_dados['fone_com_representante'],
        novos_dados['celular_representante'], novos_dados['email_representante'],
        novos_dados['end_residencial_representante'], novos_dados['bairro_representante'],
        novos_dados['cidade_representante'], novos_dados['estado_representante'],
        novos_dados['cep_representante'], novos_dados['nome_socio'],
        novos_dados['cpf_socio'], parse_data_para_db(novos_dados['data_nascimento_socio']),
        novos_dados['profissao_socio'], novos_dados['nacionalidade_socio'],
        novos_dados['fone_resid_socio'], novos_dados['fone_com_socio'],
        novos_dados['celular_socio'], novos_dados['email_socio'],
        novos_dados['end_residencial_socio'], novos_dados['bairro_socio'],
        novos_dados['cidade_socio'], novos_dados['estado_socio'],
        novos_dados['cep_socio'], novos_dados['documentos_empresa'],
        novos_dados['documentos_socios'], novos_dados['condomino_indicado_pj'],
        id_vendedor
    ))
    conn.commit()
    conn.close()

def deletar_comprador(id_comprador):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM compradores WHERE id = ?', (id_comprador,))
    cursor.execute('DELETE FROM dependentes WHERE id_titular = ? AND tipo_titular = ?', (id_comprador, 'comprador'))
    conn.commit()
    conn.close()

def deletar_vendedor(id_vendedor):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM vendedores WHERE id = ?', (id_vendedor,))
    cursor.execute('DELETE FROM dependentes WHERE id_titular = ? AND tipo_titular = ?', (id_vendedor, 'vendedor'))
    conn.commit()
    conn.close()

def deletar_dependente(id_dependente):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM dependentes WHERE id = ?', (id_dependente,))
    conn.commit()
    conn.close()

# --- Funções de Geração de PDF ---
def gerar_pdf_comprador(data):
    """Gera um PDF para a ficha de Comprador (Pessoa Física)."""
    file_name = f"Ficha_Comprador_{data['nome_comprador'].replace(' ', '_')}.pdf"
    doc = SimpleDocTemplate(file_name, pagesize=A4,
                            rightMargin=inch/2, leftMargin=inch/2,
                            topMargin=inch/2, bottomMargin=inch/2)
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(name='TitleStyle', fontSize=18, leading=22, alignment=TA_CENTER,
                              spaceAfter=14, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='SubtitleStyle', fontSize=14, leading=18, alignment=TA_LEFT,
                              spaceBefore=10, spaceAfter=8, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='NormalStyle', fontSize=10, leading=12, alignment=TA_LEFT,
                              spaceAfter=4))
    styles.add(ParagraphStyle(name='FieldStyle', fontSize=10, leading=12, alignment=TA_LEFT,
                              spaceAfter=4, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='SmallText', fontSize=8, leading=10, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='CenteredSmallText', fontSize=8, leading=10, alignment=TA_CENTER))

    story = []

    # Title
    story.append(Paragraph("Ficha Cadastral Pessoa Física – Cessão e Transferência de Direitos", styles['TitleStyle']))
    story.append(Spacer(1, 0.2 * inch))

    # Empreendimento Info
    story.append(Paragraph(f"<b>Empreendimento:</b> {data.get('empreendimento', '')} <b>QD:</b> {data.get('qd', '')} <b>LT:</b> {data.get('lt', '')} <b>Ativo:</b> {'(X)' if data.get('ativo') else '( )'} <b>Quitado:</b> {'(X)' if data.get('quitado') else '( )'}", styles['NormalStyle']))
    story.append(Paragraph(f"<b>Corretor(a):</b> {data.get('corretor', '')} <b>Imobiliária:</b> {data.get('imobiliaria', '')}", styles['NormalStyle']))
    story.append(Spacer(1, 0.2 * inch))

    # COMPRADOR(A)
    story.append(Paragraph("COMPRADOR(A):", styles['SubtitleStyle']))
    story.append(Paragraph(f"<b>Nome:</b> {data.get('nome_comprador', '')}", styles['NormalStyle']))
    story.append(Paragraph(f"<b>Profissão:</b> {data.get('profissao_comprador', '')} <b>Nacionalidade:</b> {data.get('nacionalidade_comprador', '')}", styles['NormalStyle']))
    story.append(Paragraph(f"<b>Fone Resid.:</b> {data.get('fone_resid_comprador', '')} <b>Fone Com.:</b> {data.get('fone_com_comprador', '')} <b>Celular:</b> {data.get('celular_comprador', '')} <b>E-mail:</b> {data.get('email_comprador', '')}", styles['NormalStyle']))
    story.append(Paragraph(f"<b>End. Residencial:</b> {data.get('end_residencial_comprador', '')} <b>Bairro:</b> {data.get('bairro_comprador', '')}", styles['NormalStyle']))
    story.append(Paragraph(f"<b>Cidade:</b> {data.get('cidade_comprador', '')} <b>Estado:</b> {data.get('estado_comprador', '')} <b>CEP:</b> {data.get('cep_comprador', '')}", styles['NormalStyle']))
    
    estado_civil_text = data.get('estado_civil_comprador', '')
    data_casamento_text = formatar_data_ptbr(data.get('data_casamento_comprador', ''))
    regime_casamento_text = data.get('regime_casamento_comprador', '')
    condicao_convivencia_val = data.get('condicao_convivencia_comprador')
    condicao_convivencia_text = "(X) Declara conviver em união estável" if condicao_convivencia_val else "( ) Declara conviver em união estável"

    story.append(Paragraph(f"<b>Estado Civil:</b> {estado_civil_text} <b>Data do Casamento:</b> {data_casamento_text} <b>Regime de Casamento:</b> {regime_casamento_text}", styles['NormalStyle']))
    story.append(Paragraph(f"<b>Condição de Convivência:</b> {condicao_convivencia_text}", styles['NormalStyle']))
    story.append(Spacer(1, 0.2 * inch))

    # CÔNJUGE/SÓCIO(A)
    story.append(Paragraph("CÔNJUGE/SÓCIO(A):", styles['SubtitleStyle']))
    if data.get('nome_conjuge'):
        story.append(Paragraph(f"<b>Nome:</b> {data.get('nome_conjuge', '')}", styles['NormalStyle']))
        story.append(Paragraph(f"<b>CPF:</b> {data.get('cpf_conjuge', '')} <b>Data de Nascimento:</b> {formatar_data_ptbr(data.get('data_nascimento_conjuge', ''))} <b>Profissão:</b> {data.get('profissao_conjuge', '')} <b>Nacionalidade:</b> {data.get('nacionalidade_conjuge', '')}", styles['NormalStyle']))
        story.append(Paragraph(f"<b>Fone Resid.:</b> {data.get('fone_resid_conjuge', '')} <b>Fone Com.:</b> {data.get('fone_com_conjuge', '')} <b>Celular:</b> {data.get('celular_conjuge', '')} <b>E-mail:</b> {data.get('email_conjuge', '')}", styles['NormalStyle']))
        story.append(Paragraph(f"<b>End. Residencial:</b> {data.get('end_residencial_conjuge', '')} <b>Bairro:</b> {data.get('bairro_conjuge', '')}", styles['NormalStyle']))
        story.append(Paragraph(f"<b>Cidade:</b> {data.get('cidade_conjuge', '')} <b>Estado:</b> {data.get('estado_conjuge', '')} <b>CEP:</b> {data.get('cep_conjuge', '')}", styles['NormalStyle']))
    else:
        story.append(Paragraph("Não informado", styles['NormalStyle']))
    story.append(Spacer(1, 0.2 * inch))

    # Documentos Necessários
    story.append(Paragraph("DOCUMENTOS NECESSÁRIOS:", styles['SubtitleStyle']))
    story.append(Paragraph(data.get('documentos_necessarios', ''), styles['NormalStyle']))
    story.append(Spacer(1, 0.2 * inch))
    
    # Condomínio / Loteamento Fechado
    story.append(Paragraph("📌 No caso de Condomínio ou Loteamento Fechado, quando a cessão for emitida para sócio(a)(s), não casados entre si e nem conviventes, é necessário indicar qual dos dois será o(a) condômino(a) 📌", styles['NormalStyle']))
    story.append(Paragraph(f"➡️ indique aqui quem será o(a) condômino(a): <u>{data.get('condomino_indicado', '')}</u>", styles['NormalStyle']))
    story.append(Spacer(1, 0.4 * inch))

    # Assinaturas
    today = datetime.now().strftime('%d/%m/%Y')
    story.append(Paragraph(f"Cidade/Estado, ____ de ___________________ de ________.", styles['NormalStyle']))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("_____________________________________", styles['CenteredSmallText']))
    story.append(Paragraph("Assinatura do(a) Comprador(a)", styles['CenteredSmallText']))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(f"Autorizado em {today}", styles['NormalStyle']))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("_____________________________________", styles['CenteredSmallText']))
    story.append(Paragraph("Imobiliária Celeste", styles['CenteredSmallText']))

    # Listagem de Dependentes (Nova Página ou continuar)
    dependentes_df = carregar_dependentes(data['id'], 'comprador')
    if not dependentes_df.empty:
        story.append(Spacer(1, 0.5 * inch)) # Add some space before new section
        story.append(Paragraph("LISTAGEM DE DEPENDENTES:", styles['SubtitleStyle']))
        story.append(Paragraph(f"<b>CONDÔMINO(A):</b> {data.get('condomino_indicado', '')}", styles['NormalStyle']))
        story.append(Spacer(1, 0.1 * inch))

        dependentes_data = [['NOME', 'CPF', 'E-MAIL', 'Fone Com.', 'Celular', 'Fone Recado', 'Grau de Parentesco']]
        for idx, dep in dependentes_df.iterrows():
            dependentes_data.append([
                dep['nome'],
                dep['cpf'],
                dep['email'],
                dep['fone_com'],
                dep['celular'],
                dep['fone_recado'],
                dep['grau_parentesco']
            ])
        
        table = Table(dependentes_data, colWidths=[2*inch, 1*inch, 1.5*inch, 1*inch, 1*inch, 1*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
        ]))
        story.append(table)

    doc.build(story)
    return file_name

def gerar_pdf_vendedor(data):
    """Gera um PDF para a ficha de Vendedor (Pessoa Jurídica)."""
    file_name = f"Ficha_Vendedor_{data['nome_comprador_pj'].replace(' ', '_')}.pdf"
    doc = SimpleDocTemplate(file_name, pagesize=A4,
                            rightMargin=inch/2, leftMargin=inch/2,
                            topMargin=inch/2, bottomMargin=inch/2)
    styles = getSampleStyleSheet()

    # Custom styles
    styles.add(ParagraphStyle(name='TitleStyle', fontSize=18, leading=22, alignment=TA_CENTER,
                              spaceAfter=14, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='SubtitleStyle', fontSize=14, leading=18, alignment=TA_LEFT,
                              spaceBefore=10, spaceAfter=8, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='NormalStyle', fontSize=10, leading=12, alignment=TA_LEFT,
                              spaceAfter=4))
    styles.add(ParagraphStyle(name='FieldStyle', fontSize=10, leading=12, alignment=TA_LEFT,
                              spaceAfter=4, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='SmallText', fontSize=8, leading=10, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='CenteredSmallText', fontSize=8, leading=10, alignment=TA_CENTER))

    story = []

    # Title
    story.append(Paragraph("Ficha Cadastral Pessoa Jurídica – Cessão e Transferência de Direitos", styles['TitleStyle']))
    story.append(Spacer(1, 0.2 * inch))

    # Empreendimento Info
    story.append(Paragraph(f"<b>Empreendimento:</b> {data.get('empreendimento', '')} <b>QD:</b> {data.get('qd', '')} <b>LT:</b> {data.get('lt', '')} <b>Ativo:</b> {'(X)' if data.get('ativo') else '( )'} <b>Quitado:</b> {'(X)' if data.get('quitado') else '( )'}", styles['NormalStyle']))
    story.append(Paragraph(f"<b>Corretor(a):</b> {data.get('corretor', '')} <b>Imobiliária:</b> {data.get('imobiliaria', '')}", styles['NormalStyle']))
    story.append(Spacer(1, 0.2 * inch))

    # COMPRADOR(A) (Empresa)
    story.append(Paragraph("COMPRADOR(A):", styles['SubtitleStyle']))
    story.append(Paragraph(f"<b>Nome da Empresa:</b> {data.get('nome_comprador_pj', '')}", styles['NormalStyle']))
    story.append(Paragraph(f"<b>Fone Resid.:</b> {data.get('fone_resid_comprador_pj', '')} <b>Fone Com.:</b> {data.get('fone_com_comprador_pj', '')} <b>Celular:</b> {data.get('celular_comprador_pj', '')} <b>E-mail:</b> {data.get('email_comprador_pj', '')}", styles['NormalStyle']))
    story.append(Paragraph(f"<b>End. Residencial/Comercial:</b> {data.get('end_residencial_comercial_pj', '')} <b>Bairro:</b> {data.get('bairro_comprador_pj', '')}", styles['NormalStyle']))
    story.append(Paragraph(f"<b>Cidade:</b> {data.get('cidade_comprador_pj', '')} <b>Estado:</b> {data.get('estado_comprador_pj', '')} <b>CEP:</b> {data.get('cep_comprador_pj', '')}", styles['NormalStyle']))
    story.append(Spacer(1, 0.2 * inch))

    # REPRESENTANTE
    story.append(Paragraph("REPRESENTANTE:", styles['SubtitleStyle']))
    if data.get('nome_representante'):
        story.append(Paragraph(f"<b>Nome:</b> {data.get('nome_representante', '')}", styles['NormalStyle']))
        story.append(Paragraph(f"<b>Profissão:</b> {data.get('profissao_representante', '')} <b>Nacionalidade:</b> {data.get('nacionalidade_representante', '')}", styles['NormalStyle']))
        story.append(Paragraph(f"<b>Fone Resid.:</b> {data.get('fone_resid_representante', '')} <b>Fone Com.:</b> {data.get('fone_com_representante', '')} <b>Celular:</b> {data.get('celular_representante', '')} <b>E-mail:</b> {data.get('email_representante', '')}", styles['NormalStyle']))
        story.append(Paragraph(f"<b>End. Residencial:</b> {data.get('end_residencial_representante', '')} <b>Bairro:</b> {data.get('bairro_representante', '')}", styles['NormalStyle']))
        story.append(Paragraph(f"<b>Cidade:</b> {data.get('cidade_representante', '')} <b>Estado:</b> {data.get('estado_representante', '')} <b>CEP:</b> {data.get('cep_representante', '')}", styles['NormalStyle']))
    else:
        story.append(Paragraph("Não informado", styles['NormalStyle']))
    story.append(Spacer(1, 0.2 * inch))

    # CÔNJUGE/SÓCIO(A)
    story.append(Paragraph("CÔNJUGE/SÓCIO(A):", styles['SubtitleStyle']))
    if data.get('nome_socio'):
        story.append(Paragraph(f"<b>Nome:</b> {data.get('nome_socio', '')}", styles['NormalStyle']))
        story.append(Paragraph(f"<b>CPF:</b> {data.get('cpf_socio', '')} <b>Data de Nascimento:</b> {formatar_data_ptbr(data.get('data_nascimento_socio', ''))} <b>Profissão:</b> {data.get('profissao_socio', '')} <b>Nacionalidade:</b> {data.get('nacionalidade_socio', '')}", styles['NormalStyle']))
        story.append(Paragraph(f"<b>Fone Resid.:</b> {data.get('fone_resid_socio', '')} <b>Fone Com.:</b> {data.get('fone_com_socio', '')} <b>Celular:</b> {data.get('celular_socio', '')} <b>E-mail:</b> {data.get('email_socio', '')}", styles['NormalStyle']))
        story.append(Paragraph(f"<b>End. Residencial:</b> {data.get('end_residencial_socio', '')} <b>Bairro:</b> {data.get('bairro_socio', '')}", styles['NormalStyle']))
        story.append(Paragraph(f"<b>Cidade:</b> {data.get('cidade_socio', '')} <b>Estado:</b> {data.get('estado_socio', '')} <b>CEP:</b> {data.get('cep_socio', '')}", styles['NormalStyle']))
    else:
        story.append(Paragraph("Não informado", styles['NormalStyle']))
    story.append(Spacer(1, 0.2 * inch))

    # DOCUMENTOS NECESSÁRIOS
    story.append(Paragraph("DOCUMENTOS NECESSÁRIOS:", styles['SubtitleStyle']))
    story.append(Paragraph(f"<b>DA EMPRESA:</b> {data.get('documentos_empresa', '')}", styles['NormalStyle']))
    story.append(Paragraph(f"<b>DOS SÓCIOS E SEUS CÔNJUGES:</b> {data.get('documentos_socios', '')}", styles['NormalStyle']))
    story.append(Spacer(1, 0.2 * inch))
    
    # Condomínio / Loteamento Fechado
    story.append(Paragraph("📌 No caso de Condomínio ou Loteamento Fechado, quando a empresa possuir mais de um(a) sócio(a) não casados entre si e nem conviventes, é necessário indicar qual do(a)(s) sócio(a)(s) será o(a) condômino(a) 📌", styles['NormalStyle']))
    story.append(Paragraph(f"➡️ indique aqui quem será o(a) condômino(a): <u>{data.get('condomino_indicado_pj', '')}</u>", styles['NormalStyle']))
    story.append(Spacer(1, 0.4 * inch))

    # Assinaturas
    today = datetime.now().strftime('%d/%m/%Y')
    story.append(Paragraph(f"Cidade/Estado, ____ de ___________________ de ________.", styles['NormalStyle']))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("_____________________________________", styles['CenteredSmallText']))
    story.append(Paragraph("Assinatura do(a) Comprador(a)", styles['CenteredSmallText']))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(f"Autorizado em {today}", styles['NormalStyle']))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("_____________________________________", styles['CenteredSmallText']))
    story.append(Paragraph("Imobiliária Celeste", styles['CenteredSmallText']))

    # Listagem de Dependentes (Nova Página ou continuar)
    dependentes_df = carregar_dependentes(data['id'], 'vendedor') # Assumindo que PJ também pode ter dependentes associados
    if not dependentes_df.empty:
        story.append(Spacer(1, 0.5 * inch)) # Add some space before new section
        story.append(Paragraph("LISTAGEM DE DEPENDENTES:", styles['SubtitleStyle']))
        story.append(Paragraph(f"<b>CONDÔMINO(A):</b> {data.get('condomino_indicado_pj', '')}", styles['NormalStyle']))
        story.append(Spacer(1, 0.1 * inch))

        dependentes_data = [['NOME', 'CPF', 'E-MAIL', 'Fone Com.', 'Celular', 'Fone Recado', 'Grau de Parentesco']]
        for idx, dep in dependentes_df.iterrows():
            dependentes_data.append([
                dep['nome'],
                dep['cpf'],
                dep['email'],
                dep['fone_com'],
                dep['celular'],
                dep['fone_recado'],
                dep['grau_parentesco']
            ])
        
        table = Table(dependentes_data, colWidths=[2*inch, 1*inch, 1.5*inch, 1*inch, 1*inch, 1*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
        ]))
        story.append(table)
        
    doc.build(story)
    return file_name

# --- Carregar dados iniciais ---
if 'compradores' not in st.session_state:
    st.session_state.compradores = carregar_compradores()

if 'vendedores' not in st.session_state:
    st.session_state.vendedores = carregar_vendedores()

# --- Interface principal ---
st.title("Sistema de Cadastro Imobiliário")

# Abas
tab1, tab2, tab3 = st.tabs([
    "Cadastro de Compradores (Pessoa Física)",
    "Cadastro de Vendedores (Pessoa Jurídica)",
    "Consulta de Registros"
])

with tab1: # Cadastro de Compradores (Pessoa Física)
    st.header("Cadastro de Compradores (Pessoa Física)")

    # Verifica se está em modo de edição
    if 'editando_comprador' in st.session_state:
        registro_comprador = st.session_state.editando_comprador
        dependentes_existentes = carregar_dependentes(registro_comprador['id'], 'comprador')
        
        with st.form("form_edicao_comprador"):
            st.subheader(f"Editando Comprador: {registro_comprador['nome_comprador']}")

            st.markdown("---")
            st.subheader("Informações do Empreendimento")
            col1, col2, col3, col4, col5 = st.columns([2,1,1,1,1])
            with col1:
                empreendimento = st.text_input("Empreendimento", value=registro_comprador.get('empreendimento', ''))
            with col2:
                qd = st.text_input("QD", value=registro_comprador.get('qd', ''))
            with col3:
                lt = st.text_input("LT", value=registro_comprador.get('lt', ''))
            with col4:
                # O valor do checkbox deve ser booleano, converter o valor do banco de dados (INTEGER)
                ativo = st.checkbox("Ativo", value=bool(registro_comprador.get('ativo', False)))
            with col5:
                # O valor do checkbox deve ser booleano, converter o valor do banco de dados (INTEGER)
                quitado = st.checkbox("Quitado", value=bool(registro_comprador.get('quitado', False)))

            col1, col2 = st.columns(2)
            with col1:
                corretor = st.text_input("Corretor(a)", value=registro_comprador.get('corretor', ''))
            with col2:
                imobiliaria = st.text_input("Imobiliária", value=registro_comprador.get('imobiliaria', ''))
            
            st.markdown("---")
            st.subheader("Dados do Comprador(a)")
            col1, col2 = st.columns(2)
            with col1:
                nome_comprador = st.text_input("Nome Completo *", value=registro_comprador.get('nome_comprador', ''))
                profissao_comprador = st.text_input("Profissão", value=registro_comprador.get('profissao_comprador', ''))
                nacionalidade_comprador = st.text_input("Nacionalidade", value=registro_comprador.get('nacionalidade_comprador', ''))
                fone_resid_comprador = st.text_input("Fone Resid.", value=registro_comprador.get('fone_resid_comprador', ''))
                fone_com_comprador = st.text_input("Fone Com.", value=registro_comprador.get('fone_com_comprador', ''))
            with col2:
                celular_comprador = st.text_input("Celular", value=registro_comprador.get('celular_comprador', ''))
                email_comprador = st.text_input("E-mail *", value=registro_comprador.get('email_comprador', ''))
                end_residencial_comprador = st.text_input("End. Residencial", value=registro_comprador.get('end_residencial_comprador', ''))
                bairro_comprador = st.text_input("Bairro", value=registro_comprador.get('bairro_comprador', ''))
                cidade_comprador = st.text_input("Cidade", value=registro_comprador.get('cidade_comprador', ''))
                estado_comprador = st.selectbox("Estado", ["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"], index=["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"].index(registro_comprador.get('estado_comprador', '')))
                cep_comprador = st.text_input("CEP", value=registro_comprador.get('cep_comprador', ''))
            
            estado_civil_comprador = st.selectbox("Estado Civil", ["", "Casado(a)", "Solteiro(a)", "Divorciado(a)", "Viúvo(a)"], index=["", "Casado(a)", "Solteiro(a)", "Divorciado(a)", "Viúvo(a)"].index(registro_comprador.get('estado_civil_comprador', '')))
            data_casamento_comprador = st.text_input("Data do Casamento (dd/mm/aaaa)", value=formatar_data_ptbr(registro_comprador.get('data_casamento_comprador', '')))
            regime_casamento_comprador = st.text_input("Regime de Casamento", value=registro_comprador.get('regime_casamento_comprador', ''))
            # O valor do checkbox deve ser booleano, converter o valor do banco de dados (INTEGER)
            condicao_convivencia_comprador = st.checkbox("Declara conviver em união estável – Apresentar comprovante de estado civil de cada um e a declaração de convivência em união estável com as assinaturas reconhecidas em Cartório.", value=bool(registro_comprador.get('condicao_convivencia_comprador', False)))

            st.markdown("---")
            st.subheader("Dados do Cônjuge/Sócio(a)")
            col1, col2 = st.columns(2)
            with col1:
                nome_conjuge = st.text_input("Nome Cônjuge/Sócio(a)", value=registro_comprador.get('nome_conjuge', ''))
                cpf_conjuge = st.text_input("CPF Cônjuge/Sócio(a)", value=registro_comprador.get('cpf_conjuge', ''))
                data_nascimento_conjuge = st.text_input("Data de Nascimento Cônjuge/Sócio(a) (dd/mm/aaaa)", value=formatar_data_ptbr(registro_comprador.get('data_nascimento_conjuge', '')))
                profissao_conjuge = st.text_input("Profissão Cônjuge/Sócio(a)", value=registro_comprador.get('profissao_conjuge', ''))
                nacionalidade_conjuge = st.text_input("Nacionalidade Cônjuge/Sócio(a)", value=registro_comprador.get('nacionalidade_conjuge', ''))
                fone_resid_conjuge = st.text_input("Fone Resid. Cônjuge/Sócio(a)", value=registro_comprador.get('fone_resid_conjuge', ''))
            with col2:
                fone_com_conjuge = st.text_input("Fone Com. Cônjuge/Sócio(a)", value=registro_comprador.get('fone_com_conjuge', ''))
                celular_conjuge = st.text_input("Celular Cônjuge/Sócio(a)", value=registro_comprador.get('celular_conjuge', ''))
                email_conjuge = st.text_input("E-mail Cônjuge/Sócio(a)", value=registro_comprador.get('email_conjuge', ''))
                end_residencial_conjuge = st.text_input("End. Residencial Cônjuge/Sócio(a)", value=registro_comprador.get('end_residencial_conjuge', ''))
                bairro_conjuge = st.text_input("Bairro Cônjuge/Sócio(a)", value=registro_comprador.get('bairro_conjuge', ''))
                cidade_conjuge = st.text_input("Cidade Cônjuge/Sócio(a)", value=registro_comprador.get('cidade_conjuge', ''))
                estado_conjuge = st.selectbox("Estado Cônjuge/Sócio(a)", ["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"], index=["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"].index(registro_comprador.get('estado_conjuge', '')))
                cep_conjuge = st.text_input("CEP Cônjuge/Sócio(a)", value=registro_comprador.get('cep_conjuge', ''))

            st.markdown("---")
            st.subheader("Documentos Necessários (Para Comprador e Cônjuge/Sócio)")
            documentos_necessarios = st.text_area("Descreva os documentos necessários", value=registro_comprador.get('documentos_necessarios', "CNH; RG e CPF; Comprovante do Estado Civil, Comprovante de Endereço, Comprovante de Renda, CND da Prefeitura e Nada Consta do Condomínio ou Associação."))
            
            st.markdown("---")
            st.subheader("Informações de Condomínio/Loteamento Fechado")
            st.markdown("📌 No caso de Condomínio ou Loteamento Fechado, quando a cessão for emitida para sócio(a)(s), não casados entre si e nem conviventes, é necessário indicar qual dos dois será o(a) condômino(a) 📌")
            condomino_indicado = st.text_input("Indique aqui quem será o(a) condômino(a)", value=registro_comprador.get('condomino_indicado', ''))

            st.markdown("---")
            st.subheader("Dependentes")
            # Exibe dependentes existentes para edição/remoção
            for i, dep in dependentes_existentes.iterrows():
                with st.expander(f"Dependente: {dep['nome']}"):
                    col_dep1, col_dep2 = st.columns(2)
                    with col_dep1:
                        dep_nome = st.text_input("Nome", value=dep['nome'], key=f"edit_dep_nome_{dep['id']}")
                        dep_cpf = st.text_input("CPF", value=dep['cpf'], key=f"edit_dep_cpf_{dep['id']}")
                        dep_email = st.text_input("E-mail", value=dep['email'], key=f"edit_dep_email_{dep['id']}")
                    with col_dep2:
                        dep_fone_com = st.text_input("Fone Com.", value=dep['fone_com'], key=f"edit_dep_fone_com_{dep['id']}")
                        dep_celular = st.text_input("Celular", value=dep['celular'], key=f"edit_dep_celular_{dep['id']}")
                        dep_fone_recado = st.text_input("Fone Recado", value=dep['fone_recado'], key=f"edit_dep_fone_recado_{dep['id']}")
                        dep_grau_parentesco = st.text_input("Grau de Parentesco", value=dep['grau_parentesco'], key=f"edit_dep_grau_parentesco_{dep['id']}")
                    
                    if st.button("Remover Dependente", key=f"remove_dep_{dep['id']}"):
                        deletar_dependente(dep['id'])
                        st.success("Dependente removido!")
                        st.session_state.compradores = carregar_compradores() # Refresh to update counts
                        st.rerun()

            st.subheader("Adicionar Novo Dependente")
            with st.expander("Novo Dependente"):
                novo_dep_nome = st.text_input("Nome do Novo Dependente", key="new_dep_nome")
                novo_dep_cpf = st.text_input("CPF do Novo Dependente", key="new_dep_cpf")
                novo_dep_email = st.text_input("E-mail do Novo Dependente", key="new_dep_email")
                novo_dep_fone_com = st.text_input("Fone Com. do Novo Dependente", key="new_dep_fone_com")
                novo_dep_celular = st.text_input("Celular do Novo Dependente", key="new_dep_celular")
                novo_dep_fone_recado = st.text_input("Fone Recado do Novo Dependente", key="new_dep_fone_recado")
                novo_dep_grau_parentesco = st.text_input("Grau de Parentesco do Novo Dependente", key="new_dep_grau_parentesco")
                if st.button("Adicionar Dependente", key="add_new_dep_btn"):
                    if novo_dep_nome:
                        salvar_dependente({
                            'id_titular': registro_comprador['id'],
                            'tipo_titular': 'comprador',
                            'nome': novo_dep_nome,
                            'cpf': novo_dep_cpf,
                            'email': novo_dep_email,
                            'fone_com': novo_dep_fone_com,
                            'celular': novo_dep_celular,
                            'fone_recado': novo_dep_fone_recado,
                            'grau_parentesco': novo_dep_grau_parentesco
                        })
                        st.success("Novo dependente adicionado!")
                        st.session_state.compradores = carregar_compradores() # Refresh to update counts
                        st.rerun()
                    else:
                        st.warning("Nome do dependente é obrigatório.")


            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.form_submit_button("Salvar Alterações"):
                    # Converter valores booleanos para INTEGER (0 ou 1) antes de salvar no DB
                    dados_atualizados = {
                        'empreendimento': empreendimento, 'qd': qd, 'lt': lt, 'ativo': int(ativo),
                        'quitado': int(quitado), 'corretor': corretor, 'imobiliaria': imobiliaria,
                        'nome_comprador': nome_comprador, 'profissao_comprador': profissao_comprador,
                        'nacionalidade_comprador': nacionalidade_comprador,
                        'fone_resid_comprador': fone_resid_comprador,
                        'fone_com_comprador': fone_com_comprador,
                        'celular_comprador': celular_comprador, 'email_comprador': email_comprador,
                        'end_residencial_comprador': end_residencial_comprador,
                        'bairro_comprador': bairro_comprador, 'cidade_comprador': cidade_comprador,
                        'estado_comprador': estado_comprador, 'cep_comprador': cep_comprador,
                        'estado_civil_comprador': estado_civil_comprador,
                        'data_casamento_comprador': data_casamento_comprador,
                        'regime_casamento_comprador': regime_casamento_comprador,
                        'condicao_convivencia_comprador': int(condicao_convivencia_comprador),
                        'nome_conjuge': nome_conjuge, 'profissao_conjuge': profissao_conjuge,
                        'nacionalidade_conjuge': nacionalidade_conjuge,
                        'fone_resid_conjuge': fone_resid_conjuge,
                        'fone_com_conjuge': fone_com_conjuge, 'celular_conjuge': celular_conjuge,
                        'email_conjuge': email_conjuge, 'end_residencial_conjuge': end_residencial_conjuge,
                        'bairro_conjuge': bairro_conjuge, 'cidade_conjuge': cidade_conjuge,
                        'estado_conjuge': estado_conjuge, 'cep_conjuge': cep_conjuge,
                        'cpf_conjuge': cpf_conjuge, 'data_nascimento_conjuge': data_nascimento_conjuge,
                        'documentos_necessarios': documentos_necessarios,
                        'condomino_indicado': condomino_indicado
                    }
                    atualizar_comprador(st.session_state.id_edicao, dados_atualizados)
                    st.session_state.compradores = carregar_compradores()
                    del st.session_state.editando_comprador
                    del st.session_state.id_edicao
                    st.success("Comprador atualizado com sucesso!")
                    st.rerun()
            with col2:
                if st.form_submit_button("Gerar PDF"):
                    pdf_file = gerar_pdf_comprador(registro_comprador)
                    with open(pdf_file, "rb") as file:
                        btn = st.download_button(
                            label="Download PDF",
                            data=file.read(),
                            file_name=pdf_file,
                            mime="application/pdf"
                        )
                    st.success(f"PDF gerado: {pdf_file}")
            with col3:
                if st.form_submit_button("Cancelar Edição"):
                    del st.session_state.editando_comprador
                    del st.session_state.id_edicao
                    st.rerun()
            with col4:
                if st.form_submit_button("Excluir Comprador"):
                    deletar_comprador(st.session_state.id_edicao)
                    st.session_state.compradores = carregar_compradores()
                    del st.session_state.editando_comprador
                    del st.session_state.id_edicao
                    st.success("Comprador removido com sucesso!")
                    st.rerun()

    else: # Modo de cadastro
        with st.form("form_comprador"):
            st.subheader("Informações do Empreendimento")
            col1, col2, col3, col4, col5 = st.columns([2,1,1,1,1])
            with col1:
                empreendimento = st.text_input("Empreendimento", key="comp_empreendimento")
            with col2:
                qd = st.text_input("QD", key="comp_qd")
            with col3:
                lt = st.text_input("LT", key="comp_lt")
            with col4:
                ativo = st.checkbox("Ativo", key="comp_ativo")
            with col5:
                quitado = st.checkbox("Quitado", key="comp_quitado")

            col1, col2 = st.columns(2)
            with col1:
                corretor = st.text_input("Corretor(a)", key="comp_corretor")
            with col2:
                imobiliaria = st.text_input("Imobiliária", key="comp_imobiliaria")

            st.markdown("---")
            st.subheader("Dados do Comprador(a)")
            col1, col2 = st.columns(2)
            with col1:
                nome_comprador = st.text_input("Nome Completo *", key="nome_comprador")
                profissao_comprador = st.text_input("Profissão", key="profissao_comprador")
                nacionalidade_comprador = st.text_input("Nacionalidade", key="nacionalidade_comprador")
                fone_resid_comprador = st.text_input("Fone Resid.", key="fone_resid_comprador")
                fone_com_comprador = st.text_input("Fone Com.", key="fone_com_comprador")
            with col2:
                celular_comprador = st.text_input("Celular", key="celular_comprador")
                email_comprador = st.text_input("E-mail *", key="email_comprador")
                end_residencial_comprador = st.text_input("End. Residencial", key="end_residencial_comprador")
                bairro_comprador = st.text_input("Bairro", key="bairro_comprador")
                cidade_comprador = st.text_input("Cidade", key="cidade_comprador")
                estado_comprador = st.selectbox("Estado", ["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"], key="estado_comprador")
                cep_comprador = st.text_input("CEP", key="cep_comprador")
            
            estado_civil_comprador = st.selectbox("Estado Civil", ["", "Casado(a)", "Solteiro(a)", "Divorciado(a)", "Viúvo(a)"], key="estado_civil_comprador")
            data_casamento_comprador = st.text_input("Data do Casamento (dd/mm/aaaa)", key="data_casamento_comprador")
            regime_casamento_comprador = st.text_input("Regime de Casamento", key="regime_casamento_comprador")
            condicao_convivencia_comprador = st.checkbox("Declara conviver em união estável – Apresentar comprovante de estado civil de cada um e a declaração de convivência em união estável com as assinaturas reconhecidas em Cartório.", key="condicao_convivencia_comprador")

            st.markdown("---")
            st.subheader("Dados do Cônjuge/Sócio(a)")
            col1, col2 = st.columns(2)
            with col1:
                nome_conjuge = st.text_input("Nome Cônjuge/Sócio(a)", key="nome_conjuge")
                cpf_conjuge = st.text_input("CPF Cônjuge/Sócio(a)", key="cpf_conjuge")
                data_nascimento_conjuge = st.text_input("Data de Nascimento Cônjuge/Sócio(a) (dd/mm/aaaa)", key="data_nascimento_conjuge")
                profissao_conjuge = st.text_input("Profissão Cônjuge/Sócio(a)", key="profissao_conjuge")
                nacionalidade_conjuge = st.text_input("Nacionalidade Cônjuge/Sócio(a)", key="nacionalidade_conjuge")
                fone_resid_conjuge = st.text_input("Fone Resid. Cônjuge/Sócio(a)", key="fone_resid_conjuge")
            with col2:
                fone_com_conjuge = st.text_input("Fone Com. Cônjuge/Sócio(a)", key="fone_com_conjuge")
                celular_conjuge = st.text_input("Celular Cônjuge/Sócio(a)", key="celular_conjuge")
                email_conjuge = st.text_input("E-mail Cônjuge/Sócio(a)", key="email_conjuge")
                end_residencial_conjuge = st.text_input("End. Residencial Cônjuge/Sócio(a)", key="end_residencial_conjuge")
                bairro_conjuge = st.text_input("Bairro Cônjuge/Sócio(a)", key="bairro_conjuge")
                cidade_conjuge = st.text_input("Cidade Cônjuge/Sócio(a)", key="cidade_conjuge")
                estado_conjuge = st.selectbox("Estado Cônjuge/Sócio(a)", ["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"], key="estado_conjuge")
                cep_conjuge = st.text_input("CEP Cônjuge/Sócio(a)", key="cep_conjuge")

            st.markdown("---")
            st.subheader("Documentos Necessários (Para Comprador e Cônjuge/Sócio)")
            documentos_necessarios = st.text_area("Descreva os documentos necessários", "CNH; RG e CPF; Comprovante do Estado Civil, Comprovante de Endereço, Comprovante de Renda, CND da Prefeitura e Nada Consta do Condomínio ou Associação.", key="documentos_necessarios_comprador")
            
            st.markdown("---")
            st.subheader("Informações de Condomínio/Loteamento Fechado")
            st.markdown("📌 No caso de Condomínio ou Loteamento Fechado, quando a cessão for emitida para sócio(a)(s), não casados entre si e nem conviventes, é necessário indicar qual dos dois será o(a) condômino(a) �")
            condomino_indicado = st.text_input("Indique aqui quem será o(a) condômino(a)", key="condomino_indicado_comprador")
            
            # Botão de cadastro
            submitted = st.form_submit_button("Cadastrar Comprador")

            if submitted:
                if not nome_comprador or not email_comprador:
                    st.error("Por favor, preencha os campos obrigatórios (Nome Completo e E-mail do Comprador).")
                else:
                    novo_comprador = {
                        'empreendimento': empreendimento, 'qd': qd, 'lt': lt, 'ativo': int(ativo), # Converter para INTEGER
                        'quitado': int(quitado), # Converter para INTEGER
                        'corretor': corretor, 'imobiliaria': imobiliaria,
                        'nome_comprador': nome_comprador, 'profissao_comprador': profissao_comprador,
                        'nacionalidade_comprador': nacionalidade_comprador,
                        'fone_resid_comprador': fone_resid_comprador,
                        'fone_com_comprador': fone_com_comprador,
                        'celular_comprador': celular_comprador, 'email_comprador': email_comprador,
                        'end_residencial_comprador': end_residencial_comprador,
                        'bairro_comprador': bairro_comprador, 'cidade_comprador': cidade_comprador,
                        'estado_comprador': estado_comprador, 'cep_comprador': cep_comprador,
                        'estado_civil_comprador': estado_civil_comprador,
                        'data_casamento_comprador': data_casamento_comprador,
                        'regime_casamento_comprador': regime_casamento_comprador,
                        'condicao_convivencia_comprador': int(condicao_convivencia_comprador), # Converter para INTEGER
                        'nome_conjuge': nome_conjuge, 'profissao_conjuge': profissao_conjuge,
                        'nacionalidade_conjuge': nacionalidade_conjuge,
                        'fone_resid_conjuge': fone_resid_conjuge,
                        'fone_com_conjuge': fone_com_conjuge, 'celular_conjuge': celular_conjuge,
                        'email_conjuge': email_conjuge, 'end_residencial_conjuge': end_residencial_conjuge,
                        'bairro_conjuge': bairro_conjuge, 'cidade_conjuge': cidade_conjuge,
                        'estado_conjuge': estado_conjuge, 'cep_conjuge': cep_conjuge,
                        'cpf_conjuge': cpf_conjuge, 'data_nascimento_conjuge': data_nascimento_conjuge,
                        'documentos_necessarios': documentos_necessarios,
                        'condomino_indicado': condomino_indicado,
                        'data_cadastro': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                    }
                    salvar_comprador(novo_comprador)
                    st.session_state.compradores = carregar_compradores()
                    st.success("Comprador cadastrado com sucesso!")
                    st.rerun() # Recarrega para limpar o formulário e atualizar a tabela


with tab2: # Cadastro de Vendedores (Pessoa Jurídica)
    st.header("Cadastro de Vendedores (Pessoa Jurídica)")

    if 'editando_vendedor' in st.session_state:
        registro_vendedor = st.session_state.editando_vendedor
        dependentes_existentes = carregar_dependentes(registro_vendedor['id'], 'vendedor')

        with st.form("form_edicao_vendedor"):
            st.subheader(f"Editando Vendedor: {registro_vendedor['nome_comprador_pj']}")

            st.markdown("---")
            st.subheader("Informações do Empreendimento")
            col1, col2, col3, col4, col5 = st.columns([2,1,1,1,1])
            with col1:
                empreendimento_v = st.text_input("Empreendimento", value=registro_vendedor.get('empreendimento', ''), key="v_empreendimento")
            with col2:
                qd_v = st.text_input("QD", value=registro_vendedor.get('qd', ''), key="v_qd")
            with col3:
                lt_v = st.text_input("LT", value=registro_vendedor.get('lt', ''), key="v_lt")
            with col4:
                # O valor do checkbox deve ser booleano, converter o valor do banco de dados (INTEGER)
                ativo_v = st.checkbox("Ativo", value=bool(registro_vendedor.get('ativo', False)), key="v_ativo")
            with col5:
                # O valor do checkbox deve ser booleano, converter o valor do banco de dados (INTEGER)
                quitado_v = st.checkbox("Quitado", value=bool(registro_vendedor.get('quitado', False)), key="v_quitado")

            col1, col2 = st.columns(2)
            with col1:
                corretor_v = st.text_input("Corretor(a)", value=registro_vendedor.get('corretor', ''), key="v_corretor")
            with col2:
                imobiliaria_v = st.text_input("Imobiliária", value=registro_vendedor.get('imobiliaria', ''), key="v_imobiliaria")

            st.markdown("---")
            st.subheader("Dados da Empresa (Comprador/Cedente)")
            col1, col2 = st.columns(2)
            with col1:
                nome_comprador_pj = st.text_input("Nome da Empresa *", value=registro_vendedor.get('nome_comprador_pj', ''))
                fone_resid_comprador_pj = st.text_input("Fone Resid. Empresa", value=registro_vendedor.get('fone_resid_comprador_pj', ''))
                fone_com_comprador_pj = st.text_input("Fone Com. Empresa", value=registro_vendedor.get('fone_com_comprador_pj', ''))
            with col2:
                celular_comprador_pj = st.text_input("Celular Empresa", value=registro_vendedor.get('celular_comprador_pj', ''))
                email_comprador_pj = st.text_input("E-mail Empresa *", value=registro_vendedor.get('email_comprador_pj', ''))
                end_residencial_comercial_pj = st.text_input("End. Residencial/Comercial Empresa", value=registro_vendedor.get('end_residencial_comercial_pj', ''))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                bairro_comprador_pj = st.text_input("Bairro Empresa", value=registro_vendedor.get('bairro_comprador_pj', ''))
            with col2:
                cidade_comprador_pj = st.text_input("Cidade Empresa", value=registro_vendedor.get('cidade_comprador_pj', ''))
            with col3:
                estado_comprador_pj = st.selectbox("Estado Empresa", ["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"], index=["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"].index(registro_vendedor.get('estado_comprador_pj', '')))
                cep_comprador_pj = st.text_input("CEP Empresa", value=registro_vendedor.get('cep_comprador_pj', ''))

            st.markdown("---")
            st.subheader("Dados do Representante")
            col1, col2 = st.columns(2)
            with col1:
                nome_representante = st.text_input("Nome Representante", value=registro_vendedor.get('nome_representante', ''))
                profissao_representante = st.text_input("Profissão Representante", value=registro_vendedor.get('profissao_representante', ''))
                nacionalidade_representante = st.text_input("Nacionalidade Representante", value=registro_vendedor.get('nacionalidade_representante', ''))
                fone_resid_representante = st.text_input("Fone Resid. Representante", value=registro_vendedor.get('fone_resid_representante', ''))
            with col2:
                fone_com_representante = st.text_input("Fone Com. Representante", value=registro_vendedor.get('fone_com_representante', ''))
                celular_representante = st.text_input("Celular Representante", value=registro_vendedor.get('celular_representante', ''))
                email_representante = st.text_input("E-mail Representante", value=registro_vendedor.get('email_representante', ''))
                end_residencial_representante = st.text_input("End. Residencial Representante", value=registro_vendedor.get('end_residencial_representante', ''))
                bairro_representante = st.text_input("Bairro Representante", value=registro_vendedor.get('bairro_representante', ''))
                cidade_representante = st.text_input("Cidade Representante", value=registro_vendedor.get('cidade_representante', ''))
                estado_representante = st.selectbox("Estado Representante", ["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"], index=["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"].index(registro_vendedor.get('estado_representante', '')))
                cep_representante = st.text_input("CEP Representante", value=registro_vendedor.get('cep_representante', ''))

            st.markdown("---")
            st.subheader("Dados do Cônjuge/Sócio(a) da Empresa")
            col1, col2 = st.columns(2)
            with col1:
                nome_socio = st.text_input("Nome Sócio", value=registro_vendedor.get('nome_socio', ''))
                cpf_socio = st.text_input("CPF Sócio", value=registro_vendedor.get('cpf_socio', ''))
                data_nascimento_socio = st.text_input("Data de Nascimento Sócio (dd/mm/aaaa)", value=formatar_data_ptbr(registro_vendedor.get('data_nascimento_socio', '')))
                profissao_socio = st.text_input("Profissão Sócio", value=registro_vendedor.get('profissao_socio', ''))
                nacionalidade_socio = st.text_input("Nacionalidade Sócio", value=registro_vendedor.get('nacionalidade_socio', ''))
                fone_resid_socio = st.text_input("Fone Resid. Sócio", value=registro_vendedor.get('fone_resid_socio', ''))
            with col2:
                fone_com_socio = st.text_input("Fone Com. Sócio", value=registro_vendedor.get('fone_com_socio', ''))
                celular_socio = st.text_input("Celular Sócio", value=registro_vendedor.get('celular_socio', ''))
                email_socio = st.text_input("E-mail Sócio", value=registro_vendedor.get('email_socio', ''))
                end_residencial_socio = st.text_input("End. Residencial Sócio", value=registro_vendedor.get('end_residencial_socio', ''))
                bairro_socio = st.text_input("Bairro Sócio", value=registro_vendedor.get('bairro_socio', ''))
                cidade_socio = st.text_input("Cidade Sócio", value=registro_vendedor.get('cidade_socio', ''))
                estado_socio = st.selectbox("Estado Sócio", ["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"], index=["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"].index(registro_vendedor.get('estado_socio', '')))
                cep_socio = st.text_input("CEP Sócio", value=registro_vendedor.get('cep_socio', ''))
            
            st.markdown("---")
            st.subheader("Documentos Necessários (Para Empresa e Sócios)")
            documentos_empresa = st.text_area("Documentos da Empresa", value=registro_vendedor.get('documentos_empresa', "CONTRATO SOCIAL E ALTERAÇÕES, COMPROVANTE DE ENDEREÇO, DECLARAÇÃO DE FATURAMENTO;"))
            documentos_socios = st.text_area("Documentos dos Sócios e Cônjuges", value=registro_vendedor.get('documentos_socios', "CNH; RG e CPF, Comprovante do Estado Civil, Comprovante de Endereço, Comprovante de Renda, CND da Prefeitura e Nada Consta do Condomínio ou Associação."))

            st.markdown("---")
            st.subheader("Informações de Condomínio/Loteamento Fechado")
            st.markdown("📌 No caso de Condomínio ou Loteamento Fechado, quando a empresa possuir mais de um(a) sócio(a) não casados entre si e nem conviventes, é necessário indicar qual do(a)(s) sócio(a)(s) será o(a) condômino(a) 📌")
            condomino_indicado_pj = st.text_input("Indique aqui quem será o(a) condômino(a) para Pessoa Jurídica", value=registro_vendedor.get('condomino_indicado_pj', ''))

            st.markdown("---")
            st.subheader("Dependentes (Associados a este vendedor - PJ)")
            for i, dep in dependentes_existentes.iterrows():
                with st.expander(f"Dependente: {dep['nome']}"):
                    col_dep1, col_dep2 = st.columns(2)
                    with col_dep1:
                        dep_nome_v = st.text_input("Nome", value=dep['nome'], key=f"edit_dep_nome_v_{dep['id']}")
                        dep_cpf_v = st.text_input("CPF", value=dep['cpf'], key=f"edit_dep_cpf_v_{dep['id']}")
                        dep_email_v = st.text_input("E-mail", value=dep['email'], key=f"edit_dep_email_v_{dep['id']}")
                    with col_dep2:
                        dep_fone_com_v = st.text_input("Fone Com.", value=dep['fone_com'], key=f"edit_dep_fone_com_v_{dep['id']}")
                        dep_celular_v = st.text_input("Celular", value=dep['celular'], key=f"edit_dep_celular_v_{dep['id']}")
                        dep_fone_recado_v = st.text_input("Fone Recado", value=dep['fone_recado'], key=f"edit_dep_fone_recado_v_{dep['id']}")
                        dep_grau_parentesco_v = st.text_input("Grau de Parentesco", value=dep['grau_parentesco'], key=f"edit_dep_grau_parentesco_v_{dep['id']}")
                    
                    if st.button("Remover Dependente", key=f"remove_dep_v_{dep['id']}"):
                        deletar_dependente(dep['id'])
                        st.success("Dependente removido!")
                        st.session_state.vendedores = carregar_vendedores() # Refresh to update counts
                        st.rerun()

            st.subheader("Adicionar Novo Dependente (para Vendedor - PJ)")
            with st.expander("Novo Dependente"):
                novo_dep_nome_v = st.text_input("Nome do Novo Dependente (Vendedor PJ)", key="new_dep_nome_v")
                novo_dep_cpf_v = st.text_input("CPF do Novo Dependente (Vendedor PJ)", key="new_dep_cpf_v")
                novo_dep_email_v = st.text_input("E-mail do Novo Dependente (Vendedor PJ)", key="new_dep_email_v")
                novo_dep_fone_com_v = st.text_input("Fone Com. do Novo Dependente (Vendedor PJ)", key="new_dep_fone_com_v")
                novo_dep_celular_v = st.text_input("Celular do Novo Dependente (Vendedor PJ)", key="new_dep_celular_v")
                novo_dep_fone_recado_v = st.text_input("Fone Recado do Novo Dependente (Vendedor PJ)", key="new_dep_fone_recado_v")
                novo_dep_grau_parentesco_v = st.text_input("Grau de Parentesco do Novo Dependente (Vendedor PJ)", key="new_dep_grau_parentesco_v")
                if st.button("Adicionar Dependente (Vendedor PJ)", key="add_new_dep_btn_v"):
                    if novo_dep_nome_v:
                        salvar_dependente({
                            'id_titular': registro_vendedor['id'],
                            'tipo_titular': 'vendedor',
                            'nome': novo_dep_nome_v,
                            'cpf': novo_dep_cpf_v,
                            'email': novo_dep_email_v,
                            'fone_com': novo_dep_fone_com_v,
                            'celular': novo_dep_celular_v,
                            'fone_recado': novo_dep_fone_recado_v,
                            'grau_parentesco': novo_dep_grau_parentesco_v
                        })
                        st.success("Novo dependente adicionado ao Vendedor PJ!")
                        st.session_state.vendedores = carregar_vendedores()
                        st.rerun()
                    else:
                        st.warning("Nome do dependente é obrigatório.")

            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.form_submit_button("Salvar Alterações"):
                    # Converter valores booleanos para INTEGER (0 ou 1) antes de salvar no DB
                    dados_atualizados = {
                        'empreendimento': empreendimento_v, 'qd': qd_v, 'lt': lt_v, 'ativo': int(ativo_v),
                        'quitado': int(quitado_v), 'corretor': corretor_v, 'imobiliaria': imobiliaria_v,
                        'nome_comprador_pj': nome_comprador_pj,
                        'fone_resid_comprador_pj': fone_resid_comprador_pj,
                        'fone_com_comprador_pj': fone_com_comprador_pj,
                        'celular_comprador_pj': celular_comprador_pj,
                        'email_comprador_pj': email_comprador_pj,
                        'end_residencial_comercial_pj': end_residencial_comercial_pj,
                        'bairro_comprador_pj': bairro_comprador_pj,
                        'cidade_comprador_pj': cidade_comprador_pj,
                        'estado_comprador_pj': estado_comprador_pj,
                        'cep_comprador_pj': cep_comprador_pj,
                        'nome_representante': nome_representante,
                        'profissao_representante': profissao_representante,
                        'nacionalidade_representante': nacionalidade_representante,
                        'fone_resid_representante': fone_resid_representante,
                        'fone_com_representante': fone_com_representante,
                        'celular_representante': celular_representante,
                        'email_representante': email_representante,
                        'end_residencial_representante': end_residencial_representante,
                        'bairro_representante': bairro_representante,
                        'cidade_representante': cidade_representante,
                        'estado_representante': estado_representante,
                        'cep_representante': cep_representante,
                        'nome_socio': nome_socio, 'cpf_socio': cpf_socio,
                        'data_nascimento_socio': data_nascimento_socio,
                        'profissao_socio': profissao_socio,
                        'nacionalidade_socio': nacionalidade_socio,
                        'fone_resid_socio': fone_resid_socio, 'fone_com_socio': fone_com_socio,
                        'celular_socio': celular_socio, 'email_socio': email_socio,
                        'end_residencial_socio': end_residencial_socio,
                        'bairro_socio': bairro_socio, 'cidade_socio': cidade_socio,
                        'estado_socio': estado_socio, 'cep_socio': cep_socio,
                        'documentos_empresa': documentos_empresa,
                        'documentos_socios': documentos_socios,
                        'condomino_indicado_pj': condomino_indicado_pj
                    }
                    atualizar_vendedor(st.session_state.id_edicao, dados_atualizados)
                    st.session_state.vendedores = carregar_vendedores()
                    del st.session_state.editando_vendedor
                    del st.session_state.id_edicao
                    st.success("Vendedor atualizado com sucesso!")
                    st.rerun()
            with col2:
                if st.form_submit_button("Gerar PDF"):
                    pdf_file = gerar_pdf_vendedor(registro_vendedor)
                    with open(pdf_file, "rb") as file:
                        btn = st.download_button(
                            label="Download PDF",
                            data=file.read(),
                            file_name=pdf_file,
                            mime="application/pdf"
                        )
                    st.success(f"PDF gerado: {pdf_file}")
            with col3:
                if st.form_submit_button("Cancelar Edição"):
                    del st.session_state.editando_vendedor
                    del st.session_state.id_edicao
                    st.rerun()
            with col4:
                if st.form_submit_button("Excluir Vendedor"):
                    deletar_vendedor(st.session_state.id_edicao)
                    st.session_state.vendedores = carregar_vendedores()
                    del st.session_state.editando_vendedor
                    del st.session_state.id_edicao
                    st.success("Vendedor removido com sucesso!")
                    st.rerun()

    else: # Modo de cadastro
        with st.form("form_vendedor"):
            st.subheader("Informações do Empreendimento")
            col1, col2, col3, col4, col5 = st.columns([2,1,1,1,1])
            with col1:
                empreendimento_v = st.text_input("Empreendimento", key="vend_empreendimento")
            with col2:
                qd_v = st.text_input("QD", key="vend_qd")
            with col3:
                lt_v = st.text_input("LT", key="vend_lt")
            with col4:
                ativo_v = st.checkbox("Ativo", key="vend_ativo")
            with col5:
                quitado_v = st.checkbox("Quitado", key="vend_quitado")

            col1, col2 = st.columns(2)
            with col1:
                corretor_v = st.text_input("Corretor(a)", key="vend_corretor")
            with col2:
                imobiliaria_v = st.text_input("Imobiliária", key="vend_imobiliaria")

            st.markdown("---")
            st.subheader("Dados da Empresa (Comprador/Cedente)")
            col1, col2 = st.columns(2)
            with col1:
                nome_comprador_pj = st.text_input("Nome da Empresa *", key="nome_comprador_pj")
                fone_resid_comprador_pj = st.text_input("Fone Resid. Empresa", key="fone_resid_comprador_pj")
                fone_com_comprador_pj = st.text_input("Fone Com. Empresa", key="fone_com_comprador_pj")
            with col2:
                celular_comprador_pj = st.text_input("Celular Empresa", key="celular_comprador_pj")
                email_comprador_pj = st.text_input("E-mail Empresa *", key="email_comprador_pj")
                end_residencial_comercial_pj = st.text_input("End. Residencial/Comercial Empresa", key="end_residencial_comercial_pj")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                bairro_comprador_pj = st.text_input("Bairro Empresa", key="bairro_comprador_pj")
            with col2:
                cidade_comprador_pj = st.text_input("Cidade Empresa", key="cidade_comprador_pj")
            with col3:
                estado_comprador_pj = st.selectbox("Estado Empresa", ["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"], key="estado_comprador_pj")
                cep_comprador_pj = st.text_input("CEP Empresa", key="cep_comprador_pj")

            st.markdown("---")
            st.subheader("Dados do Representante")
            col1, col2 = st.columns(2)
            with col1:
                nome_representante = st.text_input("Nome Representante", key="nome_representante")
                profissao_representante = st.text_input("Profissão Representante", key="profissao_representante")
                nacionalidade_representante = st.text_input("Nacionalidade Representante", key="nacionalidade_representante")
                fone_resid_representante = st.text_input("Fone Resid. Representante", key="fone_resid_representante")
            with col2:
                fone_com_representante = st.text_input("Fone Com. Representante", key="fone_com_representante")
                celular_representante = st.text_input("Celular Representante", key="celular_representante")
                email_representante = st.text_input("E-mail Representante", key="email_representante")
                end_residencial_representante = st.text_input("End. Residencial Representante", key="end_residencial_representante")
                bairro_representante = st.text_input("Bairro Representante", key="bairro_representante")
                cidade_representante = st.text_input("Cidade Representante", key="cidade_representante")
                estado_representante = st.selectbox("Estado Representante", ["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"], key="estado_representante")
                cep_representante = st.text_input("CEP Representante", key="cep_representante")

            st.markdown("---")
            st.subheader("Dados do Cônjuge/Sócio(a) da Empresa")
            col1, col2 = st.columns(2)
            with col1:
                nome_socio = st.text_input("Nome Sócio", key="nome_socio")
                cpf_socio = st.text_input("CPF Sócio", key="cpf_socio")
                data_nascimento_socio = st.text_input("Data de Nascimento Sócio (dd/mm/aaaa)", key="data_nascimento_socio")
                profissao_socio = st.text_input("Profissão Sócio", key="profissao_socio")
                nacionalidade_socio = st.text_input("Nacionalidade Sócio", key="nacionalidade_socio")
                fone_resid_socio = st.text_input("Fone Resid. Sócio", key="fone_resid_socio")
            with col2:
                fone_com_socio = st.text_input("Fone Com. Sócio", key="fone_com_socio")
                celular_socio = st.text_input("Celular Sócio", key="celular_socio")
                email_socio = st.text_input("E-mail Sócio", key="email_socio")
                end_residencial_socio = st.text_input("End. Residencial Sócio", key="end_residencial_socio")
                bairro_socio = st.text_input("Bairro Sócio", key="bairro_socio")
                cidade_socio = st.text_input("Cidade Sócio", key="cidade_socio")
                estado_socio = st.selectbox("Estado Sócio", ["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"], key="estado_socio")
                cep_socio = st.text_input("CEP Sócio", key="cep_socio")
            
            st.markdown("---")
            st.subheader("Documentos Necessários (Para Empresa e Sócios)")
            documentos_empresa = st.text_area("Documentos da Empresa", "CONTRATO SOCIAL E ALTERAÇÕES, COMPROVANTE DE ENDEREÇO, DECLARAÇÃO DE FATURAMENTO;", key="documentos_empresa_vendedor")
            documentos_socios = st.text_area("Documentos dos Sócios e Cônjuges", "CNH; RG e CPF, Comprovante do Estado Civil, Comprovante de Endereço, Comprovante de Renda, CND da Prefeitura e Nada Consta do Condomínio ou Associação.", key="documentos_socios_vendedor")

            st.markdown("---")
            st.subheader("Informações de Condomínio/Loteamento Fechado")
            st.markdown("📌 No caso de Condomínio ou Loteamento Fechado, quando a empresa possuir mais de um(a) sócio(a) não casados entre si e nem conviventes, é necessário indicar qual do(a)(s) sócio(a)(s) será o(a) condômino(a) 📌")
            condomino_indicado_pj = st.text_input("Indique aqui quem será o(a) condômino(a) para Pessoa Jurídica", key="condomino_indicado_vendedor_pj")

            # Botão de cadastro
            submitted = st.form_submit_button("Cadastrar Vendedor")

            if submitted:
                if not nome_comprador_pj or not email_comprador_pj:
                    st.error("Por favor, preencha os campos obrigatórios (Nome da Empresa e E-mail da Empresa).")
                else:
                    novo_vendedor = {
                        'empreendimento': empreendimento_v, 'qd': qd_v, 'lt': lt_v, 'ativo': int(ativo_v), # Converter para INTEGER
                        'quitado': int(quitado_v), # Converter para INTEGER
                        'corretor': corretor_v, 'imobiliaria': imobiliaria_v,
                        'nome_comprador_pj': nome_comprador_pj,
                        'fone_resid_comprador_pj': fone_resid_comprador_pj,
                        'fone_com_comprador_pj': fone_com_comprador_pj,
                        'celular_comprador_pj': celular_comprador_pj,
                        'email_comprador_pj': email_comprador_pj,
                        'end_residencial_comercial_pj': end_residencial_comercial_pj,
                        'bairro_comprador_pj': bairro_comprador_pj,
                        'cidade_comprador_pj': cidade_comprador_pj,
                        'estado_comprador_pj': estado_comprador_pj,
                        'cep_comprador_pj': cep_comprador_pj,
                        'nome_representante': nome_representante,
                        'profissao_representante': profissao_representante,
                        'nacionalidade_representante': nacionalidade_representante,
                        'fone_resid_representante': fone_resid_representante,
                        'fone_com_representante': fone_com_representante,
                        'celular_representante': celular_representante,
                        'email_representante': email_representante,
                        'end_residencial_representante': end_residencial_representante,
                        'bairro_representante': bairro_representante,
                        'cidade_representante': cidade_representante,
                        'estado_representante': estado_representante,
                        'cep_representante': cep_representante,
                        'nome_socio': nome_socio, 'cpf_socio': cpf_socio,
                        'data_nascimento_socio': data_nascimento_socio,
                        'profissao_socio': profissao_socio,
                        'nacionalidade_socio': nacionalidade_socio,
                        'fone_resid_socio': fone_resid_socio, 'fone_com_socio': fone_com_socio,
                        'celular_socio': celular_socio, 'email_socio': email_socio,
                        'end_residencial_socio': end_residencial_socio,
                        'bairro_socio': bairro_socio, 'cidade_socio': cidade_socio,
                        'estado_socio': estado_socio, 'cep_socio': cep_socio,
                        'documentos_empresa': documentos_empresa,
                        'documentos_socios': documentos_socios,
                        'condomino_indicado_pj': condomino_indicado_pj,
                        'data_cadastro': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                    }
                    salvar_vendedor(novo_vendedor)
                    st.session_state.vendedores = carregar_vendedores()
                    st.success("Vendedor cadastrado com sucesso!")
                    st.rerun() # Recarrega para limpar o formulário e atualizar a tabela

with tab3: # Consulta de Registros
    st.header("Consulta de Registros")

    tipo_consulta = st.radio("Tipo de Consulta",
                             ["Compradores (Pessoa Física)", "Vendedores (Pessoa Jurídica)"],
                             horizontal=True)

    df_display = pd.DataFrame()
    if tipo_consulta == "Compradores (Pessoa Física)":
        df = st.session_state.compradores.copy()
        if not df.empty:
            # Seleciona e renomeia colunas para exibição amigável
            df_display = df[['id', 'nome_comprador', 'email_comprador', 'celular_comprador', 'cidade_comprador', 'estado_comprador', 'data_cadastro']].copy()
            df_display.columns = ['ID', 'Nome', 'E-mail', 'Celular', 'Cidade', 'Estado', 'Data de Cadastro']
    else: # Vendedores (Pessoa Jurídica)
        df = st.session_state.vendedores.copy()
        if not df.empty:
            # Seleciona e renomeia colunas para exibição amigável
            df_display = df[['id', 'nome_comprador_pj', 'email_comprador_pj', 'celular_comprador_pj', 'cidade_comprador_pj', 'estado_comprador_pj', 'data_cadastro']].copy()
            df_display.columns = ['ID', 'Nome da Empresa', 'E-mail da Empresa', 'Celular da Empresa', 'Cidade da Empresa', 'Estado da Empresa', 'Data de Cadastro']

    if not df_display.empty:
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            filtro_nome = st.text_input("Filtrar por nome/empresa", key=f"filtro_nome_{tipo_consulta}")

        # Aplicar filtros
        if filtro_nome:
            if tipo_consulta == "Compradores (Pessoa Física)":
                df_filtered = df[df['nome_comprador'].str.contains(filtro_nome, case=False, na=False)]
            else:
                df_filtered = df[df['nome_comprador_pj'].str.contains(filtro_nome, case=False, na=False)]
            
            # Recria df_display com as colunas corretas após o filtro
            if tipo_consulta == "Compradores (Pessoa Física)":
                df_display = df_filtered[['id', 'nome_comprador', 'email_comprador', 'celular_comprador', 'cidade_comprador', 'estado_comprador', 'data_cadastro']].copy()
                df_display.columns = ['ID', 'Nome', 'E-mail', 'Celular', 'Cidade', 'Estado', 'Data de Cadastro']
            else:
                df_display = df_filtered[['id', 'nome_comprador_pj', 'email_comprador_pj', 'celular_comprador_pj', 'cidade_comprador_pj', 'estado_comprador_pj', 'data_cadastro']].copy()
                df_display.columns = ['ID', 'Nome da Empresa', 'E-mail da Empresa', 'Celular da Empresa', 'Cidade da Empresa', 'Estado da Empresa', 'Data de Cadastro']
        else:
             df_filtered = df # Se não há filtro de nome, use o DataFrame original

        # Formatar datas antes de exibir na tabela
        for col in df_display.columns:
            if 'Data' in col: # Verifica se a coluna tem 'Data' no nome
                df_display[col] = df_display[col].apply(formatar_data_ptbr)
        
        st.dataframe(df_display)

        # Seleção de registro para edição/exclusão
        if not df_filtered.empty:
            registros = df_filtered.to_dict('records')
            options = [f"{r['id']} - {r.get('nome_comprador', r.get('nome_comprador_pj', ''))}"
                       for r in registros]
            
            selected_option = st.selectbox("Selecione um registro para ação:", ["Selecione..."] + options, key=f"select_registro_{tipo_consulta}")
            
            if selected_option != "Selecione...":
                selected_id = int(selected_option.split(' - ')[0])
                registro_selecionado = next((r for r in registros if r['id'] == selected_id), None)
                
                if registro_selecionado:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("Editar Registro", key=f"edit_btn_{tipo_consulta}"):
                            if tipo_consulta == "Compradores (Pessoa Física)":
                                st.session_state.editando_comprador = registro_selecionado
                            else:
                                st.session_state.editando_vendedor = registro_selecionado
                            st.session_state.id_edicao = registro_selecionado['id']
                            st.rerun()
                    with col2:
                        if st.button("Excluir Registro", key=f"delete_btn_{tipo_consulta}"):
                            if tipo_consulta == "Compradores (Pessoa Física)":
                                deletar_comprador(registro_selecionado['id'])
                                st.session_state.compradores = carregar_compradores()
                            else:
                                deletar_vendedor(registro_selecionado['id'])
                                st.session_state.vendedores = carregar_vendedores()
                            st.success("Registro removido com sucesso!")
                            st.rerun()
                    with col3:
                        if st.button("Gerar PDF do Registro", key=f"gerar_pdf_btn_{tipo_consulta}"):
                            if tipo_consulta == "Compradores (Pessoa Física)":
                                pdf_file = gerar_pdf_comprador(registro_selecionado)
                            else:
                                pdf_file = gerar_pdf_vendedor(registro_selecionado)
                            with open(pdf_file, "rb") as file:
                                st.download_button(
                                    label="Download PDF",
                                    data=file.read(),
                                    file_name=pdf_file,
                                    mime="application/pdf"
                                )
                            st.success(f"PDF gerado para {registro_selecionado.get('nome_comprador', registro_selecionado.get('nome_comprador_pj'))}!")
                            # Optional: Clean up the generated PDF file if not needed after download
                            # os.remove(pdf_file)
    else:
        st.warning("Nenhum registro encontrado para esta categoria.")

    # Opções de exportação
    if not df.empty: # Exporta o DataFrame completo, não o filtrado para exibição
        st.download_button(
            label="Exportar todos os dados para CSV",
            data=df.to_csv(index=False, sep=';').encode('utf-8'),
            file_name=f"{tipo_consulta.lower().replace(' ', '_').replace('(pessoa_física)', '').replace('(pessoa_jurídica)', '')}_completo_{datetime.now().strftime('%d%m%Y')}.csv",
            mime='text/csv'
        )
�
