from flask import Flask, request, jsonify
from flask_cors import CORS  
import google.generativeai as genai
import pymupdf  # PyMuPDF is still imported as fitz



app = Flask(__name__)
CORS(app)  


genai.configure(api_key="AIzaSyDWbxlYuOTGyBmiAkt-FYMswcnAKiMZo3I")


def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pymupdf.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text() + "\n"
    except Exception as e:
        print("Error reading PDF:", e)
    return text

pdf_text = extract_text_from_pdf("instructions.pdf")  


model = genai.GenerativeModel("gemini-pro-beta")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"response": "Prosim, napišite vprašanje!"})

  
    prompt = f"Uporabite naslednje smernice:\n\n{pdf_text}\n\nUporabnik: {user_input}\nOdgovor:"

    response = model.generate_content(prompt)
    return jsonify({"response": response.text})

if __name__ == "__main__":
    from waitress import serve
    import os
    port = int(os.environ.get("PORT", 5000))  
    serve(app, host="0.0.0.0", port=port)

