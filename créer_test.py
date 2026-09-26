# créer_test.py
from reportlab.pdfgen import canvas

c = canvas.Canvas("source_test.pdf")
c.drawString(100, 750, "Nom: Jean Dupont")
c.drawString(100, 700, "Date de naissance: 12/05/1990")
c.drawString(100, 650, "Adresse: 10 rue de la Paix, Nantes")
c.save()