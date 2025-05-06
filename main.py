import os
import time
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

# Načítanie API kľúča zo súboru .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Inicializácia Flask servera
app = Flask(__name__)

# Pamäť konverzácie
session_memory = []

# Ochrana proti spamovaniu API požiadavkami
last_request_time = 0

# Funkcia na rozpoznanie matematických otázok
def is_math_related(prompt):
    math_keywords = ["derivácia", "integrál", "rovnica", "Pytagorova veta", "sinus", "cosinus", "limita", "f(x)"]
    return any(word in prompt.lower() for word in math_keywords)

@app.route('/chat', methods=['POST'])
def chat():
    global session_memory, last_request_time

    if time.time() - last_request_time < 2:  # Limit požiadaviek každé 2 sekundy
        return jsonify({"error": "Príliš veľa požiadaviek, skúste znova neskôr."}), 429
    
    last_request_time = time.time()

    data = request.get_json()
    prompt = data.get("prompt", "")

    if not prompt:
        return jsonify({"error": "Žiadosť musí obsahovať 'prompt'"}), 400

    if not is_math_related(prompt):
        return jsonify({"message": "Prepáč, ale odpovedám iba na matematické otázky."})

    # Systémová správa: chatbot odpovedá iba na matematické otázky
    messages = [
        {"role": "system", "content": "Si expert na matematiku. Odpovedáš len na matematické otázky. Ak je otázka príliš zložitá, poskytnem polopatistické vysvetlenie."},
        {"role": "user", "content": prompt}
    ]

    session_memory.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=session_memory
        )

        answer = response.choices[0].message.content
        session_memory.append({"role": "assistant", "content": answer})

        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
