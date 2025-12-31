# Guia: Google Apps Script (Alternativa Recomendada)

## 🎯 Por que usar Google Apps Script?

O Google está bloqueando automação de login. O **Google Apps Script** resolve isso porque:

✅ **Já está autenticado** - Não precisa fazer login  
✅ **Gratuito** - Sem custos  
✅ **Agendamento nativo** - Triggers do Google  
✅ **Sem servidor** - Roda na nuvem do Google  
✅ **Mais confiável** - Não é bloqueado como automação  

## 📋 Como Configurar

### 1. Acesse Google Apps Script

1. Vá para: https://script.google.com
2. Clique em **"Novo projeto"**
3. Cole o código do arquivo `looker_studio_to_seatalk_google_apps_script.js`

### 2. Configure as Variáveis

Edite as variáveis no início do código:

```javascript
const CONFIG = {
  REPORT_URL: 'https://lookerstudio.google.com/reporting/SEU_REPORT_ID',
  WEBHOOK_URL: 'https://openapi.seatalk.io/webhook/group/SEU_WEBHOOK_ID',
  SCREENSHOT_API_KEY: 'SUA_API_KEY',
  SCREENSHOT_SERVICE: 'screenshotlayer'
};
```

### 3. Configure Serviço de Screenshot

**Opção A: ScreenshotLayer (Recomendado)**
- Site: https://screenshotlayer.com
- Grátis: 100 screenshots/mês
- Cadastre-se e obtenha sua API key
- Configure `SCREENSHOT_API_KEY` com sua chave

**Opção B: HTML/CSS to Image**
- Site: https://htmlcsstoimage.com
- Grátis: 50 imagens/mês
- Use o método alternativo no código

### 4. Teste

1. Clique em **"Executar"** → `lookerStudioToSeaTalk`
2. Autorize o acesso (primeira vez)
3. Verifique os logs

### 5. Agende Execução

Execute a função `setupDailyTrigger()` para agendar execução diária às 9h.

## 🔄 Comparação: GitHub Actions vs Google Apps Script

| Recurso | GitHub Actions | Google Apps Script |
|---------|---------------|-------------------|
| Autenticação | Precisa login automático | ✅ Já autenticado |
| Detecção de bot | ❌ Pode ser bloqueado | ✅ Não é bloqueado |
| Custo | Gratuito (limites) | ✅ Gratuito |
| Agendamento | ✅ Cron jobs | ✅ Triggers nativos |
| Screenshot | Playwright (navegador) | API externa |
| Complexidade | Média | ✅ Baixa |

## ⚠️ Limitações do Google Apps Script

- **Precisa serviço de screenshot externo** (mas é gratuito)
- **Limite de execução**: 6 minutos
- **Limite de API calls**: 20.000/dia

## 🚀 Recomendação

**Use Google Apps Script** se:
- Quer solução mais simples
- Não quer lidar com login automático
- Quer algo mais confiável

**Use GitHub Actions** se:
- Quer controle total
- Já tem infraestrutura
- Precisa de mais recursos

