from flask import redirect, url_for
from .taxonomy import taxonomy
from .tagger_logic import (
    tag_pain_description,
    generate_patient_summary,
    generate_doctor_summary,
    generate_entailment_summary
)


from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import re

# --- Curated triggers for the UI ---
TRIGGERS_UI = [
    "Menstruation",
    "Ovulation",
    "Sex / Intercourse",
    "Going to the toilet – urination",
    "Going to the toilet – bowel emptying",
    "Daily life / Background",
    "Physical activity",
    "Sleep / Rest",
    "Other",
]

# --- Canonical trigger phrases used inside the text so the tagger recognizes them ---
# These MUST match the context patterns in tagger_logic.py
CANON = {
    "menstruation": "menstruation",
    "ovulation": "ovulation",
    "intercourse": "intercourse",
    "toilet": "going to the toilet",
    "baseline": "rest of the month",
    "activity": "physical activity",
    "rest": "rest",
    "other": "other",
}

# Regex normalisation (catch common variants & punctuation)
NORMALIZE_PATTERNS = [
    (r"\bmenstruation\b|\bperiod\b|\bmenstrual period\b",
     CANON["menstruation"]),
    (r"\bovulation?\b", CANON["ovulation"]),
    (r"\bsex\b|\bintercourse\b", CANON["intercourse"]),
    (r"going to the toilet\s*[–-]\s*urination|\burination\b|\bpee\b|\bwee\b", CANON["toilet"]),
    (r"going to the toilet\s*[–-]\s*bowel emptying|\b(defecat(?:ion|e)|bowel (?:movement|emptying)|poop)\b", CANON["toilet"]),
    (r"\bdaily life\b|\bbackground\b|rest of (?:the )?month",
     CANON["baseline"]),
    (r"\bphysical activity\b|\bactivity\b|\bexercise\b", CANON["activity"]),
    (r"\bsleep\b|\brest\b", CANON["rest"]),
    (r"\bother\b", CANON["other"]),
]


def normalize_triggers(text: str) -> str:
    if not text:
        return text
    out = text.replace("–", "-").replace("—", "-")
    for pat, canon in NORMALIZE_PATTERNS:
        out = re.sub(pat, canon, out, flags=re.IGNORECASE)
    return out


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_default_secret")

CORS(app, resources={r"/*": {"origins": [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]}})


@app.route("/", methods=["GET"])
def index():
    # Render the inline HTML, passing taxonomy to front-end JS for category/expressions
    return render_template("index.html", taxonomy=taxonomy)


@app.route("/evidence", methods=["GET"])
def evidence_page():
    # renders backend/templates/evidence.html
    return render_template("evidence.html")


# optional alias so /evidence.html also works


@app.route("/evidence.html", methods=["GET"])
def evidence_html_alias():
    return redirect(url_for("evidence_page"))


@app.route("/analyze", methods=["POST"])
def analyze():
    # Accept either constructed text or fallback from individual fields
    description = (request.form.get("description", "") or "").strip()

    # Optional structured inputs (used to build text if description is empty)
    trigger = (request.form.get("trigger", "") or "").strip()
    category = (request.form.get("category", "") or "").strip()
    expression = (request.form.get("expression", "") or "").strip()

    # Optional context
    name = (request.form.get("name", "") or "").strip()
    duration = (request.form.get("duration", "") or "").strip()
    overall = (request.form.get("overall", "") or "").strip()
    qol = (request.form.get("qol", "") or "").strip()

    # If textarea is empty but the user filled the 3 selects, build a minimal description on the server.
    if not description:
        bits = []
        if trigger and category and expression:
            nice_cat = category.replace("_", " ")
            bits.append(f"During {trigger}: {expression} ({nice_cat}).")
        if overall:
            bits.append(f"Overall: {overall}.")
        if qol:
            bits.append(f"Quality of life: {qol}.")
        description = " ".join(bits).strip()

    # Normalise trigger labels so the tagger recognises them
    description = normalize_triggers(description)

    if description:
        try:
            results = tag_pain_description(
                description,
                name=name or None,
                duration=duration or None
            )

            results["input"] = description
            plain = generate_patient_summary(results)
            doctor = generate_doctor_summary(results)
            entail = generate_entailment_summary(
                results.get("entailments", {}))

            payload = {
                "ok": True,
                "patient": plain,
                "doctor": doctor,
                "entailments": entail,
                "results": results,
            }
            # Always return JSON (front-end fetch expects it)
            return jsonify(payload)
        except Exception as e:
            return jsonify({"ok": False, "error": str(e), "input": description}), 500

    return jsonify({"ok": False, "error": "No description provided."}), 400

# Simple health-check / JSON testing route


@app.route("/analyze.json", methods=["POST"])
def analyze_json():
    data = request.get_json(silent=True) or {}
    description = normalize_triggers((data.get("description") or "").strip())
    name = (data.get("name") or "").strip()
    duration = (data.get("duration") or "").strip()

    try:
        results = tag_pain_description(
            description,
            name=name or None,
            duration=duration or None
        )

        results["input"] = description
        plain = generate_patient_summary(results)
        doctor = generate_doctor_summary(results)
        entail = generate_entailment_summary(results.get("entailments", {}))

        payload = {
            "ok": True,
            "patient": plain,
            "doctor": doctor,
            "entailments": entail,
            "results": results,
        }
        return jsonify(payload)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e), "input": description}), 500


if __name__ == "__main__":
    app.run(debug=True, port=int(os.getenv("PORT", "5001")))
