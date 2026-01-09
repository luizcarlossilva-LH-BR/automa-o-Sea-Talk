# Configurar Google Service Account para Planilha Privada

## Passo 1: Criar Projeto no Google Cloud

1. Acesse: https://console.cloud.google.com/
2. Clique em **Selecionar projeto** (topo da página)
3. Clique em **Novo Projeto**
4. Nome: `dashboard-seatalk` (ou outro nome)
5. Clique em **Criar**

## Passo 2: Ativar Google Sheets API

1. No menu lateral, vá em **APIs e Serviços** → **Biblioteca**
2. Pesquise por **Google Sheets API**
3. Clique nela e depois em **Ativar**

## Passo 3: Criar Service Account

1. No menu lateral, vá em **APIs e Serviços** → **Credenciais**
2. Clique em **Criar Credenciais** → **Conta de serviço**
3. Preencha:
   - Nome: `sheets-reader`
   - ID: `sheets-reader` (gerado automaticamente)
4. Clique em **Criar e Continuar**
5. Em "Conceder acesso", pule clicando em **Continuar**
6. Clique em **Concluir**

## Passo 4: Gerar Chave JSON

1. Na lista de contas de serviço, clique na conta criada (`sheets-reader@...`)
2. Vá na aba **Chaves**
3. Clique em **Adicionar chave** → **Criar nova chave**
4. Selecione **JSON**
5. Clique em **Criar**
6. O arquivo JSON será baixado automaticamente

## Passo 5: Compartilhar a Planilha

1. Abra o arquivo JSON baixado
2. Copie o valor do campo `"client_email"` (ex: `sheets-reader@projeto.iam.gserviceaccount.com`)
3. Abra sua planilha no Google Sheets
4. Clique em **Compartilhar**
5. Cole o email do Service Account
6. Selecione **Leitor** (ou Editor se precisar escrever)
7. Clique em **Enviar**

## Passo 6: Configurar no Streamlit Cloud

### Opção A: Colar o JSON direto (mais fácil)

1. No Streamlit Cloud, vá em **Settings** → **Secrets**
2. Cole assim:

```toml
GOOGLE_SHEET_ID = "seu_sheet_id_aqui"
SHEET_NAME_SOC = "SOC"
SHEET_NAME_HUB = "HUB"

[gcp_service_account]
type = "service_account"
project_id = "seu-projeto"
private_key_id = "abc123..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "sheets-reader@seu-projeto.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

### Opção B: JSON em uma linha

1. Converta o JSON para uma única linha (remova quebras de linha)
2. No Streamlit Cloud, cole assim:

```toml
GOOGLE_SHEET_ID = "seu_sheet_id_aqui"
GOOGLE_CREDENTIALS = '{"type":"service_account","project_id":"...","private_key":"..."}'
```

## Passo 7: Configurar no GitHub Actions

1. Vá no repositório GitHub → **Settings** → **Secrets and variables** → **Actions**
2. Adicione os secrets:
   - `GOOGLE_SHEET_ID`: ID da planilha
   - `GOOGLE_CREDENTIALS`: O JSON completo (em uma linha)

---

## Dicas

- O email do Service Account parece: `nome@projeto.iam.gserviceaccount.com`
- Compartilhe a planilha com esse email como se fosse uma pessoa
- O Service Account só consegue acessar planilhas compartilhadas com ele
