import os
import zipfile

PASTA_DESTINO = "."
PASTA_BACKUP = "z_backup"

def restaurar_backup():
    arquivos = sorted([
        f for f in os.listdir(PASTA_BACKUP)
        if f.endswith(".zip")
    ], reverse=True)

    if not arquivos:
        print("❌ Nenhum backup encontrado.")
        return

    caminho_arquivo = os.path.join(PASTA_BACKUP, arquivos[0])
    with zipfile.ZipFile(caminho_arquivo, "r") as zipf:
        zipf.extractall(PASTA_DESTINO)

    print(f"✅ Backup restaurado: {arquivos[0]}")

if __name__ == "__main__":
    restaurar_backup()
