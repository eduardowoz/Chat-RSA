@echo off
ECHO.
ECHO ======================================================
ECHO         INICIANDO OS SERVIDORES DO CHAT-RSA
ECHO ======================================================
ECHO.

ECHO -> Iniciando o Servidor A (Alice) na porta 5000...
cd ServidorA
start "Servidor A" cmd /k python app.py --my-port 5000 --peer-port 5001 --user Eduardo

cd ..

ECHO -> Iniciando o Servidor B (Bob) na porta 5001...
cd ServidorB
start "Servidor B" cmd /k python app.py --my-port 5001 --peer-port 5000 --user Escobar

ECHO.
ECHO -> Os dois servidores foram iniciados em janelas separadas.