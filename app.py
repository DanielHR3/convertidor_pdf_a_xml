import os
import PyPDF2
from lxml import etree
from flask import Flask, request, redirect, url_for, send_from_directory, render_template, flash

def extract_text_from_pdf(pdf_path):
    pdf_reader = PyPDF2.PdfReader(pdf_path)
    num_pages = len(pdf_reader.pages)
    text = ""
    
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        text += page.extract_text() + "\n"
        
    return text

def create_xml(data, output_path):
    root = etree.Element("Document")

    sections = {
        "ProfessionalProfile": [],
        "WorkExperience": [],
        "Education": [],
        "Skills": [],
        "ContactInfo": [],
        "Other": []
    }

    current_section = "Other"
    
    for paragraph in data.split("\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if any(keyword in paragraph for keyword in ["Professional Profile", "Professional Objective", "Professional experience"]):
            current_section = "ProfessionalProfile"
        elif any(keyword in paragraph for keyword in ["Work Experience", "Experience", "Technical assistance", "Exam applicator", "Corrective maintenance", "Technical Support", "Computer assistant", "Exam applicator", "Technical assistance"]):
            current_section = "WorkExperience"
        elif any(keyword in paragraph for keyword in ["Education", "University", "School", "Autonomous University", "Digital University", "XXI Century University Center"]):
            current_section = "Education"
        elif any(keyword in paragraph for keyword in ["Skills", "Certifications", "Knowledge", "Solid programming knowledge", "Technical skills", "CSS", "PHP", "HTML", "JavaScript", "MySQL", "Database management"]):
            current_section = "Skills"
        elif any(keyword in paragraph for keyword in ["Contact Info", "Contact", "Email", "Phone", "Address", "City"]):
            current_section = "ContactInfo"
        sections[current_section].append(paragraph)
    
    for section, paragraphs in sections.items():
        section_element = etree.SubElement(root, section)
        for paragraph in paragraphs:
            if paragraph:
                text_element = etree.SubElement(section_element, "Paragraph")
                text_element.text = paragraph
    
    permissions = etree.SubElement(root, "Permissions")
    permission1 = etree.SubElement(permissions, "Permission")
    permission1.text = "PermisoEjemplo"
    
    tree = etree.ElementTree(root)
    tree.write(output_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")

def process_pdf_to_xml(pdf_path, output_xml_path):
    pdf_text = extract_text_from_pdf(pdf_path)
    create_xml(pdf_text, output_xml_path)

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necesario para usar flash messages
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'xmls'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and file.filename.endswith('.pdf'):
            filename = file.filename
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(pdf_path)
            xml_filename = os.path.splitext(filename)[0] + ".xml"
            output_xml_path = os.path.join(OUTPUT_FOLDER, xml_filename)
            process_pdf_to_xml(pdf_path, output_xml_path)
            return redirect(url_for('uploaded_file', filename=xml_filename))
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
