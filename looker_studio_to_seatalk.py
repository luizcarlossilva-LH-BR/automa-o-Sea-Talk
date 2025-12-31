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
            # Acessa o relatório
            print(f"📊 Acessando relatório: {report_url}")
            await page.goto(report_url, wait_until='domcontentloaded', timeout=60000)
            await asyncio.sleep(5)  # Aguarda página inicial carregar
            
            # Verifica se precisa fazer login
            current_url = page.url
            print(f"📍 URL após acessar relatório: {current_url}")
            
            is_login_page = 'accounts.google.com' in current_url or 'signin' in current_url.lower()
            is_already_logged = 'lookerstudio.google.com' in current_url and 'accounts.google.com' not in current_url
            
            # Se já está logado, não precisa fazer nada
            if is_already_logged:
                print("✅ Já está logado! Continuando...")
            # Se está na página de login e tem email/senha, faz login automático
            elif is_login_page and email and password:
                print("🔐 Detectada página de login. Fazendo login automático...")
                if user_data_dir:
                    print("   (Usando perfil persistente, mas fazendo login na primeira vez)")
            # Se está na página de login mas não tem email/senha
            elif is_login_page and not email:
                print("⚠️ Página de login detectada, mas email/senha não fornecidos!")
                print("   Configure GOOGLE_EMAIL e GOOGLE_PASSWORD nos Secrets do GitHub")
                raise Exception("Login necessário mas credenciais não fornecidas")
            
            # Se precisa fazer login e tem credenciais, faz login automático
            if is_login_page and email and password:
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
                    print("🔍 Procurando campo de email...")
                    print(f"📍 URL atual: {page.url}")
                    
                    # Aguarda a página de login carregar completamente
                    await asyncio.sleep(3)
                    
                    email_selectors = [
                        '#identifierId', 
                        'input[type="email"]', 
                        'input[name="identifier"]',
                        'input[aria-label*="email" i]',
                        'input[aria-label*="Email" i]',
                        'input[id*="identifier"]',
                        'input[placeholder*="email" i]',
                        'input[placeholder*="Email" i]',
                        'input[autocomplete="username"]'
                    ]
                    email_field = None
                    email_selector_used = None
                    
                    # Aguarda até 30 segundos pelo campo de email
                    for selector in email_selectors:
                        try:
                            print(f"   Tentando seletor: {selector}")
                            # Aguarda o elemento estar visível e habilitado
                            email_field = await page.wait_for_selector(
                                selector, 
                                timeout=30000, 
                                state='visible'
                            )
                            
                            if email_field:
                                # Verifica se está realmente visível e interativo
                                is_visible = await email_field.is_visible()
                                is_enabled = await email_field.is_enabled()
                                print(f"   Campo encontrado - Visível: {is_visible}, Habilitado: {is_enabled}")
                                
                                if is_visible and is_enabled:
                                    email_selector_used = selector
                                    print(f"✅ Campo de email encontrado e pronto: {selector}")
                                    break
                                else:
                                    print(f"   Campo encontrado mas não está pronto")
                                    email_field = None
                        except Exception as e:
                            print(f"   Seletor {selector} não encontrado: {str(e)[:50]}")
                            continue
                    
                    if not email_field:
                        # Tenta método alternativo: procurar por qualquer input visível
                        print("⚠️ Seletores específicos não funcionaram. Tentando método alternativo...")
                        try:
                            all_inputs = await page.query_selector_all('input[type="text"], input[type="email"]')
                            print(f"   Encontrados {len(all_inputs)} inputs na página")
                            for inp in all_inputs:
                                is_vis = await inp.is_visible()
                                placeholder = await inp.get_attribute('placeholder') or ''
                                name = await inp.get_attribute('name') or ''
                                print(f"   Input - Visível: {is_vis}, Placeholder: {placeholder}, Name: {name}")
                                if is_vis and ('email' in placeholder.lower() or 'identifier' in name.lower()):
                                    email_field = inp
                                    email_selector_used = 'input[type="text"]'
                                    print("✅ Campo encontrado via método alternativo!")
                                    break
                        except Exception as e:
                            print(f"   Método alternativo falhou: {e}")
                    
                    if not email_field:
                        # Se não encontrou, pode já estar logado ou página diferente
                        print("⚠️ Campo de email não encontrado. Verificando se já está logado...")
                        final_url = page.url
                        if 'lookerstudio.google.com' in final_url and 'accounts.google.com' not in final_url:
                            print("✅ Parece que já está logado ou não precisa de login")
                        else:
                            print("❌ Não foi possível encontrar campo de email!")
                            # Tira screenshot para debug
                            debug_screenshot = await page.screenshot(full_page=True)
                            print(f"   Screenshot de debug capturado (tamanho: {len(debug_screenshot)} bytes)")
                            raise Exception("Campo de email não encontrado na página de login")
                    else:
                        # Preenche o email de forma mais robusta
                        print(f"📧 Preenchendo email: {email[:3]}***")
                        
                        # Limpa o campo primeiro (caso tenha algo)
                        await email_field.click()
                        await asyncio.sleep(0.5)
                        await email_field.fill('')  # Limpa
                        await asyncio.sleep(0.5)
                        
                        # Preenche o email
                        await email_field.fill(email)
                        await asyncio.sleep(1)
                        
                        # Verifica se foi preenchido
                        value = await email_field.input_value()
                        if value == email:
                            print("✅ Email preenchido com sucesso!")
                        else:
                            print(f"⚠️ Email pode não ter sido preenchido corretamente. Valor: {value[:10]}...")
                            # Tenta novamente
                            await email_field.fill(email)
                            await asyncio.sleep(1)
                        
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
                            await asyncio.sleep(8)  # Aumentado para 8 segundos
                            
                            # Verifica se foi redirecionado ou se há erro
                            current_url_after_email = page.url
                            print(f"📍 URL após preencher email: {current_url_after_email}")
                            
                            # Verifica se foi rejeitado pelo Google
                            if 'signin/rejected' in current_url_after_email or 'challenge' in current_url_after_email:
                                print("⚠️ Google rejeitou o login ou pediu verificação adicional")
                                print("   Possíveis causas:")
                                print("   - Google detectou automação")
                                print("   - Necessário 2FA ou verificação")
                                print("   - Captcha necessário")
                                print("   - Conta bloqueada temporariamente")
                                
                                # Tenta verificar se há mensagem de erro na página
                                try:
                                    error_elements = await page.query_selector_all('[role="alert"], .error, [class*="error"], [id*="error"]')
                                    if error_elements:
                                        for elem in error_elements[:3]:  # Primeiros 3 erros
                                            text = await elem.inner_text()
                                            if text:
                                                print(f"   Mensagem de erro: {text[:100]}")
                                except:
                                    pass
                                
                                raise Exception("Google rejeitou o login. Pode ser necessário verificação manual ou 2FA.")
                            
                            # Verifica se já foi redirecionado para o relatório
                            if 'lookerstudio.google.com' in current_url_after_email and 'accounts.google.com' not in current_url_after_email:
                                print("✅ Já foi redirecionado para o relatório após email!")
                                # Pode não precisar de senha (se já estiver logado)
                            else:
                                # Preenche senha
                                print("🔍 Procurando campo de senha...")
                                password_selectors = [
                                    'input[name="password"]', 
                                    'input[type="password"]',
                                    'input[aria-label*="password" i]',
                                    'input[aria-label*="Password" i]',
                                    'input[aria-label*="senha" i]',
                                    'input[aria-label*="Senha" i]',
                                    'input[id*="password"]',
                                    'input[autocomplete="current-password"]',
                                    'input[placeholder*="password" i]',
                                    'input[placeholder*="senha" i]'
                                ]
                                password_field = None
                                password_selector_used = None
                                
                                for selector in password_selectors:
                                    try:
                                        print(f"   Tentando seletor: {selector}")
                                        password_field = await page.wait_for_selector(selector, timeout=20000, state='visible')
                                        if password_field:
                                            # Verifica se está visível e habilitado
                                            is_visible = await password_field.is_visible()
                                            is_enabled = await password_field.is_enabled()
                                            if is_visible and is_enabled:
                                                password_selector_used = selector
                                                print(f"✅ Campo de senha encontrado: {selector}")
                                                break
                                            else:
                                                password_field = None
                                    except Exception as e:
                                        print(f"   Seletor {selector} não encontrado: {str(e)[:50]}")
                                        continue
                                
                                # Se não encontrou, tenta método alternativo
                                if not password_field:
                                    print("⚠️ Seletores específicos não funcionaram. Tentando método alternativo...")
                                    try:
                                        all_inputs = await page.query_selector_all('input[type="password"]')
                                        print(f"   Encontrados {len(all_inputs)} inputs de senha na página")
                                        for inp in all_inputs:
                                            is_vis = await inp.is_visible()
                                            if is_vis:
                                                password_field = inp
                                                password_selector_used = 'input[type="password"]'
                                                print("✅ Campo encontrado via método alternativo!")
                                                break
                                    except Exception as e:
                                        print(f"   Método alternativo falhou: {e}")
                            
                                if not password_field:
                                    # Verifica se não precisa de senha (já logado)
                                    final_check_url = page.url
                                    if 'lookerstudio.google.com' in final_check_url:
                                        print("✅ Não precisa de senha - já está logado!")
                                    else:
                                        print("⚠️ Campo de senha não encontrado")
                                        print(f"   URL atual: {final_check_url}")
                                        # Tira screenshot para debug
                                        try:
                                            debug_screenshot = await page.screenshot(full_page=True)
                                            print(f"   Screenshot de debug capturado (tamanho: {len(debug_screenshot)} bytes)")
                                        except:
                                            pass
                                        raise Exception("Campo de senha não encontrado na página de login")
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
                        print(f"   URL atual: {final_url}")
                        raise Exception(f"Erro no login: {e}")
            
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
    
    # Debug: verifica se as variáveis foram lidas (sem mostrar valores completos)
    if EMAIL:
        print(f"📧 Email configurado: {EMAIL[:3]}***@{EMAIL.split('@')[1] if '@' in EMAIL else '***'}")
    else:
        print("⚠️ GOOGLE_EMAIL não encontrado nas variáveis de ambiente")
    
    if PASSWORD:
        print(f"🔑 Senha configurada: {'*' * len(PASSWORD)}")
    else:
        print("⚠️ GOOGLE_PASSWORD não encontrado nas variáveis de ambiente")
    
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

