import os
import zipfile
import datetime

PASTA_ORIGEM = "."
PASTA_DESTINO = "z_backup"

def criar_backup():
    if not os.path.exists(PASTA_DESTINO):
        os.makedirs(PASTA_DESTINO)

    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"backup_{agora}.zip"
    caminho_zip = os.path.join(PASTA_DESTINO, nome_arquivo)

    with zipfile.ZipFile(caminho_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for raiz, dirs, arquivos in os.walk(PASTA_ORIGEM):
            if any(p in raiz for p in [".venv", "z_backup"]):
                continue
            for arquivo in arquivos:
                if arquivo in ["zFazBackup.py", "zRestauraUltimoBackup.py"]:
                    continue
                caminho_completo = os.path.join(raiz, arquivo)
                arcname = os.path.relpath(caminho_completo, PASTA_ORIGEM)
                zipf.write(caminho_completo, arcname)

    print(f"✅ Backup criado em: {caminho_zip}")

if __name__ == "__main__":
    criar_backup()
