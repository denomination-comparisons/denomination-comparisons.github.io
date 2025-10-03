
import spacy
import random

# --- FÖRBEREDELSER ---

# Ladda spaCy-modellen en gång när modulen importeras för effektivitet.
try:
    nlp = spacy.load("sv_core_news_sm")
except OSError:
    print("Kunde inte hitta spaCy-modellen 'sv_core_news_sm'. Försöker ladda ner...")
    try:
        spacy.cli.download("sv_core_news_sm")
        nlp = spacy.load("sv_core_news_sm")
    except Exception as e:
        print(f"Kunde inte ladda ner modellen: {e}")
        nlp = None

# En lista med ord som kan signalera att texten behandlar känsliga ämnen.
SENSITIVE_THEMES = ["ras", "kön", "sexualitet", "religion", "politik", "diskriminering", "invandring", "lgbtq", "hbtq"]

def generate_questions(text: str):
    """
    Analyserar en text och genererar källkritiska frågor.

    Args:
        text (str): Texten som ska analyseras.

    Returns:
        dict: En dictionary med en lista av frågor ("questions") och varningar ("warnings").
    """
    if not nlp:
        return {
            "questions": [],
            "warnings": ["spaCy-modellen är inte laddad. Analysen kan inte genomföras."]
        }

    doc = nlp(text)
    questions = []
    warnings = []

    # 1. Grundläggande källkritiska frågor (alltid med)
    questions.extend([
        "Vem är avsändaren (författaren/organisationen) och vad är deras syfte?",
        "När publicerades texten och är den fortfarande relevant?",
        "Är detta en förstahands- eller andrahandskälla? Hur påverkar det trovärdigheten?",
        "Vilka bevis eller källor presenteras i texten? Är de kontrollerbara?"
    ])

    # 2. ARTI-relaterade frågor (för att tänka som en AI)
    questions.extend([
        "[Transparens] Hur öppet redovisas informationens ursprung? Finns det dolda avsikter?",
        "[Klassificering] Vilka kategorier eller grupper skapas i texten? Är indelningen rättvis och neutral?",
        "[Prediktion] Görs några förutsägelser? På vilka grunder och hur sannolika är de?"
    ])

    # 3. Dynamiska frågor baserade på innehållet
    noun_chunks = sorted([chunk.text for chunk in doc.noun_chunks if len(chunk.text.split()) > 1], key=len, reverse=True)
    if noun_chunks:
        questions.append(f"Texten fokuserar på '{noun_chunks[0]}'. Hur definieras detta begrepp? Finns det andra perspektiv? ")

    adjectives = [token.text for token in doc if token.pos_ == "ADJ"]
    if adjectives:
         questions.append(f"Identifiera värdeladdade ord (t.ex. '{random.choice(adjectives)}'). Vilken känsla eller åsikt förmedlar de?")

    # 4. Etisk analys och reflektionsfrågor
    found_themes = [theme for theme in SENSITIVE_THEMES if theme in text.lower()]
    if found_themes:
        theme_str = ", ".join(found_themes)
        warnings.append(f"Varning: Texten berör potentiellt känsliga teman ({theme_str}).")
        questions.append(f"[Reflektion] Texten nämner '{theme_str}'. Vilka perspektiv kan saknas i denna framställning?")

    random.shuffle(questions)
    final_questions = questions[:10] # Begränsa till max 10 frågor

    return {"questions": final_questions, "warnings": warnings}
