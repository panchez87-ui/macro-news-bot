# -*- coding: utf-8 -*-
"""
Configuración del bot: fuentes RSS, palabras clave y pesos por tema.
Todo esto es ajustable sin tocar la lógica en bot.py.
"""

# --- Fuentes RSS (100% gratuitas, sin API key) ---
FEEDS = [
    "https://oilprice.com/rss/main",
    "https://www.federalreserve.gov/feeds/press_all.xml",
    "https://home.treasury.gov/rss/press-releases.xml",
    "https://www.marketwatch.com/rss/topstories",
    "https://www.marketwatch.com/rss/marketpulse",
    "https://www.cnbc.com/id/20910258/device/rss/rss.html",  # CNBC World Economy
    "https://www.cnbc.com/id/19836768/device/rss/rss.html",  # CNBC Energy
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://feeds.feedburner.com/zerohedge/feed",
    "https://www.investing.com/rss/news_301.rss",  # Economic news
]

# --- Palabras clave por categoría, con peso de importancia ---
# Se buscan en minúsculas dentro del título + resumen de cada noticia.
KEYWORDS = {
    "PETRÓLEO": {
        "opec+": 3, "opec": 2, "oil production cut": 4, "output cut": 3,
        "crude oil": 2, "oil price": 2, "brent crude": 2, "wti crude": 2,
        "oil supply": 3, "oil embargo": 5, "oil tanker": 3, "refinery attack": 5,
        "saudi aramco": 3, "pipeline attack": 4, "energy crisis": 3,
    },
    "RUSIA-OTAN": {
        "nato troops": 5, "article 5": 6, "nato": 2, "russia": 2,
        "kremlin": 2, "putin": 2, "ukraine": 2, "russian troops": 3,
        "sanctions on russia": 4, "missile strike": 4, "nuclear": 5,
        "escalation": 3, "mobilization": 4, "direct conflict": 5,
    },
    "ESTRECHO DE ORMUZ": {
        "strait of hormuz": 6, "hormuz": 5, "iran": 2, "tehran": 2,
        "irgc": 3, "houthi": 3, "red sea": 3, "tanker seized": 5,
        "iran missile": 4, "israel iran": 4, "gulf of oman": 4,
        "blockade": 5, "tanker attack": 5,
    },
    "FED": {
        "federal reserve": 3, "fomc": 4, "powell": 3, "interest rate": 3,
        "rate hike": 4, "rate cut": 4, "emergency meeting": 6,
        "surprise cut": 6, "surprise hike": 6, "quantitative tightening": 3,
        "quantitative easing": 3, "basis points": 3, "fed minutes": 3,
        "jackson hole": 2,
    },
    "DÓLAR": {
        "dollar index": 3, "dxy": 3, "us dollar": 2, "dollar strength": 2,
        "dollar weakness": 2, "currency intervention": 5, "de-dollarization": 4,
        "dollar collapse": 6, "dollar surge": 3, "dollar plunge": 4,
    },
    "BONOS DEL TESORO": {
        "treasury yield": 3, "10-year yield": 4, "treasury bond": 2,
        "bond market": 2, "yield curve": 3, "treasury auction": 3,
        "debt ceiling": 4, "credit rating downgrade": 6, "flight to safety": 3,
        "yield spike": 5, "inverted yield curve": 4,
    },
}

# Palabras que amplifican la importancia sin importar la categoría
BOOST_KEYWORDS = {
    "breaking": 3, "emergency": 3, "surge": 2, "plunge": 3, "crash": 4,
    "record high": 2, "record low": 2, "unexpected": 2, "surprise": 3,
    "halts trading": 4, "circuit breaker": 5, "war": 3, "attack": 3,
    "invasion": 5,
}

# Umbral mínimo de score para considerar una noticia "importante"
SCORE_THRESHOLD = 5

# Máximo de alertas a enviar por ejecución (para no saturar Telegram)
MAX_ALERTS_PER_RUN = 6

# Ventana de tiempo hacia atrás para considerar una noticia "nueva" (minutos)
LOOKBACK_MINUTES = 75

# Cuántos días guardar en el historial de IDs ya vistos
STATE_MAX_AGE_DAYS = 7
