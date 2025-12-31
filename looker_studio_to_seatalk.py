"""
Script para capturar imagem do Looker Studio e enviar para o SeaTalk
Usa Playwright para automação do navegador
"""

import requests
import os
import base64
import tempfile
import asyncio
from typing import Optional
from playwright.async_api import async_playwright
from playwright.async_api import async_playwright


async def capture_looker_studio_screenshot(
    report_url: str,
    email: Optional[str] = None,
    password: Optional[str] = None,
    wait_time: int = 60,
    output_path: Optional[str] = None,
    headless: bool = True,
    user_data_dir: Optional[str] = None
) -> bytes:
    """
    Captura um screenshot de um relatório do Looker Studio
    
    Args:
        report_url: URL do relatório do Looker Studio
        email: Email para login (DEPRECADO: use user_data_dir com perfil já logado)
        password: Senha para login (DEPRECADO: use user_data_dir com perfil já logado)
        wait_time: Tempo de espera para carregar (segundos)
        output_path: Caminho para salvar screenshot (opcional)
        headless: Se True, executa sem abrir janela do navegador
        user_data_dir: Caminho para o diretório de dados do usuário do Chrome (perfil persistente)
    
    Returns:
        bytes: Dados binários da imagem PNG
    """
    async with async_playwright() as p:
        print("🌐 Iniciando navegador...")
        
        # Se user_data_dir foi fornecido, usa perfil persistente do Chrome
        if user_data_dir:
            print(f"📁 Usando perfil persistente do Chrome: {user_data_dir}")
            print("   (O Chrome já deve estar logado no Gmail neste perfil)")
            print("   Na primeira vez, faça login manualmente. Nas próximas, já estará logado!")
            
            # Cria o diretório se não existir
            os.makedirs(user_data_dir, exist_ok=True)
            
            # Usa launch_persistent_context para manter sessão e cookies
            context = await p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=headless,
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                args=['--disable-blink-features=AutomationControlled']
            )
            
            # Pega a primeira página ou cria uma nova
            pages = context.pages
            if pages:
                page = pages[0]
            else:
                page = await context.new_page()
        else:
            # Modo antigo (sem perfil persistente) - não recomendado
            print("⚠️ Usando modo sem perfil persistente (não recomendado)")
            browser = await p.chromium.launch(headless=headless)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = await context.new_page()
        
        try:
            # Se está usando perfil persistente, não precisa fazer login automático
            if user_data_dir:
                print("✅ Usando perfil persistente - login já deve estar feito")
                print("   Se não estiver logado, faça login manualmente nesta primeira execução")
            
            # Acessa o relatório
            print(f"📊 Acessando relatório: {report_url}")
            await page.goto(report_url, wait_until='domcontentloaded', timeout=60000)
            await asyncio.sleep(3)  # Aguarda página inicial carregar
            
            # Se não está usando perfil persistente e tem email/senha, tenta login automático
            if not user_data_dir and email and password:
                print("🔐 Verificando se precisa fazer login...")
                print(f"📍 URL atual: {page.url}")
                
                # Aguarda mais tempo para ver se redireciona para login
                await asyncio.sleep(5)
                current_url = page.url
                print(f"📍 URL após espera: {current_url}")
                
                is_login_page = 'accounts.google.com' in current_url or 'signin' in current_url.lower() or 'login' in current_url.lower()
                
                # Se não está na página de login, aguarda mais um pouco (pode redirecionar)
                if not is_login_page:
                    print("⏳ Aguardando redirecionamento para login...")
                    await asyncio.sleep(10)  # Aumentado para 10 segundos
                    current_url = page.url
                    print(f"📍 URL após segunda espera: {current_url}")
                    is_login_page = 'accounts.google.com' in current_url or 'signin' in current_url.lower() or 'login' in current_url.lower()
                
                # Verifica se já está no relatório (não precisa login)
                if 'lookerstudio.google.com' in current_url and 'accounts.google.com' not in current_url:
                    print("✅ Já está no relatório, não precisa fazer login!")
                elif is_login_page:
                    print("🔐 Detectada página de login, fazendo login...")
                else:
                    # Tenta fazer login mesmo assim (pode estar em uma página intermediária)
                    print("🔐 Tentando fazer login (página pode não ter redirecionado ainda)...")
                
                try:
                    # Aguarda campo de email aparecer (pode ter diferentes seletores)
                    email_selectors = [
                        '#identifierId', 
                        'input[type="email"]', 
                        'input[name="identifier"]',
                        'input[aria-label*="email" i]',
                        'input[aria-label*="Email" i]',
                        'input[id*="identifier"]'
                    ]
                    email_field = None
                    email_selector_used = None
                    
                    print("🔍 Procurando campo de email...")
                    # Aguarda até 20 segundos pelo campo de email
                    for selector in email_selectors:
                        try:
                            print(f"   Tentando seletor: {selector}")
                            email_field = await page.wait_for_selector(selector, timeout=20000, state='visible')
                            if email_field:
                                email_selector_used = selector
                                print(f"✅ Campo de email encontrado: {selector}")
                                break
                        except Exception as e:
                            print(f"   Seletor {selector} não encontrado: {str(e)[:50]}")
                            continue
                    
                    if not email_field:
                        # Se não encontrou, pode já estar logado ou página diferente
                        print("⚠️ Campo de email não encontrado. Verificando se já está logado...")
                        final_url = page.url
                        if 'lookerstudio.google.com' in final_url and 'accounts.google.com' not in final_url:
                            print("✅ Parece que já está logado ou não precisa de login")
                        else:
                            print("⚠️ Não foi possível encontrar campo de email. Continuando...")
                    else:
                        await page.fill(email_selector_used, email)
                        print("📧 Email preenchido")
                        
                        # Clica em próximo
                        print("🔍 Procurando botão 'Próximo'...")
                        next_selectors = [
                            '#identifierNext', 
                            'button:has-text("Next")', 
                            'button:has-text("Próximo")',
                            'button[type="button"]:has-text("Next")',
                            'button[aria-label*="Next" i]',
                            'button[id*="Next"]'
                        ]
                        clicked = False
                        for next_sel in next_selectors:
                            try:
                                print(f"   Tentando seletor: {next_sel}")
                                next_btn = await page.wait_for_selector(next_sel, timeout=5000, state='visible')
                                if next_btn:
                                    await next_btn.click()
                                    clicked = True
                                    print(f"✅ Botão 'Próximo' clicado: {next_sel}")
                                    break
                            except Exception as e:
                                print(f"   Seletor {next_sel} não encontrado: {str(e)[:50]}")
                                continue
                        
                        if not clicked:
                            print("⚠️ Botão 'Próximo' não encontrado. Tentando método alternativo...")
                            # Tenta pressionar Enter
                            try:
                                await page.keyboard.press('Enter')
                                print("   Pressionou Enter como alternativa")
                                clicked = True
                            except:
                                pass
                        
                        if clicked:
                            print("⏳ Aguardando página de senha carregar...")
                            await asyncio.sleep(5)  # Aumentado para 5 segundos
                            
                            # Preenche senha
                            print("🔍 Procurando campo de senha...")
                            password_selectors = [
                                'input[name="password"]', 
                                'input[type="password"]',
                                'input[aria-label*="password" i]',
                                'input[aria-label*="Password" i]',
                                'input[id*="password"]'
                            ]
                            password_field = None
                            password_selector_used = None
                            
                            for selector in password_selectors:
                                try:
                                    print(f"   Tentando seletor: {selector}")
                                    password_field = await page.wait_for_selector(selector, timeout=15000, state='visible')
                                    if password_field:
                                        password_selector_used = selector
                                        print(f"✅ Campo de senha encontrado: {selector}")
                                        break
                                except Exception as e:
                                    print(f"   Seletor {selector} não encontrado: {str(e)[:50]}")
                                    continue
                            
                            if not password_field:
                                print("⚠️ Campo de senha não encontrado")
                            else:
                                await page.fill(password_selector_used, password)
                                print("🔑 Senha preenchida")
                                
                                # Clica em próximo
                                print("🔍 Procurando botão 'Próximo' da senha...")
                                password_next_selectors = [
                                    '#passwordNext', 
                                    'button:has-text("Next")', 
                                    'button:has-text("Próximo")',
                                    'button[type="button"]:has-text("Next")',
                                    'button[aria-label*="Next" i]',
                                    'button[id*="Next"]'
                                ]
                                clicked = False
                                for next_sel in password_next_selectors:
                                    try:
                                        print(f"   Tentando seletor: {next_sel}")
                                        next_btn = await page.wait_for_selector(next_sel, timeout=5000, state='visible')
                                        if next_btn:
                                            await next_btn.click()
                                            clicked = True
                                            print(f"✅ Botão 'Próximo' da senha clicado: {next_sel}")
                                            break
                                    except Exception as e:
                                        print(f"   Seletor {next_sel} não encontrado: {str(e)[:50]}")
                                        continue
                                
                                if not clicked:
                                    print("⚠️ Botão 'Próximo' da senha não encontrado. Tentando Enter...")
                                    try:
                                        await page.keyboard.press('Enter')
                                        clicked = True
                                    except:
                                        pass
                                
                                if clicked:
                                    print("⏳ Aguardando login completar...")
                                    # Aguarda redirecionamento para o relatório (aguarda até 60 segundos)
                                    max_wait = 60
                                    waited = 0
                                    while waited < max_wait:
                                        await asyncio.sleep(3)
                                        current_url = page.url
                                        print(f"   Aguardando... ({waited}s) URL: {current_url[:80]}")
                                        
                                        # Verifica se está no relatório
                                        if 'lookerstudio.google.com' in current_url and 'accounts.google.com' not in current_url:
                                            print("✅ Redirecionado para o relatório!")
                                            break
                                        
                                        # Verifica se ainda está na página de login (pode ter dado erro)
                                        if 'accounts.google.com' in current_url and waited > 20:
                                            print("⚠️ Ainda na página de login após 20s. Verificando se há erro...")
                                            # Tenta verificar se há mensagem de erro
                                            try:
                                                error_elements = await page.query_selector_all('[role="alert"], .error, [class*="error"]')
                                                if error_elements:
                                                    print("❌ Possível erro no login detectado")
                                            except:
                                                pass
                                        
                                        waited += 3
                                    
                                    await asyncio.sleep(5)  # Aguarda carregar após login
                                    
                                    # Verifica se realmente conseguiu acessar o relatório
                                    final_url = page.url
                                    if 'lookerstudio.google.com' in final_url and 'accounts.google.com' not in final_url:
                                        print("✅ Login realizado com sucesso!")
                                    else:
                                        print(f"⚠️ URL final: {final_url}")
                                        print("⚠️ Pode não ter conseguido fazer login completamente")
                                else:
                                    print("⚠️ Botão de senha 'Próximo' não encontrado")
                
                except Exception as e:
                    print(f"⚠️ Erro no processo de login: {e}")
                    # Verifica se conseguiu acessar o relatório mesmo assim
                    final_url = page.url
                    if 'lookerstudio.google.com' in final_url and 'accounts.google.com' not in final_url:
                        print("✅ Parece que conseguiu acessar o relatório mesmo assim")
                    else:
                        print("❌ Não foi possível fazer login. Verifique email e senha.")
                        raise Exception(f"Erro no login: {e}")
            else:
                print("ℹ️ Email e senha não fornecidos, pulando login")
            
            # VERIFICA SE ESTÁ NO RELATÓRIO ANTES DE CAPTURAR
            print("🔍 Verificando se está no relatório do Looker Studio...")
            final_check_url = page.url
            print(f"📍 URL final: {final_check_url}")
            
            # Se ainda está na página de login, aguarda mais
            if 'accounts.google.com' in final_check_url or 'signin' in final_check_url.lower():
                print("⚠️ Ainda na página de login! Aguardando mais tempo...")
                max_retry = 30  # 30 tentativas de 2 segundos = 60 segundos
                retry_count = 0
                while retry_count < max_retry:
                    await asyncio.sleep(2)
                    current_url = page.url
                    if 'lookerstudio.google.com' in current_url and 'accounts.google.com' not in current_url:
                        print("✅ Finalmente redirecionado para o relatório!")
                        break
                    retry_count += 1
                    if retry_count % 5 == 0:
                        print(f"   Ainda aguardando... ({retry_count * 2}s)")
                
                # Verifica novamente
                final_url_after_wait = page.url
                if 'accounts.google.com' in final_url_after_wait:
                    print("❌ ERRO: Ainda na página de login após aguardar!")
                    print("   Possíveis causas:")
                    print("   - Email ou senha incorretos")
                    print("   - Google pedindo verificação adicional (2FA, captcha)")
                    print("   - Bloqueio de automação pelo Google")
                    raise Exception("Não foi possível sair da página de login do Google")
            
            # Verifica se realmente está no Looker Studio
            if 'lookerstudio.google.com' not in page.url:
                print(f"⚠️ URL atual não é do Looker Studio: {page.url}")
                print("   Aguardando redirecionamento...")
                await asyncio.sleep(10)
            
            # Aguarda o tempo configurado para o relatório carregar
            print(f"⏳ Aguardando {wait_time} segundos para o relatório carregar completamente...")
            await asyncio.sleep(wait_time)
            
            # Verificação final antes de capturar
            final_url_before_screenshot = page.url
            print(f"📍 URL antes de capturar screenshot: {final_url_before_screenshot}")
            
            if 'accounts.google.com' in final_url_before_screenshot:
                print("❌ ERRO CRÍTICO: Ainda na página de login! Não será possível capturar o relatório.")
                raise Exception("Não foi possível acessar o relatório - ainda na página de login do Google")
            
            if 'lookerstudio.google.com' not in final_url_before_screenshot:
                print("⚠️ AVISO: URL não parece ser do Looker Studio")
            
            # Captura screenshot
            print("📸 Capturando screenshot...")
            screenshot_bytes = await page.screenshot(full_page=True, type='png', timeout=30000)
            print(f"✅ Screenshot capturado! Tamanho: {len(screenshot_bytes)} bytes")
            
            # Salva arquivo se solicitado
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(screenshot_bytes)
                print(f"💾 Screenshot salvo em: {output_path}")
            
            return screenshot_bytes
            
        finally:
            if user_data_dir:
                # Com perfil persistente, apenas fecha o contexto (mantém dados salvos)
                await context.close()
                print("🔒 Navegador fechado (perfil salvo)")
            else:
                await browser.close()
                print("🔒 Navegador fechado")


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


