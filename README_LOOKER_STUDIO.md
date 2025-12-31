# Looker Studio → SeaTalk: Envio Automatizado de Screenshots

Este script captura screenshots de relatórios do Looker Studio (Google Data Studio) e envia automaticamente para um grupo no SeaTalk.

## 📋 Requisitos

- Python 3.7+
- Conta Google com acesso ao Looker Studio
- URL do relatório do Looker Studio
- Webhook do SeaTalk

## 🚀 Instalação

### 1. Instalar dependências Python

```bash
pip install -r requirements.txt
```

### 2. Instalar navegadores do Playwright

```bash
playwright install chromium
```

**Nota:** O Playwright precisa baixar o Chromium na primeira vez. Isso pode demorar alguns minutos.

## ⚙️ Configuração

### 1. Obter URL do Relatório

1. Abra o relatório no Looker Studio
2. Copie a URL completa do navegador
3. Exemplo: `https://lookerstudio.google.com/reporting/5122833b-f83e-4786-b6fb-3cb9cd8f84e8/page/p_5k1isy2qwd/edit`

**Dica:** Você pode usar a URL de visualização (sem `/edit`) para uma versão mais limpa:
- URL de edição: `.../edit`
- URL de visualização: `.../view` (recomendado)

### 2. Configurar o Script

Edite o arquivo `looker_studio_to_seatalk.py` e ajuste as variáveis na função `main()`:

```python
# CONFIGURAÇÕES
REPORT_URL = "https://lookerstudio.google.com/reporting/SEU_REPORT_ID"
WEBHOOK_URL = "https://openapi.seatalk.io/webhook/group/SEU_WEBHOOK_ID"

# Se o relatório for privado, você precisa fazer login
EMAIL = None  # "seu_email@gmail.com"  # Descomente se necessário
PASSWORD = None  # "sua_senha"  # Descomente se necessário

# Tempo de espera para o relatório carregar (segundos)
WAIT_TIME = 15  # Aumente se o relatório for grande

# Se False, abre o navegador para você ver (útil para debug)
HEADLESS = True
```

## 📖 Uso

### Execução Básica

```bash
python looker_studio_to_seatalk.py
```

### Uso como Módulo

```python
from looker_studio_to_seatalk import looker_studio_to_seatalk

result = looker_studio_to_seatalk(
    report_url="https://lookerstudio.google.com/reporting/...",
    webhook_url="https://openapi.seatalk.io/webhook/group/...",
    wait_time=15,
    save_screenshot=True
)

if result.get('success'):
    print("✅ Imagem enviada com sucesso!")
    print(f"Message ID: {result['response'].get('message_id')}")
else:
    print(f"❌ Erro: {result.get('error')}")
```

## 🔐 Autenticação

### Relatórios Públicos

Se o relatório for público, não precisa de login:

```python
result = looker_studio_to_seatalk(
    report_url="...",
    webhook_url="...",
    email=None,
    password=None
)
```

### Relatórios Privados

Se o relatório for privado, você precisa fazer login:

```python
result = looker_studio_to_seatalk(
    report_url="...",
    webhook_url="...",
    email="seu_email@gmail.com",
    password="sua_senha"
)
```

**⚠️ Segurança:** Para maior segurança, use variáveis de ambiente:

```python
import os

EMAIL = os.getenv("GOOGLE_EMAIL")
PASSWORD = os.getenv("GOOGLE_PASSWORD")
```

## 🎯 Funcionalidades

### Captura de Screenshot

- Captura screenshot completo da página (full page)
- Remove elementos de UI (menus, botões) automaticamente
- Aguarda o relatório carregar completamente antes de capturar

### Envio para SeaTalk

- Codifica imagem em base64
- Envia via webhook do SeaTalk
- Retorna Message ID para confirmação

## ⚙️ Parâmetros

| Parâmetro | Tipo | Descrição | Padrão |
|-----------|------|-----------|--------|
| `report_url` | str | URL do relatório do Looker Studio | - |
| `webhook_url` | str | URL do webhook do SeaTalk | - |
| `email` | str (opcional) | Email para login | None |
| `password` | str (opcional) | Senha para login | None |
| `wait_time` | int | Tempo de espera (segundos) | 15 |
| `save_screenshot` | bool | Salvar screenshot localmente | False |
| `headless` | bool | Executar sem abrir navegador | True |

