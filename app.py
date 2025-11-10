from flask import Flask, request, render_template
import os, requests, uuid

ENDPOINT = os.getenv("TRANSLATOR_ENDPOINT", "https://api.cognitive.microsofttranslator.com")
KEY = os.getenv("TRANSLATOR_KEY")
REGION = os.getenv("TRANSLATOR_REGION", "eastus")

app = Flask(__name__)

def translate_text(text, targets):
    """Call Azure Translator to translate `text` into list of language codes in `targets`."""
    if not KEY:
        raise RuntimeError("TRANSLATOR_KEY is not set in environment variables.")
    url = f"{ENDPOINT}/translate"
    params = [
        ("api-version", "3.0"),
    ] + [("to", t) for t in targets]  # multiple &to=xx parameters
    headers = {
        "Ocp-Apim-Subscription-Key": KEY,
        "Ocp-Apim-Subscription-Region": REGION,
        "Content-Type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4())
    }
    body = [{"Text": text}]
    r = requests.post(url, params=params, headers=headers, json=body, timeout=15)
    r.raise_for_status()
    data = r.json()
    # data[0]["translations"] -> list of { "text": "...", "to": "xx" }
    return data[0].get("translations", [])

@app.route("/", methods=["GET", "POST"])
def index():
    result = []
    text = ""
    targets_str = "hi,fr,ja"  # default suggestions
    error = None

    if request.method == "POST":
        text = request.form.get("text", "").strip()
        targets_str = request.form.get("targets", "hi,fr,ja").strip()
        targets = [t.strip() for t in targets_str.split(",") if t.strip()]
        try:
            if not text:
                error = "Please enter some text to translate."
            elif not targets:
                error = "Please specify at least one target language code."
            else:
                result = translate_text(text, targets)
        except Exception as e:
            error = str(e)

    return render_template("index.html", result=result, text=text, targets=targets_str, error=error)

if __name__ == "__main__":
    # For Azure Cloud Shell, prefer port 8080 and host 0.0.0.0
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
