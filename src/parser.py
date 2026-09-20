import json
import os
import re

import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-haiku-4-5"


def parse_document(text: str, form_fields: list) -> dict:
    fields_str = json.dumps(form_fields, ensure_ascii=False)

    prompt = f"""
Extract information from this document to fill a form.

Form fields to fill:
{fields_str}

For each field, find the corresponding value in the document.
If information is missing, use null.
Return ONLY a valid JSON object, no markdown, no explanation, no backticks.

Document:
{text}
"""

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Erreur : la variable d'environnement ANTHROPIC_API_KEY est absente. "
              "Définissez-la dans un fichier .env (voir .env.example).")
        return {}

    client = anthropic.Anthropic(api_key=api_key)

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.AuthenticationError:
        print("Erreur : clé API Anthropic invalide.")
        return {}
    except anthropic.RateLimitError:
        print("Erreur : quota Anthropic dépassé ou trop de requêtes (rate limit).")
        return {}
    except anthropic.APITimeoutError:
        print("Erreur : délai d'attente dépassé lors de l'appel à l'API Anthropic.")
        return {}
    except anthropic.APIStatusError as e:
        print(f"Erreur API Anthropic ({e.status_code}) : {e.message}")
        return {}
    except anthropic.APIConnectionError:
        print("Erreur : impossible de contacter l'API Anthropic (problème réseau).")
        return {}

    content = next((b.text for b in response.content if b.type == "text"), "").strip()

    # 🔧 Nettoyer les backticks markdown si présents
    content = re.sub(r"```json\s*", "", content)
    content = re.sub(r"```\s*", "", content)
    content = content.strip()

    # 🔧 Extraire uniquement la partie JSON si du texte parasite est présent
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        content = match.group(0)

    try:
        return json.loads(content)

    except json.JSONDecodeError:
        # Afficher ce que le LLM a vraiment retourné pour déboguer
        print("Réponse brute du LLM :", content)
        return {"raw_output": content}
