from flask import Flask, request
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app)

@app.post("/ask")
def ask():
    body = request.get_json()
    question = body["query"]

    # uruchom rag.py i odbierz dokładnie taki sam tekst jak w konsoli
    result = subprocess.run(
        ["python", "rag.py", question],
        capture_output=True,
        text=True
    )

    # Zwracamy CZYSTY TEKST, a nie JSON
    return result.stdout, 200, {"Content-Type": "text/plain; charset=utf-8"}

app.run(host="0.0.0.0", port=5000)
