from flask import Flask, request, render_template, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
import tempfile
import traceback

# Text extraction libraries
try:
    import fitz  # PyMuPDF for PDF text
except Exception:
    fitz = None
try:
    from PIL import Image
    import pytesseract
except Exception:
    Image = None
    pytesseract = None

# For calling Gemini (user must configure)
import requests
import os

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB

ALLOWED_EXT = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}

def allowed_file(filename):
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXT

def extract_text_from_pdf(path):
    if not fitz:
        return "PDF extraction not available: PyMuPDF (fitz) not installed on server."
    try:
        doc = fitz.open(path)
        pages = []
        for page in doc:
            pages.append(page.get_text("text"))
        return "\\n".join(pages)
    except Exception as e:
        return f"PDF extraction error: {e}"

def extract_text_from_image(path):
    if not pytesseract or not Image:
        return "OCR not available: Pillow or pytesseract not installed."
    try:
        text = pytesseract.image_to_string(Image.open(path))
        return text
    except Exception as e:
        return f"OCR error: {e}"

def call_gemini_for_recommendations(prompt):
    """
    Placeholder function to call Gemini API. The user must set environment variable GEMINI_API_KEY
    and GEMINI_MODEL (optional). This function only demonstrates how to make a POST request.
    If the API key is not set, the function returns a local heuristic suggestion instead.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    model = os.environ.get("GEMINI_MODEL", "gemini-1.0")  # user can customize
    if not api_key:
        # Fallback simple heuristic recommendations
        recs = [
            "Use shorter captions (<= 100 chars) to increase readability.",
            "Add 1-2 relevant hashtags.",
            "Include a call-to-action (e.g., 'Tell us your thoughts!').",
            "Post image carousels for higher engagement on multi-photo posts.",
        ]
        return {"source": "local-fallback", "recommendations": recs, "note": "Set GEMINI_API_KEY env var to enable AI recommendations."}

    url = "https://api.google.com/gemini/v1beta/generate"  # NOTE: example endpoint — user should replace with actual endpoint from Gemini docs
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "prompt": prompt,
        "max_output_tokens": 512,
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # The exact response shape depends on Gemini API — adapt as needed.
        return {"source": "gemini", "raw": data}
    except Exception as e:
        return {"source": "error", "error": str(e), "trace": traceback.format_exc()}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if not allowed_file(f.filename):
        return jsonify({"error": "Unsupported file type"}), 400
    filename = secure_filename(f.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    f.save(save_path)
    # Extract text
    _, ext = os.path.splitext(filename.lower())
    if ext == ".pdf":
        text = extract_text_from_pdf(save_path)
    else:
        text = extract_text_from_image(save_path)
    return jsonify({"filename": filename, "text": text})

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json() or {}
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400
    prompt = f"Analyzing the following social media content. Provide concise suggestions to improve engagement (format as JSON list):\\n\\n{text}\\n\\nGive suggestions focusing on caption length, hashtags, tone, multimedia suggestions, and posting time."
    res = call_gemini_for_recommendations(prompt)
    return jsonify(res)

@app.route("/download/<path:filename>")
def download_file(filename):
    dirpath = os.path.dirname(__file__)
    return send_from_directory(directory=dirpath, path=filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
