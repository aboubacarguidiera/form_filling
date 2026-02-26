# pour un pdf interacftif (acroform) 
import pypdf

def get_form_fields(form_path: str) -> dict:
    reader = pypdf.PdfReader(form_path)
    fields = reader.get_fields()
    if not fields:
        return {}
    # Retourne {nom_du_champ: valeur_actuelle (vide)}
    return {k: v.get("/V", "") for k, v in fields.items()}


def get_form_fields_from_text(text: str) -> list[str]:
    # Simple heuristique : chercher des lignes avec "Nom:", "Date:", etc.
    # En vrai, on pourrait faire du NLP pour détecter les labels de champs
    lines = text.splitlines()
    potential_fields = []
    for line in lines:
        if ":" in line:
            label = line.split(":")[0].strip()
            if len(label) < 30:  # éviter les lignes trop longues
                potential_fields.append(label)
    return potential_fields