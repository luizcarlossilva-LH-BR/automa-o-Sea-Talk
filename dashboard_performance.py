"""
Dashboard de Performance 3PL - Streamlit
Busca dados do Google Sheets
Execute: streamlit run dashboard_performance.py
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os
import json

# ============================================
# CONFIGURACAO DA PAGINA
# ============================================

st.set_page_config(
    page_title="Performance 3PL - SOC/HUB",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# CONFIGURACAO DO GOOGLE SHEETS
# ============================================

def get_config(key: str, default: str = "") -> str:
    """Busca configuracao de secrets do Streamlit ou variaveis de ambiente"""
    # Tenta Streamlit secrets primeiro (Streamlit Cloud)
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except:
        return os.getenv(key, default)

# ID da planilha do Google Sheets (extraido da URL)
# Exemplo: https://docs.google.com/spreadsheets/d/SHEET_ID/edit
SHEET_ID = get_config("GOOGLE_SHEET_ID", "")

# Nomes das abas na planilha
SHEET_NAME_SOC = get_config("SHEET_NAME_SOC", "SOC")
SHEET_NAME_HUB = get_config("SHEET_NAME_HUB", "HUB")
SHEET_NAME_REPORT = get_config("SHEET_NAME_REPORT", "REPORT")

# Credenciais do Service Account (JSON em base64 ou path para arquivo)
GOOGLE_CREDENTIALS = get_config("GOOGLE_CREDENTIALS", "")

# ============================================
# ESTILOS CSS
# ============================================

st.markdown("""
<style>
    .block-container {
        padding-top: 0.5rem;
        padding-bottom: 0rem;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
        max-width: 100%;
    }
    
    .main-header {
        background: linear-gradient(135deg, #FF6B35 0%, #FF8C42 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        margin-bottom: 10px;
        text-align: center;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 1.4rem;
        font-weight: bold;
    }
    
    .section-header {
        background: #FF6B35;
        color: white;
        padding: 5px 10px;
        font-size: 0.9rem;
        font-weight: bold;
        margin: 10px 0 5px 0;
        border-radius: 3px;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stDataFrame {
        font-size: 0.7rem;
    }
    
    div[data-testid="stDataFrame"] > div {
        width: 100% !important;
    }
    
    div[data-testid="stDataFrame"] td {
        text-align: center !important;
    }
    
    div[data-testid="stDataFrame"] th {
        text-align: center !important;
    }
    
    .dvn-scroller.stDataFrameGlideDataEditor {
        width: 100% !important;
    }
    
    div[data-testid="stDataFrame"] {
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    div[data-testid="stDataFrame"] iframe {
        width: 100% !important;
    }
    
    .element-container:has(div[data-testid="stDataFrame"]) {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    div[data-testid="stVerticalBlock"] > div {
        gap: 0 !important;
    }
    
    .element-container:has(div[data-testid="stMarkdownContainer"]) {
        margin-bottom: 0 !important;
    }
    
    div[data-testid="stDataFrame"] > div > div {
        border-left: 2px solid #FF6B35 !important;
        border-right: 2px solid #FF6B35 !important;
    }
    
    .report-title {
        background: #FF6B35;
        color: white;
        padding: 8px 15px;
        text-align: center;
        font-weight: bold;
        font-size: 1rem;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    
    .card-container {
        border: 2px solid #FF6B35;
        border-radius: 5px;
        margin-bottom: 10px;
        background: white;
    }
    
    .card-header {
        background: #fff3e0;
        padding: 8px;
        border-bottom: 1px solid #FF6B35;
    }
    
    .data-source-info {
        background: #e3f2fd;
        border: 1px solid #2196f3;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
        font-size: 0.8rem;
    }
    
    .error-box {
        background: #ffebee;
        border: 1px solid #f44336;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# FUNCOES PARA CARREGAR DADOS DO GOOGLE SHEETS
# ============================================

@st.cache_data(ttl=300)  # Cache por 5 minutos
def load_from_sheets_public(sheet_id: str, sheet_name: str) -> pd.DataFrame:
    """
    Carrega dados de uma planilha PUBLICA do Google Sheets
    A planilha deve estar compartilhada como "Qualquer pessoa com o link pode ver"
    """
    try:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar aba '{sheet_name}': {str(e)}")
        return pd.DataFrame()


def get_google_credentials():
    """
    Obtem credenciais do Google de diferentes fontes:
    1. st.secrets["gcp_service_account"] (formato Streamlit Cloud)
    2. st.secrets["GOOGLE_CREDENTIALS"] (JSON string)
    3. Variavel de ambiente GOOGLE_CREDENTIALS
    """
    import base64
    
    # Tenta formato Streamlit Cloud (gcp_service_account)
    try:
        if "gcp_service_account" in st.secrets:
            return dict(st.secrets["gcp_service_account"])
    except:
        pass
    
    # Tenta GOOGLE_CREDENTIALS como JSON string
    creds_str = get_config("GOOGLE_CREDENTIALS", "")
    if creds_str:
        try:
            if creds_str.startswith('{'):
                return json.loads(creds_str)
            else:
                # Tenta decodificar base64
                return json.loads(base64.b64decode(creds_str).decode('utf-8'))
        except:
            pass
    
    return None


def load_from_sheets_private(sheet_id: str, sheet_name: str) -> pd.DataFrame:
    """
    Carrega dados de uma planilha PRIVADA do Google Sheets usando Service Account
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        creds_dict = get_google_credentials()
        if not creds_dict:
            return pd.DataFrame()
        
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets.readonly',
            'https://www.googleapis.com/auth/drive.readonly'
        ]
        
        credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        gc = gspread.authorize(credentials)
        
        spreadsheet = gc.open_by_key(sheet_id)
        worksheet = spreadsheet.worksheet(sheet_name)
        
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
        
    except Exception as e:
        st.error(f"Erro ao carregar aba '{sheet_name}' (privada): {str(e)}")
        return pd.DataFrame()


def load_sheet_data(sheet_id: str, sheet_name: str) -> pd.DataFrame:
    """
    Carrega dados do Google Sheets (tenta publico primeiro, depois privado)
    """
    if not sheet_id:
        return pd.DataFrame()
    
    # Verifica se tem credenciais configuradas
    has_credentials = get_google_credentials() is not None
    
    if has_credentials:
        # Se tem credenciais, usa direto (planilha privada)
        df = load_from_sheets_private(sheet_id, sheet_name)
        if not df.empty:
            return df
    
    # Tenta carregar como planilha publica
    df = load_from_sheets_public(sheet_id, sheet_name)
    
    return df


# ============================================
# DADOS FICTICIOS (FALLBACK)
# ============================================

def get_sample_data_soc():
    """Retorna dados de exemplo para SOC"""
    return pd.DataFrame({
        'REGIONAL': ['SPC/SUL', 'SPC/SUL', 'SPC/SUL', 'SPI/SUD', 'SPI/SUD', 'SPC/SUL', 'SPC/SUL', 'SPC/SUL', 'SPI/SUD', 'SPC/SUL', 'SPC/SUL', 'SPC/SUL', 'SPC/SUL', 'SPI/SUD', 'SPC/SUL'],
        'SOC': ['SOC-SP5', 'SOC-SP2', 'SOC-BA2', 'SOC-PR1', 'SOC-PE2', 'SOC-SP8', 'SOC-RJ2', 'SOC-MG2', 'SOC-RJ1', 'SOC-SP7', 'SOC-RS2', 'SOC-SP6', 'SOC-SP15', 'SOC-SP25', 'SOC-GO2'],
        'EM ATRIBUICAO': [3, 2, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
        'AG. CHEGADA': [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
        'AG. CARREG.': [89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89],
        'CARREGANDO': [23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23],
        'CARREGADOS': [12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12],
        'AG. DESCARGA': [58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58],
        'NO SHOW': [1, 2, 3, 2, 1, 4, 5, 1, 2, 6, 4, 5, 1, 1, 2],
        '%NS': ['-3.50%', '-3.50%', '-3.50%', '-3.50%', '-3.50%', '-3.50%', '-3.50%', '-3.50%', '-3.50%', '-3.50%', '-3.50%', '-3.50%', '-3.50%', '-3.50%', '-3.50%'],
        'INFRUT.': [10, 15, 1, 2, 1, 9, 1, 2, 6, 4, 5, 1, 1, 2, 2],
        '% INFRUT.': [0.50, 1.00, 0.75, 0.25, 1.00, 0.30, 0.01, 0.10, 0.15, 0.20, 0.21, 0.21, 0.45, 0.02, 0.02],
        'CANCELADO': [50, 25, 35, 20, 40, 27, 24, 22, 19, 17, 14, 12, 9, 4, 2],
        '%CANCELADO': [0.25, 1.50, 0.75, 1.33, 1.58, 1.58, 1.58, 1.58, 1.58, 1.58, 1.58, 1.58, 1.58, 1.58, 1.58],
        'FECHADAS': [2500, 6000, 5000, 7000, 8250, 9500, 10750, 12000, 13250, 14500, 15750, 17000, 18250, 20750, 22000],
        '%ETA ORIGEM': [99.00, 98.00, 96.00, 93.33, 91.33, 89.33, 87.33, 85.33, 83.33, 81.33, 79.33, 77.33, 75.33, 71.33, 69.33],
        '%CPT': [96, 83, 93, 70, 91, 80, 78, 76, 74, 72, 70, 67, 65, 61, 59],
        '%ETA DESTINO': [97, 95, 93, 93, 93, 93, 92, 92, 91, 91, 90, 89, 89, 88, 87],
        '%SPOT': [-7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50],
        'SPOT PEND.': [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
    })


def get_sample_data_hub():
    """Retorna dados de exemplo para HUB"""
    return pd.DataFrame({
        'REGIONAL': ['SPC/SUL', 'SPC/SUL', 'SPC/SUL', 'SPI/SUD', 'SPI/SUD', 'SPI/SUD', 'SPC/SUL', 'SPC/SUL', 'SPI/SUD', 'SPI/SUD', 
                     'SPC/SUL', 'SPC/SUL', 'SPC/SUL', 'SPI/SUD', 'SPI/SUD', 'SPC/SUL', 'SPC/SUL', 'SPC/SUL', 'SPC/SUL', 'SPI/SUD',
                     'SPI/SUD', 'SPI/SUD', 'SPC/SUL', 'SPC/SUL', 'SPC/SUL', 'SPI/SUD', 'SPI/SUD', 'SPI/SUD', 'SPC/SUL', 'SPC/SUL',
                     'SPC/SUL', 'SPC/SUL', 'SPC/SUL'],
        'HUB': ['HUB-LMS-04', 'HUB-LPB-02', 'HUB-LMA-02', 'HUB-LPR-18', 'HUB-LMG-38', 'HUB-LES-03', 'HUB-LPE-06', 'HUB-LMG-21', 
                'HUB-LSP-26', 'HUB-LMG-43', 'HUB-LSP-35', 'HUB-LSP-73', 'HUB-LES-07', 'HUB-LRJ-21', 'HUB-LES-09', 'HUB-LSP-100',
                'HUB-LES-10', 'HUB-LMG-23', 'HUB-LPE-11', 'HUB-LSP-63', 'HUB-LRJ-27', 'HUB-LMG-38', 'HUB-LAL-03', 'HUB-LMT-02',
                'HUB-LSP-97', 'HUB-LSC-13', 'HUB-LRJ-03', 'HUB-LSP-10', 'HUB-LSP-88', 'HUB-LSP-38', 'HUB-LSP-82', 'HUB-LDF-03', 'HUB-LSE-03'],
        'EM ATRIBUICAO': [3, 2, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 3, 5, 4, 4, 5, 5, 2, 4, 4, 5, 3, 2, 4, 4, 5, 3, 2],
        'AG. CHEGADA': [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
        'AG. CARREG.': [89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89, 89],
        'CARREGANDO': [23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23],
        'CARREGADOS': [12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12],
        'AG. DESCARGA': [56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56],
        'NO SHOW': [1, 2, 1, 2, 3, 5, 9, 1, 2, 6, 4, 5, 8, 6, 1, 2, 10, 15, 1, 2, 3, 5, 10, 15, 1, 2, 3, 5, 9, 1, 2, 4, 4],
        '%NS': ['0.01%', '0.10%', '0.15%', '0.20%', '0.21%', '0.25%', '0.30%', '0.45%', '0.01%', '0.10%', '0.15%', '0.20%', '0.21%', '0.25%', '0.30%', 
                '0.45%', '0.01%', '0.10%', '0.15%', '0.01%', '0.10%', '0.15%', '0.20%', '0.21%', '0.25%', '0.01%', '0.10%', '0.15%', '0.20%', '0.21%', '0.25%', '0.01%', '0.10%'],
        'INFRUT.': [10, 15, 1, 2, 3, 5, 9, 1, 2, 6, 4, 5, 8, 6, 1, 2, 10, 15, 1, 2, 3, 5, 10, 15, 1, 2, 3, 5, 9, 1, 2, 4, 4],
        '% INFRUT.': [0.50, 1.00, 0.75, 0.25, 1.00, 0.00, 0.30, 0.01, 0.10, 0.15, 0.20, 0.21, 0.25, 0.30, 0.45, 0.02, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 1.00, 1.00, 0.75, 0.25, 1.00, 0.00, 0.30, 0.01, 0.10, 0.15, 0.20],
        'CANCELADO': [50, 25, 35, 20, 40, 29, 24, 22, 19, 17, 14, 12, 9, 7, 4, 2, -1, -4, -6, -9, -11, -14, -16, -19, -21, -24, -26, -29, -31, -34, -36, -39, -41],
        '%CANCELADO': [0.25, 1.60, 0.75, 1.33, 1.58, 1.58, 1.58, 1.58, 1.58, 1.58, 1.58, 1.58, 1.58, 1.58, 1.58, 1.58, 1.83, 1.93, 1.93, 1.98, 2.02, 2.07, 2.12, 2.17, 2.22, 2.28, 2.31, 2.41, 2.45, 2.60, 2.65, 2.80, 2.80],
        'FECHADAS': [2500, 6000, 5000, 7000, 8250, 9500, 10750, 12000, 13250, 14500, 15750, 17000, 18250, 19500, 20750, 1, 17750, 18515, 19280, 20044, 20809, 21574, 22339, 23103, 23868, 24633, 25397, 26162, 26927, 27692, 28456, 29221, 29986],
        '%ETA ORIGEM': [99.00, 98.00, 95.00, 93.33, 91.33, 89.33, 87.33, 85.33, 83.33, 81.33, 79.33, 77.33, 75.33, 73.33, 71.33, 69.33, 87.33, 85.33, 83.33, 81.33, 69.33, 67.33, 65.33, 53.33, 51.33, 49.33, 47.33, 45.33, 43.33, 41.33, 39.33, 37.33, 35.33],
        '%CPT': [96, 83, 93, 70, 91, 80, 78, 76, 74, 72, 70, 67, 65, 63, 61, 59, 57, 55, 53, 51, 49, 48, 44, 42, 40, 38, 36, 34, 30, 28, 26, 25, 23],
        '%ETA DESTINO': [97, 95, 94, 93, 95, 93, 92, 90, 91, 91, 90, 90, 89, 89, 88, 87, 86, 89, 85, 85, 84, 83, 83, 83, 82, 81, 80, 79, 79, 79, 77, 77, 77],
        '%SPOT': [-7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50, -7.50],
        'SPOT PEND.': [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
    })


# ============================================
# CARREGAR DADOS
# ============================================

# Status da fonte de dados
data_source = "Dados de exemplo (configure GOOGLE_SHEET_ID para usar dados reais)"
using_real_data = False

if SHEET_ID:
    df_soc = load_sheet_data(SHEET_ID, SHEET_NAME_SOC)
    df_hub = load_sheet_data(SHEET_ID, SHEET_NAME_HUB)
    
    if not df_soc.empty and not df_hub.empty:
        data_source = f"Google Sheets (ID: {SHEET_ID[:20]}...)"
        using_real_data = True
    else:
        df_soc = get_sample_data_soc()
        df_hub = get_sample_data_hub()
        data_source = "Dados de exemplo (erro ao carregar do Sheets)"
else:
    df_soc = get_sample_data_soc()
    df_hub = get_sample_data_hub()


# ============================================
# DADOS REPORT AUTOMATICO
# ============================================

report_data = [
    {'soc': 'SOC-MG2', 'data': datetime.now().strftime('%d/%m/%Y'), 'horario': datetime.now().strftime('%Hh'), 'programadas': 108, 'fechadas': 92,
     'abertas': {'EM ATRIBUICAO': (23, 21.30), 'AGUARDANDO CHEGADA': (4, 3.70), 'AGUARDANDO CARREGAMENTO': (8, 7.41),
                 'CARREGANDO': (23, 21.30), 'EM TRANSITO': (40, 37.04), 'AGUARDANDO DESCARGA': (10, 9.26)},
     'performance': {'CANCELADAS': (2, 98.00), 'NO SHOW': (1, 98.50), 'INFRUTIFERAS': (1, 99.00),
                     'ETA ORIGEM': (1, 99.00), 'CPT ORIGEM': (14, 85.00), 'SPOT': (55, 40.00), 'TENDENCIA': (37, 60.00)}},
    {'soc': 'SOC-RJ1', 'data': datetime.now().strftime('%d/%m/%Y'), 'horario': datetime.now().strftime('%Hh'), 'programadas': 108, 'fechadas': 92,
     'abertas': {'EM ATRIBUICAO': (23, 21.30), 'AGUARDANDO CHEGADA': (4, 3.70), 'AGUARDANDO CARREGAMENTO': (8, 7.41),
                 'CARREGANDO': (23, 21.30), 'EM TRANSITO': (40, 37.04), 'AGUARDANDO DESCARGA': (10, 9.26)},
     'performance': {'CANCELADAS': (2, 98.00), 'NO SHOW': (1, 98.50), 'INFRUTIFERAS': (1, 99.00),
                     'ETA ORIGEM': (1, 99.00), 'CPT ORIGEM': (14, 85.00), 'SPOT': (55, 40.00), 'TENDENCIA': (37, 60.00)}},
    {'soc': 'SOC-RJ2', 'data': datetime.now().strftime('%d/%m/%Y'), 'horario': datetime.now().strftime('%Hh'), 'programadas': 108, 'fechadas': 92,
     'abertas': {'EM ATRIBUICAO': (23, 21.30), 'AGUARDANDO CHEGADA': (4, 3.70), 'AGUARDANDO CARREGAMENTO': (8, 7.41),
                 'CARREGANDO': (23, 21.30), 'EM TRANSITO': (40, 37.04), 'AGUARDANDO DESCARGA': (10, 9.26)},
     'performance': {'CANCELADAS': (2, 98.00), 'NO SHOW': (1, 98.50), 'INFRUTIFERAS': (1, 99.00),
                     'ETA ORIGEM': (1, 99.00), 'CPT ORIGEM': (14, 85.00), 'SPOT': (55, 40.00), 'TENDENCIA': (37, 60.00)}},
    {'soc': 'SOC-GO1', 'data': datetime.now().strftime('%d/%m/%Y'), 'horario': datetime.now().strftime('%Hh'), 'programadas': 108, 'fechadas': 92,
     'abertas': {'EM ATRIBUICAO': (23, 21.30), 'AGUARDANDO CHEGADA': (4, 3.70), 'AGUARDANDO CARREGAMENTO': (8, 7.41),
                 'CARREGANDO': (23, 21.30), 'EM TRANSITO': (40, 37.04), 'AGUARDANDO DESCARGA': (10, 9.26)},
     'performance': {'CANCELADAS': (2, 98.00), 'NO SHOW': (1, 98.50), 'INFRUTIFERAS': (1, 99.00),
                     'ETA ORIGEM': (1, 99.00), 'CPT ORIGEM': (14, 85.00), 'SPOT': (55, 40.00), 'TENDENCIA': (37, 60.00)}},
    {'soc': 'SOC-RS1', 'data': datetime.now().strftime('%d/%m/%Y'), 'horario': datetime.now().strftime('%Hh'), 'programadas': 108, 'fechadas': 92,
     'abertas': {'EM ATRIBUICAO': (23, 21.30), 'AGUARDANDO CHEGADA': (4, 3.70), 'AGUARDANDO CARREGAMENTO': (8, 7.41),
                 'CARREGANDO': (23, 21.30), 'EM TRANSITO': (40, 37.04), 'AGUARDANDO DESCARGA': (10, 9.26)},
     'performance': {'CANCELADAS': (2, 98.00), 'NO SHOW': (1, 98.50), 'INFRUTIFERAS': (1, 99.00),
                     'ETA ORIGEM': (1, 99.00), 'CPT ORIGEM': (14, 85.00), 'SPOT': (55, 40.00), 'TENDENCIA': (37, 60.00)}},
    {'soc': 'SOC-SP8', 'data': datetime.now().strftime('%d/%m/%Y'), 'horario': datetime.now().strftime('%Hh'), 'programadas': 108, 'fechadas': 92,
     'abertas': {'EM ATRIBUICAO': (23, 21.30), 'AGUARDANDO CHEGADA': (4, 3.70), 'AGUARDANDO CARREGAMENTO': (8, 7.41),
                 'CARREGANDO': (23, 21.30), 'EM TRANSITO': (40, 37.04), 'AGUARDANDO DESCARGA': (10, 9.26)},
     'performance': {'CANCELADAS': (2, 98.00), 'NO SHOW': (1, 98.50), 'INFRUTIFERAS': (1, 99.00),
                     'ETA ORIGEM': (1, 99.00), 'CPT ORIGEM': (14, 85.00), 'SPOT': (55, 40.00), 'TENDENCIA': (37, 60.00)}},
]


# ============================================
# FUNCOES DE CORES
# ============================================

def color_infrut(val):
    try:
        v = float(val)
        if v >= 1.0:
            return 'background-color: #ffcdd2; color: #c62828;'
        elif v >= 0.5:
            return 'background-color: #ffe0b2; color: #e65100;'
        elif v >= 0.25:
            return 'background-color: #fff9c4; color: #f57f17;'
        else:
            return 'background-color: #c8e6c9; color: #2e7d32;'
    except:
        return ''

def color_eta(val):
    try:
        v = float(val)
        if v >= 95:
            return 'background-color: #81c784; color: #1b5e20;'
        elif v >= 85:
            return 'background-color: #c8e6c9; color: #2e7d32;'
        elif v >= 75:
            return 'background-color: #fff9c4; color: #f57f17;'
        elif v >= 60:
            return 'background-color: #ffe0b2; color: #e65100;'
        else:
            return 'background-color: #ffcdd2; color: #c62828;'
    except:
        return ''

def color_cancelado(val):
    try:
        v = float(val)
        if v <= 0.5:
            return 'background-color: #81c784; color: #1b5e20;'
        elif v <= 1.0:
            return 'background-color: #c8e6c9; color: #2e7d32;'
        elif v <= 1.5:
            return 'background-color: #fff9c4; color: #f57f17;'
        elif v <= 2.0:
            return 'background-color: #ffe0b2; color: #e65100;'
        else:
            return 'background-color: #ffcdd2; color: #c62828;'
    except:
        return ''

def render_card_header(data):
    """Renderiza o cabecalho do card"""
    return f'''
<div style="border: 2px solid #FF6B35; border-radius: 5px 5px 0 0; font-size: 0.75rem; margin: 0;">
    <div style="background: #fff3e0; padding: 5px 8px;">
        <div style="display: flex; justify-content: space-between;"><span style="color: #666;">OPERACAO:</span><span style="color: #FF6B35; font-weight: bold;">{data['soc']}</span></div>
        <div style="display: flex; justify-content: space-between;"><span style="color: #666;">DATA:</span><span style="color: #FF6B35; font-weight: bold;">{data['data']}</span></div>
        <div style="display: flex; justify-content: space-between;"><span style="color: #666;">HORARIO:</span><span style="color: #FF6B35; font-weight: bold;">{data['horario']}</span></div>
        <div style="display: flex; justify-content: space-between;"><span style="color: #666;">TRIPS PROGRAMADAS:</span><span style="color: #FF6B35; font-weight: bold;">{data['programadas']}</span></div>
        <div style="display: flex; justify-content: space-between;"><span style="color: #666;">TRIPS FECHADAS:</span><span style="color: #FF6B35; font-weight: bold;">{data['fechadas']}</span></div>
    </div>
</div>
'''

def render_section_title(title):
    """Renderiza titulo de secao"""
    return f'<div style="background: #FF6B35; color: white; padding: 4px 8px; text-align: center; font-size: 0.7rem; font-weight: bold; margin: 0; border-left: 2px solid #FF6B35; border-right: 2px solid #FF6B35;">{title}</div>'

def create_abertas_df(data):
    """Cria DataFrame para secao ABERTAS"""
    rows = []
    for label, (valor, pct) in data['abertas'].items():
        rows.append({'Status': label, 'Qtd': valor, '%': f'{pct:.2f}%'})
    total = sum([v[0] for v in data['abertas'].values()])
    rows.append({'Status': 'TOTAL', 'Qtd': total, '%': ''})
    return pd.DataFrame(rows)

def create_performance_df(data):
    """Cria DataFrame para secao PERFORMANCE"""
    rows = []
    for label, (valor, pct) in data['performance'].items():
        rows.append({'Indicador': label, 'Qtd': valor, '%': f'{pct:.2f}%'})
    return pd.DataFrame(rows)


# ============================================
# HEADER
# ============================================

st.markdown(f"""
<div class="main-header">
    <h1>📊 Performance 3PL - SOC / HUB</h1>
</div>
""", unsafe_allow_html=True)

# Info da fonte de dados (removido para screenshot limpo)
# st.markdown(f'<div class="data-source-info">📁 Fonte: {data_source}</div>', unsafe_allow_html=True)

# ============================================
# ABAS
# ============================================

tab1, tab2 = st.tabs(["📋 Tabelas SOC/HUB", "📊 Report Automatico"])

# ============================================
# ABA 1: TABELAS SOC/HUB
# ============================================

with tab1:
    st.markdown('<div class="section-header">📍 Por SOC</div>', unsafe_allow_html=True)
    
    styled_soc = df_soc.style.map(
        color_infrut, subset=['% INFRUT.']
    ).map(
        color_eta, subset=['%ETA ORIGEM', '%CPT', '%ETA DESTINO']
    ).map(
        color_cancelado, subset=['%CANCELADO']
    ).format({
        '% INFRUT.': '{:.2f}%',
        'CANCELADO': '{:.0f}',
        '%CANCELADO': '{:.2f}%',
        '%ETA ORIGEM': '{:.2f}%',
        '%CPT': '{:.0f}%',
        '%ETA DESTINO': '{:.0f}%',
        '%SPOT': '{:.2f}%'
    }).set_properties(**{'text-align': 'center'})
    
    st.dataframe(
        styled_soc,
        use_container_width=True,
        hide_index=True,
        height=280
    )
    
    st.markdown('<div class="section-header">🏢 Por HUB</div>', unsafe_allow_html=True)
    
    styled_hub = df_hub.style.map(
        color_infrut, subset=['% INFRUT.']
    ).map(
        color_eta, subset=['%ETA ORIGEM', '%CPT', '%ETA DESTINO']
    ).map(
        color_cancelado, subset=['%CANCELADO']
    ).format({
        '% INFRUT.': '{:.2f}%',
        'CANCELADO': '{:.0f}',
        '%CANCELADO': '{:.2f}%',
        '%ETA ORIGEM': '{:.2f}%',
        '%CPT': '{:.0f}%',
        '%ETA DESTINO': '{:.0f}%',
        '%SPOT': '{:.2f}%'
    }).set_properties(**{'text-align': 'center'})
    
    st.dataframe(
        styled_hub,
        use_container_width=True,
        hide_index=True,
        height=450
    )

# ============================================
# ABA 2: REPORT AUTOMATICO
# ============================================

with tab2:
    st.markdown('<div class="report-title">Report Automatico - 1h a 1h</div>', unsafe_allow_html=True)
    
    # Primeira linha - 3 cards
    cols1 = st.columns(3)
    for i, col in enumerate(cols1):
        if i < len(report_data):
            with col:
                with st.container():
                    st.markdown(render_card_header(report_data[i]), unsafe_allow_html=True)
                    st.markdown(render_section_title('ABERTAS'), unsafe_allow_html=True)
                    st.dataframe(create_abertas_df(report_data[i]), hide_index=True, use_container_width=True, height=180)
                    st.markdown(render_section_title('PERFORMANCE'), unsafe_allow_html=True)
                    st.dataframe(create_performance_df(report_data[i]), hide_index=True, use_container_width=True, height=180)
    
    st.markdown('<div class="report-title">Report Automatico - 1h a 1h</div>', unsafe_allow_html=True)
    
    # Segunda linha - 3 cards
    cols2 = st.columns(3)
    for i, col in enumerate(cols2):
        idx = i + 3
        if idx < len(report_data):
            with col:
                with st.container():
                    st.markdown(render_card_header(report_data[idx]), unsafe_allow_html=True)
                    st.markdown(render_section_title('ABERTAS'), unsafe_allow_html=True)
                    st.dataframe(create_abertas_df(report_data[idx]), hide_index=True, use_container_width=True, height=180)
                    st.markdown(render_section_title('PERFORMANCE'), unsafe_allow_html=True)
                    st.dataframe(create_performance_df(report_data[idx]), hide_index=True, use_container_width=True, height=180)

# ============================================
# RODAPE
# ============================================

st.markdown(f"""
<div style="text-align: center; color: #999; font-size: 0.7rem; margin-top: 5px;">
    Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Fonte: {data_source}
</div>
""", unsafe_allow_html=True)
