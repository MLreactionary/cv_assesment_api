from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import spacy
import pdfplumber
from docx import Document
from PIL import Image
import pytesseract

app = FastAPI()
nlp = spacy.load("en_core_web_sm")

# Define response model
class AssessmentResult(BaseModel):
    criteria_met: dict
    rating: str

# Define keywords for each O-1A criterion
criteria_keywords = {
    "Awards": ["award", "honor", "prize", "recognition"],
    "Membership": ["member of", "fellowship", "committee"],
    "Press": ["media", "interview", "article", "featured"],
    "Judging": ["judge", "reviewer", "panel"],
    "Original Contribution": ["invention", "patent", "breakthrough"],
    "Scholarly Articles": ["publication", "research paper", "journal"],
    "Critical Employment": ["leadership", "founder", "director"],
    "High Remuneration": ["salary", "compensation", "earnings"]
}

# Function to extract text from PDFs
def extract_text_from_pdf(file):
    try:
        with pdfplumber.open(file) as pdf:
            return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

# Function to extract text from Word documents
def extract_text_from_docx(file):
    try:
        doc = Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing DOCX: {str(e)}")

# Function to extract text from images using OCR
def extract_text_from_image(file):
    try:
        image = Image.open(file)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

# Function to assess CV content
def assess_cv(text: str) -> AssessmentResult:
    doc = nlp(text)
    criteria_met = {criterion: [] for criterion in criteria_keywords}

    for sent in doc.sents:
        for criterion, keywords in criteria_keywords.items():
            if any(keyword in sent.text.lower() for keyword in keywords):
                criteria_met[criterion].append(sent.text)

    met_count = sum(bool(v) for v in criteria_met.values())
    rating = "high" if met_count >= 6 else "medium" if met_count >= 3 else "low"

    return AssessmentResult(criteria_met=criteria_met, rating=rating)

# API endpoint to upload CV and get assessment
@app.post("/assess-cv", response_model=AssessmentResult)
async def assess_cv_endpoint(file: UploadFile = File(...)):
    try:
        # Extract text from PDF, DOCX, or Image
        if file.filename.endswith(".pdf"):
            text = extract_text_from_pdf(file.file)
        elif file.filename.endswith(".docx"):
            text = extract_text_from_docx(file.file)
        elif file.filename.endswith((".png", ".jpg", ".jpeg")):
            text = extract_text_from_image(file.file)
        else:
            text = (await file.read()).decode("utf-8")

        if not text.strip():
            raise HTTPException(status_code=400, detail="Empty document uploaded.")

        result = assess_cv(text)
        return result
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid file format. Only PDF, DOCX, and image files are supported.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
