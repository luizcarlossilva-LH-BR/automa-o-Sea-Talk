"""
Exemplo simples de uso do envio de imagem para SeaTalk
"""

from test_send_image_seatalk import send_image_to_seatalk

# Exemplo básico
def exemplo_simples():
    """Exemplo mais simples de uso"""
    
    # Configurações
    imagem = "sua_imagem.png"
    url_api = "https://api.seatalk.io/v1/messages"  # Ajuste conforme a API do SeaTalk
    token = "seu_token_de_autenticacao"
    
    # Envia a imagem
    resultado = send_image_to_seatalk(
        image_path=imagem,
        webhook_url=url_api,
        token=token
    )
    
    # Verifica o resultado
    if resultado['success']:
        print("✅ Imagem enviada com sucesso!")
        print(f"Resposta: {resultado['response']}")
    else:
        print(f"❌ Erro: {resultado.get('error')}")


if __name__ == "__main__":
    exemplo_simples()

