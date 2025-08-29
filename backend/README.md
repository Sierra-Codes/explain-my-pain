# Explain My Pain 🩺🧠

**Explain My Pain** is a patient-centered web app that uses natural language processing (NLP) to analyze metaphorical descriptions of chronic pelvic pain, particularly in endometriosis. It transforms free-text pain descriptions into structured summaries to support doctor–patient communication, clinical understanding, and research into figurative language in healthcare.

---

## 🧩 What It Does

- **Identifies metaphorical language** using a custom taxonomy  
- **Tags metaphors** by type and maps them to experiential and emotional dimensions  
- **Generates outputs** tailored for:  
  - 🫂 **Patients** (“How this might feel to you”)  
  - 🩺 **Doctors** (“Clinical notes”)  
- **Supports structured summaries** ready for printing or discussion

---

## 🛠️ Tech Stack

- **Python** (Flask)  
- **Regex-based NLP** with a handcrafted metaphor taxonomy  
- **HTML/CSS** (Jinja templates)  
- **JSON-based knowledge base** for metaphor types, entailments, and rephrasings  
- **Print-ready UI** for exporting symptom summaries

---

## 📂 Project Structure

```
.
├── app.py                 # Flask app logic and routes
├── tagger_logic.py        # Core metaphor tagging engine
├── entailments.py         # Returns experiential/affective entailments
├── taxonomy.json          # Metaphor taxonomy
├── clinical_map.json      # Clinical interpretations
├── templates/
│   ├── index.html         # Main app UI
│   ├── pdf_template.html  # Printable output
│   ├── samples.html       # Example phrases
│   └── evidence.html      # Research evidence and medical sources
└── static/                # (Optional) style/media assets
```

---

## 🧪 Example Use Case

**Input:**

> “When I ovulate, it feels like someone is strangling my womb. During my period, it’s like a fireball tearing through me.”

**Detected Tags:**

- `strangling` → `constriction_pressure`  
- `fireball`, `tearing` → `heat`, `violent_action`

**Output:**

- Natural-language summary for the patient  
- Structured clinical summary for the doctor  
- Experiential entailments (e.g., inflammation, internal pressure)

---

## 🔍 Who Is It For?

- People living with **endometriosis** or **chronic pelvic pain**  
- Clinicians seeking **clearer patient narratives**  
- Researchers exploring **health communication and metaphor**  
- Employers or funders looking for **real-world NLP + digital health projects**

---

## 🚀 How to Run Locally

```bash
# 1. Clone the repo and set up a virtual environment
git clone https://github.com/yourusername/explain-my-pain.git
cd explain-my-pain
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install flask

# 3. Run the app
python app.py

# 4. Visit in your browser
http://127.0.0.1:5000/
```

---

## 👩‍💻 Developer

**Dr Stella Bullo**  
Linguist · Python Developer · NLP Specialist  
ORCID: [0000-0002-7402-0819](https://orcid.org/0000-0002-7402-0819)  
🌐 [Portfolio](https://stellabullo.com) · 🐙 [GitHub](https://github.com/Sierra-Codes)

---

## 📚 Research & Ethics

This tool was created by a researcher and developer with lived experience of endometriosis. It builds on peer-reviewed literature, patient narratives, and ethical principles in health communication.

It aims to amplify patient voices while supporting clinicians with better linguistic tools.

> ⚠️ This is not a diagnostic tool. Outputs are meant to support—never replace—medical consultation or care.

For detailed sources and methodology, see the [Evidence & Sources](templates/evidence.html) page.

---

## 📝 License

This project is licensed under the [MIT License](LICENSE).
