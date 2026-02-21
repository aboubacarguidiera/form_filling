import ollama
import json

def parse_document(text):

    prompt = f"""
Extract structured information from this document.

Return ONLY valid JSON. The output can be just a JSON object, no other text. The type of the output should be
a JSON object.

Example format:

{{
"name": "",
"email": "",
"skills": []
}}

Document:
{text}
"""

    response = ollama.chat(
        model="mistral",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    content = response["message"]["content"]

    try:
        return json.loads(content)
    except:
        return {"raw_output": content}

# This function takes the parsed data and fills a template with it. The template is a pdf with blank fields.

