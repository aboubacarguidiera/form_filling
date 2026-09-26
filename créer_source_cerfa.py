# créer_source_cerfa.py
# Document source fictif correspondant aux champs du Cerfa 14011
# (déclaration de perte de CNI/passeport) pour tester le pipeline complet.
from reportlab.pdfgen import canvas

c = canvas.Canvas("source_test_cerfa.pdf")
c.drawString(100, 750, "Nom de famille: Lefebvre")
c.drawString(100, 720, "Prénom(s): Marie Claire")
c.drawString(100, 690, "Né(e) le: 03/11/1985")
c.drawString(100, 660, "Adresse: 25 avenue de la République")
c.drawString(100, 630, "Code postal: 44100")
c.drawString(100, 600, "Ville: Nantes")
c.drawString(100, 570, "Pays: France")
c.drawString(100, 540, "N° de passeport: 19AB12345")
c.drawString(100, 510, "N° de carte d'identité: 123456789012")
c.save()
