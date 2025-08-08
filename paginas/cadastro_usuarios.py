import streamlit as st
import streamlit as st
from funcoes_compartilhadas.estilos import aplicar_estilo_padrao, set_page_title
aplicar_estilo_padrao()
set_page_title("Cadastro de Usuários")
st.markdown("""
    <style>
    .topbar {position: fixed;top: 0;left: 0;width: 100vw;height: 64px;background: #263a53;display: flex;align-items: center;z-index: 100;box-shadow: 0 2px 8px #0002;}
    .topbar-logo {height: 40px;margin-left: 32px;margin-right: 24px;}
    .topbar-menu {display: flex;gap: 32px;}
    .topbar-menu a {color: #fff;font-size: 1.1rem;text-decoration: none;font-weight: 500;padding: 8px 0;transition: color 0.2s;}
    .topbar-menu a:hover {color: #42a5f5;}
    .topbar-account {margin-left: auto;margin-right: 32px;background: #42a5f5;color: #fff;border-radius: 8px;padding: 8px 18px;font-weight: 600;font-size: 1rem;box-shadow: 0 2px 8px #0002;}
    .stApp {padding-top: 72px !important;}
    </style>
    <div class="topbar">
        <img src="https://raw.githubusercontent.com/Notalize/brand-assets/main/logo-notalize.png" class="topbar-logo" alt="Logo" />
        <div class="topbar-menu">
            <a href="#">Cadastros</a>
            <a href="#">Administrativo</a>
            <a href="#">Busca de Documentos</a>
            <a href="#">NF-e | NFC-e | CF-e</a>
            <a href="#">CT-e</a>
            <a href="#">NFC-e</a>
            <a href="#">MDF-e</a>
            <a href="#">Relatórios</a>
        </div>
        <div class="topbar-account">Minha Conta</div>
    </div>
""", unsafe_allow_html=True)
import streamlit as st
from funcoes_compartilhadas.conversa_banco import salvar_usuario, conectar_google_sheets
from funcoes_compartilhadas.estilos import aplicar_estilo_padrao

def exibir():
    aplicar_estilo_padrao()
    st.header("Cadastro de Usuários")

    tipo = st.radio("Tipo de Usuário", ["Escritório", "Cliente"])
    with st.form("form_usuario"):
        nome = st.text_input("Nome")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")

        if tipo == "Escritório":
            permitir_cadastros = st.checkbox("Permitir Cadastros")
            permitir_ver_arquivo = st.checkbox("Permitir Ver Arquivo")
            permitir_ver_xml = st.checkbox("Permitir Ver XML")

            if st.form_submit_button("Salvar"):
                permissoes = {
                    "cadastrar": permitir_cadastros,
                    "ver_arquivo": permitir_ver_arquivo,
                    "ver_xml": permitir_ver_xml
                }
                salvar_usuario(nome, email, senha, "Escritorio", permissoes=permissoes)
                st.success("Usuário do escritório cadastrado.")

        else:
            planilha = conectar_google_sheets()
            empresas = planilha.worksheet("Empresas").col_values(2)[1:]
            empresa = st.selectbox("Empresa", empresas)
            permitir_ver_arquivo = st.checkbox("Permitir Ver Arquivo")
            permitir_ver_xml = st.checkbox("Permitir Ver XML")

            if st.form_submit_button("Salvar"):
                permissoes = {
                    "ver_arquivo": permitir_ver_arquivo,
                    "ver_xml": permitir_ver_xml
                }
                salvar_usuario(nome, email, senha, "Cliente", empresa=empresa, permissoes=permissoes)
                st.success("Usuário de cliente cadastrado.")
