from flask import Flask, request, render_template, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
import traceback
import requests
import json
import re
from dotenv import load_dotenv
import pytesseract

# Linux path after installation
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

import random

# Load environment variables from .env
load_dotenv()

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

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB

ALLOWED_EXT = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp", ".avif"}


def allowed_file(filename):
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXT


def extract_text_from_pdf(path):
    if not fitz:
        return "PDF extraction not available: PyMuPDF (fitz) not installed."
    try:
        doc = fitz.open(path)
        pages = [page.get_text("text") for page in doc]
        text = "\n".join(pages).strip()

        # Fallback to OCR if no text found
        if not text:
            return extract_text_from_image(path)
        return text
    except Exception as e:
        return f"PDF extraction error: {e}"


def extract_text_from_image(path):
    if not pytesseract or not Image:
        return "OCR not available: Pillow or pytesseract not installed."
    try:
        return pytesseract.image_to_string(Image.open(path)).strip()
    except Exception as e:
        return f"OCR error: {e}"


def call_gemini_for_recommendations(prompt):
    api_key = os.environ.get("GEMINI_API_KEY")
    model = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

    if not api_key:
        return {
            "source": "local-fallback",
            "recommendations": [
                {"aspect": "Caption Length", "suggestion": "Use concise captions (under 100 chars)."},
                {"aspect": "Hashtags", "suggestion": "Add 3–5 relevant hashtags."}
            ],
            "note": "No GEMINI_API_KEY found. Using fallback."
        }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        resp = requests.post(url, headers=headers, params={"key": api_key}, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        # Extract model output text
        text = ""
        if "candidates" in data and data["candidates"]:
            text = data["candidates"][0]["content"]["parts"][0]["text"]

        # Clean ```json wrappers
        cleaned = re.sub(r"```[a-zA-Z]*", "", text).replace("```", "").strip()

        # Parse JSON if valid
        try:
            recommendations = json.loads(cleaned)
        except Exception:
            recommendations = [{"aspect": "General", "suggestion": cleaned}]

        return {"source": "gemini", "recommendations": recommendations}
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

    # Extract text (PDF → text, else OCR)
    _, ext = os.path.splitext(filename.lower())
    text = extract_text_from_pdf(save_path) if ext == ".pdf" else extract_text_from_image(save_path)

    return jsonify({
        "filename": filename,
        "text": text,
        "file_url": f"/uploads/{filename}"
    })


@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json() or {}
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    prompt = (
        "You are an AI content strategist. Analyze the following text for social media engagement:\n\n"
        f"{text}\n\n"
        "Respond ONLY in JSON array format, where each item has:\n"
        "{ 'aspect': '...', 'suggestion': '...' }\n"
        "Focus on caption length, hashtags, tone, multimedia suggestions, posting time, and engagement."
    )
    res = call_gemini_for_recommendations(prompt)
    return jsonify(res)


@app.route("/analyze_post", methods=["POST"])
def analyze_post():
    data = request.get_json()
    text = data.get("text", "")

    # --- Extract likes from text using regex ---
    likes = 0
    match_likes = re.search(r"([\d,]+)\s+likes", text, re.IGNORECASE)
    if match_likes:
        likes = int(match_likes.group(1).replace(",", ""))

    # --- Estimate comments count ---
    # For now, count how many lines look like user comments (heuristic: contains '@' or more than 3 words)
    comments_lines = [line for line in text.splitlines() if "@" in line or len(line.split()) > 3]
    comments = len(comments_lines)

    # If no likes detected, fall back to random
    if likes == 0:
        likes = random.randint(100, 1000)
    if comments == 0:
        comments = random.randint(10, 100)

    # Call AI recommendation logic
    prompt = (
        "You are an AI content strategist. Analyze the following text for social media engagement:\n\n"
        f"{text}\n\n"
        "Respond ONLY in JSON array format, where each item has:\n"
        "{ 'aspect': '...', 'suggestion': '...' }\n"
    )
    ai_result = call_gemini_for_recommendations(prompt)

    # Growth after AI suggestion (simulate improvement)
    updated_likes = int(likes * 1.2)
    updated_comments = int(comments * 1.3)

    return jsonify({
        "likes": likes,
        "comments": comments,
        "updated_likes": updated_likes,
        "updated_comments": updated_comments,
        "recommendations": ai_result
    })



@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/download/<path:filename>")
def download_file(filename):
    dirpath = os.path.dirname(__file__)
    return send_from_directory(directory=dirpath, path=filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
