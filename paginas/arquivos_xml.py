import gspread
import streamlit as st
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

XML_BASE = Path(r"https://github.com/Carlos-Comini/PROJETO_XML/tree/main/xmls")

def get_cnpjs_planilha():
    import json
    from google.oauth2.service_account import Credentials
    credenciais_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    credenciais = Credentials.from_service_account_info(credenciais_dict)
    gc = gspread.authorize(credenciais)
    sh = gc.open_by_key('1bJOkcArR6DZK_7SYwiAiFZEPE9t8HQ1d6ZmDoigCPJw')
    ws = sh.worksheet('Empresas')
    cnpjs = ws.col_values(2)[1:]      # Segunda coluna: CNPJ
    razoes = ws.col_values(3)[1:]     # Terceira coluna: Razão Social
    return {cnpj: razao for cnpj, razao in zip(cnpjs, razoes)}

def parse_xml(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

        ide = root.find(".//nfe:ide", ns)
        emit = root.find(".//nfe:emit", ns)
        dest = root.find(".//nfe:dest", ns)
        total = root.find(".//nfe:ICMSTot", ns)

        numero = ide.find("nfe:nNF", ns).text if ide is not None else "—"
        data_emissao = ide.find("nfe:dhEmi", ns).text[:10] if ide is not None else "—"
        cnpj_emit = emit.find("nfe:CNPJ", ns).text if emit is not None else "—"
        cnpj_dest = dest.find("nfe:CNPJ", ns).text if dest is not None else "—"
        valor = total.find("nfe:vNF", ns).text if total is not None else "—"

        return {
            "Número": numero,
            "Data": data_emissao,
            "CNPJ_Emitente": cnpj_emit,
            "CNPJ_Destinatario": cnpj_dest,
            "Valor": valor
        }
    except:
        return {"Número": "Erro", "Data": "Erro", "CNPJ_Emitente": "Erro", "CNPJ_Destinatario": "Erro", "Valor": "Erro"}

def exibir():
    st.title("📂 Gestão de Arquivos XML")
    st.subheader("📤 Enviar XML manualmente")
    uploaded = st.file_uploader("Escolha um ou mais arquivos XML", type=["xml"], accept_multiple_files=True)

    if uploaded:
        cnpjs_empresas = get_cnpjs_planilha()
        for file in uploaded:
            temp_path = XML_BASE / "temp.xml"
            with open(temp_path, "wb") as f:
                f.write(file.read())
            info = parse_xml(temp_path)
            if info["CNPJ_Destinatario"] in cnpjs_empresas:
                cnpj = info["CNPJ_Destinatario"]
            elif info["CNPJ_Emitente"] in cnpjs_empresas:
                cnpj = info["CNPJ_Emitente"]
            else:
                cnpj = "geral"
            hoje = datetime.today().strftime("%Y_%m_%d")
            pasta_destino = XML_BASE / cnpj / hoje
            pasta_destino.mkdir(parents=True, exist_ok=True)
            caminho = pasta_destino / file.name
            temp_path.replace(caminho)
        st.success(f"{len(uploaded)} arquivo(s) salvo(s) com sucesso!")

    st.subheader("📁 Arquivos Recebidos")
    cnpjs_empresas = get_cnpjs_planilha()
    dados = []
    for cnpj_dir in XML_BASE.iterdir():
        if cnpj_dir.is_dir():
            if st.session_state.get("usuario", {}).get("Tipo") == "Cliente":
                if cnpj_dir.name != st.session_state["usuario"]["Empresa_ID"]:
                    continue
            razao_social = cnpjs_empresas.get(cnpj_dir.name, cnpj_dir.name)
            for data_dir in cnpj_dir.iterdir():
                for xml in data_dir.glob("*.xml"):
                    info = parse_xml(xml)
                    info["Empresa"] = razao_social
                    info["Arquivo"] = xml.name
                    info["Caminho"] = str(xml)
                    if info["CNPJ_Destinatario"] in cnpjs_empresas:
                        info["Tipo"] = "ENTRADA"
                        info["CNPJ"] = info["CNPJ_Destinatario"]
                        info["Razao_Social"] = cnpjs_empresas.get(info["CNPJ_Destinatario"], "—")
                    elif info["CNPJ_Emitente"] in cnpjs_empresas:
                        info["Tipo"] = "SAÍDA"
                        info["CNPJ"] = info["CNPJ_Emitente"]
                        info["Razao_Social"] = cnpjs_empresas.get(info["CNPJ_Emitente"], "—")
                    else:
                        info["Tipo"] = "OUTRO"
                        info["CNPJ"] = "-"
                        info["Razao_Social"] = "—"
                    dados.append(info)
    empresas = sorted(set(d["Empresa"] for d in dados))
    filtro_empresa = st.selectbox("Empresa", ["Todas"] + empresas)
    if filtro_empresa != "Todas":
        dados = [d for d in dados if d["Empresa"] == filtro_empresa]
    for d in dados:
        with st.expander(f'📄 {d["Arquivo"]} — {d["Data"]} — R$ {d["Valor"]} — {d["Tipo"]}'):
            st.write(f"**Número:** {d['Número']}")
            st.write(f"**CNPJ ({d['Tipo']}):** {d['CNPJ']}")
            st.write(f"**Razão Social:** {d['Razao_Social']}")
            st.write(f"**Empresa:** {d['Empresa']}")
            st.download_button("⬇️ Baixar XML", data=open(d["Caminho"], "rb"), file_name=d["Arquivo"])