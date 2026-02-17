"""
Краткое обобщение текста через Google Gemini API для публикации в одно сообщение Telegram.
"""
import logging
import re

import requests

logger = logging.getLogger(__name__)

MAX_SUMMARY_CHARS = 3800

BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

# Модели по приоритету (часть могла быть снята с поддержки — пробуем по порядку)
GEMINI_MODELS = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro",
    "gemini-1.5-pro-latest",
    "gemini-pro",
    "gemini-3-flash-preview",
    "gemini-3-pro-preview",
]


def _get_available_model(api_key: str) -> str | None:
    """Возвращает первую доступную модель из списка (GET /v1beta/models)."""
    try:
        resp = requests.get(
            f"{BASE_URL}/models?key={api_key}",
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        names = {m.get("name", "").replace("models/", "") for m in (data.get("models") or [])}
        for model in GEMINI_MODELS:
            if model in names:
                return model
        if names:
            return next(iter(names))
    except Exception as e:
        logger.debug("Could not list Gemini models: %s", e)
    return None


def summarize_for_telegram(full_text: str, api_key: str) -> str:
    """
    Отправляет полный текст в Gemini, возвращает краткое обобщение (до MAX_SUMMARY_CHARS).
    При ошибке (в т.ч. 404 по модели) пробует другие модели; если всё неудача — обрезает текст.
    """
    if not api_key or not full_text.strip():
        return _truncate(full_text, MAX_SUMMARY_CHARS)
    prompt = f"""Ты — редактор новостей. Обобщи следующий текст новости кратко и по делу на русском языке.
Сохрани главные факты и суть. Результат не длиннее {MAX_SUMMARY_CHARS} символов — ограничение одного сообщения в мессенджере.
Пиши сплошным текстом, без подзаголовков. Не добавляй вступлений вроде «Краткое содержание» — только суть новости.

Текст новости:
---
{full_text[:12000]}
---"""
    models_to_try = [*(GEMINI_MODELS)]
    available = _get_available_model(api_key)
    if available and available not in models_to_try:
        models_to_try.insert(0, available)
    elif available:
        models_to_try = [available] + [m for m in models_to_try if m != available]
    last_error = None
    for model in models_to_try:
        url = f"{BASE_URL}/models/{model}:generateContent?key={api_key}"
        try:
            resp = requests.post(
                url,
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "maxOutputTokens": 1024,
                        "temperature": 0.3,
                    },
                },
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates") or []
            if not candidates:
                continue
            parts = (candidates[0].get("content") or {}).get("parts") or []
            if not parts:
                continue
            summary = (parts[0].get("text") or "").strip()
            summary = re.sub(r"\n{3,}", "\n\n", summary)
            if summary:
                logger.info("Gemini model used: %s", model)
                return summary[:MAX_SUMMARY_CHARS]
        except requests.HTTPError as e:
            last_error = e
            if e.response is not None and e.response.status_code == 404:
                continue
            break
        except Exception as e:
            last_error = e
            break
    logger.warning("Gemini summarize failed (last: %s), using truncate", last_error)
    return _truncate(full_text, MAX_SUMMARY_CHARS)


def _truncate(text: str, max_len: int) -> str:
    """Обрезает текст до max_len символов с многоточием."""
    text = (text or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rsplit(maxsplit=1)[0] + "…"
