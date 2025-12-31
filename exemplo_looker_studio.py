"""
Exemplo prático de uso: Looker Studio → SeaTalk
"""

import os
from looker_studio_to_seatalk import looker_studio_to_seatalk


def exemplo_basico():
    """
    Exemplo básico de uso
    """
    # CONFIGURAÇÕES - AJUSTE AQUI
    config = {
        "report_url": "https://lookerstudio.google.com/reporting/5122833b-f83e-4786-b6fb-3cb9cd8f84e8/page/p_5k1isy2qwd/view",
        "webhook_url": "https://openapi.seatalk.io/webhook/group/ow74rcc5T5Cit5c2dRZB6Q",
        "wait_time": 15,
        "save_screenshot": True,
        "headless": True
    }
    
    print("🚀 Iniciando captura Looker Studio → SeaTalk...")
    result = looker_studio_to_seatalk(**config)
    
    if result.get('success'):
        print("\n✅ Sucesso! Screenshot enviado para o SeaTalk")
        if isinstance(result.get('response'), dict):
            print(f"📨 Message ID: {result['response'].get('message_id')}")
    else:
        print(f"\n❌ Erro: {result.get('error')}")


def exemplo_com_login():
    """
    Exemplo com login (para relatórios privados)
    """
    config = {
        "report_url": "https://lookerstudio.google.com/reporting/5122833b-f83e-4786-b6fb-3cb9cd8f84e8/page/p_5k1isy2qwd/view",
        "webhook_url": "https://openapi.seatalk.io/webhook/group/ow74rcc5T5Cit5c2dRZB6Q",
        "email": "seu_email@gmail.com",  # Ajuste aqui
        "password": "sua_senha",  # Ajuste aqui
        "wait_time": 20,
        "save_screenshot": True,
        "headless": True
    }
    
    print("🚀 Iniciando captura com login...")
    result = looker_studio_to_seatalk(**config)
    
    if result.get('success'):
        print("\n✅ Sucesso!")
    else:
        print(f"\n❌ Erro: {result.get('error')}")


def exemplo_com_variaveis_ambiente():
    """
    Exemplo usando variáveis de ambiente (mais seguro)
    """
    config = {
        "report_url": os.getenv("LOOKER_STUDIO_REPORT_URL", "https://lookerstudio.google.com/reporting/..."),
        "webhook_url": os.getenv("SEATALK_WEBHOOK_URL", "https://openapi.seatalk.io/webhook/group/..."),
        "email": os.getenv("GOOGLE_EMAIL"),
        "password": os.getenv("GOOGLE_PASSWORD"),
        "wait_time": int(os.getenv("WAIT_TIME", "15")),
        "save_screenshot": False,
        "headless": True
    }
    
    # Validação
    if not config["report_url"] or not config["webhook_url"]:
        print("❌ Erro: Configure as variáveis de ambiente:")
        print("   - LOOKER_STUDIO_REPORT_URL")
        print("   - SEATALK_WEBHOOK_URL")
        print("   - GOOGLE_EMAIL (opcional)")
        print("   - GOOGLE_PASSWORD (opcional)")
        return
    
    print("🚀 Iniciando captura...")
    result = looker_studio_to_seatalk(**config)
    
    if result.get('success'):
        print("\n✅ Sucesso!")
    else:
        print(f"\n❌ Erro: {result.get('error')}")


def exemplo_multiplos_relatorios():
    """
    Exemplo enviando múltiplos relatórios
    """
    relatorios = [
        {
            "nome": "Relatório de Vendas",
            "url": "https://lookerstudio.google.com/reporting/.../view"
        },
        {
            "nome": "Relatório de Marketing",
            "url": "https://lookerstudio.google.com/reporting/.../view"
        }
    ]
    
    config_base = {
        "webhook_url": "https://openapi.seatalk.io/webhook/group/ow74rcc5T5Cit5c2dRZB6Q",
        "wait_time": 15,
        "save_screenshot": False,
        "headless": True
    }
    
    print("🚀 Enviando múltiplos relatórios...\n")
    
    for relatorio in relatorios:
        print(f"📊 Processando: {relatorio['nome']}")
        
        result = looker_studio_to_seatalk(
            report_url=relatorio['url'],
            **config_base
        )
        
        if result.get('success'):
            print(f"✅ {relatorio['nome']} enviado com sucesso!\n")
        else:
            print(f"❌ Erro ao enviar {relatorio['nome']}: {result.get('error')}\n")


def exemplo_debug():
    """
    Exemplo com debug (headless=False para ver o navegador)
    """
    config = {
        "report_url": "https://lookerstudio.google.com/reporting/5122833b-f83e-4786-b6fb-3cb9cd8f84e8/page/p_5k1isy2qwd/view",
        "webhook_url": "https://openapi.seatalk.io/webhook/group/ow74rcc5T5Cit5c2dRZB6Q",
        "wait_time": 20,
        "save_screenshot": True,
        "headless": False  # Abre o navegador para você ver
    }
    
    print("🚀 Iniciando captura (modo debug - navegador visível)...")
    result = looker_studio_to_seatalk(**config)
    
    if result.get('success'):
        print("\n✅ Sucesso!")
    else:
        print(f"\n❌ Erro: {result.get('error')}")


if __name__ == "__main__":
    # Escolha qual exemplo executar:
    
    # Exemplo 1: Básico (relatório público)
    exemplo_basico()
    
    # Exemplo 2: Com login (relatório privado)
    # exemplo_com_login()
    
    # Exemplo 3: Com variáveis de ambiente (recomendado)
    # exemplo_com_variaveis_ambiente()
    
    # Exemplo 4: Múltiplos relatórios
    # exemplo_multiplos_relatorios()
    
    # Exemplo 5: Debug (ver o navegador)
    # exemplo_debug()

