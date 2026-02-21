from src import config
import pdfplumber
import pytesseract
from PIL import Image


def extract_text_from_pdf(path: str) -> str:
    text = ""

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    
        if text.strip():
           return text 
        for page in pdf.pages:
            page2img = page.to_image(resolution=300).original
            print(type(page2img)) 
            page_text =  pytesseract.image_to_string(page2img, lang="eng+fra")
            if page_text:
                text += page_text + "\n"
    return text if text.strip() else "Aucun texte extrait"
## ici extraire du texte depuis une image avec la biblio image from PIL


def extract_text_from_image(path: str) -> str:
    img = Image.open(path)
    text = pytesseract.image_to_string(img, lang="eng+fra")
    return text 

# POUR Afficher l'image 
def display_im(path:str)->str:
    img = Image.open(path)

    return img 

def extract_text(path: str) -> str:
    if path.lower().endswith(".pdf"):
        return extract_text_from_pdf(path)

    return extract_text_from_image(path)

