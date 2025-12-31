# Guia de Instalação - Looker Studio → SeaTalk

## Passo a Passo Completo

### 1. Instalar Python

Certifique-se de ter Python 3.7 ou superior instalado:

```bash
python --version
```

Se não tiver, baixe em: https://www.python.org/downloads/

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Instalar Playwright

```bash
playwright install chromium
```

**Importante:** Este comando baixa o navegador Chromium (cerca de 200MB). Pode demorar alguns minutos na primeira vez.

### 4. Verificar Instalação

Teste se tudo está funcionando:

```bash
python -c "import playwright; print('Playwright instalado!')"
```

### 5. Configurar o Script

Edite `looker_studio_to_seatalk.py` e configure:

```python
REPORT_URL = "https://lookerstudio.google.com/reporting/SEU_ID/view"
WEBHOOK_URL = "https://openapi.seatalk.io/webhook/group/SEU_WEBHOOK"
```

### 6. Testar

Execute o script:

```bash
python looker_studio_to_seatalk.py
```

## Solução de Problemas Comuns

### Erro: "playwright not found"

```bash
pip install playwright
playwright install chromium
```

### Erro: "chromium not found"

```bash
playwright install chromium
```

### Erro no Windows: "playwright install"

Se der erro no Windows, tente:

```bash
python -m playwright install chromium
```

### Erro de permissão

No Linux/Mac, pode precisar de permissão:

```bash
chmod +x looker_studio_to_seatalk.py
```

## Próximos Passos

1. ✅ Instalação completa
2. 📝 Configure o script com suas URLs
3. 🧪 Teste com um relatório público primeiro
4. 🔄 Configure automação (cron, task scheduler, etc.)

## Verificação Rápida

Execute este comando para verificar se tudo está OK:

```bash
python -c "from looker_studio_to_seatalk import looker_studio_to_seatalk; print('✅ Tudo OK!')"
```

Se não der erro, está tudo instalado corretamente!

