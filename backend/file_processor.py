from PIL import Image
import pytesseract
import PyPDF2
import docx2txt
import io


def process_file(uploaded_file) -> str:
    """
    Processes uploaded files and extracts text content.

    Supported:
    ✅ Plain text files
    ✅ PDFs (basic text extraction)
    ✅ DOCX Word documents
    ✅ Images with OCR (jpg, png, etc.)
    ✅ Placeholders for Excel/PowerPoint

    Returns:
    Extracted text or descriptive error message.
    """
    file_type = uploaded_file.type.lower()
    file_name = uploaded_file.name.lower()

    try:
        if "text" in file_type:
            content = uploaded_file.read().decode("utf-8")
            return content.strip() or "⚠️ Empty text file."

        if file_name.endswith(".pdf"):
            reader = PyPDF2.PdfReader(uploaded_file)
            extracted = " ".join(filter(None, (page.extract_text() for page in reader.pages)))
            return extracted.strip() or "⚠️ PDF has no extractable text."

        if file_name.endswith(".docx"):
            text = docx2txt.process(uploaded_file)
            return text.strip() or "⚠️ Word document is empty."

        if file_name.endswith((".xlsx", ".xls")):
            return "📊 Excel file detected. Parsing not implemented."

        if file_name.endswith((".pptx", ".ppt")):
            return "📈 PowerPoint file detected. Parsing not implemented."

        if "image" in file_type:
            image = Image.open(uploaded_file)
            text = pytesseract.image_to_string(image)
            return text.strip() or "⚠️ No text detected in image."

    except Exception as e:
        return f"⚠️ Error processing file: {str(e)}"

    return "❌ Unsupported file type."