async def looker_studio_to_seatalk_async(
    report_url: str,
    webhook_url: str,
    email: Optional[str] = None,
    password: Optional[str] = None,
    wait_time: int = 60,
    save_screenshot: bool = False,
    headless: bool = True,
    user_data_dir: Optional[str] = None
) -> dict:
    """
    Função principal assíncrona: Captura screenshot do Looker Studio e envia para o SeaTalk
    
    Args:
        report_url: URL do relatório do Looker Studio
        webhook_url: URL do webhook do SeaTalk
        email: Email para login (DEPRECADO: use user_data_dir)
        password: Senha para login (DEPRECADO: use user_data_dir)
        wait_time: Tempo de espera para carregar (segundos)
        save_screenshot: Se True, salva o screenshot localmente
        headless: Se True, executa sem abrir janela do navegador
        user_data_dir: Caminho para perfil persistente do Chrome (recomendado)
    
    Returns:
        dict: Resultado da operação
    """
    temp_path = None
    
    try:
        # Captura screenshot
        screenshot_bytes = await capture_looker_studio_screenshot(
            report_url=report_url,
            email=email,
            password=password,
            wait_time=wait_time,
            output_path=temp_path if save_screenshot else None,
            headless=headless,
            user_data_dir=user_data_dir
        )
        
        # Salva sempre para debug (para você verificar se a captura está correta)
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".png",
            prefix="looker_studio_"
        )
        temp_file.write(screenshot_bytes)
        temp_path = temp_file.name
        temp_file.close()
        print(f"💾 Screenshot salvo para verificação em: {temp_path}")
        print(f"   (Abra este arquivo para verificar se a captura está correta)")
        
        # Envia para o SeaTalk
        result = send_image_to_seatalk(
            image_data=screenshot_bytes,
            webhook_url=webhook_url,
            image_format="png"
        )
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
    finally:
        # Limpa arquivo temporário se foi criado
        if temp_path and os.path.exists(temp_path) and not save_screenshot:
            try:
                os.unlink(temp_path)
            except:
                pass


