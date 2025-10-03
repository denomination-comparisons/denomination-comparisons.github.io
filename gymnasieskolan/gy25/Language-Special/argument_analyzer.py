# Fil: argument_analyzer.py (Uppdaterad variant)
#
# Ämne: Svenska / Argumentationsanalys / ARTI (NLP, Textklassificering)
# Uppgift: Analysera en text eller taltranskript för att identifiera och kategorisera argument samt struktur.
#
# Denna uppdaterade version inkluderar kategorier för muntlig framställning enligt Delprov A (inledning, huvuddel, avslutning).
# Anpassad för att hantera svenska accenter och ge feedback på balans (nyanserat innehåll) för att stödja elevers förberedelser.
# Exempel: Använd på artikeln "Evolutionen gjorde oss talrädda" som bas för ett anförande om talrädsla.

import re
from collections import defaultdict

# Uppdaterade kategorier med oral struktur och nyckelord från artikeln/Delprov A
ARGUMENT_KATEGORIER = {
    "inledning": ["introducera", "inleda", "börja", "tema", "ämne", "syfte", "presentation", "väcka intresse"],
    "huvuddel": ["resonemang", "argument", "förklara", "beskriva", "kommentera", "reflektera", "exempel", "synpunkt"],
    "avslutning": ["avsluta", "sammanfatta", "konkludera", "uppmaning", "reflektion", "slutsats"],
    "evolutionär": ["evolution", "överlevnad", "primater", "flock", "social", "hierarki", "utstött", "hotade", "rädsla", "fobi"],
    "genetisk": ["gener", "ärftligt", "dna", "tvillingstudier", "biologisk", "arv"],
    "social_inlärning": ["lära", "modellinlärning", "föräldrar", "uppväxt", "miljö", "erfarenhet", "beteende"],
    "fysiologisk_modern": ["stress", "puls", "svettas", "fight-or-flight", "kroppslig", "samhälle", "arbetsliv", "konsekvenser", "informationssamhälle"],
    "psykologisk": ["ångest", "rädsla", "fobi", "självkänsla", "tankar", "känslor", "självförtroende"]
}

def dela_upp_i_meningar(text):
    """
    Delar upp en text i meningar. Hanterar svenska skiljetecken och bevarar struktur för talanalys.
    """
    meningar = re.split(r'(?<=[.!?])\s+', text)
    return [m.strip() for m in meningar if m.strip()]

def analysera_argument(text):
    """
    Analyserar texten för argumentkategorier och struktur. Ger feedback på balans och nyanser.
    """
    meningar = dela_upp_i_meningar(text)
    mening_kategorier = []
    kategori_antal = defaultdict(int)
    
    for mening in meningar:
        hittade_kategorier = set()
        for kategori, nyckelord in ARGUMENT_KATEGORIER.items():
            for ord in nyckelord:
                if re.search(r'\b' + re.escape(ord) + r'\b', mening, re.IGNORECASE):
                    hittade_kategorier.add(kategori)
        
        if hittade_kategorier:
            mening_kategorier.append((mening, list(hittade_kategorier)))
            for kat in hittade_kategorier:
                kategori_antal[kat] += 1
        else:
            mening_kategorier.append((mening, ["okategoriserad"]))
            kategori_antal["okategoriserad"] += 1

    # Generera feedback
    feedback = []
    feedback.append("--- Argumentations- och Strukturanalys ---")
    feedback.append("Översikt över kategorisering (inkl. talstruktur):")
    for mening, kategorier in mening_kategorier:
        feedback.append(f"- '{mening[:70]}...' -> Kategorier: {', '.join(kategorier)}")

    feedback.append("\n--- Sammanfattning av kategorier ---")
    for kategori, antal in sorted(kategori_antal.items()):
        feedback.append(f"- {kategori.replace('_', ' ').capitalize()}: {antal} meningar")

    feedback.append("\n--- Feedback på balans (nyanserat innehåll) ---")
    struktur_kategorier = {"inledning", "huvuddel", "avslutning"}
    aktiva_struktur = struktur_kategorier.intersection(kategori_antal)
    if len(aktiva_struktur) < 3:
        saknade = struktur_kategorier - aktiva_struktur
        feedback.append(f"Strukturen saknar balans: Överväg att lägga till {', '.join(saknade)} för bättre disposition.")
    else:
        feedback.append("Bra struktur: Inledning, huvuddel och avslutning täcks!")

    argument_kategorier = set(ARGUMENT_KATEGORIER) - struktur_kategorier
    aktiva_argument = argument_kategorier.intersection(kategori_antal)
    if len(aktiva_argument) < 2:
        feedback.append("Argumentationen är ensidig. Lägg till fler perspektiv för nyans (t.ex. genetisk + psykologisk).")
    else:
        feedback.append("Bra nyans: Flera argumentperspektiv täcks!")

    if kategori_antal["okategoriserad"] > 0:
        feedback.append(f"\nOBS: {kategori_antal["okategoriserad"]} okategoriserade meningar. Förtydliga eller lägg till nyckelord.")

    return "\n".join(feedback)

# Exempelanvändning med artikelutdrag som taltranskript
artikel_utdrag = """
Inledning: Idag ska jag tala om talrädsla baserat på artikeln 'Evolutionen gjorde oss talrädda' av Peter Letmark.
Huvuddel: Evolutionärt har rädslan hjälpt oss att undvika utstöttning i flockar. Genetiskt är det ärftligt, som tvillingstudier visar.
Social inlärning från föräldrar spelar roll. I modernt samhälle orsakar det stress och hinder i arbetsliv.
Avslutning: Träna genom att börja smått för att övervinna talängslan.
"""

print(analysera_argument(artikel_utdrag))