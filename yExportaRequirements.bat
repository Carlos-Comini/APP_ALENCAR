@echo off
echo 🔥 Ativando ambiente virtual e gerando requirements.txt...
.\.venv\Scripts\activate && pip freeze > requirements.txt
echo ✅ Arquivo requirements.txt gerado com sucesso!
pause