## 🔄 Automação

### Agendamento com Cron (Linux/Mac)

```bash
# Executa diariamente às 9h
0 9 * * * /usr/bin/python3 /caminho/para/looker_studio_to_seatalk.py
```

### Agendamento com Task Scheduler (Windows)

1. Abra o **Agendador de Tarefas**
2. Crie uma nova tarefa
3. Configure para executar `python looker_studio_to_seatalk.py`
4. Defina o agendamento desejado

### Agendamento com Python (schedule)

```python
import schedule
import time
from looker_studio_to_seatalk import looker_studio_to_seatalk

def enviar_relatorio():
    looker_studio_to_seatalk(
        report_url="...",
        webhook_url="...",
        wait_time=15
    )

# Agenda para executar diariamente às 9h
schedule.every().day.at("09:00").do(enviar_relatorio)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## 🐛 Solução de Problemas

### Erro: "playwright not installed"

```bash
playwright install chromium
```

### Relatório não carrega completamente

Aumente o `wait_time`:

```python
wait_time=30  # Aumente para relatórios grandes
```

### Erro de autenticação

- Verifique se o email e senha estão corretos
- Se usar 2FA, pode precisar de senha de app
- Tente executar com `headless=False` para ver o que acontece

### Screenshot em branco

- Verifique se a URL está correta
- Tente usar a URL de visualização (`/view`) em vez de edição (`/edit`)
- Aumente o `wait_time`
- Execute com `headless=False` para ver o que está acontecendo

### Imagem muito grande

O SeaTalk tem limite de 5MB. Se a imagem for muito grande:

- Reduza o tamanho do viewport no código
- Use `full_page=False` (modifique o código)
- Compresse a imagem antes de enviar

## 📝 Exemplo Completo

```python
from looker_studio_to_seatalk import looker_studio_to_seatalk
import os

# Configurações
config = {
    "report_url": "https://lookerstudio.google.com/reporting/...",
    "webhook_url": "https://openapi.seatalk.io/webhook/group/...",
    "email": os.getenv("GOOGLE_EMAIL"),
    "password": os.getenv("GOOGLE_PASSWORD"),
    "wait_time": 20,
    "save_screenshot": True,
    "headless": True
}

# Executa
result = looker_studio_to_seatalk(**config)

# Verifica resultado
if result.get('success'):
    print("✅ Sucesso!")
    print(f"Message ID: {result['response'].get('message_id')}")
else:
    print(f"❌ Erro: {result.get('error')}")
```

## 🔒 Segurança

### Variáveis de Ambiente (Recomendado)

```bash
# Linux/Mac
export GOOGLE_EMAIL="seu_email@gmail.com"
export GOOGLE_PASSWORD="sua_senha"
export SEATALK_WEBHOOK_URL="https://openapi.seatalk.io/webhook/group/..."

# Windows PowerShell
$env:GOOGLE_EMAIL="seu_email@gmail.com"
$env:GOOGLE_PASSWORD="sua_senha"
$env:SEATALK_WEBHOOK_URL="https://openapi.seatalk.io/webhook/group/..."
```

### Senha de App (2FA)

Se você usa autenticação de dois fatores:

1. Acesse: https://myaccount.google.com/apppasswords
2. Crie uma senha de app
3. Use essa senha no script (não sua senha normal)

## 📊 Dicas

1. **URL de Visualização:** Use `/view` em vez de `/edit` para uma captura mais limpa
2. **Tempo de Espera:** Relatórios grandes podem precisar de 20-30 segundos
3. **Debug:** Use `headless=False` para ver o que está acontecendo
4. **Múltiplos Relatórios:** Crie uma lista e itere sobre ela

## 🆘 Suporte

Se encontrar problemas:

1. Execute com `headless=False` para ver o navegador
2. Verifique os logs de erro
3. Aumente o `wait_time`
4. Verifique se o relatório está acessível no navegador

