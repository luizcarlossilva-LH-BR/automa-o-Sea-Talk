# Como Configurar para Relatórios Privados

Se o relatório do Looker Studio é **privado**, você precisa configurar o login.

## Opção 1: Configurar Diretamente no Código

Edite o arquivo `looker_studio_to_seatalk.py` e configure:

```python
EMAIL = "seu_email@gmail.com"
PASSWORD = "sua_senha"
```

## Opção 2: Usar Variáveis de Ambiente (Recomendado - Mais Seguro)

### Windows PowerShell:
```powershell
$env:GOOGLE_EMAIL="seu_email@gmail.com"
$env:GOOGLE_PASSWORD="sua_senha"
python looker_studio_to_seatalk.py
```

### Windows CMD:
```cmd
set GOOGLE_EMAIL=seu_email@gmail.com
set GOOGLE_PASSWORD=sua_senha
python looker_studio_to_seatalk.py
```

### Linux/Mac:
```bash
export GOOGLE_EMAIL="seu_email@gmail.com"
export GOOGLE_PASSWORD="sua_senha"
python looker_studio_to_seatalk.py
```

## Autenticação de Dois Fatores (2FA)

Se você usa autenticação de dois fatores no Google:

1. Acesse: https://myaccount.google.com/apppasswords
2. Crie uma **Senha de App**
3. Use essa senha de app no script (não sua senha normal)

## Exemplo Completo

```python
# No arquivo looker_studio_to_seatalk.py, função main():

EMAIL = "seu_email@gmail.com"  # Seu email do Google
PASSWORD = "sua_senha_ou_senha_de_app"  # Senha ou senha de app
```

## Testando

Para testar se o login está funcionando, execute com `headless=False`:

```python
HEADLESS = False  # Isso abre o navegador para você ver
```

Assim você pode ver se o login está funcionando corretamente.

## Segurança

⚠️ **Nunca compartilhe suas credenciais!**

- Use variáveis de ambiente em produção
- Use senha de app em vez da senha principal
- Não commite credenciais no Git

