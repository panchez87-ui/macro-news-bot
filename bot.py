# -*- coding: utf-8 -*-
"""
Bot de noticias macroeconómicas -> Telegram.

Revisa fuentes RSS gratuitas cada hora (vía GitHub Actions), puntúa cada
noticia según palabras clave relacionadas con: petróleo, Rusia-OTAN,
Estrecho de Ormuz, FED, dólar y bonos del Tesoro de EE.UU., y envía a
Telegram solo lo que supera un umbral de "impacto en mercado".

No usa ningún modelo de IA de pago: el filtrado es 100% por reglas
(palabras clave + pesos), por lo que correr esto no tiene costo.
"""
import os
import sys
import json
import hashlib
import time
from datetime import datetime, timezone, timedelta

import feedparser
import requests

from config import (
    FEEDS,
    KEYWORDS,
    BOOST_KEYWORDS,
    SCORE_THRESHOLD,
    MAX_ALERTS_PER_RUN,
    LOOKBACK_MINUTES,
    STATE_MAX_AGE_DAYS,
)

STATE_FILE = os.path.join(os.path.dirname(__file__), "state", "sent_ids.json")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2, sort_keys=True)


def prune_state(state):
    cutoff = datetime.now(timezone.utc) - timedelta(days=STATE_MAX_AGE_DAYS)
    cutoff_ts = cutoff.timestamp()
    return {k: v for k, v in state.items() if v.get("ts", 0) >= cutoff_ts}


def entry_id(entry):
    key = entry.get("link") or entry.get("title", "")
    return hashlib.sha256(key.encode("utf-8", "ignore")).hexdigest()


def entry_timestamp(entry):
    for field in ("published_parsed", "updated_parsed"):
        t = entry.get(field)
        if t:
            return datetime(*t[:6], tzinfo=timezone.utc).timestamp()
    return None


def score_entry(title, summary):
    text = f"{title} {summary}".lower()
    score = 0
    matched_categories = set()
    matched_terms = []

    for category, terms in KEYWORDS.items():
        for term, weight in terms.items():
            if term in text:
                score += weight
                matched_categories.add(category)
                matched_terms.append(term)

    for term, weight in BOOST_KEYWORDS.items():
        if term in text:
            score += weight
            matched_terms.append(term)

    return score, matched_categories, matched_terms


def fetch_candidates():
    now = datetime.now(timezone.utc).timestamp()
    lookback_cutoff = now - LOOKBACK_MINUTES * 60
    candidates = []

    for url in FEEDS:
        try:
            parsed = feedparser.parse(url)
        except Exception as e:
            print(f"[WARN] No se pudo leer feed {url}: {e}", file=sys.stderr)
            continue

        for entry in parsed.entries:
            ts = entry_timestamp(entry)
            if ts is None or ts < lookback_cutoff:
                continue

            title = entry.get("title", "").strip()
            summary = entry.get("summary", "") or entry.get("description", "")
            link = entry.get("link", "")
            if not title or not link:
                continue

            score, categories, terms = score_entry(title, summary)
            candidates.append(
                {
                    "id": entry_id(entry),
                    "title": title,
                    "link": link,
                    "ts": ts,
                    "score": score,
                    "categories": sorted(categories),
                    "terms": terms,
                    "source": url,
                }
            )

    return candidates


def format_message(item):
    cats = ", ".join(item["categories"]) if item["categories"] else "General"
    dt = datetime.fromtimestamp(item["ts"], tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return (
        f"🚨 <b>{cats}</b> (score {item['score']})\n"
        f"{item['title']}\n"
        f"🕒 {dt}\n"
        f"{item['link']}"
    )


def send_telegram(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[ERROR] Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID", file=sys.stderr)
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    try:
        resp = requests.post(url, data=payload, timeout=15)
        if resp.status_code != 200:
            print(f"[ERROR] Telegram respondió {resp.status_code}: {resp.text}", file=sys.stderr)
            return False
        return True
    except requests.RequestException as e:
        print(f"[ERROR] Fallo al enviar a Telegram: {e}", file=sys.stderr)
        return False


def main():
    state = prune_state(load_state())
    candidates = fetch_candidates()

    new_candidates = [c for c in candidates if c["id"] not in state]
    important = [c for c in new_candidates if c["score"] >= SCORE_THRESHOLD]
    important.sort(key=lambda c: c["score"], reverse=True)
    to_send = important[:MAX_ALERTS_PER_RUN]

    sent_count = 0
    for item in to_send:
        if send_telegram(format_message(item)):
            sent_count += 1
        time.sleep(1)  # evitar rate limit de Telegram

    # Marcar como "vistas" TODAS las noticias procesadas en esta corrida
    # (se hayan enviado o no), para no re-evaluarlas en la próxima hora.
    now = datetime.now(timezone.utc).timestamp()
    for c in new_candidates:
        state[c["id"]] = {"ts": now, "title": c["title"]}

    save_state(state)

    print(
        f"Feeds revisados: {len(FEEDS)} | "
        f"Noticias nuevas analizadas: {len(new_candidates)} | "
        f"Importantes encontradas: {len(important)} | "
        f"Enviadas: {sent_count}"
    )


if __name__ == "__main__":
    main()
