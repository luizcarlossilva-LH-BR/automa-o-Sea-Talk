"""
Captura screenshot do Dashboard de Performance e envia para SeaTalk
Execute: python enviar_dashboard_seatalk.py

IMPORTANTE: O dashboard deve estar rodando primeiro!
Execute em outro terminal: streamlit run dashboard_performance.py
"""

import asyncio
import os
import base64
import requests
from playwright.async_api import async_playwright

# ============================================
# CONFIGURACOES
# ============================================

# URL do dashboard Streamlit (deve estar rodando)
STREAMLIT_URL = os.getenv("STREAMLIT_URL", "http://localhost:8501")

# URL do webhook do SeaTalk
WEBHOOK_URL = os.getenv(
    "WEBHOOK_URL",
    "https://openapi.seatalk.io/webhook/group/ow74rcc5T5Cit5c2dRZB6Q"
)

# Tempo de espera para o dashboard carregar (segundos)
WAIT_TIME = int(os.getenv("WAIT_TIME", "5"))

# Modo headless (True = nao mostra navegador)
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"

# Viewport para capturar tela inteira (1920x1080 = Full HD)
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080


# ============================================
# FUNCOES
# ============================================

async def capture_both_tabs(
    streamlit_url: str,
    wait_time: int = 5,
    headless: bool = True
) -> tuple:
    """
    Captura screenshots das duas abas do dashboard
    
    Args:
        streamlit_url: URL do dashboard Streamlit
        wait_time: Tempo de espera para carregar (segundos)
        headless: Se True, executa sem abrir janela
    
    Returns:
        tuple: (screenshot_tab1_bytes, screenshot_tab2_bytes)
    """
    async with async_playwright() as p:
        print("🌐 Iniciando navegador...")
        
        browser = await p.chromium.launch(headless=headless)
        
        # Viewport grande para capturar dashboard completo em uma tela
        context = await browser.new_context(
            viewport={'width': VIEWPORT_WIDTH, 'height': VIEWPORT_HEIGHT},
            device_scale_factor=1
        )
        page = await context.new_page()
        
        screenshots = []
        
        try:
            print(f"📊 Acessando dashboard: {streamlit_url}")
            await page.goto(streamlit_url, wait_until='networkidle', timeout=60000)
            
            print(f"⏳ Aguardando {wait_time}s para dashboard carregar...")
            await asyncio.sleep(wait_time)
            
            # Aguarda elementos do Streamlit
            try:
                await page.wait_for_selector('[data-testid="stAppViewContainer"]', timeout=10000)
                print("✅ Dashboard carregado!")
            except:
                print("⚠️ Elementos do Streamlit nao detectados, continuando...")
            
            # ========================================
            # CAPTURA ABA 1: Tabelas SOC/HUB
            # ========================================
            print()
            print("=" * 50)
            print("📋 Capturando ABA 1: Tabelas SOC/HUB")
            print("=" * 50)
            
            # Clica na primeira aba
            try:
                tabs = await page.query_selector_all('button[data-baseweb="tab"]')
                if len(tabs) >= 1:
                    await tabs[0].click()
                    print("✅ Clicou na aba 'Tabelas SOC/HUB'")
                    await asyncio.sleep(2)
            except Exception as e:
                print(f"⚠️ Nao foi possivel clicar na aba 1: {e}")
            
            # Aguarda tabelas renderizarem
            try:
                await page.wait_for_selector('[data-testid="stDataFrame"]', timeout=5000)
                print("✅ Tabelas carregadas!")
            except:
                print("⚠️ Aguardando tabelas renderizarem...")
                await asyncio.sleep(2)
            
            # Scroll para o topo
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(0.5)
            
            print("📸 Capturando screenshot da ABA 1...")
            screenshot1 = await page.screenshot(
                full_page=False,
                type='png',
                timeout=30000
            )
            screenshots.append(screenshot1)
            print(f"✅ Screenshot ABA 1 capturado! Tamanho: {len(screenshot1)} bytes")
            
            # Salva screenshot 1
            with open("dashboard_tab1_soc_hub.png", 'wb') as f:
                f.write(screenshot1)
            print("💾 Salvo: dashboard_tab1_soc_hub.png")
            
            # ========================================
            # CAPTURA ABA 2: Report Automatico
            # ========================================
            print()
            print("=" * 50)
            print("📊 Capturando ABA 2: Report Automatico")
            print("=" * 50)
            
            # Clica na segunda aba
            try:
                tabs = await page.query_selector_all('button[data-baseweb="tab"]')
                if len(tabs) >= 2:
                    await tabs[1].click()
                    print("✅ Clicou na aba 'Report Automatico'")
                    await asyncio.sleep(3)  # Mais tempo para carregar os cards
            except Exception as e:
                print(f"⚠️ Nao foi possivel clicar na aba 2: {e}")
            
            # Aguarda conteudo carregar
            await asyncio.sleep(2)
            
            # Scroll para o topo
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(0.5)
            
            print("📸 Capturando screenshot da ABA 2...")
            screenshot2 = await page.screenshot(
                full_page=False,
                type='png',
                timeout=30000
            )
            screenshots.append(screenshot2)
            print(f"✅ Screenshot ABA 2 capturado! Tamanho: {len(screenshot2)} bytes")
            
            # Salva screenshot 2
            with open("dashboard_tab2_report.png", 'wb') as f:
                f.write(screenshot2)
            print("💾 Salvo: dashboard_tab2_report.png")
            
            return tuple(screenshots)
            
        finally:
            await browser.close()
            print()
            print("🔒 Navegador fechado")


