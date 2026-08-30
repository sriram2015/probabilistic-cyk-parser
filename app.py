from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pcfg_parser import PCFGParser

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)

parser = PCFGParser()

@app.get("/")
def home():
    return send_from_directory(app.static_folder, "index.html")

@app.get("/api/grammar")
def grammar():
    return jsonify({
        "start_symbol": parser.start_symbol,
        "rules": parser.rules_for_display()
    })

@app.post("/api/parse")
def parse_sentence():
    body = request.get_json(silent=True) or {}
    sentence = body.get("sentence", "")
    if not isinstance(sentence, str) or not sentence.strip():
        return jsonify({"error": "Please enter a sentence."}), 400

    try:
        result = parser.parse(sentence)
        return jsonify(result)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Parsing failed: {exc}"}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
