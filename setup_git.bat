@echo off
echo ========================================
echo Setup Git para GitHub Actions
echo ========================================
echo.

REM Verifica se git está instalado
git --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Git nao encontrado!
    echo Instale o Git: https://git-scm.com/downloads
    pause
    exit /b 1
)

echo [1/4] Inicializando repositorio Git...
git init
if errorlevel 1 (
    echo ERRO ao inicializar Git
    pause
    exit /b 1
)

echo.
echo [2/4] Adicionando arquivos...
git add .
if errorlevel 1 (
    echo ERRO ao adicionar arquivos
    pause
    exit /b 1
)

echo.
echo [3/4] Fazendo commit inicial...
git commit -m "Initial commit: Looker Studio to SeaTalk automation"
if errorlevel 1 (
    echo AVISO: Pode ser que nao haja mudancas para commitar
)

echo.
echo [4/4] Configurando remote...
echo.
echo Por favor, informe:
echo   1. Seu usuario do GitHub (ex: seuusuario)
set /p GITHUB_USER="Usuario GitHub: "
echo   2. Nome do repositorio (ex: looker-studio-seatalk)
set /p REPO_NAME="Nome do repositorio: "

git remote add origin https://github.com/%GITHUB_USER%/%REPO_NAME%.git
if errorlevel 1 (
    echo AVISO: Remote pode ja existir. Continuando...
    git remote set-url origin https://github.com/%GITHUB_USER%/%REPO_NAME%.git
)

echo.
echo ========================================
echo Configuracao concluida!
echo ========================================
echo.
echo Proximos passos:
echo 1. Crie o repositorio no GitHub: https://github.com/new
echo 2. Execute: git push -u origin main
echo 3. Configure os Secrets no GitHub (veja SETUP_GITHUB.md)
echo.
pause

