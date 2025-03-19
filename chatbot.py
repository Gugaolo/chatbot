from flask import Flask, request, jsonify
from flask_cors import CORS  
import google.generativeai as genai
import pymupdf  # PyMuPDF (importan kot fitz)
import os

app = Flask(__name__)
CORS(app, resources={r"/chat": {"origins": "https://hobiji-chatbot.lovestoblog.com"}})

# 🔹 Nastavi API ključ pravilno
API_KEY = "AIzaSyDWbxlYuOTGyBmiAkt-FYMswcnAKiMZo3I"  # Zamenjaj z dejanskim ključem
genai.configure(api_key=API_KEY)

# 🔹 Preveri, kateri model je na voljo
AVAILABLE_MODELS = ["gemini-pro", "gemini-pro-1.0", "gemini-pro-vision"]
model_name = "gemini-pro"  # Privzeto

try:
    model = genai.GenerativeModel(model_name)
except Exception as e:
    print(f"Napaka pri nalaganju modela {model_name}: {e}")
    model = None  # Če model ne deluje, ga nastavimo na None

# 🔹 Funkcija za branje PDF-ja
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pymupdf.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text() + "\n"
    except Exception as e:
        print("Napaka pri branju PDF:", e)
    return text

pdf_text = extract_text_from_pdf("instructions.pdf")  

@app.route("/chat", methods=["POST"])
def chat():
    if model is None:
        return jsonify({"response": "Napaka: Model ni bil uspešno naložen."})

    data = request.get_json()
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"response": "Prosim, napišite vprašanje!"})

    # 🔹 Oblikovanje vprašanja za model
    prompt = f"Uporabite naslednje smernice:\n\n{pdf_text}\n\nUporabnik: {user_input}\nOdgovor:"

    try:
        response = model.generate_content(prompt)
        return jsonify({"response": response.text})
    except Exception as e:
        print("Napaka pri generiranju odgovora:", e)
        return jsonify({"response": "Prišlo je do napake pri generiranju odgovora."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  
    app.run(host="0.0.0.0", port=port, debug=True)
