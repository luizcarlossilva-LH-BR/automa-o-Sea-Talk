"""
Script simplificado para buscar imagem do Looker e enviar para o SeaTalk
Usa apenas requests (sem SDK do Looker)
"""

import requests
import os
import base64
import tempfile
from typing import Optional


def get_looker_access_token(
    looker_url: str,
    client_id: str,
    client_secret: str
) -> str:
    """
    Obtém um token de acesso do Looker via API
    
    Args:
        looker_url: URL base do Looker (ex: https://yourcompany.looker.com)
        client_id: Client ID da API
        client_secret: Client Secret da API
    
    Returns:
        str: Token de acesso
    """
    url = f"{looker_url}/api/3.1/login"
    data = {
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    print(f"🔐 Autenticando no Looker ({looker_url})...")
    response = requests.post(url, json=data, timeout=30)
    response.raise_for_status()
    
    token = response.json()["access_token"]
    print("✅ Autenticação bem-sucedida!")
    return token


def get_looker_dashboard_image(
    looker_url: str,
    access_token: str,
    dashboard_id: str,
    output_format: str = "png"
) -> bytes:
    """
    Obtém uma imagem de um dashboard do Looker
    
    Args:
        looker_url: URL base do Looker
        access_token: Token de acesso
        dashboard_id: ID do dashboard
        output_format: Formato (png, jpeg, pdf)
    
    Returns:
        bytes: Dados binários da imagem
    """
    url = f"{looker_url}/api/3.1/dashboards/{dashboard_id}/export/{output_format}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print(f"📊 Buscando dashboard {dashboard_id} do Looker...")
    response = requests.get(url, headers=headers, timeout=120)
    response.raise_for_status()
    
    print(f"✅ Imagem obtida! Tamanho: {len(response.content)} bytes")
    return response.content


def get_looker_look_image(
    looker_url: str,
    access_token: str,
    look_id: str,
    output_format: str = "png"
) -> bytes:
    """
    Obtém uma imagem de um look do Looker
    
    Args:
        looker_url: URL base do Looker
        access_token: Token de acesso
        look_id: ID do look
        output_format: Formato (png, jpeg, pdf)
    
    Returns:
        bytes: Dados binários da imagem
    """
    url = f"{looker_url}/api/3.1/looks/{look_id}/run/{output_format}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print(f"📊 Buscando look {look_id} do Looker...")
    response = requests.get(url, headers=headers, timeout=120)
    response.raise_for_status()
    
    print(f"✅ Imagem obtida! Tamanho: {len(response.content)} bytes")
    return response.content


def get_looker_query_image(
    looker_url: str,
    access_token: str,
    query_id: str,
    output_format: str = "png"
) -> bytes:
    """
    Obtém uma imagem de uma query do Looker
    
    Args:
        looker_url: URL base do Looker
        access_token: Token de acesso
        query_id: ID da query
        output_format: Formato (png, jpeg, pdf)
    
    Returns:
        bytes: Dados binários da imagem
    """
    url = f"{looker_url}/api/3.1/queries/{query_id}/run/{output_format}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print(f"📊 Buscando query {query_id} do Looker...")
    response = requests.get(url, headers=headers, timeout=120)
    response.raise_for_status()
    
    print(f"✅ Imagem obtida! Tamanho: {len(response.content)} bytes")
    return response.content


def send_image_to_seatalk(
    image_data: bytes,
    webhook_url: str,
    image_format: str = "png"
) -> dict:
    """
    Envia uma imagem (em bytes) para o SeaTalk
    
    Args:
        image_data: Dados binários da imagem
        webhook_url: URL do webhook do SeaTalk
        image_format: Formato da imagem (png, jpeg)
    
    Returns:
        dict: Resposta da API
    """
    # Codifica a imagem em base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    # Prepara os headers
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Formato correto para webhook do SeaTalk
    payload = {
        "tag": "image",
        "image_base64": {
            "content": image_base64
        }
    }
    
    print(f"📤 Enviando imagem para o SeaTalk...")
    try:
        response = requests.post(
            webhook_url,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        response.raise_for_status()
        result = response.json() if response.content else response.text
        
        if isinstance(result, dict) and result.get('code') == 0:
            print("✅ Imagem enviada com sucesso para o SeaTalk!")
            print(f"📨 Message ID: {result.get('message_id', 'N/A')}")
        else:
            print(f"⚠️ Resposta: {result}")
        
        return {
            'success': True,
            'status_code': response.status_code,
            'response': result
        }
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        print(f"❌ Erro ao enviar: {error_msg}")
        return {
            'success': False,
            'error': error_msg,
            'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
            'response_text': getattr(e.response, 'text', None) if hasattr(e, 'response') else None
        }


def looker_to_seatalk(
    looker_url: str,
    looker_client_id: str,
    looker_client_secret: str,
    webhook_url: str,
    dashboard_id: Optional[str] = None,
    query_id: Optional[str] = None,
    look_id: Optional[str] = None,
    output_format: str = "png",
    save_temp_file: bool = False
) -> dict:
    """
    Função principal: Busca imagem do Looker e envia para o SeaTalk
    
    Args:
        looker_url: URL base do Looker
        looker_client_id: Client ID da API do Looker
        looker_client_secret: Client Secret da API do Looker
        webhook_url: URL do webhook do SeaTalk
        dashboard_id: ID do dashboard (opcional)
        query_id: ID da query (opcional)
        look_id: ID do look (opcional)
        output_format: Formato de saída (png, jpeg)
        save_temp_file: Se True, salva a imagem temporariamente
    
    Returns:
        dict: Resultado da operação
    """
    temp_path = None
    
    try:
        # Autentica no Looker
        access_token = get_looker_access_token(
            looker_url=looker_url,
            client_id=looker_client_id,
            client_secret=looker_client_secret
        )
        
        # Obtém a imagem do Looker
        if dashboard_id:
            image_data = get_looker_dashboard_image(
                looker_url=looker_url,
                access_token=access_token,
                dashboard_id=dashboard_id,
                output_format=output_format
            )
        elif look_id:
            image_data = get_looker_look_image(
                looker_url=looker_url,
                access_token=access_token,
                look_id=look_id,
                output_format=output_format
            )
        elif query_id:
            image_data = get_looker_query_image(
                looker_url=looker_url,
                access_token=access_token,
                query_id=query_id,
                output_format=output_format
            )
        else:
            raise ValueError("É necessário fornecer dashboard_id, query_id ou look_id")
        
        # Salva temporariamente se solicitado
        if save_temp_file:
            temp_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=f".{output_format}",
                prefix="looker_export_"
            )
            temp_file.write(image_data)
            temp_path = temp_file.name
            temp_file.close()
            print(f"💾 Imagem salva temporariamente em: {temp_path}")
        
        # Envia para o SeaTalk
        result = send_image_to_seatalk(
            image_data=image_data,
            webhook_url=webhook_url,
            image_format=output_format
        )
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
    finally:
        # Limpa arquivo temporário se foi criado
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass


def main():
    """
    Função principal para teste
    """
    # CONFIGURAÇÕES DO LOOKER
    LOOKER_URL = "https://yourcompany.looker.com"  # URL do seu Looker
    LOOKER_CLIENT_ID = "seu_client_id"  # Client ID da API
    LOOKER_CLIENT_SECRET = "seu_client_secret"  # Client Secret da API
    
    # CONFIGURAÇÕES DO SEATALK
    WEBHOOK_URL = "https://openapi.seatalk.io/webhook/group/ow74rcc5T5Cit5c2dRZB6Q"
    
    # CONFIGURAÇÕES DE EXPORTAÇÃO
    # Escolha UMA das opções abaixo:
    DASHBOARD_ID = "123"  # ID do dashboard (ou None)
    QUERY_ID = None  # ID da query (ou None)
    LOOK_ID = None  # ID do look (ou None)
    OUTPUT_FORMAT = "png"  # png, jpeg, pdf
    
    print("=" * 60)
    print("Looker → SeaTalk: Envio Automatizado de Imagens")
    print("=" * 60)
    
    # Validação
    if not DASHBOARD_ID and not QUERY_ID and not LOOK_ID:
        print("\n❌ Erro: É necessário fornecer DASHBOARD_ID, QUERY_ID ou LOOK_ID")
        return
    
    # Executa o processo
    result = looker_to_seatalk(
        looker_url=LOOKER_URL,
        looker_client_id=LOOKER_CLIENT_ID,
        looker_client_secret=LOOKER_CLIENT_SECRET,
        webhook_url=WEBHOOK_URL,
        dashboard_id=DASHBOARD_ID,
        query_id=QUERY_ID,
        look_id=LOOK_ID,
        output_format=OUTPUT_FORMAT,
        save_temp_file=True  # Salva arquivo temporário para debug
    )
    
    print("\n" + "=" * 60)
    if result.get('success'):
        print("✅ Processo concluído com sucesso!")
    else:
        print(f"❌ Erro: {result.get('error')}")
    print("=" * 60)


if __name__ == "__main__":
    main()

