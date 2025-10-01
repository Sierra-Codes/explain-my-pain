# tagger_logic.py — taxonomy-aligned metaphor tagger with patient/doctor narratives
# Uses Bullo's research-derived taxonomy.

from __future__ import annotations
import re
import sys
from typing import Dict, List, Set, Optional, Any

# -----------------------
# Imports (package-aware)
# Try relative first (when running as a package, e.g. on Render),
# then fall back to absolute (when run from inside backend/ locally).
# -----------------------
try:
    from .taxonomy import taxonomy as _TAXONOMY  # type: ignore
except Exception:
    try:
        from taxonomy import taxonomy as _TAXONOMY  # type: ignore
    except Exception as e:
        raise ImportError(
            "Could not import taxonomy. Ensure backend/taxonomy.py defines `taxonomy` "
            "with keys: metaphor_types, graduation_modifiers, triggers, life_impact_clues."
        ) from e


def _empty_entailments(_category: str) -> Dict[str, List[str]]:
    # Safe default so app runs even if entailments import fails
    return {"experiential": [], "affective": []}


try:
    # Expecting: def get_entailments(category: str) -> dict
    from .entailments import get_entailments as _get_entailments  # type: ignore
except Exception:
    try:
        from entailments import get_entailments as _get_entailments  # type: ignore
    except Exception:
        print("[WARN] entailments.get_entailments not found; using empty entailments.", file=sys.stderr)
        _get_entailments = _empty_entailments

# -----------------------
# Public knobs (populated from taxonomy)
# -----------------------
METAPHOR_TYPES: Dict[str, Dict[str, Any]] = {}
GRADUATION: List[str] = []
TRIGGERS: List[str] = []
LIFE_IMPACT: List[str] = []

# Precompiled patterns holder
_COMPILED: Dict[str, List[re.Pattern]] = {}

# -----------------------
# Normalization
# -----------------------


def _normalize(text: Any) -> str:
    """Lowercase; remove punctuation except spaces & apostrophes; collapse whitespace."""
    if not isinstance(text, str):
        text = "" if text is None else str(text)
    text = re.sub(r"[^\w\s']", " ", text.lower()).strip()
    return re.sub(r"\s+", " ", text)


# -----------------------
# Variants helpers
# -----------------------
_BRIT_AMER_MAP = {
    "labour": {"labor"},
    "favourite": {"favorite"},
    "colour": {"color"},
    "behaviour": {"behavior"},
    "odour": {"odor"},
    "oestrogen": {"estrogen"},
    "haemorrhage": {"hemorrhage"},
}


def _brit_amer_variants(word: str) -> List[str]:
    w = (word or "").strip().lower()
    alts = {w}
    for brit, amer in _BRIT_AMER_MAP.items():
        if w == brit:
            alts |= amer
        if w in amer:
            alts.add(brit)
    return sorted(alts)


def _irregular_word_variants(word: str) -> List[str]:
    w = (word or "").strip().lower()
    alts = {w}
    specific = {
        "knife": {"knives"},
        "leaf": {"leaves"},
        "wolf": {"wolves"},
        "calf": {"calves"},
        "shelf": {"shelves"},
        "loaf": {"loaves"},
        "life": {"lives"},
        "wife": {"wives"},
    }
    if w in specific:
        alts |= specific[w]
    if w.endswith("fe") and len(w) > 2:
        alts.add(w[:-2] + "ves")
    if w.endswith("f") and len(w) > 1:
        alts.add(w[:-1] + "ves")
    # British/American variants (e.g., labour|labor)
    alts |= set(_brit_amer_variants(w))
    return sorted(alts)

# -----------------------
# Expression compiler (hyphen-aware)
# -----------------------


