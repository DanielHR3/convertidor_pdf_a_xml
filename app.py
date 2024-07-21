import os
import PyPDF2
from lxml import etree
from flask import Flask, request, redirect, url_for, send_from_directory, render_template, flash

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'xmls'
SCHEMA_FILE = 'schema/schema.xsd'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def extract_text_from_pdf(pdf_path):
    pdf_reader = PyPDF2.PdfReader(pdf_path)
    num_pages = len(pdf_reader.pages)
    text = ""
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        text += page.extract_text() + "\n"
    return text

def create_xml(data, output_path):
    root = etree.Element("TituloElectronico", xmlns="https://www.siged.sep.gob.mx/titulos/", version="1.0", folioControl="sampleFolioControl")
    firma_responsables = etree.SubElement(root, "FirmaResponsables")
    firma_responsable = etree.SubElement(firma_responsables, "FirmaResponsable", nombre="MIGUEL ANGEL", primerApellido="ALEJO", segundoApellido="MACIAS", curp="AEMM830225HDFLCG04", idCargo="1", cargo="DIRECTOR", abrTitulo="Dr.", sello="sampleSello", certificadoResponsable="sampleCertificado", noCertificadoResponsable="00001000000409837457")
    institucion = etree.SubElement(root, "Institucion", cveInstitucion="090002", nombreInstitucion="INSTITUTO POLITÉCNICO NACIONAL")
    carrera = etree.SubElement(root, "Carrera", cveCarrera="515237", nombreCarrera="TÉCNICO EN PLÁSTICOS", fechaInicio="2006-01-01", fechaTerminacion="2009-01-01", idAutorizacionReconocimiento="3", autorizacionReconocimiento="AUTORIZACIÓN FEDERAL")
    profesionista = etree.SubElement(root, "Profesionista", curp="AOJM910903MMCLMR07", nombre="MARIANA", primerApellido="ALONSO", segundoApellido="JIMENEZ", correoElectronico="a.mar.sanorbac_jimenez@hotmail.com")
    expedicion = etree.SubElement(root, "Expedicion", fechaExpedicion="2013-12-04", idModalidadTitulacion="1", modalidadTitulacion="POR TESIS", fechaExamenProfesional="2009-08-05", cumplioServicioSocial="1", idFundamentoLegalServicioSocial="1", fundamentoLegalServicioSocial="ART. 52 LRART. 5 CONST", idEntidadFederativa="09", entidadFederativa="CIUDAD DE MÉXICO")
    antecedente = etree.SubElement(root, "Antecedente", institucionProcedencia="ESCUELA SECUNDARIA TECNICA 47, MÉXICO, D. F.", idTipoEstudioAntecedente="6", tipoEstudioAntecedente="SECUNDARIA", idEntidadFederativa="09", entidadFederativa="CIUDAD DE MÉXICO")
    tree = etree.ElementTree(root)
    tree.write(output_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")
    validate_xml(output_path, SCHEMA_FILE)

def validate_xml(xml_file, xsd_file):
    schema = etree.XMLSchema(file=xsd_file)
    parser = etree.XMLParser(schema=schema)
    with open(xml_file, 'rb') as f:
        etree.fromstring(f.read(), parser)

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

def process_pdf_to_xml(pdf_path, output_xml_path):
    pdf_text = extract_text_from_pdf(pdf_path)
    create_xml(pdf_text, output_xml_path)

if __name__ == '__main__':
    app.run(debug=True)
