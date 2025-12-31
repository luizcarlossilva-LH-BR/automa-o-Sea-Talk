#!/bin/bash

echo "========================================"
echo "Setup Git para GitHub Actions"
echo "========================================"
echo ""

# Verifica se git está instalado
if ! command -v git &> /dev/null; then
    echo "ERRO: Git não encontrado!"
    echo "Instale o Git: https://git-scm.com/downloads"
    exit 1
fi

echo "[1/4] Inicializando repositório Git..."
git init

echo ""
echo "[2/4] Adicionando arquivos..."
git add .

echo ""
echo "[3/4] Fazendo commit inicial..."
git commit -m "Initial commit: Looker Studio to SeaTalk automation" || echo "AVISO: Pode ser que não haja mudanças para commitar"

echo ""
echo "[4/4] Configurando remote..."
echo ""
echo "Por favor, informe:"
read -p "  1. Seu usuário do GitHub (ex: seuusuario): " GITHUB_USER
read -p "  2. Nome do repositório (ex: looker-studio-seatalk): " REPO_NAME

git remote add origin "https://github.com/${GITHUB_USER}/${REPO_NAME}.git" 2>/dev/null || \
git remote set-url origin "https://github.com/${GITHUB_USER}/${REPO_NAME}.git"

echo ""
echo "========================================"
echo "Configuração concluída!"
echo "========================================"
echo ""
echo "Próximos passos:"
echo "1. Crie o repositório no GitHub: https://github.com/new"
echo "2. Execute: git push -u origin main"
echo "3. Configure os Secrets no GitHub (veja SETUP_GITHUB.md)"
echo ""

