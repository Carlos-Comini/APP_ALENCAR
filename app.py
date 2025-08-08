import streamlit as st
import streamlit.components.v1 as components
from paginas import cadastro_empresas, cadastro_usuarios, arquivos_xml, dashboard, arquivo
from funcoes_compartilhadas.conversa_banco import autenticar_usuario
from funcoes_compartilhadas.estilos import aplicar_estilo_padrao

st.set_page_config(layout="wide", page_title="Gestão de XML")

# Estilo fullscreen real + sem sidebar
st.markdown("""
    <style>
        #MainMenu, header, footer {
            visibility: hidden;
        }
        .css-1d391kg, .css-fblp2m { display: none; }
        .block-container {
            padding: 1rem 2rem;
            max-width: 100%;
        }
        html, body, .stApp {
            height: 100%;
            margin: 0;
            padding: 0;
            overflow-x: hidden;
        }
        /* Centraliza o card de login */
        .stApp > div:first-child {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
    </style>
""", unsafe_allow_html=True)

# Inicializa variáveis de sessão
if "usuario_autenticado" not in st.session_state:
    st.session_state.usuario_autenticado = False
if "tipo_usuario" not in st.session_state:
    st.session_state.tipo_usuario = ""
if "dados_usuario" not in st.session_state:
    st.session_state.dados_usuario = {}

def exibir_login_html():
    with open("index_embutido_streamlit.html", "r", encoding="utf-8") as f:
        html = f.read()
    components.html(html, height=900, scrolling=False)

def processa_login_por_url():
    email = st.query_params.get("email")
    senha = st.query_params.get("senha")
    if email and senha:
        sucesso, tipo, dados = autenticar_usuario(email, senha)
        if sucesso:
            st.session_state.usuario_autenticado = True
            st.session_state.tipo_usuario = tipo
            st.session_state.dados_usuario = dados
            st.rerun()
        else:
            st.error("❌ Login inválido.")

if not st.session_state.usuario_autenticado:
    exibir_login_html()
    processa_login_por_url()
else:
    aplicar_estilo_padrao()

    # Inicializa o menu na sessão se não existir
    if "menu" not in st.session_state:
        st.session_state["menu"] = "Dashboard"

    # Permissões do usuário logado
    dados_usuario = st.session_state.get("dados_usuario", {})
    tipo_usuario = st.session_state.get("tipo_usuario", "")
    permitir_cadastros = dados_usuario.get("Permitir_Cadastros", "Não") in ["Sim", 1, True, "1"]
    permitir_ver_arquivo = dados_usuario.get("Ver_Arquivos", "Não") in ["Sim", 1, True, "1"]
    permitir_ver_xml = dados_usuario.get("Ver_XML", "Não") in ["Sim", 1, True, "1"]

    # Monta menu conforme permissões
    menu_labels = ["Dashboard"]
    if permitir_cadastros:
        menu_labels.append("Empresas Clientes")
        menu_labels.append("Usuários")
    if permitir_ver_xml:
        menu_labels.append("XMLs")
    if permitir_ver_arquivo:
        menu_labels.append("Arquivos")
    menu_labels.append("Sair")

    cols = st.columns(len(menu_labels))
    for i, label in enumerate(menu_labels):
        if cols[i].button(label, key=f"menu_{label}"):
            st.session_state["menu"] = label

    menu = st.session_state["menu"]
    # Exibe apenas o conteúdo da página selecionada conforme permissões
    if menu == "Dashboard":
        dashboard.exibir()
    elif menu == "Empresas Clientes" and permitir_cadastros:
        cadastro_empresas.exibir()
    elif menu == "Usuários" and permitir_cadastros:
        cadastro_usuarios.exibir()
    elif menu == "XMLs" and permitir_ver_xml:
        arquivos_xml.exibir()
    elif menu == "Arquivos" and permitir_ver_arquivo:
        arquivo.exibir()
    elif menu == "Sair":
        st.session_state.usuario_autenticado = False
        st.session_state.tipo_usuario = ""
        st.session_state.dados_usuario = {}
        st.rerun()
