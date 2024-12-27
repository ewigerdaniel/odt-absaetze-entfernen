from flask import Flask, request, send_file, render_template
import os
import zipfile
import shutil
from lxml import etree

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
TEMP_DIR = "temp_dir"

# Erstelle Ordner für Uploads und Verarbeitung
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def process_odt(input_path, output_path):
    """Bearbeitet die ODT-Datei und speichert die Ausgabe."""
    try:
        # Entpacken
        with zipfile.ZipFile(input_path, 'r') as zip_ref:
            zip_ref.extractall(TEMP_DIR)
        
        # Bearbeiten der content.xml
        content_path = os.path.join(TEMP_DIR, "content.xml")
        parser = etree.XMLParser(remove_blank_text=False)
        tree = etree.parse(content_path, parser)
        root = tree.getroot()

        # Namensräume
        namespaces = {'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'}
        paragraphs = root.xpath("//text:p", namespaces=namespaces)

        # Absätze zusammenführen
        i = 0
        while i < len(paragraphs) - 1:
            current = paragraphs[i]
            next_para = paragraphs[i + 1]

            if current.text and next_para.text:
                current.text = f"{current.text} {next_para.text}".strip()
                parent = next_para.getparent()
                parent.remove(next_para)
                paragraphs.pop(i + 1)
            else:
                i += 1

        # Speichern
        tree.write(content_path, pretty_print=True, encoding="UTF-8", xml_declaration=True)

        # Neu packen
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            for root, _, files in os.walk(TEMP_DIR):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, TEMP_DIR)
                    zip_ref.write(file_path, arcname)
    finally:
        # Temporären Ordner löschen
        shutil.rmtree(TEMP_DIR, ignore_errors=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Datei speichern
        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            return "Keine Datei hochgeladen.", 400
        
        input_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
        output_path = os.path.join(PROCESSED_FOLDER, "output.odt")
        uploaded_file.save(input_path)

        # Datei verarbeiten
        process_odt(input_path, output_path)

        # Datei zur Verfügung stellen
        return send_file(output_path, as_attachment=True)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

