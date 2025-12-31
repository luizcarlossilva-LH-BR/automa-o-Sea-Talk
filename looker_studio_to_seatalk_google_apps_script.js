/**
 * Looker Studio → SeaTalk: Automação via Google Apps Script
 * 
 * Vantagens:
 * - Já autenticado com Google (sem login necessário)
 * - Agendamento nativo (triggers)
 * - Sem necessidade de servidor
 * - Gratuito
 * 
 * Como usar:
 * 1. Acesse: https://script.google.com
 * 2. Crie um novo projeto
 * 3. Cole este código
 * 4. Configure as variáveis abaixo
 * 5. Execute lookerStudioToSeaTalk() para testar
 * 6. Execute setupDailyTrigger() para agendar
 */

// ============================================
// CONFIGURAÇÕES
// ============================================
const CONFIG = {
  // URL do relatório do Looker Studio
  REPORT_URL: 'https://lookerstudio.google.com/reporting/SEU_REPORT_ID/page/SEU_PAGE_ID',
  
  // URL do webhook do SeaTalk
  WEBHOOK_URL: 'https://openapi.seatalk.io/webhook/group/SEU_WEBHOOK_ID',
  
  // Opção 1: Usar serviço de screenshot (recomendado)
  // ScreenshotLayer: https://screenshotlayer.com (100 screenshots/mês grátis)
  SCREENSHOT_API_KEY: 'SUA_API_KEY_AQUI',
  SCREENSHOT_SERVICE: 'screenshotlayer', // 'screenshotlayer' ou 'htmlcsstoimage'
  
  // Opção 2: URL de exportação do Looker Studio (se disponível)
  USE_EXPORT_URL: false,
  EXPORT_URL: '', // URL de exportação direta do relatório
};

// ============================================
// FUNÇÃO PRINCIPAL
// ============================================
function lookerStudioToSeaTalk() {
  try {
    Logger.log('🚀 Iniciando automação Looker Studio → SeaTalk');
    
    // 1. Captura screenshot do relatório
    let imageBase64;
    
    if (CONFIG.USE_EXPORT_URL && CONFIG.EXPORT_URL) {
      // Método 1: Usar URL de exportação direta
      Logger.log('📸 Usando URL de exportação...');
      imageBase64 = getImageFromExportUrl(CONFIG.EXPORT_URL);
    } else {
      // Método 2: Usar serviço de screenshot
      Logger.log('📸 Capturando screenshot via API...');
      imageBase64 = captureScreenshot(CONFIG.REPORT_URL);
    }
    
    if (!imageBase64) {
      throw new Error('Não foi possível capturar a imagem');
    }
    
    Logger.log('✅ Screenshot capturado! Tamanho: ' + (imageBase64.length / 1024).toFixed(2) + ' KB');
    
    // 2. Envia para SeaTalk
    Logger.log('📤 Enviando para SeaTalk...');
    const result = sendToSeaTalk(imageBase64, CONFIG.WEBHOOK_URL);
    
    if (result.success) {
      Logger.log('✅ Imagem enviada com sucesso!');
      Logger.log('📨 Message ID: ' + result.message_id);
      return result;
    } else {
      throw new Error('Erro ao enviar: ' + result.error);
    }
    
  } catch (error) {
    Logger.log('❌ Erro: ' + error.toString());
    throw error;
  }
}

// ============================================
// CAPTURA DE SCREENSHOT
// ============================================

/**
 * Captura screenshot usando ScreenshotLayer
 */
function captureScreenshot(url) {
  try {
    Logger.log('📸 Capturando screenshot via ScreenshotLayer...');
    
    const apiUrl = 'https://api.screenshotlayer.com/api/capture';
    const params = [
      'access_key=' + CONFIG.SCREENSHOT_API_KEY,
      'url=' + encodeURIComponent(url),
      'viewport=1920x1080',
      'width=1920',
      'format=png',
      'delay=10', // Aguarda 10 segundos para carregar completamente
      'fullpage=1' // Captura página completa
    ].join('&');
    
    const response = UrlFetchApp.fetch(apiUrl + '?' + params);
    const responseCode = response.getResponseCode();
    
    if (responseCode === 200) {
      const imageBlob = response.getBlob();
      const imageBase64 = Utilities.base64Encode(imageBlob.getBytes());
      Logger.log('✅ Screenshot capturado com sucesso!');
      return imageBase64;
    } else {
      const errorText = response.getContentText();
      Logger.log('❌ Erro ao capturar screenshot: ' + responseCode);
      Logger.log('Resposta: ' + errorText);
      
      // Tenta método alternativo
      Logger.log('🔄 Tentando método alternativo...');
      return captureScreenshotAlternative(url);
    }
    
  } catch (error) {
    Logger.log('❌ Erro ao capturar screenshot: ' + error.toString());
    throw error;
  }
}

