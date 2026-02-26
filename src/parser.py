import ollama
import json
import re

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

    try:
        response = ollama.chat(
            model="mistral",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response["message"]["content"].strip()

        # 🔧 Nettoyer les backticks markdown si présents
        content = re.sub(r"```json\s*", "", content)
        content = re.sub(r"```\s*", "", content)
        content = content.strip()

        # 🔧 Extraire uniquement la partie JSON si du texte parasite est présent
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            content = match.group(0)

        return json.loads(content)

    except json.JSONDecodeError:
        # Afficher ce que le LLM a vraiment retourné pour déboguer
        print("Réponse brute du LLM :", content)
        return {"raw_output": content}