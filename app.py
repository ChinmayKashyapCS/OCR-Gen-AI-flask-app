import os
from flask import Flask, render_template, request
from PIL import Image
import pytesseract

import google.generativeai as genai

genai.configure(

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.0-flash"
)

# -------------------------

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "bmp",
    "tiff"
}


def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


@app.route("/", methods=["GET", "POST"])
def index():

    extracted_text = ""
    ai_response = ""

    if request.method == "POST":

        action = request.form.get("action")

        # ---------------- OCR ----------------

        if action == "extract":

            file = request.files["image"]

            if file and allowed_file(file.filename):

                filepath = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    file.filename
                )

                file.save(filepath)

                image = Image.open(filepath)

                image = image.convert("L")

                extracted_text = (
                    pytesseract.image_to_string(image)
                )

        # ---------------- GEMINI ----------------

        elif action == "ask_ai":

            extracted_text = request.form.get(
                "context_text"
            )

            prompt = request.form.get(
                "prompt"
            )

            try:

                response = model.generate_content(
                    f"""
Use ONLY this OCR extracted text.

Context:
{extracted_text}

Question:
{prompt}
"""
                )

                ai_response = response.text

            except Exception as e:

                ai_response = (
                    f"Gemini Error: {str(e)}"
                )

    return render_template(
        "index.html",
        extracted_text=extracted_text,
        ai_response=ai_response
    )


if __name__ == "__main__":
    app.run(debug=True)