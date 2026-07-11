# Ernesto Investing AI

Sistema web de apoyo a decisiones de inversión bursátil que combina datos reales
de Yahoo Finance con seis modelos de Inteligencia Artificial (SVC, LSTM, BiLSTM,
GRU, SimpleRNN y un Regresor LSTM) para generar señales de compra/venta y
pronósticos de precio sobre cinco empresas mineras con operaciones en Perú.

Proyecto final — curso **Introducción al Desarrollo de Software (iDeSo)**,
FISI, Universidad Nacional Mayor de San Marcos. Prof. Mg. Ing. Ernesto D.
Cancho-Rodríguez, MBA (The George Washington University).

## Tickers del estudio

| Ticker | Empresa | Bolsa |
|---|---|---|
| FSM | Fortuna Silver Mines Inc. | NYSE |
| VOLCABC1.LM | Volcan Compañía Minera S.A.A. | BVL |
| ABX.TO | Barrick Gold Corporation | TSX |
| BVN | Compañía de Minas Buenaventura S.A.A. | NYSE |
| BHP | BHP Billiton Limited | NYSE |

## Arquitectura

```
Yahoo Finance (yfinance)
        │
        ▼
Notebooks de Google Colab (ingesta + entrenamiento de modelos)
        │
        ▼
MongoDB Atlas (precios_ohlcv, predicciones, metricas_modelos,
                sentimiento_noticias, usuarios)
        │
        ▼
API FastAPI + ngrok (18 endpoints, solo lectura, nunca recalcula)
        │
        ├──▶ Frontend HTML (18 páginas, desplegado en GitHub Pages)
        └──▶ App Streamlit (7 páginas, desplegada en Streamlit Community Cloud)
```

## Estructura del repositorio

```
ernesto-investing-ai/
├── backend/            API FastAPI (auth, 8 routers, esquemas Pydantic)
├── notebooks/          6 notebooks de Google Colab (datos + modelos + API)
├── frontend/           18 páginas HTML/CSS/JS (login + 15 módulos + detalle de ticker)
├── streamlit_app/      App Streamlit alternativa (7 páginas)
└── docs/                Material para informe, PPT y video (a completar)
```

## Cómo levantar el sistema desde cero

### 1. MongoDB Atlas
Crea una cuenta gratuita, un clúster M0, un usuario de base de datos y
habilita el acceso desde cualquier IP (`0.0.0.0/0`, necesario porque Colab
no tiene IP fija). Copia tu cadena de conexión (`MONGO_URI`).

### 2. Notebooks de Google Colab (en este orden)
1. `01_Ingesta_MongoDB.ipynb` — descarga datos reales y calcula indicadores.
2. `02_Clasificador_SVC.ipynb`
3. `03_Clasificadores_RNN_LSTM_BiLSTM.ipynb` y `03b_..._GRU_SimpleRNN.ipynb`
4. `04_Regresor_LSTM.ipynb`
5. `05_Sentimiento_NLP.ipynb` (independiente, no requiere los anteriores)
6. `06_API_FastAPI_ngrok.ipynb` — levanta el backend y lo expone a Internet.

Cada notebook necesita el Secret `MONGO_URI` configurado en Colab (ícono
de llave 🔑). El Notebook 06 además necesita `NGROK_AUTH_TOKEN` (cuenta
gratuita en ngrok.com) y `JWT_SECRET` (cualquier cadena larga y aleatoria).

### 3. Frontend HTML
```bash
cd frontend
python -m http.server 8000
```
Abre `http://localhost:8000`. En la pantalla de login, despliega
"Configuración avanzada" y pega la URL de ngrok que imprimió el Notebook 06.

> **Importante:** abrir los archivos HTML con doble clic (`file://`) no
> funciona, porque el shell de navegación usa `fetch()` para inyectar el
> sidebar y los navegadores bloquean eso por CORS en `file://`. Usa siempre
> un servidor local o el despliegue real en GitHub Pages.

### 4. App Streamlit
```bash
cd streamlit_app
pip install -r ../requirements.txt
streamlit run app.py
```
Pega la misma URL de ngrok en la barra lateral. La mayoría de los endpoints
de datos no requieren sesión iniciada (solo `/api/auth/*` y la watchlist la
necesitan), así que la app Streamlit funciona sin login.

## Despliegue

- **Frontend:** GitHub Pages, apuntando a la carpeta `frontend/`.
- **API:** Google Colab + ngrok (temporal, ideal para la demo en vivo) o,
  para una URL permanente, cualquier servicio con soporte Docker/Python.
- **Streamlit:** Streamlit Community Cloud, apuntando a `streamlit_app/app.py`.

## Stack tecnológico

Python · FastAPI · MongoDB Atlas · yfinance · scikit-learn ·
TensorFlow/Keras · NLTK (VADER) · Plotly.js/Plotly Python · Streamlit ·
HTML5 · CSS3 · JavaScript vanilla · JWT · bcrypt

## Modelos de IA implementados

| Modelo | Tipo | Framework |
|---|---|---|
| SVC (GridSearchCV) | Clasificación binaria BUY/SELL | scikit-learn |
| LSTM | Clasificación binaria BUY/SELL | TensorFlow/Keras |
| BiLSTM | Clasificación binaria BUY/SELL | TensorFlow/Keras |
| GRU | Clasificación binaria BUY/SELL | TensorFlow/Keras |
| SimpleRNN | Clasificación binaria BUY/SELL | TensorFlow/Keras |
| Regresor LSTM | Pronóstico de precio (7/14/30/60 días) | TensorFlow/Keras |
| VADER | Análisis de sentimiento de noticias | NLTK |