def _compile_expression(expr: str) -> re.Pattern:
    r"""
    Build a forgiving regex from a taxonomy expression:
      - treat spaces or hyphens in the expression as interchangeable ([-\s]+)
      - for single tokens, match root + (ing|ed|es|s)
      - include irregular alternations + Brit/Amer variants (labour|labor)
    """
    expr = (expr or "").strip().lower()
    if not expr:
        return re.compile(r"(?!x)x")  # never matches

    # If expression contains space OR hyphen, treat both as separators
    if re.search(r"[ \-]", expr):
        parts = [re.escape(p) for p in re.split(r"[ \-]+", expr) if p]
        pattern = r"\b" + r"(?:[-\s]+)".join(parts) + r"\b"
        return re.compile(pattern, re.I)

    # Single-token case
    word = expr
    irregulars = set(_irregular_word_variants(word))
    root = re.sub(r"(?:ing|ed|es|s)$", "", word)
    variants = {word, root} | irregulars
    if len(root) >= 2 and root[-1] == root[-2]:
        variants.add(root[:-1])

    alts = []
    for v in variants:
        if v.endswith("ves"):
            alts.append(re.escape(v))
        elif len(v) >= 3:
            alts.append(re.escape(v) + r"(?:ing|ed|es|s)?")
        else:
            alts.append(re.escape(v))
    alts = sorted(set(alts), key=len, reverse=True)
    pattern = r"\b(?:%s)\b" % "|".join(alts)
    return re.compile(pattern, re.I)

# -----------------------
# Compile from taxonomy
# -----------------------


def _compile_from_taxonomy(tax: Dict[str, Any]) -> None:
    global METAPHOR_TYPES, GRADUATION, TRIGGERS, LIFE_IMPACT, _COMPILED
    METAPHOR_TYPES = dict(tax.get("metaphor_types", {}) or {})
    GRADUATION = list(tax.get("graduation_modifiers", []) or [])
    TRIGGERS = list(tax.get("triggers", []) or [])
    LIFE_IMPACT = list(tax.get("life_impact_clues", []) or [])
    _COMPILED = {
        mtype: [_compile_expression(e)
                for e in (data or {}).get("expressions", [])]
        for mtype, data in METAPHOR_TYPES.items()
    }


def reload_taxonomy(new_taxonomy: Dict[str, Any]) -> None:
    """If you swap taxonomy at runtime, call this to recompile patterns."""
    if not isinstance(new_taxonomy, dict) or "metaphor_types" not in new_taxonomy:
        raise ValueError("new_taxonomy must be a dict with 'metaphor_types'.")
    _compile_from_taxonomy(new_taxonomy)


_compile_from_taxonomy(_TAXONOMY)

# -----------------------
# Matching
# -----------------------


def _match_metaphors_in(text_norm: str) -> Set[str]:
    found: Set[str] = set()
    for mtype, pats in _COMPILED.items():
        for pat in pats:
            if pat.search(text_norm):
                found.add(mtype)
                break
    return found

# -----------------------
# Debias predator vs violent_action
# -----------------------


def _debias_predator_vs_violent(chunk_text: str, cats: Set[str]) -> Set[str]:
    if "violent_action" in cats and "predator" in cats:
        low = (chunk_text or "").lower()
        anticip = re.search(r"\b(waiting|about to|ready to|going to)\s+attack\b", low) or \
            re.search(r"\battack me\b", low)
        if anticip and any(tok in low for tok in ("lurking", "monster", "beast", "predator")):
            cats = set(cats)
            cats.discard("violent_action")
    return cats


# -----------------------
# Context detection (precompiled)
# -----------------------
_CONTEXT_PATTERNS_RAW = {
    "menstruation": [
        r"\b(during|on|with)\s+(my\s+)?period\b",
        r"\bmenstruat(?:e|ion|ing|ory)\b",
        r"\b(menses|bleeding|time of the month)\b",
    ],
    "ovulation": [
        r"\bovulat(?:e|ion|ing|ory)\b",
        r"\bmid\s*cycle\b",
        r"\b(fertile|egg\s*release)\b",
    ],
    "intercourse": [
        r"\b(during|with)\s+(sex|intercourse|penetration)\b",
        r"\bpenetration\b",
    ],
    "defecation": [
        r"\b(during|when|while)\s+(poo|poop|defecat(?:e|ion)|bowel (?:movement|movements)|going to the toilet)\b",
        r"\bgoing to the toilet\b",
        r"\bpassing (?:stool|bowel movements?)\b",
    ],
    "baseline": [
        r"\b(rest of the month|outside (?:of )?(?:flares|periods?)|most days|all the time|baseline)\b",
        r"\bbetween (?:periods|flares)\b",
    ],
}
_CONTEXTS = {ctx: [re.compile(p, re.I) for p in pats]
             for ctx, pats in _CONTEXT_PATTERNS_RAW.items()}


