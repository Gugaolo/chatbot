from flask import Flask, request, jsonify
from flask_cors import CORS  
import google.generativeai as genai
import fitz  # PyMuPDF for extracting text from PDF

app = Flask(__name__)
CORS(app)  

# Configure Gemini API key
genai.configure(api_key="AIzaSyDWbxlYuOTGyBmiAkt-FYMswcnAKiMZo3I")

# Load PDF and extract text
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text() + "\n"
    except Exception as e:
        print("Error reading PDF:", e)
    return text

pdf_text = extract_text_from_pdf("instructions.pdf")  # Change to your actual PDF file

# Model for generating responses
model = genai.GenerativeModel("gemini-pro")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"response": "Prosim, napišite vprašanje!"})

    # Combine PDF instructions with user input
    prompt = f"Uporabite naslednje smernice:\n\n{pdf_text}\n\nUporabnik: {user_input}\nOdgovor:"

    response = model.generate_content(prompt)
    return jsonify({"response": response.text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
