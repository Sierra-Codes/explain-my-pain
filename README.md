# Explain My Pain

**Explain My Pain** helps people describe pelvic and endometriosis‑related pain clearly.  
It turns simple choices (when it happens, what it feels like) into:

- a short, friendly **patient summary** (“This is your pain explained”), and  
- clear, structured **notes for clinicians** (grouped by context, with concise language).

This app was developed from research led by linguistics PhD and health communication specialist **Dr Stella Bullo**.  
See also the forthcoming article: **Bullo, S. (2025). _The Language of Endometriosis: A Taxonomy of Pain Descriptors_.**

---

## Who is it for?

- **People living with pelvic/endo pain** who want help explaining their symptoms.  
- **Clinicians** who appreciate a quick, structured summary of the patient’s language.  
- **Researchers & educators** exploring pain metaphors and communication.

---

## What the app does (in plain terms)

1. You choose **when** the pain happens (e.g., during menstruation, ovulation, intercourse, toilet, background/rest of month, activity, sleep/rest).  
2. You choose **what it feels like** from curated categories (e.g., *cutting*, *constriction/pressure*, *electric*, *heat*, *weight/burden*, etc.), then pick a ready‑made expression (e.g., “like broken glass”, “tightening”, “zapping”).  
3. *(Optional)* You tick some **overall** feelings and **quality‑of‑life** impacts (e.g., “I feel isolated”, “Affects my productivity”).

The app then builds two accessible summaries:

- **Patient summary** – uses “you” language and plain words.  
- **Clinician notes** – grouped by clinical contexts (e.g., *Menstruation‑related pain*, *Dyspareunia (pain with intercourse)*, etc.), plus a short **Metaphor interpretation** section.

There’s also an **Evidence** page with key references.

---

## Why this helps

- Many people struggle to find the words for pain.  
- Clinicians often need structured, concise notes.  
- Shared language improves consultations and reduces “lost in translation” moments.

---

## What you see on the page

- **“What you’ve added”** – a quick preview of your selected descriptions by context.  
- **This is your pain explained (patient)** – a short paragraph in friendly, everyday language.  
- **Notes your doctor may find useful (clinician)** – headings by context with compact statements, plus optional **Metaphor interpretation**.  
- **Evidence** – a link to key literature and clinical guidance at `/evidence`.

---

## Data & privacy

- The app runs **locally on your computer** (a small Flask server).  
- **No third‑party APIs**. No data is sent elsewhere.  
- Refreshing the page clears the working state.

> This tool supports communication. It is **not** a diagnostic device and does not replace medical advice.

---

## Quick start (local use)

```bash
# From the repo root:
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open in your browser:

- App: `http://127.0.0.1:5001/`  
- Evidence: `http://127.0.0.1:5001/evidence`

> If you see “Port 5001 in use”, run with another port:  
> `PORT=5002 python app.py` → then open `http://127.0.0.1:5002/`.

---

## How it works (a peek under the hood)

- A curated **taxonomy of pain metaphors** powers the choices (see `backend/taxonomy.py`).  
- The front‑end builds a clean text description and sends it to the server.  
- The back‑end (**Flask**) tags it and generates two summaries (patient + clinician).  
- Clinician notes are normalized to consistent headings and ordering.

---

## Evidence & references

Open **`/evidence`** for a short, readable list. Core references include:

- Bullo, S. (2020). “I feel like I’m being stabbed by a thousand tiny men”: The challenges of communicating endometriosis pain. _Health_, 24(5), 476–492.  
- Bullo, S., & Hearn, J. H. (2021). Parallel worlds and personified pain: A mixed‑methods analysis of pain metaphor use by women with endometriosis. _British Journal of Health Psychology_, 26(2), 271–288. doi:10.1111/bjhp.12472  
- Latest clinical guidelines relevant to your region.

---

## Troubleshooting

- **The page loads but the Evidence link 404s**  
  Make sure `backend/templates/evidence.html` exists and `app.py` has:
  ```python
  @app.route("/evidence")
  def evidence_page():
      return render_template("evidence.html")
  ```
  You can also add an alias:
  ```python
  @app.route("/evidence.html")
  def evidence_html_alias():
      from flask import redirect, url_for
      return redirect(url_for("evidence_page"))
  ```

- **“Port is in use”**  
  Another instance is running. Either close it or run:  
  `PORT=5002 python app.py`

- **Blank output**  
  Add at least one description *or* tick Overall/Quality‑of‑life options, then press **Continue**.

---

## For developers

**Project structure**
```
explain-my-pain/
├─ backend/
│  ├─ app.py                  # Flask routes (/ , /analyze, /evidence)
│  ├─ taxonomy.py             # Curated metaphor types & expressions
│  ├─ tagger_logic.py         # Tagging + summary generation
│  ├─ templates/
│  │  ├─ index.html           # UI + inline JS
│  │  └─ evidence.html        # Evidence page
│  └─ static/                 # (optional assets)
├─ requirements.txt
└─ README.md
```

**.gitignore** already excludes `__pycache__`, `.DS_Store`, and virtual envs.  
No API keys required.

---

## Accessibility

- Keyboard‑reachable controls and clear labels  
- High‑contrast palette  
- Concise language with minimal jargon

---

## License

Add the license you prefer (e.g., MIT/Apache‑2.0/CC‑BY‑NC) as `LICENSE` in the repo root.

---

## Acknowledgements & citation

- Research & taxonomy: **Dr Stella Bullo**  
- UX/engineering support: collaborators (see commit history)

If you use this app or taxonomy in research/clinical settings, please cite:

> Bullo, S. (2025). _The Language of Endometriosis: A Taxonomy of Pain Descriptors_.  
> Bullo, S. (2020); Bullo, S., & Hearn, J. H. (2021).
