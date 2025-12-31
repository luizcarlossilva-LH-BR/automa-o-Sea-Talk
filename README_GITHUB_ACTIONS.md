# Deploy no GitHub Actions

Este guia explica como configurar o projeto para rodar automaticamente no GitHub Actions.

## 📋 Pré-requisitos

1. Conta no GitHub
2. Repositório criado (ou este projeto)

## 🚀 Passo a Passo

### 1. Criar Repositório no GitHub

1. Acesse https://github.com/new
2. Crie um novo repositório (pode ser privado)
3. Nome sugerido: `looker-studio-seatalk-automation`

### 2. Fazer Upload do Código

**Opção A: Via Git (Recomendado)**

```bash
# Inicializa git (se ainda não tiver)
git init

# Adiciona arquivos
git add .

# Commit inicial
git commit -m "Initial commit: Looker Studio to SeaTalk automation"

# Adiciona remote do GitHub
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git

# Envia código
git branch -M main
git push -u origin main
```

**Opção B: Via Interface do GitHub**

1. No GitHub, clique em "uploading an existing file"
2. Arraste todos os arquivos do projeto
3. Faça commit

### 3. Configurar Secrets no GitHub

1. No seu repositório, vá em **Settings** → **Secrets and variables** → **Actions**
2. Clique em **New repository secret**
3. Adicione os seguintes secrets:

   - **`REPORT_URL`**: URL do seu relatório do Looker Studio
     ```
     https://lookerstudio.google.com/reporting/b2db60d7-e301-47e9-993d-feed2ae7aa8c/page/p_frvkotnvfd
     ```
   
   - **`WEBHOOK_URL`**: URL do webhook do SeaTalk
     ```
     https://openapi.seatalk.io/webhook/group/ow74rcc5T5Cit5c2dRZB6Q
     ```
   
   - **`GOOGLE_EMAIL`** (opcional): Seu email do Google
   - **`GOOGLE_PASSWORD`** (opcional): Sua senha do Google (ou senha de app)

### 4. Configurar Agendamento

Edite o arquivo `.github/workflows/looker-seatalk.yml` e ajuste o cron:

```yaml
schedule:
  - cron: '0 9 * * *'  # Diariamente às 9h UTC
```

**Exemplos de horários:**

- `'0 9 * * *'` - Diariamente às 9h UTC
- `'0 */6 * * *'` - A cada 6 horas
- `'0 9 * * 1-5'` - Segunda a sexta às 9h UTC
- `'0 9,15 * * *'` - Às 9h e 15h UTC diariamente

**Converter para seu fuso horário:**
- UTC-3 (Brasil): `'0 12 * * *'` = 9h no Brasil
- Use: https://crontab.guru/

### 5. Testar Execução Manual

1. No GitHub, vá em **Actions**
2. Clique em **Looker Studio → SeaTalk Automation**
3. Clique em **Run workflow**
4. Selecione branch e clique em **Run workflow**
5. Aguarde a execução

## ⚙️ Configurações Avançadas

### Executar Manualmente com Parâmetros

No GitHub Actions, você pode executar manualmente e passar:
- URL do relatório diferente
- Tempo de espera diferente

### Ajustar Timeout

Se o relatório demorar muito, ajuste no workflow:

```yaml
timeout-minutes: 15  # Aumente se necessário
```

### Notificações

Adicione notificação em caso de erro (opcional):

```yaml
- name: Notificar em caso de erro
  if: failure()
  uses: actions/github-script@v6
  with:
    script: |
      // Adicione lógica de notificação aqui
```

## 🔐 Segurança

### Secrets vs Variáveis

- **Secrets**: Dados sensíveis (senhas, tokens)
- **Variables**: Dados não sensíveis (URLs públicas)

### Boas Práticas

1. ✅ Use secrets para dados sensíveis
2. ✅ Não commite `.env` ou credenciais
3. ✅ Use senha de app do Google (não senha principal)
4. ✅ Revise logs antes de fazer commit

## 📊 Monitoramento

### Ver Logs

1. Vá em **Actions** no GitHub
2. Clique na execução desejada
3. Veja os logs de cada step

### Verificar Execuções

- ✅ Verde = Sucesso
- ❌ Vermelho = Erro
- 🟡 Amarelo = Em execução

## 🐛 Troubleshooting

### Erro: "Playwright not found"

O workflow já instala automaticamente. Se der erro, verifique se o step de instalação está correto.

### Erro: "Timeout"

Aumente `timeout-minutes` no workflow ou `WAIT_TIME` nas variáveis.

### Erro: "Login failed"

- Verifique se email e senha estão corretos nos secrets
- Use senha de app se tiver 2FA
- Verifique se o relatório não mudou de URL

### Screenshot em branco

- Aumente `WAIT_TIME` (pode precisar de mais tempo)
- Verifique se a URL do relatório está correta
- Veja os artifacts gerados em caso de erro

## 📅 Agendamento Personalizado

### Múltiplos Horários

```yaml
schedule:
  - cron: '0 9 * * *'   # 9h
  - cron: '0 15 * * *'  # 15h
  - cron: '0 21 * * *'  # 21h
```

### Dias Específicos

```yaml
schedule:
  - cron: '0 9 * * 1'   # Segundas às 9h
  - cron: '0 9 * * 5'   # Sextas às 9h
```

## 💡 Dicas

1. **Primeira Execução**: Execute manualmente primeiro para testar
2. **Logs**: Sempre verifique os logs após a primeira execução
3. **Horários**: Teste em horários diferentes para ver qual funciona melhor
4. **Backup**: Mantenha uma cópia local do código

## 📝 Checklist

Antes de fazer deploy:

- [ ] Repositório criado no GitHub
- [ ] Código enviado para o repositório
- [ ] Secrets configurados (REPORT_URL, WEBHOOK_URL)
- [ ] Workflow criado (`.github/workflows/looker-seatalk.yml`)
- [ ] Agendamento configurado
- [ ] Teste manual executado com sucesso
- [ ] Logs verificados

## 🎉 Pronto!

Depois de configurar, o GitHub Actions executará automaticamente no horário agendado!

Para verificar:
1. Vá em **Actions** no seu repositório
2. Veja as execuções agendadas
3. Verifique os logs

