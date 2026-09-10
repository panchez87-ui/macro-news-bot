# Macro News Bot 🚨

Bot gratuito que revisa noticias macroeconómicas cada hora y te avisa por
Telegram **solo** cuando algo importante pasa en:

- 🛢️ Petróleo (OPEC, producción, precios)
- ⚔️ Rusia - OTAN
- 🚢 Estrecho de Ormuz / Irán
- 🏦 FED (tasas de interés, Powell, FOMC)
- 💵 Dólar (DXY, intervención, de-dolarización)
- 📉 Bonos del Tesoro de EE.UU. (yields, subastas, rating)

**Costo: $0.** Corre en GitHub Actions (gratis para repos públicos, y muy
por debajo del límite gratuito en repos privados), usa RSS gratuitos como
fuente y un filtro por palabras clave (sin IA de pago, sin tokens).

---

## Cómo funciona

1. Cada hora, GitHub Actions ejecuta [`bot.py`](bot.py).
2. El script lee las fuentes RSS definidas en [`config.py`](config.py).
3. Cada noticia de la última hora recibe un **puntaje** según cuántas
   palabras clave de impacto contiene (ver `KEYWORDS` en `config.py`).
4. Si el puntaje supera el umbral (`SCORE_THRESHOLD`, por defecto 5), se
   envía a tu Telegram. El resto se descarta.
5. Se guarda un registro de qué noticias ya se procesaron
   (`state/sent_ids.json`) para no repetir avisos.

---

## Paso a paso para ponerlo en marcha

### 1. Crear el repositorio en GitHub

1. Ve a https://github.com/new
2. Ponle un nombre, por ejemplo `macro-news-bot`.
3. Puede ser **público** (recomendado: minutos de Actions ilimitados y
   gratis) o privado (también gratis, muy por debajo de las 2000 min/mes
   incluidas). No importa para este proyecto, no hay datos sensibles en el código.
4. No agregues README ni .gitignore desde la web (ya los tienes aquí).
5. Crea el repo y copia la URL que te da (algo como
   `https://github.com/TU_USUARIO/macro-news-bot.git`).

### 2. Subir este proyecto

Abre una terminal en esta carpeta (`macro-news-bot`) y ejecuta:

```bash
git init
git add .
git commit -m "Initial commit: macro news bot"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/macro-news-bot.git
git push -u origin main
```

### 3. Obtener tu `chat_id` de Telegram

Ya tienes tu bot creado con @BotFather (tienes el **token**). Ahora
necesitas tu `chat_id`:

1. Abre Telegram y busca tu bot, mándale cualquier mensaje (ej: "hola").
2. En el navegador, abre esta URL reemplazando `<TOKEN>` por tu token real:
   `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Busca en el JSON el campo `"chat":{"id": 123456789, ...}` — ese número
   es tu `chat_id`.

   > Si quieres recibir los avisos en un grupo en vez de un chat privado,
   > agrega el bot al grupo, escribe algo en el grupo, y repite el paso 2:
   > el `chat_id` del grupo aparecerá como un número negativo.

### 4. Configurar los secretos en GitHub (nunca los pegues en el código)

1. En tu repo de GitHub: **Settings → Secrets and variables → Actions →
   New repository secret**.
2. Crea el secreto `TELEGRAM_BOT_TOKEN` con el token de tu bot.
3. Crea el secreto `TELEGRAM_CHAT_ID` con el chat_id que obtuviste.

### 5. Probarlo manualmente

1. En tu repo de GitHub, ve a la pestaña **Actions**.
2. Selecciona el workflow **Macro News Bot**.
3. Click en **Run workflow** (botón a la derecha) para probarlo sin
   esperar a que llegue la hora en punto.
4. Revisa los logs del run — al final te dice cuántas noticias
   analizó/envió. Si todo está bien, deberías recibir mensajes en
   Telegram (solo si hay algo que supere el umbral en ese momento).

A partir de ahí, correrá solo, cada hora, para siempre — sin que tengas
que hacer nada ni encender tu computadora.

---

## Ajustar la sensibilidad

Si te llegan muy pocas o demasiadas noticias, edita en
[`config.py`](config.py):

- `SCORE_THRESHOLD`: bájalo para recibir más avisos, súbelo para recibir
  menos (más estrictos).
- `KEYWORDS` / `BOOST_KEYWORDS`: agrega o quita términos y pesos según lo
  que te interese.
- `FEEDS`: agrega o quita fuentes RSS. Ten en cuenta que las URLs de RSS
  a veces cambian o dejan de funcionar; si un feed falla, el bot lo
  ignora y sigue con los demás (verás un `[WARN]` en los logs).

## Notas

- Las noticias llegan en su idioma original (mayormente inglés), porque
  traducirlas automáticamente requeriría un servicio adicional. Si más
  adelante quieres traducción automática, se puede agregar sin costo con
  `deep-translator` (usa Google Translate de forma no oficial).
- GitHub Actions no garantiza el minuto exacto del cron (puede haber
  algunos minutos de retraso en horas pico), pero corre de forma
  confiable cada hora.
