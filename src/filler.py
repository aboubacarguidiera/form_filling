import ollama
import json 
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
def fill_template(parsed_data, document_path):
    # This is a placeholder function. You would need to use a library like ReportLab or PyPDF2 to fill in the PDF template with the parsed data.
    # For example, you could use ReportLab to create a new PDF and write the parsed data into it.

    prompt = f"""Fill in the following PDF template with the provided structured data. 
The structured data is in JSON format and contains the following fields: name, email, skills.
There might be some fields that are not exactly matching the template, so you should do your best to fill in the relevant information in the PDF.
Structured data:
{json.dumps(parsed_data, indent=2)}
PDF template path: {document_path}
"""
    

    

    c = canvas.Canvas(document_path.replace(".pdf", "_filled.pdf"), pagesize=letter)
    c.drawString(100, 750, f"Name: {parsed_data.get('name', '')}")
    c.drawString(100, 730, f"Email: {parsed_data.get('email', '')}")
    c.drawString(100, 710, f"Skills: {', '.join(parsed_data.get('skills', []))}")
    c.save()