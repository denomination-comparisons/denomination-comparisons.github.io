# Importerar nödvändiga bibliotek.
# Flask används för att skapa ett webb-API.
# spaCy är ett avancerat bibliotek för att förstå och analysera mänskligt språk.
import spacy
from flask import Flask, request, jsonify

# --- FÖRBEREDELSER ---

# Vi försöker ladda den svenska språkmodellen för spaCy.
# Modellen hjälper programmet att förstå svensk grammatik, ord och sammanhang.
# Om modellen inte finns, skrivs ett felmeddelande ut med instruktioner för att ladda ner den.
# Du laddar ner den genom att skriva följande i din terminal:
# python -m spacy download sv_core_news_sm
try:
    nlp = spacy.load("sv_core_news_sm")
except OSError:
    print("Kunde inte hitta spaCy-modellen \'sv_core_news_sm\'.")
    print("Kör kommandot: python -m spacy download sv_core_news_sm")
    nlp = None

# En lista med ord som kan signalera att texten behandlar känsliga ämnen.
# Koden kommer att reagera om något av dessa ord (eller liknande) finns i texten.
SENSITIVE_THEMES = ["ras", "kön", "sexualitet", "religion", "politik", "diskriminering", "invandring"]

def generate_kallkritik_questions(text):
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

    # --- TEXTANALYS MED SPACY ---
    # spaCy bearbetar texten och skapar ett "doc"-objekt.
    # Det här objektet innehåller all information som spaCy har extraherat,
    # t.ex. vilka ord som är substantiv, vilka som är namn på personer, etc.
    doc = nlp(text)

    # --- FRÅGEGENERERING ---

    # En lista för att samla alla genererade frågor.
    questions = []
    # En lista för eventuella varningar, t.ex. om känsliga teman.
    warnings = []

    # 1. Grundläggande källkritiska frågor (alltid med)
    questions.extend([
        "Vem är avsändaren (författaren/organisationen) bakom texten och vad vet vi om dem?",
        "Vilket syfte verkar texten ha? (t.ex. informera, övertyga, underhålla)",
        "Vem är den troliga målgruppen för texten? Hur anpassas språket och innehållet till dem?",
        "Är texten aktuell? När publicerades den och kan händelser efteråt ha förändrat situationen?",
        "Är detta en förstahandskälla (ett ögonvittne) eller en andrahandskälla (återberättar något)? Hur påverkar det trovärdigheten?"
    ])

    # 2. ARTI-relaterade frågor (för att tänka som en AI)
    questions.extend([
        "[Transparens] Vilka källor eller bevis hänvisar texten till? Är källorna redovisade öppet och är de trovärdiga?",
        "[Klassificering] Vilka grupper av människor, idéer eller händelser beskrivs? Är indelningen neutral eller vinklad?",
        "[Prediktion] Görs det några förutsägelser om framtiden i texten? Vilka argument används för att stödja dessa förutsägelser?"
    ])

    # 3. Dynamiska frågor baserade på innehållet
    # Hitta substantivfraser (centrala begrepp)
    # Vi tar de 3 längsta begreppen för att ställa en fråga.
    noun_chunks = sorted([chunk.text for chunk in doc.noun_chunks if len(chunk.text.split()) > 1], key=len, reverse=True)
    if noun_chunks:
        questions.append(f"Texten nämner begreppet '{noun_chunks[0]}'. Hur definieras eller används det? Finns det andra sätt att se på det begreppet?")

    # Hitta värdeladdade ord (adjektiv)
    # Vi letar efter adjektiv som kan uttrycka en åsikt.
    adjectives = [token.text for token in doc if token.pos_ == "ADJ"]
    if adjectives:
         questions.append(f"Identifiera 2-3 värdeladdade ord (t.ex. adjektiv som '{adjectives[0]}') i texten. Vilken känsla eller åsikt förmedlar de?")


    # 4. Etisk analys och reflektionsfrågor
    # Vi går igenom vår lista med känsliga teman.
    found_themes = [theme for theme in SENSITIVE_THEMES if theme in text.lower()]
    if found_themes:
        # Om ett känsligt tema hittas, lägg till en varning.
        theme_str = ", ".join(found_themes)
        warnings.append(f"Varning: Texten berör potentiellt känsliga teman ({theme_str}). Det är extra viktigt med ett balanserat och respektfullt förhållningssätt.")
        # Lägg också till en specifik reflektionsfråga.
        questions.append(f"[Reflektion] Texten tar upp '{theme_str}'. Vilka olika perspektiv och erfarenheter kan finnas kring detta ämne som inte tas upp i texten?")


    # Begränsa till max 10 frågor för att inte överväldiga.
    # Vi blandar frågorna lite för variation.
    import random
    random.shuffle(questions)
    final_questions = questions[:10]


    return {"questions": final_questions, "warnings": warnings}

# --- FLASK API ---
# Skapar en Flask-app. Detta är "motorn" i vårt webb-API.
app = Flask(__name__)

# Bestämmer att funktionen nedan ska köras när någon skickar
# en POST-förfrågan till webbadressen /generate_questions.
@app.route("/generate_questions", methods=["POST"])
def api_generate():
    # Hämtar JSON-datan från förfrågan.
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Ingen text skickades med i förfrågan. Skicka JSON på formatet {'text': 'din text här'}"}), 400

    # Plockar ut texten från datan.
    text_to_analyze = data.get("text", "")

    # Anropar vår huvudfunktion för att generera frågorna.
    result = generate_kallkritik_questions(text_to_analyze)

    # Skickar tillbaka resultatet som JSON.
    return jsonify(result)

# Denna del körs bara om du startar skriptet direkt (t.ex. med "python app.py").
# Den startar en lokal webbserver så att du kan testa ditt API.
if __name__ == "__main__":
    # Viktigt: Se till att spaCy-modellen är nedladdad innan du kör.
    if nlp is None:
        print("-" * 50)
        print("Programmet kan inte starta webbservern eftersom spaCy-modellen saknas.")
        print("Avslutar. Följ instruktionerna ovan för att ladda ner modellen.")
        print("-" * 50)
    else:
        print("-" * 50)
        print("Flask-servern startar...")
        print("Gå till http://127.0.0.1:5000")
        print("Du kan nu skicka POST-requests till /generate_questions")
        print("Använd ett verktyg som Postman eller curl för att testa:")
        print('curl -X POST -H "Content-Type: application/json" -d 
{'''text''': '''Skriv din text här'''}
 http://127.0.0.1:5000/generate_questions')
        print("-" * 50)
        app.run(debug=True)
