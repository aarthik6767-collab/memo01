import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai

from chatbot_config import SYSTEM_PROMPT

load_dotenv()

app = Flask(__name__)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is missing from the .env file.")

client = genai.Client(api_key=api_key)
MODEL_NAME = "gemini-3.1-flash-lite"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"reply": "Please enter a vehicle maintenance or troubleshooting question."}), 400

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=f"{SYSTEM_PROMPT}\n\nUser question:\n{user_message}"
        )
        reply = (response.text or "").strip()

        if not reply:
            reply = "I couldn't generate a response right now. Please try your vehicle question again."

        return jsonify({"reply": reply})

    except Exception:
        return jsonify({
            "reply": "Sorry, AutoCare AI is temporarily unable to respond. Please check your Gemini API configuration and try again."
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
