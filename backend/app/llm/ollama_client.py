import logging
import requests

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class OllamaUnavailableError(RuntimeError):
    pass


def query_ollama(prompt: str) -> str:
    """
    Query the local Ollama model.

    Optimised for:
    - low-RAM laptops
    - lower hallucination rate
    - grounded RAG responses
    - shorter response latency
    """

    settings = get_settings()

    url = f"{settings.ollama_url}/api/generate"

    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "options": {
            # lower hallucination
            "temperature": 0.1,

            # faster / shorter outputs
            "num_predict": 120,

            # keep context window smaller
            "num_ctx": 2048,

            # slightly more deterministic
            "top_p": 0.9,
        },
    }

    try:
        logger.info(
            "Sending request to Ollama model=%s url=%s",
            settings.ollama_model,
            url,
        )

        response = requests.post(
            url,
            json=payload,
            timeout=120,
        )

        response.raise_for_status()

    except requests.RequestException as exc:
        logger.exception("Ollama request failed")

        raise OllamaUnavailableError(
            (
                "Could not connect to Ollama. "
                "Ensure Ollama is running and the model is available. "
                f"URL={url} MODEL={settings.ollama_model}"
            )
        ) from exc

    try:
        data = response.json()
    except ValueError as exc:
        logger.exception("Invalid JSON returned from Ollama")

        raise OllamaUnavailableError(
            "Ollama returned an invalid response."
        ) from exc

    answer = data.get("response", "").strip()

    if not answer:
        logger.warning("Ollama returned empty response")

        return (
            "I could not generate an answer from the uploaded documents."
        )

    return answer