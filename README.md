
# Social Media Content Analyzer

A lightweight Flask app that accepts PDFs and images, extracts text, and provides AI-driven engagement recommendations.

## Approach

I developed a lightweight Flask web application that allows users to upload PDFs and images to automatically extract text and generate actionable engagement insights. For PDFs, text extraction is handled using PyMuPDF, while images are processed with Tesseract OCR. The extracted content is then sent to an AI service, which provides recommendations for improving social media engagement, including optimizing post structure, captions, and hashtags.

The frontend features a clean, single-page HTML interface with drag-and-drop uploads, live previews for images and PDFs, and clear loading indicators, ensuring a smooth and responsive experience on both desktop and mobile devices. The backend provides a RESTful endpoint for requesting AI recommendations and includes error handling for unsupported file types or extraction issues, maintaining reliability and user confidence.

This solution emphasizes clarity, ease of deployment, and extensibility. Developers can easily swap the AI integration, add user authentication, or expand analytics. The application is lightweight, can run locally, or be deployed on cloud platforms, making it accessible to content creators, marketers, and small businesses seeking immediate, AI-driven feedback on their posts.


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

   
## 🚀 Live Demo

Check out the live project here: [Social Media Analyzer](https://social-media-content-analyzer-4.onrender.com/)


## Outcome of the Project

### Dashboard View
![Text Extraction](https://github.com/user-attachments/assets/b8f13da5-5de3-43d0-af04-2f856f670669)


### Upload Preview
![Recommendations for More Engagement improvements](https://github.com/user-attachments/assets/e6812a7c-a70b-404d-a2a3-f1a2aa9fa97b)



## Notes
- The `call_gemini_for_recommendations` function uses a placeholder URL. Please replace with the official Gemini REST endpoint and adapt the request/response parsing per Google's docs.
- This project focuses on clarity and extensibility. You can add persistent storage, user accounts, or switch to a hosted AI provider easily.
