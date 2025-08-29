
# Social Media Content Analyzer

A lightweight Flask app that accepts PDFs and images, extracts text, and provides AI-driven engagement recommendations.

## Features
- Upload PDFs and images (drag-and-drop or file picker)
- Extract text from PDFs (PyMuPDF) and images (Tesseract OCR)
- AI recommendations via Gemini API (placeholder) or a local fallback
- Basic error handling and loading states

## Setup (Linux / macOS)
1. Install system dependencies:
   - Tesseract OCR (e.g., `sudo apt install tesseract-ocr` or on macOS `brew install tesseract`)
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. (Optional) Set the Gemini API key and model in environment:
   ```bash
   export GEMINI_API_KEY="your_key_here"
   export GEMINI_MODEL="gemini-1.0"
   ```
4. Run the app:
   ```bash
   python app.py
   ```
5. Open http://127.0.0.1:5000 in your browser.

## Notes
- The `call_gemini_for_recommendations` function uses a placeholder URL. Please replace with the official Gemini REST endpoint and adapt the request/response parsing per Google's docs.
- This project focuses on clarity and extensibility. You can add persistent storage, user accounts, or switch to a hosted AI provider easily.