def looker_studio_to_seatalk(
    report_url: str,
    webhook_url: str,
    email: Optional[str] = None,
    password: Optional[str] = None,
    wait_time: int = 60,
    save_screenshot: bool = False,
    headless: bool = True,
    user_data_dir: Optional[str] = None
) -> dict:
    """
    Função principal (wrapper síncrono): Captura screenshot do Looker Studio e envia para o SeaTalk
    
    Args:
        report_url: URL do relatório do Looker Studio
        webhook_url: URL do webhook do SeaTalk
        email: Email para login (DEPRECADO: use user_data_dir)
        password: Senha para login (DEPRECADO: use user_data_dir)
        wait_time: Tempo de espera para carregar (segundos)
        save_screenshot: Se True, salva o screenshot localmente
        headless: Se True, executa sem abrir janela do navegador
        user_data_dir: Caminho para perfil persistente do Chrome (recomendado)
    
    Returns:
        dict: Resultado da operação
    """
    return asyncio.run(looker_studio_to_seatalk_async(
        report_url=report_url,
        webhook_url=webhook_url,
        email=email,
        password=password,
        wait_time=wait_time,
        save_screenshot=save_screenshot,
        headless=headless,
        user_data_dir=user_data_dir
    ))


def main():
    """
    Função principal para teste
    """
    # CONFIGURAÇÕES - Lê de variáveis de ambiente ou usa valores padrão
    # No GitHub Actions, configure como secrets
    REPORT_URL = os.getenv("REPORT_URL", "https://lookerstudio.google.com/reporting/b2db60d7-e301-47e9-993d-feed2ae7aa8c/page/p_frvkotnvfd")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://openapi.seatalk.io/webhook/group/ow74rcc5T5Cit5c2dRZB6Q")
    
    # PERFIL PERSISTENTE DO CHROME
    # Em GitHub Actions, o perfil não persiste entre execuções
    # Por isso, precisamos usar autenticação automática ou outra estratégia
    USER_DATA_DIR = os.path.join(os.getcwd(), "chrome_profile")
    
    # Email e senha (para GitHub Actions, pode ser necessário)
    EMAIL = os.getenv("GOOGLE_EMAIL")
    PASSWORD = os.getenv("GOOGLE_PASSWORD")
    
    # Tempo de espera para o relatório carregar (segundos)
    WAIT_TIME = int(os.getenv("WAIT_TIME", "60"))
    
    # Headless mode (no GitHub Actions sempre true)
    HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
    
    print("=" * 60)
    print("Looker Studio → SeaTalk: Envio Automatizado de Screenshots")
    print("=" * 60)
    print(f"📊 Relatório: {REPORT_URL}")
    print(f"🌐 Webhook: {WEBHOOK_URL}")
    print(f"⏱️  Tempo de espera: {WAIT_TIME}s")
    print(f"👁️  Headless: {HEADLESS}")
    if USER_DATA_DIR:
        print(f"📁 Perfil Chrome: {USER_DATA_DIR}")
    if EMAIL:
        print(f"📧 Email configurado: {EMAIL[:3]}***")
    print("=" * 60)
    
    # Executa o processo
    result = looker_studio_to_seatalk(
        report_url=REPORT_URL,
        webhook_url=WEBHOOK_URL,
        email=EMAIL,
        password=PASSWORD,
        wait_time=WAIT_TIME,
        save_screenshot=True,  # Salva screenshot para debug
        headless=HEADLESS,
        user_data_dir=USER_DATA_DIR  # Usa perfil persistente
    )
    
    print("\n" + "=" * 60)
    if result.get('success'):
        print("✅ Processo concluído com sucesso!")
    else:
        print(f"❌ Erro: {result.get('error')}")
    print("=" * 60)


if __name__ == "__main__":
    main()

