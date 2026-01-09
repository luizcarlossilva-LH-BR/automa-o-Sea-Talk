# Dashboard Performance 3PL - SeaTalk

Dashboard Streamlit para visualização de métricas de performance de transportadores, com envio automático para grupos no SeaTalk.

## Início Rápido

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Iniciar o Dashboard

Windows:
```
iniciar_dashboard.bat
```

Ou linha de comando:
```bash
streamlit run dashboard_performance.py
```

O dashboard abre em: http://localhost:8501

### 3. Enviar para o SeaTalk

Em outro terminal:

Windows:
```
enviar_seatalk.bat
```

Ou linha de comando:
```bash
python enviar_dashboard_seatalk.py
```

## Estrutura do Projeto

```
projeto/
├── dashboard_performance.py      # Dashboard Streamlit principal
├── enviar_dashboard_seatalk.py   # Script para capturar e enviar
├── iniciar_dashboard.bat         # Script para iniciar dashboard (Windows)
├── enviar_seatalk.bat            # Script para enviar (Windows)
├── requirements.txt              # Dependências Python
├── README.md                     # Este arquivo
└── chrome_profile/               # Perfil do Chrome (gerado automaticamente)
```

## O Dashboard

O dashboard inclui:

- Header com título e data de atualização
- 10 KPIs no topo (Total de Viagens, ETA, CPT, etc.)
- Tabela Operação (transportadores x indicadores)
- Tabela Planejamento (Scheduling, Tendência, SPOT, etc.)
- Tabela General (CMK, Check List, Treinamento)
- Cores condicionais: verde (>=95%), amarelo (>=80%), laranja (>=60%), vermelho (<60%)

## Configurações

### Alterar Webhook do SeaTalk

Edite enviar_dashboard_seatalk.py:

```python
WEBHOOK_URL = "https://openapi.seatalk.io/webhook/group/SEU_WEBHOOK"
```

### Alterar Dados do Dashboard

Edite dashboard_performance.py e modifique os dicionários:
- data_operacao - Dados da tabela Operação
- data_planejamento - Dados da tabela Planejamento
- data_general - Dados da tabela General
- kpis - Valores dos cards no topo

## Personalização

### Cores das Células

No arquivo dashboard_performance.py, função color_performance():

```python
if v >= 95:    # Verde
elif v >= 80:  # Amarelo
elif v >= 60:  # Laranja
else:          # Vermelho
```

### Viewport (Tamanho da Captura)

No arquivo enviar_dashboard_seatalk.py:

```python
VIEWPORT_WIDTH = 1920   # Largura
VIEWPORT_HEIGHT = 1080  # Altura
```

## Licença

Uso interno.
