# Fil: validator.py (Uppdaterad variant)
#
# Ämne: Svenska / Källkritik / ARTI (RegEx)
# Uppgift: Enkel validering av källhänvisningsformat, nu anpassad för muntliga hänvisningar (mindre strikt för tal).
#
# Uppdatering: Mindre strikt för verbala format (t.ex. "som Letmark skriver i DN"), lägg till check för smidig integration i tal.
# Använd för att validera elevers förberedelser inför Delprov A, där källor ska vävas in naturligt.

import re

def validera_enkel_kallhanvisning(kallhanvisning_strang):
    """
    Validerar en källhänvisning (nu även verbal). Kontrollerar grundläggande delar med flexibilitet för tal.
    """
    feedback = []

    # Flexiblare författarcheck (t.ex. "Letmark" eller "Peter Letmark")
    if not re.search(r'[A-Öa-ö\s]+', kallhanvisning_strang):
        feedback.append("Författarnamn saknas eller är fel (t.ex. 'Letmark' eller 'Peter Letmark').")

    # Titel i citattecken eller nämnd verbalt (t.ex. "artikeln om talrädsla")
    if not re.search(r'(".*?"|artikeln|texten)', kallhanvisning_strang, re.IGNORECASE):
        feedback.append("Titel saknas eller inte markerad (t.ex. 'Evolutionen gjorde oss talrädda' eller 'artikeln').")

    # Publikation (t.ex. "DN" eller "*DN*")
    if not re.search(r'(\* [A-Öa-ö]+\*|[A-Öa-ö]+)', kallhanvisning_strang):
        feedback.append("Publikation saknas (t.ex. 'DN' eller '*DN*').")

    # Datum (flexibelt: YYYY-MM-DD eller "2012")
    if not re.search(r'\d{4}(-\d{2}-\d{2})?', kallhanvisning_strang):
        feedback.append("Datum saknas eller fel (t.ex. '2012-05-04' eller '2012').")

    # Ny: Check för smidig integration (t.ex. "som ... skriver i")
    if re.search(r'(som|enligt|i|av).*skriver', kallhanvisning_strang, re.IGNORECASE):
        feedback.append("Bra: Smidig infogning (vävd in i talet)!")
    else:
        feedback.append("Tips: Infoga smidigare, t.ex. 'som Letmark skriver i DN' för bättre flyt i anförandet.")

    if len([f for f in feedback if not f.startswith("Bra:")]) == 0:
        return "Källhänvisning ser korrekt ut. ✓ (Anpassad för muntligt tal.)"
    else:
        return "Problem hittades:\n" + "\n".join(feedback)

# Exempelanvändning för verbal hänvisning
exempel_verbal = "som Peter Letmark skriver i DN-artikeln 'Evolutionen gjorde oss talrädda' från 2012"
print(validera_enkel_kallhanvisning(exempel_verbal))
