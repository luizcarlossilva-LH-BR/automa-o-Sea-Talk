# Configuração GitHub Actions - Dashboard SeaTalk

## 📋 Passos para Configurar

### 1. Criar Repositório no GitHub

Se ainda não tem um repositório:
```bash
# No PowerShell, na pasta do projeto
git init
git add .
git commit -m "Dashboard Performance 3PL"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/SEU_REPO.git
git push -u origin main
```

### 2. Configurar Secrets

Acesse seu repositório no GitHub → **Settings** → **Secrets and variables** → **Actions**

Clique em **New repository secret** e adicione:

| Secret | Valor | Obrigatório |
|--------|-------|-------------|
| `SEATALK_WEBHOOK_URL` | `https://openapi.seatalk.io/webhook/group/SEU_ID` | ✅ Sim |
| `GOOGLE_SHEET_ID` | ID da planilha (ver abaixo) | ✅ Sim |
| `GOOGLE_CREDENTIALS` | JSON do Service Account (ver abaixo) | ❌ Só para planilhas privadas |

### 3. Configurar o Google Sheets

#### Opção A: Planilha Pública (mais simples)

1. Abra sua planilha no Google Sheets
2. Clique em **Compartilhar** → **Alterar para qualquer pessoa com o link**
3. Copie o ID da planilha da URL:
   ```
   https://docs.google.com/spreadsheets/d/ESTE_E_O_ID/edit
   ```
4. Adicione o ID como secret `GOOGLE_SHEET_ID`

#### Opção B: Planilha Privada (com Service Account)

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um projeto ou use um existente
3. Ative a **Google Sheets API**
4. Crie uma **Service Account** e baixe o JSON
5. Compartilhe a planilha com o email do Service Account
6. Converta o JSON para base64 e adicione como secret `GOOGLE_CREDENTIALS`

### 4. Estrutura da Planilha

Sua planilha deve ter as seguintes abas:

**Aba "SOC"** com colunas:
- REGIONAL, SOC, EM ATRIBUICAO, AG. CHEGADA, AG. CARREG., CARREGANDO, CARREGADOS
- AG. DESCARGA, NO SHOW, %NS, INFRUT., % INFRUT., CANCELADO, %CANCELADO
- FECHADAS, %ETA ORIGEM, %CPT, %ETA DESTINO, %SPOT, SPOT PEND.

**Aba "HUB"** com as mesmas colunas (substituindo SOC por HUB)

### 3. Executar o Workflow

**Manualmente:**
1. Vá em **Actions** no seu repositório
2. Selecione **Dashboard Performance → SeaTalk**
3. Clique em **Run workflow**

**Automaticamente:**
- O workflow está configurado para rodar Segunda a Sexta às 8h (horário de Brasília)
- Edite o arquivo `.github/workflows/dashboard-seatalk.yml` para ajustar o horário

### 4. Verificar Execução

Após executar:
1. Vá em **Actions** → selecione a execução
2. Veja os logs de cada step
3. Os screenshots ficam disponíveis em **Artifacts**

## ⏰ Horários Programados

Para alterar o horário, edite a linha `cron` no arquivo `.github/workflows/dashboard-seatalk.yml`:

```yaml
schedule:
  # Formato: minuto hora dia-mes mes dia-semana
  # Exemplos:
  - cron: '0 11 * * 1-5'   # Seg-Sex 8h Brasilia (11h UTC)
  - cron: '0 14 * * 1-5'   # Seg-Sex 11h Brasilia (14h UTC)
  - cron: '30 17 * * 1-5'  # Seg-Sex 14:30h Brasilia (17:30h UTC)
```

**Conversão UTC → Brasília**: Brasília = UTC - 3 horas

## 🔧 Troubleshooting

### Erro: "SEATALK_WEBHOOK_URL not found"
- Verifique se o secret foi criado corretamente
- O nome deve ser exatamente `SEATALK_WEBHOOK_URL`

### Dashboard não carrega
- Aumente o `WAIT_TIME` no workflow para 15 ou 20 segundos
- Verifique se o `dashboard_performance.py` está correto

### Screenshots em branco
- O Streamlit pode precisar de mais tempo para iniciar
- Edite o `sleep 10` no workflow para `sleep 20`

## 📁 Arquivos do Projeto

```
├── .github/
│   └── workflows/
│       └── dashboard-seatalk.yml    # Workflow do GitHub Actions
├── dashboard_performance.py          # Dashboard Streamlit
├── enviar_dashboard_seatalk.py       # Script de captura e envio
├── requirements.txt                  # Dependências Python
└── README.md                         # Documentação
```
