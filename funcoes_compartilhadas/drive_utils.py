from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os

# Caminho para o arquivo de credenciais do service account
SERVICE_ACCOUNT_FILE = 'credenciais.json'  # ajuste se necessário

def autenticar_drive():
    gauth = GoogleAuth()
    gauth.LoadServiceConfigFile(SERVICE_ACCOUNT_FILE)
    gauth.ServiceAuth()
    return GoogleDrive(gauth)

def upload_para_drive(caminho_arquivo, nome_arquivo, id_pasta):
    """
    Faz upload de um arquivo local para uma pasta específica no Google Drive.
    caminho_arquivo: caminho local do arquivo
    nome_arquivo: nome que o arquivo terá no Drive
    id_pasta: ID da pasta de destino no Drive
    """
    drive = autenticar_drive()
    file_drive = drive.CreateFile({'title': nome_arquivo, 'parents': [{'id': id_pasta}]})
    file_drive.SetContentFile(caminho_arquivo)
    file_drive.Upload()
    return file_drive['id']

def listar_arquivos_drive(id_pasta, prefixo=None):
    """
    Lista arquivos em uma pasta do Google Drive. Se prefixo for informado, filtra pelo início do nome.
    """
    drive = autenticar_drive()
    query = f"'{id_pasta}' in parents and trashed=false"
    if prefixo:
        query += f" and title contains '{prefixo}'"
    file_list = drive.ListFile({'q': query}).GetList()
    return file_list

def baixar_arquivo_drive(file_id):
    """
    Baixa o conteúdo de um arquivo do Google Drive pelo ID.
    Retorna bytes.
    """
    drive = autenticar_drive()
    file_drive = drive.CreateFile({'id': file_id})
    return file_drive.GetContentString(encoding='utf-8')
