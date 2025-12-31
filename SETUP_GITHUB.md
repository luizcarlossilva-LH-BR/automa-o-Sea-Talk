# 🚀 Setup Rápido - GitHub Actions

Guia rápido para configurar o projeto no GitHub Actions.

## ⚡ Passo a Passo Rápido

### 1. Criar Repositório

1. Acesse: https://github.com/new
2. Nome: `looker-studio-seatalk` (ou outro)
3. Marque como **Private** (recomendado)
4. Clique em **Create repository**

### 2. Enviar Código

**No terminal/PowerShell:**

```bash
# Navegue até a pasta do projeto
cd "C:\projeto\automação sea talk"

# Inicializa git (se ainda não tiver)
git init

# Adiciona todos os arquivos
git add .

# Commit inicial
git commit -m "Initial commit: Looker Studio to SeaTalk automation"

# Adiciona o repositório remoto (substitua SEU_USUARIO e SEU_REPOSITORIO)
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git

# Envia o código
git branch -M main
git push -u origin main
```

**Ou use a interface do GitHub:**
- No GitHub, clique em "uploading an existing file"
- Arraste todos os arquivos
- Faça commit

### 3. Configurar Secrets

1. No GitHub, vá em: **Settings** → **Secrets and variables** → **Actions**
2. Clique em **New repository secret**
3. Adicione:

   **Secret 1:**
   - Name: `REPORT_URL`
   - Value: `https://lookerstudio.google.com/reporting/b2db60d7-e301-47e9-993d-feed2ae7aa8c/page/p_frvkotnvfd`
   
   **Secret 2:**
   - Name: `WEBHOOK_URL`
   - Value: `https://openapi.seatalk.io/webhook/group/ow74rcc5T5Cit5c2dRZB6Q`
   
   **Secret 3 (Opcional - se precisar de login):**
   - Name: `GOOGLE_EMAIL`
   - Value: `seu_email@gmail.com`
   
   **Secret 4 (Opcional - se precisar de login):**
   - Name: `GOOGLE_PASSWORD`
   - Value: `sua_senha_ou_senha_de_app`

### 4. Testar

1. Vá em **Actions** no GitHub
2. Clique em **Looker Studio → SeaTalk Automation**
3. Clique em **Run workflow** → **Run workflow**
4. Aguarde a execução (pode demorar 2-3 minutos)
5. Veja os logs clicando na execução

### 5. Configurar Agendamento (Opcional)

Edite `.github/workflows/looker-seatalk.yml`:

```yaml
schedule:
  - cron: '0 12 * * *'  # Diariamente às 12h UTC (9h no Brasil)
```

**Converter horário:**
- Brasil (UTC-3): `'0 12 * * *'` = 9h no Brasil
- Use: https://crontab.guru/

## ✅ Pronto!

O GitHub Actions executará automaticamente no horário agendado!

## 🔍 Verificar Execuções

1. Vá em **Actions**
2. Veja as execuções (verde = sucesso, vermelho = erro)
3. Clique para ver logs detalhados

## 🐛 Problemas?

### Erro: "Secrets not found"
- Verifique se configurou os secrets corretamente
- Nomes devem ser exatos: `REPORT_URL`, `WEBHOOK_URL`

### Erro: "Playwright not found"
- O workflow instala automaticamente
- Se der erro, verifique os logs

### Screenshot em branco
- Aumente `WAIT_TIME` no secret ou workflow
- Verifique se a URL está correta

## 📝 Próximos Passos

- ✅ Código no GitHub
- ✅ Secrets configurados
- ✅ Workflow criado
- ✅ Teste manual executado
- ✅ Agendamento configurado (opcional)

**Agora é só aguardar!** 🎉

