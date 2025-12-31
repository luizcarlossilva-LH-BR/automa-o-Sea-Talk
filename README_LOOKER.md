# Looker → SeaTalk: Envio Automatizado de Imagens

Este script permite buscar imagens do Looker (dashboards, looks ou queries) e enviá-las automaticamente para um grupo no SeaTalk.

## Arquivos

- **`looker_to_seatalk_simple.py`** - Versão simplificada (recomendada, usa apenas `requests`)
- **`looker_to_seatalk.py`** - Versão completa com SDK do Looker (opcional)

## Instalação

### Versão Simplificada (Recomendada)

```bash
pip install requests
```

### Versão com SDK

```bash
pip install requests looker-sdk
```

## Configuração

### 1. Obter Credenciais do Looker

1. Acesse o Looker como administrador
2. Vá em **Admin** → **API**
3. Crie uma nova aplicação ou use uma existente
4. Anote o **Client ID** e **Client Secret**
5. Anote a **URL base** do seu Looker (ex: `https://yourcompany.looker.com`)

### 2. Obter IDs do Looker

Você precisa de um dos seguintes IDs:

- **Dashboard ID**: Encontrado na URL do dashboard
  - Exemplo: `https://yourcompany.looker.com/dashboards/123` → ID é `123`
- **Look ID**: Encontrado na URL do look
  - Exemplo: `https://yourcompany.looker.com/looks/456` → ID é `456`
- **Query ID**: Pode ser obtido via API ou na URL da query

### 3. Configurar o Script

Edite o arquivo `looker_to_seatalk_simple.py` e ajuste as variáveis na função `main()`:

```python
# CONFIGURAÇÕES DO LOOKER
LOOKER_URL = "https://yourcompany.looker.com"
LOOKER_CLIENT_ID = "seu_client_id"
LOOKER_CLIENT_SECRET = "seu_client_secret"

# CONFIGURAÇÕES DO SEATALK
WEBHOOK_URL = "https://openapi.seatalk.io/webhook/group/ow74rcc5T5Cit5c2dRZB6Q"

# CONFIGURAÇÕES DE EXPORTAÇÃO
DASHBOARD_ID = "123"  # Escolha dashboard, look ou query
LOOK_ID = None
QUERY_ID = None
OUTPUT_FORMAT = "png"  # png, jpeg, pdf
```

## Uso

### Execução Básica

```bash
python looker_to_seatalk_simple.py
```

### Uso como Módulo

```python
from looker_to_seatalk_simple import looker_to_seatalk

result = looker_to_seatalk(
    looker_url="https://yourcompany.looker.com",
    looker_client_id="seu_client_id",
    looker_client_secret="seu_client_secret",
    webhook_url="https://openapi.seatalk.io/webhook/group/...",
    dashboard_id="123",
    output_format="png"
)

if result['success']:
    print("✅ Imagem enviada com sucesso!")
    print(f"Message ID: {result['response'].get('message_id')}")
else:
    print(f"❌ Erro: {result.get('error')}")
```

## Funcionalidades

### Tipos de Exportação Suportados

1. **Dashboard**: Exporta um dashboard completo como imagem
2. **Look**: Exporta um look específico como imagem
3. **Query**: Exporta o resultado de uma query como imagem

### Formatos Suportados

- **PNG** (recomendado para imagens)
- **JPEG** (para fotos/gráficos)
- **PDF** (para relatórios completos)

## Automação

### Agendamento com Cron (Linux/Mac)

```bash
# Executa diariamente às 9h
0 9 * * * /usr/bin/python3 /caminho/para/looker_to_seatalk_simple.py
```

### Agendamento com Task Scheduler (Windows)

1. Abra o **Agendador de Tarefas**
2. Crie uma nova tarefa
3. Configure para executar `python looker_to_seatalk_simple.py`
4. Defina o agendamento desejado

### Agendamento com Python (schedule)

```python
import schedule
import time
from looker_to_seatalk_simple import looker_to_seatalk

def enviar_relatorio():
    looker_to_seatalk(
        looker_url="...",
        looker_client_id="...",
        looker_client_secret="...",
        webhook_url="...",
        dashboard_id="123"
    )

# Agenda para executar diariamente às 9h
schedule.every().day.at("09:00").do(enviar_relatorio)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Solução de Problemas

### Erro de Autenticação

- Verifique se o **Client ID** e **Client Secret** estão corretos
- Certifique-se de que a aplicação tem permissões adequadas no Looker

### Erro ao Buscar Imagem

- Verifique se o **ID** (dashboard/look/query) está correto
- Certifique-se de que você tem permissão para acessar o recurso
- Alguns dashboards podem demorar para renderizar - aumente o timeout se necessário

### Erro ao Enviar para SeaTalk

- Verifique se a **URL do webhook** está correta
- Certifique-se de que a imagem não excede 5MB
- Verifique a conexão com a internet

### Imagem muito grande

- Use formato JPEG em vez de PNG para reduzir o tamanho
- Considere exportar apenas visualizações específicas em vez do dashboard completo

## Exemplo Completo

```python
from looker_to_seatalk_simple import looker_to_seatalk

# Configurações
config = {
    "looker_url": "https://yourcompany.looker.com",
    "looker_client_id": "abc123",
    "looker_client_secret": "xyz789",
    "webhook_url": "https://openapi.seatalk.io/webhook/group/ow74rcc5T5Cit5c2dRZB6Q",
    "dashboard_id": "123",
    "output_format": "png",
    "save_temp_file": True
}

# Executa
result = looker_to_seatalk(**config)

# Verifica resultado
if result.get('success'):
    print("✅ Sucesso!")
    print(f"Message ID: {result['response'].get('message_id')}")
else:
    print(f"❌ Erro: {result.get('error')}")
```

## Notas Importantes

- As credenciais do Looker devem ser mantidas seguras (use variáveis de ambiente)
- O token de acesso do Looker expira após um tempo - o script faz nova autenticação a cada execução
- Imagens muito grandes podem demorar para processar
- O SeaTalk pode ter limitações de tamanho de arquivo (geralmente 5MB)

## Variáveis de Ambiente (Recomendado)

Para maior segurança, use variáveis de ambiente:

```python
import os

LOOKER_URL = os.getenv("LOOKER_URL")
LOOKER_CLIENT_ID = os.getenv("LOOKER_CLIENT_ID")
LOOKER_CLIENT_SECRET = os.getenv("LOOKER_CLIENT_SECRET")
WEBHOOK_URL = os.getenv("SEATALK_WEBHOOK_URL")
```

Configure no sistema:
```bash
# Linux/Mac
export LOOKER_URL="https://yourcompany.looker.com"
export LOOKER_CLIENT_ID="seu_client_id"
export LOOKER_CLIENT_SECRET="seu_client_secret"
export SEATALK_WEBHOOK_URL="https://openapi.seatalk.io/webhook/group/..."

# Windows
set LOOKER_URL=https://yourcompany.looker.com
set LOOKER_CLIENT_ID=seu_client_id
set LOOKER_CLIENT_SECRET=seu_client_secret
set SEATALK_WEBHOOK_URL=https://openapi.seatalk.io/webhook/group/...
```

