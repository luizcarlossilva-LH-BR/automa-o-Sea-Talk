# Looker Studio → SeaTalk: Automação de Envio de Relatórios

Automação para capturar screenshots de relatórios do Looker Studio e enviar automaticamente para grupos no SeaTalk.

## 🚀 Funcionalidades

- ✅ Captura automática de screenshots do Looker Studio
- ✅ Envio automático para grupos no SeaTalk
- ✅ Suporte a perfil persistente do Chrome (login manual uma vez)
- ✅ Execução agendada via GitHub Actions
- ✅ Configuração via variáveis de ambiente

## 📋 Requisitos

- Python 3.7+
- Playwright
- Conta Google com acesso ao Looker Studio
- Webhook do SeaTalk

## 🛠️ Instalação Local

```bash
# Clone o repositório
git clone <seu-repositorio>
cd projeto

# Instale dependências
pip install -r requirements.txt

# Instale navegadores do Playwright
playwright install chromium
```

## ⚙️ Configuração

### 1. Configurar Variáveis de Ambiente

Crie um arquivo `.env` (ou use secrets no GitHub Actions):

```env
REPORT_URL=https://lookerstudio.google.com/reporting/SEU_ID
WEBHOOK_URL=https://openapi.seatalk.io/webhook/group/SEU_WEBHOOK
WAIT_TIME=60
HEADLESS=true
```

### 2. Primeira Execução (Login)

```bash
# Execute com HEADLESS=false para fazer login
python looker_studio_to_seatalk.py
```

- O Chrome abrirá
- Faça login no Gmail manualmente
- O perfil será salvo em `chrome_profile/`

### 3. Próximas Execuções

```bash
# Já estará logado automaticamente
python looker_studio_to_seatalk.py
```

## ☁️ Deploy no GitHub Actions

### Configuração Rápida

1. **Crie repositório no GitHub**
2. **Configure Secrets:**
   - `REPORT_URL` - URL do relatório
   - `WEBHOOK_URL` - URL do webhook
   - `GOOGLE_EMAIL` (opcional)
   - `GOOGLE_PASSWORD` (opcional)

3. **Ajuste agendamento** em `.github/workflows/looker-seatalk.yml`

4. **Execute manualmente** para testar

Veja [README_GITHUB_ACTIONS.md](README_GITHUB_ACTIONS.md) para instruções detalhadas.

## 📁 Estrutura do Projeto

```
.
├── looker_studio_to_seatalk.py  # Script principal
├── test_send_image_seatalk.py   # Teste de envio de imagem
├── requirements.txt              # Dependências
├── .github/
│   └── workflows/
│       └── looker-seatalk.yml   # Workflow do GitHub Actions
├── chrome_profile/              # Perfil do Chrome (não commitar)
└── README.md                    # Este arquivo
```

## 🔧 Uso

### Execução Manual

```python
from looker_studio_to_seatalk import looker_studio_to_seatalk

result = looker_studio_to_seatalk(
    report_url="https://lookerstudio.google.com/...",
    webhook_url="https://openapi.seatalk.io/webhook/...",
    wait_time=60,
    headless=True,
    user_data_dir="./chrome_profile"
)
```

### Execução via GitHub Actions

O workflow executa automaticamente no horário agendado. Você pode também executar manualmente:

1. Vá em **Actions** no GitHub
2. Selecione **Looker Studio → SeaTalk Automation**
3. Clique em **Run workflow**

## 📚 Documentação

- [README_GITHUB_ACTIONS.md](README_GITHUB_ACTIONS.md) - Guia completo de deploy
- [GUIA_PERFIL_PERSISTENTE.md](GUIA_PERFIL_PERSISTENTE.md) - Como usar perfil do Chrome
- [CONFIGURAR_RELATORIO_PRIVADO.md](CONFIGURAR_RELATORIO_PRIVADO.md) - Configuração de login

## 🔒 Segurança

- ⚠️ **Nunca commite** arquivos `.env` ou credenciais
- ✅ Use **Secrets** no GitHub para dados sensíveis
- ✅ Use **senha de app** do Google (não senha principal)
- ✅ O arquivo `.gitignore` já está configurado

## 🐛 Troubleshooting

### Erro de login
- Verifique email e senha
- Use senha de app se tiver 2FA
- Faça login manualmente na primeira vez

### Screenshot em branco
- Aumente `WAIT_TIME`
- Verifique se a URL está correta
- Execute com `HEADLESS=False` para debug

### Erro no GitHub Actions
- Verifique os secrets configurados
- Veja os logs em **Actions**
- Aumente `timeout-minutes` se necessário

## 📝 Licença

Este projeto é de uso interno.

## 🤝 Contribuindo

Para melhorias, abra uma issue ou pull request.
