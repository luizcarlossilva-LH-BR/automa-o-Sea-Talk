# Guia: Usando Perfil Persistente do Chrome

## O que é?

O perfil persistente do Chrome permite que você faça login **uma única vez** e o navegador lembrará da sua sessão nas próximas execuções.

## Como Funciona?

1. **Primeira Execução:**
   - O Chrome abre com um perfil novo
   - Você faz login no Gmail manualmente
   - O perfil é salvo no diretório `chrome_profile`

2. **Próximas Execuções:**
   - O Chrome abre já logado
   - Não precisa fazer login novamente
   - Funciona automaticamente!

## Configuração

No arquivo `looker_studio_to_seatalk.py`, na função `main()`:

```python
# Perfil persistente (RECOMENDADO)
USER_DATA_DIR = os.path.join(os.getcwd(), "chrome_profile")
```

Ou use um caminho absoluto:

```python
USER_DATA_DIR = r"C:\Users\SeuUsuario\chrome_profile_looker"
```

## Primeira Execução

1. Configure `HEADLESS = False` para ver o navegador
2. Execute o script:
   ```bash
   python looker_studio_to_seatalk.py
   ```
3. O Chrome abrirá - faça login no Gmail manualmente
4. Aguarde o script completar
5. Pronto! O perfil está salvo

## Próximas Execuções

1. Pode usar `HEADLESS = True` se quiser
2. Execute normalmente:
   ```bash
   python looker_studio_to_seatalk.py
   ```
3. O Chrome já estará logado automaticamente!

## Vantagens

✅ **Mais confiável** - Não depende de automação de login  
✅ **Mais seguro** - Não precisa salvar senha no código  
✅ **Funciona com 2FA** - Você faz login manualmente uma vez  
✅ **Persistente** - Mantém sessão entre execuções  
✅ **Sem erros de login** - Não precisa lidar com captchas ou mudanças na página de login

## Localização do Perfil

O perfil é salvo em:
- **Relativo**: `chrome_profile/` (na pasta do projeto)
- **Absoluto**: O caminho que você especificar

## Limpeza

Se quiser fazer login novamente (com outra conta, por exemplo):

1. Delete a pasta `chrome_profile`
2. Execute o script novamente
3. Faça login com a nova conta

## Troubleshooting

### Perfil não está salvando login

- Verifique se a pasta `chrome_profile` existe
- Verifique permissões de escrita na pasta
- Tente usar um caminho absoluto

### Quer usar outra conta

- Delete a pasta `chrome_profile`
- Execute novamente e faça login com a nova conta

### Erro ao abrir perfil

- Certifique-se de que o Chrome não está aberto em outro lugar
- Feche todas as instâncias do Chrome
- Execute o script novamente

