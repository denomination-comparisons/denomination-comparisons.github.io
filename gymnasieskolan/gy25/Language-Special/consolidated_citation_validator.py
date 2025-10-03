# Consolidated Citation Validator
# Combines robust and simple validation from citation_validator.py and validator.py
# For Swedish language education, source criticism

import re

def validate_citation(citation_str, mode='robust'):
    """
    Validates citation in text. Mode: 'robust' or 'simple'.
    Robust: Detailed parsing, Simple: Basic checks.
    """
    if mode == 'robust':
        return validate_robust_citation(citation_str)
    else:
        return validate_simple_citation(citation_str)

def validate_robust_citation(citation_str):
    """
    Robust validation with detailed parsing.
    """
    feedback = []
    validated_info = {}

    match = re.match(r"^\s*(?:som|av|i|enligt)?\s*([A-Öa-ö\s]+?)(?:\s*skriver)?,\s*('[^']+'|artikeln|texten),\s*(\*[^\*]+\*|[^\*]+),\s*(\d{4}(-\d{2}-\d{2})?)\s*$", citation_str, re.IGNORECASE)

    if not match:
        feedback.append("Formatet matchar inte. Prova: 'Författare, 'Titel', *Publikation*, ÅÅÅÅ-MM-DD' eller verbal 'som Letmark skriver i DN, 2012'.")
        if not re.search(r'[A-Öa-ö\s]+', citation_str):
            feedback.append("  - Författare saknas.")
        if not re.search(r'('[^']+'|artikeln|texten)', citation_str, re.IGNORECASE):
            feedback.append("  - Titel saknas eller inte markerad.")
        if not re.search(r'(\*[^\*]+\*|[^\*]+)', citation_str):
            feedback.append("  - Publikation saknas.")
        if not re.search(r'\d{4}(-\d{2}-\d{2})?', citation_str):
            feedback.append("  - Datum saknas.")
        return "Problem:\n" + "\n".join(feedback)

    validated_info['författare'] = match.group(1).strip()
    validated_info['titel'] = match.group(2).strip()
    validated_info['publikation'] = match.group(3).strip()
    validated_info['datum'] = match.group(4).strip()

    if re.search(r'(som|av|i|enligt).*skriver', citation_str, re.IGNORECASE):
        feedback.append("Bra: Smidig infogning för tal (anpassad till situationen)!")
    else:
        feedback.append("Tips: För muntligt - väv in som 'som Letmark skriver' för bättre flyt.")

    if not feedback or all(f.startswith("Bra:") for f in feedback):
        return "Korrekt. ✓\nInfo:\n" + "\n".join(f"  {k.capitalize()}: {v}" for k,v in validated_info.items())
    else:
        return "Problem:\n" + "\n".join(feedback)

def validate_simple_citation(citation_str):
    """
    Simple validation with basic checks.
    """
    feedback = []

    if not re.search(r'[A-Öa-ö\s]+', citation_str):
        feedback.append("Författarnamn saknas eller är fel (t.ex. 'Letmark' eller 'Peter Letmark').")

    if not re.search(r'(".*?"|artikeln|texten)', citation_str, re.IGNORECASE):
        feedback.append("Titel saknas eller inte markerad (t.ex. 'Evolutionen gjorde oss talrädda' eller 'artikeln').")

    if not re.search(r'(\* [A-Öa-ö]+\*|[A-Öa-ö]+)', citation_str):
        feedback.append("Publikation saknas (t.ex. 'DN' eller '*DN*').")

    if not re.search(r'\d{4}(-\d{2}-\d{2})?', citation_str):
        feedback.append("Datum saknas eller fel (t.ex. '2012-05-04' eller '2012').")

    if re.search(r'(som|enligt|i|av).*skriver', citation_str, re.IGNORECASE):
        feedback.append("Bra: Smidig infogning (vävd in i talet)!")
    else:
        feedback.append("Tips: Infoga smidigare, t.ex. 'som Letmark skriver i DN' för bättre flyt i anförandet.")

    if len([f for f in feedback if not f.startswith("Bra:")]) == 0:
        return "Källhänvisning ser korrekt ut. ✓ (Anpassad för muntligt tal.)"
    else:
        return "Problem hittades:\n" + "\n".join(feedback)

# Example
if __name__ == "__main__":
    example = "som Peter Letmark skriver i 'Evolutionen gjorde oss talrädda', DN, 2012"
    print("Robust:", validate_citation(example, 'robust'))
    print("Simple:", validate_citation(example, 'simple'))