from flask import Flask, request, jsonify
from flask_cors import CORS  
import google.generativeai as genai
import pymupdf
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

API_KEY = "AIzaSyDWbxlYuOTGyBmiAkt-FYMswcnAKiMZo3I"
genai.configure(api_key=API_KEY)

AVAILABLE_MODELS = ["gemini-pro", "gemini-pro-1.0", "gemini-pro-vision"]
model_name = "gemini-pro"

try:
    model = genai.GenerativeModel(model_name)
except Exception as e:
    print(f"Error loading model {model_name}: {e}")
    model = None

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

@app.route("/chat", methods=["POST"])
def chat():
    if model is None:
        return jsonify({"response": "Error: Model not loaded."}), 500

    try:
        data = request.get_json()
        print("Received message:", data)

        if not isinstance(data, dict) or "message" not in data:
            return jsonify({"response": "Error: Invalid JSON format."}), 400

        user_input = data["message"].strip()
        if not user_input:
            return jsonify({"response": "Please write a question!"}), 400

        prompt = f"Use the following guidelines:\n\n{pdf_text}\n\n:User  {user_input}\nAnswer:"
        print("Sending prompt:", prompt)

        response = model.generate_content(prompt)
        if not response or not hasattr(response, "text"):
            return jsonify({"response": "Error: Model did not return a response."}), 500

        print("Model response:", response.text)
        return jsonify({"response": response.text})

    except Exception as e:
        print("Error generating response:", str(e))
        return jsonify({"response": "An error occurred while generating the response."}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  
    app.run(host="0.0.0.0", port=port, debug=True)