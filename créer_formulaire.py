# créer_formulaire.py
from reportlab.pdfgen import canvas

c = canvas.Canvas("formulaire_test.pdf")
c.drawString(100, 750, "Nom:")
c.drawString(100, 700, "Date de naissance:")
c.drawString(100, 650, "Adresse:")
c.save()