def _find_spans(text: str) -> Dict[str, List[str]]:
    raw = (text or "").strip()
    if not raw:
        return {k: [] for k in _CONTEXTS.keys()} | {"baseline": [""]}
    sentences = re.split(r'(?<=[.!?;])\s+|\n+', raw)
    sentences = [s.strip() for s in sentences if s.strip()]
    spans = {k: [] for k in _CONTEXTS.keys()}
    for sent in sentences:
        low = sent.lower()
        for ctx, pats in _CONTEXTS.items():
            if any(p.search(low) for p in pats):
                spans[ctx].append(sent)
    if not any(spans.values()):
        spans["baseline"] = [raw]
    return spans

# -----------------------
# List mentions (triggers/life impact)
# -----------------------


def _detect_list_mentions(text_norm: str, items: List[str]) -> List[str]:
    hits = []
    for item in items:
        tok = (item or "").strip().lower()
        if tok and tok in text_norm:
            hits.append(item)
    return sorted(set(hits))

# -----------------------
# Signals summary
# -----------------------


def _summarize_signals(entailments: dict) -> str:
    items: List[str] = []
    if isinstance(entailments, dict):
        for vals in entailments.values():
            if isinstance(vals, dict):
                items.extend(vals.get("experiential", []) or [])
                items.extend(vals.get("affective", []) or [])
            elif isinstance(vals, list):
                items.extend(vals)
    AFFECTIVE_HINTS = (
        "fear", "anxiety", "threat", "loss of control", "powerless", "powerlessness",
        "hopeless", "worry", "violation", "invasion", "anticipat", "sentience",
        "identity", "dissociation", "detachment", "stress", "hypervigilance",
    )
    SENSORY_HINTS = (
        "inflammation", "irritation", "temperature", "heat", "hot", "burn", "searing",
        "piercing", "sharp", "localized", "pressure", "tight", "tightening", "constriction",
        "crush", "heavy", "heaviness", "shock", "zapping", "tingling", "electr", "spasm",
        "nerve", "neuropath", "tearing", "pulling", "weight", "drag",
    )
    sens, emo = set(), set()
    for p in items:
        s = str(p).strip()
        if not s:
            continue
        low = s.lower()
        is_aff = any(k in low for k in AFFECTIVE_HINTS)
        is_sens = any(k in low for k in SENSORY_HINTS)
        if is_aff and not is_sens:
            emo.add(s)
        elif is_sens and not is_aff:
            sens.add(s)
        elif is_aff and is_sens:
            emo.add(s)

    def _fmt(seq, label):
        if not seq:
            return ""
        vals = sorted(seq)
        if len(vals) > 8:
            vals = vals[:7] + ["…"]
        return f"**{label}**: " + ", ".join(vals) + "."
    parts = []
    sc = _fmt(sens, "Sensory cues")
    ec = _fmt(emo, "Emotional cues")
    if sc:
        parts.append(sc)
    if ec:
        parts.append(ec)
    return "\n".join(parts)

# -----------------------
# Public API
# -----------------------


def tag_pain_description(description: Any, name: Optional[str] = None, duration: Optional[str] = None) -> Dict[str, Any]:
    raw = (description or "").strip() if isinstance(
        description, str) else _normalize(description)
    norm = _normalize(raw)
    spans = _find_spans(raw)

    matched_by_context: Dict[str, List[str]] = {}
    global_matched: Set[str] = set()
    entailments: Dict[str, Dict[str, List[str]]] = {}

    for ctx, chunks in spans.items():
        ctx_found: Set[str] = set()
        for chunk in chunks:
            cats = _match_metaphors_in(_normalize(chunk))
            cats = _debias_predator_vs_violent(chunk, cats)
            ctx_found |= cats
        if ctx_found:
            matched_by_context[ctx] = sorted(ctx_found)
            global_matched |= ctx_found

    for mtype in sorted(global_matched):
        entailments[mtype] = _get_entailments(mtype)

    triggers_detected = _detect_list_mentions(
        norm, TRIGGERS) if TRIGGERS else []
    life_impact_detected = _detect_list_mentions(
        norm, LIFE_IMPACT) if LIFE_IMPACT else []

    return {
        "matched_metaphors": {m: True for m in sorted(global_matched)},
        "matched_by_context": matched_by_context,
        "entailments": entailments,
        "user_info": {
            "name": name.strip() if isinstance(name, str) and name.strip() else None,
            "duration": duration.strip() if isinstance(duration, str) and duration.strip() else None,
        },
        "input": raw,
        "extras": {
            "triggers_detected": triggers_detected,
            "life_impact_detected": life_impact_detected,
        },
    }


