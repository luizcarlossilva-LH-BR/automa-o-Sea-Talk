"""
Script de teste para envio de imagem ao SeaTalk
"""

import requests
import os
import base64
from pathlib import Path
from typing import Optional


def send_image_to_seatalk_webhook(
    image_path: str,
    webhook_url: str,
    token: Optional[str] = None
) -> dict:
    """
    Envia uma imagem para o SeaTalk via webhook (formato JSON)
    
    Args:
        image_path: Caminho para o arquivo de imagem
        webhook_url: URL do webhook do SeaTalk
        token: Token de autenticação (opcional, geralmente já está na URL)
    
    Returns:
        dict: Resposta da API
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {image_path}")
    
    # Lê e codifica a imagem em base64
    with open(image_path, 'rb') as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Determina o tipo de conteúdo baseado na extensão
    file_extension = Path(image_path).suffix.lower()
    content_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    content_type = content_types.get(file_extension, 'image/jpeg')
    
    # Prepara os headers
    headers = {
        'Content-Type': 'application/json'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'
        # Ou pode ser necessário adicionar o token na URL ou como query parameter
    
    # Formato 1: Payload JSON com imagem em base64 (formato comum para webhooks)
    payload = {
        "tag": "image",
        "image": {
            "image_url": f"data:{content_type};base64,{image_data}"
        }
    }
    
    try:
        response = requests.post(
            webhook_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        
        return {
            'success': True,
            'status_code': response.status_code,
            'response': response.json() if response.content else response.text
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': str(e),
            'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
            'response_text': getattr(e.response, 'text', None) if hasattr(e, 'response') else None
        }


def send_image_to_seatalk_webhook_alternative(
    image_path: str,
    webhook_url: str,
    token: Optional[str] = None
) -> dict:
    """
    Envia uma imagem para o SeaTalk via webhook (formato alternativo)
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {image_path}")
    
    # Lê e codifica a imagem em base64
    with open(image_path, 'rb') as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    file_extension = Path(image_path).suffix.lower()
    content_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    content_type = content_types.get(file_extension, 'image/jpeg')
    
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    # Formato 2: Formato alternativo
    payload = {
        "message_type": "image",
        "image": image_data,
        "content_type": content_type,
        "filename": os.path.basename(image_path)
    }
    
    try:
        response = requests.post(
            webhook_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        
        return {
            'success': True,
            'status_code': response.status_code,
            'response': response.json() if response.content else response.text
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': str(e),
            'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
            'response_text': getattr(e.response, 'text', None) if hasattr(e, 'response') else None
        }

def send_image_to_seatalk_webhook(
    image_path: str,
    webhook_url: str,
    token: Optional[str] = None
) -> dict:
    """
    Envia uma imagem para o SeaTalk via webhook (formato JSON correto)
    
    Args:
        image_path: Caminho para o arquivo de imagem
        webhook_url: URL do webhook do SeaTalk
        token: Token de autenticação (opcional, geralmente já está na URL)
    
    Returns:
        dict: Resposta da API
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {image_path}")
    
    # Lê e codifica a imagem em base64
    with open(image_path, 'rb') as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Prepara os headers
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Formato correto para webhook do SeaTalk
    payload = {
        "tag": "image",
        "image_base64": {
            "content": image_data
        }
    }
    
    try:
        response = requests.post(
            webhook_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        
        return {
            'success': True,
            'status_code': response.status_code,
            'response': response.json() if response.content else response.text
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': str(e),
            'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
            'response_text': getattr(e.response, 'text', None) if hasattr(e, 'response') else None
        }

def main():
    """
    Função principal para teste
    """
    # CONFIGURAÇÕES - AJUSTE AQUI
    IMAGE_PATH = "test_image.png"  # Caminho para sua imagem de teste
    WEBHOOK_URL = "https://openapi.seatalk.io/webhook/group/ow74rcc5T5Cit5c2dRZB6Q"  # URL do webhook
    TOKEN = "0DwNScoT1UHxDyeCCfmtMLzM94OuIQmn"  # Token (pode não ser necessário se já estiver na URL)
    
    print("=" * 50)
    print("Teste de Envio de Imagem para SeaTalk")
    print("=" * 50)
    
    # Verifica se a imagem existe
    if not os.path.exists(IMAGE_PATH):
        print(f"\n❌ Erro: Imagem não encontrada em: {IMAGE_PATH}")
        print("\n💡 Dica: Crie uma imagem de teste ou ajuste o caminho IMAGE_PATH")
        return
    
    print(f"\n📸 Imagem: {IMAGE_PATH}")
    print(f"🌐 URL: {WEBHOOK_URL}")
    print(f"📏 Tamanho: {os.path.getsize(IMAGE_PATH)} bytes")
    
    # Método 1: Formato JSON com tag "image" (formato mais comum para webhooks)
    print("\n" + "-" * 50)
    print("Método 1: Formato JSON (tag: image)")
    print("-" * 50)
    
    result1 = send_image_to_seatalk_webhook(
        image_path=IMAGE_PATH,
        webhook_url=WEBHOOK_URL,
        token=TOKEN
    )
    
    if result1['success']:
        print("✅ Sucesso!")
        print(f"Status Code: {result1['status_code']}")
        print(f"Resposta: {result1['response']}")
    else:
        print("❌ Erro no envio:")
        print(f"Erro: {result1.get('error', 'Desconhecido')}")
        print(f"Status Code: {result1.get('status_code', 'N/A')}")
        if result1.get('response_text'):
            print(f"Resposta do servidor: {result1['response_text']}")
    
    # Método 2: Formato alternativo JSON
    print("\n" + "-" * 50)
    print("Método 2: Formato JSON alternativo")
    print("-" * 50)
    
    result2 = send_image_to_seatalk_webhook_alternative(
        image_path=IMAGE_PATH,
        webhook_url=WEBHOOK_URL,
        token=TOKEN
    )
    
    if result2['success']:
        print("✅ Sucesso!")
        print(f"Status Code: {result2['status_code']}")
        print(f"Resposta: {result2['response']}")
    else:
        print("❌ Erro no envio:")
        print(f"Erro: {result2.get('error', 'Desconhecido')}")
        print(f"Status Code: {result2.get('status_code', 'N/A')}")
        if result2.get('response_text'):
            print(f"Resposta do servidor: {result2['response_text']}")
    
    # Método 3: Multipart/form-data (caso a API aceite)
    print("\n" + "-" * 50)
    print("Método 3: Multipart/form-data")
    print("-" * 50)
    
    result3 = send_image_to_seatalk_multipart(
        image_path=IMAGE_PATH,
        webhook_url=WEBHOOK_URL,
        token=TOKEN
    )
    
    if result3['success']:
        print("✅ Sucesso!")
        print(f"Status Code: {result3['status_code']}")
        print(f"Resposta: {result3['response']}")
    else:
        print("❌ Erro no envio:")
        print(f"Erro: {result3.get('error', 'Desconhecido')}")
        print(f"Status Code: {result3.get('status_code', 'N/A')}")
        if result3.get('response_text'):
            print(f"Resposta do servidor: {result3['response_text']}")
    
    print("\n" + "=" * 50)
    print("Teste concluído!")
    print("=" * 50)


if __name__ == "__main__":
    main()