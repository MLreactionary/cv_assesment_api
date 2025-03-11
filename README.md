# cv_assesment_api
## **1. Why These Design Choices?**
### **FastAPI for Backend**
- Chosen for its **speed**, **automatic request validation**, and **built-in API documentation**.
- Supports **async processing**, improving API response time.

### **OCR & Text Extraction**
- **PDF Processing**: Used `pdfplumber` (superior to `PyPDF2` in text accuracy).
- **Image Processing**: Used `pytesseract` (Tesseract OCR for text recognition).
- **Text Files**: Read directly using Python's built-in methods.

### **NLP for Named Entity Recognition (NER)**
- Library: `spaCy`
- Extracts relevant entities (awards, publications, references, etc.) from CVs.
- Helps assess O-1A visa eligibility based on extracted key phrases.

---

## **2. How to Evaluate the API Output**
### **Functional Evaluation**
| Test Case | Input | Expected Output |
|-----------|-------|----------------|
| Valid PDF Upload | PDF with text | Extracted text in JSON format |
| Valid Image Upload | Image with text | Extracted text in JSON format |
| Invalid File Type | `.exe` file | `415 Unsupported Media Type` error |
| Large File (>5MB) | Large PDF | API should process without timeout |

### **Performance Evaluation**
- API response time should be **<1 sec** for standard CVs.
- Evaluate OCR accuracy for **handwritten vs. printed text**.
- Stress test with **multiple concurrent requests**.

---

## **3. Additional Enhancements**
- Store CV data in a database for **historical analysis**.
- Train an ML model to **score CVs based on historical trends**.
- Expand to support **job-role-specific CV assessments**.