CLINICAL_REPHRASINGS: Dict[str, str] = {
    "violent_action": "Your pain may feel like a violent intrusion on your body, consistent with severe, traumatic episodes.",
    "cutting_tools": "The pain resembles being cut or pierced, possibly indicating sharp, localized discomfort.",
    "internal_machinery": "It feels like something mechanical is grinding or compressing your insides — a harsh, internal disruption.",
    "constriction_pressure": "You may feel intense internal pressure or tightening, as if your body is being squeezed or strangled.",
    "electric_force": "It’s like sudden, sharp shocks or buzzing, which could reflect nerve sensitivity or episodic flare-ups.",
    "weight_burden": "Your pain feels heavy and draining, as if you're carrying something too weighty for your body to bear.",
    "heat": "There’s a burning or searing quality to your pain, often associated with inflammation or heat deep inside.",
    "birth_labour": "The pain mimics labour or birthing sensations — cyclical, intense, and radiating from deep within the pelvis.",
    "lingering_force": "Even when not at its peak, the pain simmers beneath the surface, never fully letting go.",
    "predator": "It feels like something foreign is lurking inside you — invasive, unpredictable, and threatening.",
    "entrapment": "You may feel trapped inside your body, caught in a loop of pain that limits your freedom.",
    "transformation_distortion": "The pain affects how you see yourself — altering your sense of identity or making you feel detached from your body.",
    "literal": "You’re using direct physical terms to describe your pain. This language is clear and still very meaningful.",
}


def generate_patient_summary(results: Dict[str, Any]) -> str:
    if not isinstance(results, dict):
        return "You're living with pain that holds deep meaning."
    matched_global = results.get("matched_metaphors", {})
    matched_ctx = results.get("matched_by_context", {})
    input_text = (results.get("input") or "")
    low_input = input_text.lower()
    name = (results.get("user_info", {}).get("name")) or "You"
    duration = results.get("user_info", {}).get("duration")

    if not matched_global:
        return f"{name}, you're living with pain that holds deep meaning. No specific metaphor patterns were identified this time."

    intro = f"{name}, you're living with pain that holds deep meaning."
    if duration:
        intro += f" You've been experiencing this for {duration.strip()}."
    lines = [intro, ""]

    order = ["menstruation", "ovulation",
             "intercourse", "defecation", "baseline"]
    labels = {
        "menstruation": "**During menstruation**",
        "ovulation": "**During ovulation**",
        "intercourse": "**During intercourse**",
        "defecation": "**When going to the toilet**",
        "baseline": "**The rest of the month**",
    }

    for ctx in order:
        cats = matched_ctx.get(ctx, [])
        if not cats:
            for pat in _CONTEXTS.get(ctx, []):
                if pat.search(low_input):
                    lines.append(
                        f"{labels[ctx]}: You mentioned this, and it matters—even if no specific patterns were detected here today.")
                    break
            continue

        PRIORITY = [
            "heat", "cutting_tools", "constriction_pressure", "electric_force",
            "weight_burden", "birth_labour", "internal_machinery", "lingering_force",
            "predator", "entrapment", "transformation_distortion", "violent_action",
        ]
        chosen = None
        for key in PRIORITY:
            if key in cats and key in CLINICAL_REPHRASINGS:
                chosen = CLINICAL_REPHRASINGS[key]
                break
        if not chosen:
            human = ", ".join(c.replace("_", " ") for c in cats[:3])
            chosen = f"You describe {human} sensations."
        lines.append(f"{labels[ctx]}: {chosen}")

    return "\n".join(lines)


