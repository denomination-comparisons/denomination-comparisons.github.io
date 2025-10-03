# Fil: citation_validator.py (Uppdaterad variant)
#
# Ämne: Svenska / Källkritik / ARTI (RegEx, Stränghantering)
# Uppgift: Robust validering av källhänvisningsformat, nu med stöd för muntliga varianter.
#
# Uppdatering: Hanterar verbal format (e.g., "i DN av Letmark, 2012"), feedback på 'smidig infogad' för Delprov A.
# Extraherar info för att hjälpa elever anpassa innehåll till situation (e.g., undvik AI-kopiering).

import re

def validera_robust_kallhanvisning(kallhanvisning_strang):
    """
    Validerar källhänvisning robust, med flex för verbal (tal) format.
    """
    feedback = []
    validerad_info = {}

    # Flexiblare match för verbal/oral (t.ex. "som Letmark skriver i DN, 2012")
    match = re.match(r"^\s*(?:som|av|i|enligt)?\s*([A-Öa-ö\s]+?)(?:\s*skriver)?,\s*('[^']+'|artikeln|texten),\s*(\*[^\*]+\*|[^\*]+),\s*(\d{4}(-\d{2}-\d{2})?)\s*$", kallhanvisning_strang, re.IGNORECASE)

    if not match:
        feedback.append("Formatet matchar inte. Prova: 'Författare, 'Titel', *Publikation*, ÅÅÅÅ-MM-DD' eller verbal 'som Letmark skriver i DN, 2012'.")
        # Specifik feedback
        if not re.search(r'[A-Öa-ö\s]+', kallhanvisning_strang):
            feedback.append("  - Författare saknas.")
        if not re.search(r'('[^']+'|artikeln|texten)', kallhanvisning_strang, re.IGNORECASE):
            feedback.append("  - Titel saknas eller inte markerad.")
        if not re.search(r'(\*[^\*]+\*|[^\*]+)', kallhanvisning_strang):
            feedback.append("  - Publikation saknas.")
        if not re.search(r'\d{4}(-\d{2}-\d{2})?', kallhanvisning_strang):
            feedback.append("  - Datum saknas.")
        return "Problem:\n" + "\n".join(feedback)
    
    validerad_info['författare'] = match.group(1).strip()
    validerad_info['titel'] = match.group(2).strip()
    validerad_info['publikation'] = match.group(3).strip()
    validerad_info['datum'] = match.group(4).strip()

    # Extra feedback för muntlig anpassning
    if re.search(r'(som|av|i|enligt).*skriver', kallhanvisning_strang, re.IGNORECASE):
        feedback.append("Bra: Smidig infogning för tal (anpassad till situationen)!")
    else:
        feedback.append("Tips: För muntligt - väv in som 'som Letmark skriver' för bättre flyt.")

    if not feedback or all(f.startswith("Bra:") for f in feedback):
        return "Korrekt. ✓\nInfo:\n" + "\n".join(f"  {k.capitalize()}: {v}" for k,v in validerad_info.items())
    else:
        return "Problem:\n" + "\n".join(feedback)

# Exempel för verbal citation
exempel_verbal = "som Peter Letmark skriver i 'Evolutionen gjorde oss talrädda', DN, 2012"
print(validera_robust_kallhanvisning(exempel_verbal))
