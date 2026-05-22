"""
Dictionary API integration.

Wraps the Free Dictionary API (https://api.dictionaryapi.dev/) and returns
a normalized dict we can save onto a Word row. The API returns nested JSON,
so this module's job is to dig out the fields we care about and ignore the rest.
"""
import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

DICTIONARY_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"
REQUEST_TIMEOUT_SECONDS = 5


def fetch_word_data(word: str) -> Optional[dict]:
    """
    Look up a word in the Free Dictionary API.

    Returns a dict with keys: definition, part_of_speech, example_sentence,
    audio_url, phonetic. Returns None if the word is not found or the API
    fails. Never raises — callers can rely on the return value alone.
    """
    url = f"{DICTIONARY_API_URL}{word.lower()}"

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        logger.warning("Dictionary API request failed for %r: %s", word, exc)
        return None

    if response.status_code != 200:
        logger.info("Dictionary API returned %s for %r", response.status_code, word)
        return None

    try:
        data = response.json()
    except ValueError:
        logger.warning("Dictionary API returned non-JSON for %r", word)
        return None

    if not data or not isinstance(data, list):
        return None

    entry = data[0]
    return _extract_fields(entry)

def _extract_fields(entry: dict) -> dict:
    """Pull the fields we want out of the API's nested response."""
    word = entry.get("word", "").lower()
    phonetic = entry.get("phonetic", "")
    audio_url = ""

    # Audio lives in a list of phonetics; find the first one with audio
    for ph in entry.get("phonetics", []):
        if ph.get("audio"):
            audio_url = ph["audio"]
            if not phonetic:
                phonetic = ph.get("text", "")
            break

    definition, part_of_speech, example_sentence = _pick_best_definition(
        entry.get("meanings", []), word
    )

    return {
        "definition": definition,
        "part_of_speech": part_of_speech,
        "example_sentence": example_sentence,
        "audio_url": audio_url,
        "phonetic": phonetic,
    }


# Preferred order — common, learnable parts of speech first
PART_OF_SPEECH_PRIORITY = ["verb", "noun", "adjective", "adverb"]

def _pick_best_definition(meanings: list, word: str) -> tuple:
    """
    Choose the most learner-friendly definition.

    Strategy:
      1. Look at the first definition of each meaning (part of speech).
      2. Skip definitions that reuse the word.
      3. Skip definitions shorter than 25 characters (usually obscure).
      4. Prefer noun definitions for words where noun makes sense as primary.
      5. Fall back to anything non-empty.
    """
    if not meanings:
        return "", "", ""

    candidates = []  # list of (text, pos, example) tuples
    fallback = None

    for meaning in meanings:
        pos = meaning.get("partOfSpeech", "")
        for d in meaning.get("definitions", []):
            text = d.get("definition", "").strip()
            example = d.get("example", "")
            if not text:
                continue

            if fallback is None:
                fallback = (text, pos, example)

            # Skip definitions that reuse the word
            if word and word in text.lower():
                continue

            # Skip very short, often-obscure definitions
            if len(text) < 25:
                continue

            candidates.append((text, pos, example))
            break  # only take the first usable definition per part of speech

    if not candidates:
        return fallback if fallback else ("", "", "")

    # Prefer noun if available, otherwise verb, otherwise whatever came first
    for preferred in ("noun", "verb", "adjective", "adverb"):
        for c in candidates:
            if c[1].lower() == preferred:
                return c

    return candidates[0]