def generate_doctor_summary(results: Dict[str, Any]) -> str:
    if not isinstance(results, dict):
        return "Here is a clinical summary based on your description:\n\n🩺 *Note*: These metaphor-based interpretations are not diagnostic."
    matched_global = results.get("matched_metaphors", {})
    matched_ctx = results.get("matched_by_context", {})
    if not matched_global:
        return ("Your description contains no specific metaphorical patterns that align with known symptom clusters. "
                "However, the language used reflects a complex experience of pain that should be discussed with a healthcare provider for further evaluation.")
    out: List[str] = ["Here is a clinical summary based on your description:\n"]

    if "ovulation" in matched_ctx:
        if any(m in matched_ctx["ovulation"] for m in ("constriction_pressure", "cutting_tools", "violent_action", "electric_force")):
            out.append("**Ovulation-related pain**")
            out.append(
                "Language indicating constriction/stabbing around ovulation suggests uterine/ovarian origin and visceral nerve sensitivity.\n")

    if "menstruation" in matched_ctx:
        if "heat" in matched_ctx["menstruation"] or "birth_labour" in matched_ctx["menstruation"]:
            out.append("**Menstruation-related pain**")
            out.append("**Bowel-related pain**")
                "Burning/flaring language aligns with inflammatory flares or neuroimmune dysregulation during menses.\n")

    if "intercourse" in matched_ctx:
        if any(m in matched_ctx["intercourse"] for m in ("violent_action", "cutting_tools", "constriction_pressure")):
            out.append("**Dyspareunia (pain with intercourse)**")
            out.append("Intrusive/cutting metaphors during intercourse may reflect pelvic floor dysfunction, trauma sequelae, or localized neuropathic irritation.\n")

    if "defecation" in matched_ctx:
        if any(m in matched_ctx["defecation"] for m in ("birth_labour", "cutting_tools", "constriction_pressure", "heat", "violent_action")):
            out.append("**Defecation-related pain**")
            out.append("Labour-like/knife-like or burning metaphors with bowel movements may indicate bowel involvement, inflammatory irritation, or nearby nerve entrapment.\n")

    if "baseline" in matched_ctx:
        if any(m in matched_ctx["baseline"] for m in ("lingering_force", "predator", "weight_burden")):
            out.append("**Chronic baseline pain**")
            out.append(
                "Persistent, lurking/heavy metaphors point to chronic inflammation with anticipatory distress.\n")

    


def generate_entailment_summary(obj: Dict[str, Any]) -> str:
    mapping: Dict[str, Dict[str, List[str]]] = {}
    if isinstance(obj, dict):
        if obj and all(isinstance(k, str) for k in obj.keys()) and isinstance(next(iter(obj.values()), {}), dict) and (
            "experiential" in next(iter(obj.values()), {}) or "affective" in next(
                iter(obj.values()), {})
        ):
            mapping = obj  # type: ignore
        elif "entailments" in obj:
            mapping = obj.get("entailments", {})  # type: ignore
    if not mapping:
        return "No experiential or affective entailments were found."
    lines = [" Clinical interpretations based on metaphor entailments:\n"]
    for mtype, vals in mapping.items():
        exp = vals.get("experiential", []) or []
        aff = vals.get("affective", []) or []
        if exp:
            lines.append(
                f"• **{mtype}** – Experiential entailments: {', '.join(exp)}")
        if aff:
            lines.append(f"  – Affective entailments: {', '.join(aff)}")
    lines.append(
        "\nThese interpretations can support shared understanding between patients and clinicians.")
    return "\n".join(lines)


def generate_doctor_narrative(results: Dict[str, Any]) -> str:
    return generate_doctor_summary(results)


__all__ = [
    "tag_pain_description",
    "generate_patient_summary",
    "generate_doctor_summary",
    "generate_doctor_narrative",
    "generate_entailment_summary",
    "reload_taxonomy",
    "METAPHOR_TYPES", "GRADUATION", "TRIGGERS", "LIFE_IMPACT",
]
