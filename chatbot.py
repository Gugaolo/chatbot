import logging
logging.basicConfig(level=logging.INFO)
import traceback
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app, resources={
    r"/chat": {
        "origins": [
            "https://hobiji-chatbot.lovestoblog.com",
            "http://hobiji-chatbot.lovestoblog.com"
        ]
    }
})

# Hugging Face API ključ
HF_API_KEY = os.environ.get("HF_API_KEY")

# Izbrani model na Hugging Face
HF_API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"  # ali drug model, če želiš

headers = {"Authorization": f"Bearer {HF_API_KEY}"}

# (če želiš še vedno brati PDF)
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        import fitz  # pymupdf
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text() + "\n"
    except Exception as e:
        print("Error reading PDF:", e)
    return text

pdf_text = extract_text_from_pdf("instructions.pdf")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        print("Received message:", data)

        if not isinstance(data, dict) or "message" not in data:
            return jsonify({"response": "Error: Invalid JSON format."}), 400

        user_input = data["message"].strip()
        if not user_input:
            return jsonify({"response": "Please write a question!"}), 400

        prompt = f"Use the following guidelines:\n\n{pdf_text}\n\nUser: {user_input}\nAnswer:"

        # Pošljemo zahtevo Hugging Face API-ju
        payload = {"inputs": prompt}
        response = requests.post(HF_API_URL, headers=headers, json=payload)

        if response.status_code != 200:
            print(f"API error: {response.status_code}, {response.text}")
            return jsonify({"response": f"Error: API returned status code {response.status_code}"}), 500

        result = response.json()

        # Hugging Face vrne list ali dict, odvisno od modela
        if isinstance(result, list) and "generated_text" in result[0]:
            generated_text = result[0]["generated_text"]
        elif isinstance(result, dict) and "generated_text" in result:
            generated_text = result["generated_text"]
        else:
            print("Unexpected API response format:", result)
            return jsonify({"response": "Error: Unexpected API response format."}), 500

        print("Model response:", generated_text)
        return jsonify({"response": generated_text})

    except Exception as e:
        print("Error generating response:", str(e))
        print(traceback.format_exc())
        return jsonify({"response": "An error occurred while generating the response."}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
