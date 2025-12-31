"""
Exemplo prático de uso: Looker → SeaTalk
"""

import os
from looker_to_seatalk_simple import looker_to_seatalk

def exemplo_basico():
    """
    Exemplo básico de uso
    """
    # CONFIGURAÇÕES - AJUSTE AQUI
    config = {
        "looker_url": "https://yourcompany.looker.com",
        "looker_client_id": "seu_client_id",
        "looker_client_secret": "seu_client_secret",
        "webhook_url": "https://openapi.seatalk.io/webhook/group/ow74rcc5T5Cit5c2dRZB6Q",
        "dashboard_id": "123",  # ID do dashboard
        "output_format": "png",
        "save_temp_file": False
    }
    
    print("🚀 Iniciando envio Looker → SeaTalk...")
    result = looker_to_seatalk(**config)
    
    if result.get('success'):
        print("\n✅ Sucesso! Imagem enviada para o SeaTalk")
        if isinstance(result.get('response'), dict):
            print(f"📨 Message ID: {result['response'].get('message_id')}")
    else:
        print(f"\n❌ Erro: {result.get('error')}")


def exemplo_com_variaveis_ambiente():
    """
    Exemplo usando variáveis de ambiente (mais seguro)
    """
    # Lê configurações das variáveis de ambiente
    config = {
        "looker_url": os.getenv("LOOKER_URL", "https://yourcompany.looker.com"),
        "looker_client_id": os.getenv("LOOKER_CLIENT_ID"),
        "looker_client_secret": os.getenv("LOOKER_CLIENT_SECRET"),
        "webhook_url": os.getenv("SEATALK_WEBHOOK_URL"),
        "dashboard_id": os.getenv("LOOKER_DASHBOARD_ID", "123"),
        "output_format": "png",
        "save_temp_file": False
    }
    
    # Validação
    if not config["looker_client_id"] or not config["looker_client_secret"]:
        print("❌ Erro: Configure as variáveis de ambiente:")
        print("   - LOOKER_URL")
        print("   - LOOKER_CLIENT_ID")
        print("   - LOOKER_CLIENT_SECRET")
        print("   - SEATALK_WEBHOOK_URL")
        print("   - LOOKER_DASHBOARD_ID (opcional)")
        return
    
    print("🚀 Iniciando envio Looker → SeaTalk...")
    result = looker_to_seatalk(**config)
    
    if result.get('success'):
        print("\n✅ Sucesso! Imagem enviada para o SeaTalk")
    else:
        print(f"\n❌ Erro: {result.get('error')}")


def exemplo_multiplos_dashboards():
    """
    Exemplo enviando múltiplos dashboards
    """
    dashboards = [
        {"id": "123", "nome": "Dashboard Vendas"},
        {"id": "456", "nome": "Dashboard Marketing"},
        {"id": "789", "nome": "Dashboard Financeiro"}
    ]
    
    config_base = {
        "looker_url": "https://yourcompany.looker.com",
        "looker_client_id": "seu_client_id",
        "looker_client_secret": "seu_client_secret",
        "webhook_url": "https://openapi.seatalk.io/webhook/group/ow74rcc5T5Cit5c2dRZB6Q",
        "output_format": "png"
    }
    
    print("🚀 Enviando múltiplos dashboards...\n")
    
    for dashboard in dashboards:
        print(f"📊 Processando: {dashboard['nome']} (ID: {dashboard['id']})")
        
        result = looker_to_seatalk(
            **config_base,
            dashboard_id=dashboard['id']
        )
        
        if result.get('success'):
            print(f"✅ {dashboard['nome']} enviado com sucesso!\n")
        else:
            print(f"❌ Erro ao enviar {dashboard['nome']}: {result.get('error')}\n")


if __name__ == "__main__":
    # Escolha qual exemplo executar:
    
    # Exemplo 1: Básico
    exemplo_basico()
    
    # Exemplo 2: Com variáveis de ambiente (recomendado)
    # exemplo_com_variaveis_ambiente()
    
    # Exemplo 3: Múltiplos dashboards
    # exemplo_multiplos_dashboards()