/**
 * Método alternativo: HTML/CSS to Image
 */
function captureScreenshotAlternative(url) {
  try {
    Logger.log('📸 Tentando método alternativo (HTML/CSS to Image)...');
    
    // HTML/CSS to Image API
    const apiUrl = 'https://hcti.io/v1/image';
    const payload = {
      'url': url,
      'viewport_width': 1920,
      'viewport_height': 1080,
      'delay': 10000 // 10 segundos
    };
    
    const options = {
      'method': 'post',
      'headers': {
        'Authorization': 'Basic ' + Utilities.base64Encode(CONFIG.SCREENSHOT_API_KEY + ':'),
        'Content-Type': 'application/json'
      },
      'payload': JSON.stringify(payload)
    };
    
    const response = UrlFetchApp.fetch(apiUrl, options);
    const result = JSON.parse(response.getContentText());
    
    if (result.url) {
      // Baixa a imagem gerada
      Logger.log('📥 Baixando imagem gerada...');
      const imageResponse = UrlFetchApp.fetch(result.url);
      const imageBlob = imageResponse.getBlob();
      return Utilities.base64Encode(imageBlob.getBytes());
    }
    
    throw new Error('Não foi possível gerar screenshot: ' + JSON.stringify(result));
    
  } catch (error) {
    Logger.log('❌ Método alternativo falhou: ' + error.toString());
    throw error;
  }
}

/**
 * Obtém imagem de URL de exportação do Looker Studio
 */
function getImageFromExportUrl(exportUrl) {
  try {
    Logger.log('📥 Obtendo imagem de URL de exportação...');
    
    const response = UrlFetchApp.fetch(exportUrl, {
      'headers': {
        'Authorization': 'Bearer ' + ScriptApp.getOAuthToken()
      }
    });
    
    const responseCode = response.getResponseCode();
    
    if (responseCode === 200) {
      const imageBlob = response.getBlob();
      const imageBase64 = Utilities.base64Encode(imageBlob.getBytes());
      Logger.log('✅ Imagem obtida com sucesso!');
      return imageBase64;
    } else {
      throw new Error('Erro ao obter imagem: HTTP ' + responseCode);
    }
    
  } catch (error) {
    Logger.log('❌ Erro ao obter imagem: ' + error.toString());
    throw error;
  }
}

// ============================================
// ENVIO PARA SEATALK
// ============================================

/**
 * Envia imagem para SeaTalk
 */
function sendToSeaTalk(imageBase64, webhookUrl) {
  try {
    const payload = {
      'tag': 'image',
      'image_base64': {
        'content': imageBase64
      }
    };
    
    const options = {
      'method': 'post',
      'headers': {
        'Content-Type': 'application/json'
      },
      'payload': JSON.stringify(payload),
      'muteHttpExceptions': true
    };
    
    const response = UrlFetchApp.fetch(webhookUrl, options);
    const responseCode = response.getResponseCode();
    const responseText = response.getContentText();
    
    Logger.log('📡 Resposta do SeaTalk: ' + responseCode);
    
    if (responseCode === 200) {
      const result = JSON.parse(responseText);
      
      if (result.code === 0) {
        return {
          'success': true,
          'message_id': result.message_id,
          'response': result
        };
      } else {
        return {
          'success': false,
          'error': result.msg || 'Erro desconhecido',
          'code': result.code,
          'response': result
        };
      }
    } else {
      return {
        'success': false,
        'error': 'HTTP ' + responseCode + ': ' + responseText
      };
    }
    
  } catch (error) {
    return {
      'success': false,
      'error': error.toString()
    };
  }
}

// ============================================
// AGENDAMENTO
// ============================================

/**
 * Configura agendamento diário (executa às 9h)
 */
function setupDailyTrigger() {
  // Remove triggers existentes
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(function(trigger) {
    if (trigger.getHandlerFunction() === 'lookerStudioToSeaTalk') {
      ScriptApp.deleteTrigger(trigger);
    }
  });
  
  // Cria novo trigger diário às 9h
  ScriptApp.newTrigger('lookerStudioToSeaTalk')
    .timeBased()
    .everyDays(1)
    .atHour(9) // 9h da manhã (ajuste conforme necessário)
    .create();
  
  Logger.log('✅ Trigger diário configurado para executar às 9h!');
}

/**
 * Remove todos os triggers
 */
function removeTriggers() {
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(function(trigger) {
    if (trigger.getHandlerFunction() === 'lookerStudioToSeaTalk') {
      ScriptApp.deleteTrigger(trigger);
    }
  });
  Logger.log('✅ Triggers removidos!');
}