def send_to_seatalk(image_data: bytes, webhook_url: str, description: str = "") -> dict:
    """
    Envia imagem para o SeaTalk
    
    Args:
        image_data: Dados binarios da imagem
        webhook_url: URL do webhook do SeaTalk
        description: Descricao para log
    
    Returns:
        dict: Resultado da operacao
    """
    # Codifica em base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    # Prepara payload
    payload = {
        "tag": "image",
        "image_base64": {
            "content": image_base64
        }
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    print(f"📤 Enviando {description}...")
    
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
            print(f"✅ {description} enviada com sucesso!")
            print(f"📨 Message ID: {result.get('message_id', 'N/A')}")
            return {
                'success': True,
                'message_id': result.get('message_id'),
                'response': result
            }
        else:
            print(f"⚠️ Resposta: {result}")
            return {
                'success': False,
                'error': f"Resposta inesperada: {result}",
                'response': result
            }
            
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        print(f"❌ Erro ao enviar: {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }


async def main():
    """Funcao principal"""
    print("=" * 70)
    print("🚀 Dashboard Performance 3PL → SeaTalk (2 TELAS)")
    print("=" * 70)
    print(f"📊 Dashboard URL: {STREAMLIT_URL}")
    print(f"🌐 Webhook URL: {WEBHOOK_URL[:50]}...")
    print(f"⏱️  Tempo de espera: {WAIT_TIME}s")
    print(f"👁️  Headless: {HEADLESS}")
    print(f"📐 Viewport: {VIEWPORT_WIDTH}x{VIEWPORT_HEIGHT}")
    print("=" * 70)
    print()
    
    # Verifica se o Streamlit esta rodando
    try:
        response = requests.get(STREAMLIT_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard Streamlit esta acessivel!")
        else:
            print(f"⚠️ Dashboard retornou status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ ERRO: Dashboard nao esta acessivel em {STREAMLIT_URL}")
        print(f"   Erro: {str(e)}")
        print()
        print("   💡 Execute primeiro em outro terminal:")
        print("      streamlit run dashboard_performance.py")
        print()
        return
    
    print()
    
    # Captura screenshots das duas abas
    try:
        screenshots = await capture_both_tabs(
            streamlit_url=STREAMLIT_URL,
            wait_time=WAIT_TIME,
            headless=HEADLESS
        )
        
        if screenshots and len(screenshots) == 2:
            print()
            print("=" * 70)
            print("📤 ENVIANDO PARA SEATALK")
            print("=" * 70)
            
            results = []
            
            # Envia ABA 1
            print()
            result1 = send_to_seatalk(
                image_data=screenshots[0],
                webhook_url=WEBHOOK_URL,
                description="ABA 1 - Tabelas SOC/HUB"
            )
            results.append(result1)
            
            # Pequena pausa entre envios
            await asyncio.sleep(1)
            
            # Envia ABA 2
            print()
            result2 = send_to_seatalk(
                image_data=screenshots[1],
                webhook_url=WEBHOOK_URL,
                description="ABA 2 - Report Automatico"
            )
            results.append(result2)
            
            # Resumo final
            print()
            print("=" * 70)
            print("📊 RESUMO DO ENVIO")
            print("=" * 70)
            
            success_count = sum(1 for r in results if r.get('success'))
            
            print(f"✅ Enviados com sucesso: {success_count}/2")
            print()
            print("📸 Screenshots salvos:")
            print("   - dashboard_tab1_soc_hub.png")
            print("   - dashboard_tab2_report.png")
            
            if success_count == 2:
                print()
                print("🎉 Todas as telas foram enviadas com sucesso!")
            elif success_count == 0:
                print()
                print("❌ Nenhuma tela foi enviada. Verifique o webhook.")
            else:
                print()
                print("⚠️ Apenas algumas telas foram enviadas.")
            
            print("=" * 70)
        else:
            print("❌ Nao foi possivel capturar os screenshots")
            
    except Exception as e:
        print(f"❌ Erro durante execucao: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
