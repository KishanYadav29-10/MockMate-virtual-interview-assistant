import os
import docx2txt
import pdfplumber
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    if not text.strip():
        text = "⚠️ No readable text extracted from PDF."
    return text

def extract_text_from_docx(docx_file):
    text = docx2txt.process(docx_file)
    if not text.strip():
        text = "⚠️ No readable text extracted from DOCX."
    return text

def parse_resume(uploaded_file):
    extension = os.path.splitext(uploaded_file.name)[1]
    if extension == '.pdf':
        return extract_text_from_pdf(uploaded_file)
    elif extension == '.docx':
        return extract_text_from_docx(uploaded_file)
    else:
        return "Unsupported file type"

def extract_links_from_pdf(pdf_file):
    links = set()
    pdf_file.seek(0)
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            annots = page.annots()
            if annots:
                for annot in annots:
                    uri = annot.info.get("uri", "")
                    if uri:
                        links.add(uri)
            for link in page.get_links():
                uri = link.get("uri", "")
                if uri:
                    links.add(uri)
    return list(links)
