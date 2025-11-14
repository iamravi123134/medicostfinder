
dir
import re
from difflib import get_close_matches

# Simple mapping: keyword -> canonical treatment code and display name
TREATMENT_KEYWORDS = {
    "appendectomy": ("APPENDECTOMY", "Appendectomy / Appendix surgery"),
    "cataract": ("CATARACT_SURGERY", "Cataract Surgery"),
    "ceaserean": ("C_SECTION", "C-Section"),
    "cesarean": ("C_SECTION", "C-Section"),
    "c-section": ("C_SECTION", "C-Section"),
    "angioplasty": ("ANGIOPLASTY", "Angioplasty"),
    "coronary angioplasty": ("ANGIOPLASTY", "Angioplasty"),
    "dialysis": ("DIALYSIS_SESSION", "Dialysis (per session)"),
    "kidney dialysis": ("DIALYSIS_SESSION", "Dialysis (per session)"),
    "mri brain": ("MRI_BRAIN", "MRI - Brain"),
    "mri": ("MRI_GENERIC", "MRI - Generic"),
    "x-ray chest": ("XRAY_CHEST", "X-Ray - Chest"),
    "xray": ("XRAY_GENERIC", "X-Ray - Generic"),
    "ct scan": ("CT_SCAN", "CT Scan"),
    "blood transfusion": ("BLOOD_TRANSFUSION", "Blood Transfusion"),
    "chemotherapy": ("CHEMO", "Chemotherapy (per cycle)"),
    # add more as needed...
}

# synonyms to expand simple matching
SYNONYMS = {
    "appendix": "appendectomy",
    "cataract surgery": "cataract",
    "mri head": "mri brain",
    "ct": "ct scan",
}

def normalize_text(text):
    return text.lower()

def extract_treatments_from_text(text, top_n=3):
    """
    Very simple heuristic extractor:
    - search for known keywords and synonyms in OCR text
    - fallback: try to find medical-phrase-like patterns (e.g., MRI, CT, Dialysis)
    Returns a list of canonical treatment codes (strings) in order of likely relevance.
    """
    norm = normalize_text(text)
    found = []
    # check synonyms first
    for syn, mapped in SYNONYMS.items():
        if syn in norm and mapped not in found:
            # map mapped to canonical code
            code, name = TREATMENT_KEYWORDS.get(mapped, (mapped.upper(), mapped))
            found.append(code)

    # check explicit keywords
    for kw, (code, _) in TREATMENT_KEYWORDS.items():
        if kw in norm and code not in found:
            found.append(code)

    # If nothing found, attempt regex for patterns like 'MRI', 'CT', 'dialysis', 'x-ray'
    if not found:
        keywords = ["mri", "ct scan", "dialysis", "x-ray", "xray", "dialysis", "angioplasty", "cataract", "appendix"]
        for k in keywords:
            if k in norm:
                if k in TREATMENT_KEYWORDS:
                    code, _ = TREATMENT_KEYWORDS[k]
                else:
                    # try partial matching
                    closest = get_close_matches(k, list(TREATMENT_KEYWORDS.keys()), n=1, cutoff=0.6)
                    if closest:
                        code, _ = TREATMENT_KEYWORDS[closest[0]]
                    else:
                        code = k.upper().replace(" ", "_")
                if code not in found:
                    found.append(code)

    # Limit to top_n
    return found[:top_n]