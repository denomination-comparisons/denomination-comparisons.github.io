
import textstat
import spacy
import nltk
import requests
from io import StringIO
import csv
from sklearn.ensemble import RandomForestClassifier

# --- Pre-load necessary models and data ---
try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    nltk.download('punkt')

try:
    nlp = spacy.load("sv_core_news_sm")
except OSError:
    print("Downloading spacy model sv_core_news_sm...")
    spacy.cli.download("sv_core_news_sm")
    nlp = spacy.load("sv_core_news_sm")

def load_frequency_list(url="https://raw.githubusercontent.com/spraakbanken/kelly-list/master/kelly.csv"):
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an exception for bad status codes
        reader = csv.reader(StringIO(response.text))
        # Skips header and creates a dictionary
        next(reader)
        freq_words = {row[0].lower(): row[1] for row in reader if len(row) > 1}
        return freq_words
    except requests.exceptions.RequestException as e:
        print(f"Error fetching frequency list: {e}")
        return {}

# Load the frequency list once when the module is imported
FREQ_LIST = load_frequency_list()

def detect_potential_bias(text):
    doc = nlp(text)
    warnings = []
    modern_terms = ["smartphone", "internet", "sociala medier", "app", "dator", "mobil", "webb", "digital", "online"]
    has_modern_context = any(term in text.lower() for term in modern_terms)
    if not has_modern_context:
        warnings.append("Text saknar moderna referenser - kan kännas främmande för IM-elever")
    
    male_pronouns = len([t for t in doc if t.text.lower() in ["han", "hans", "honom", "mannen"]])
    female_pronouns = len([t for t in doc if t.text.lower() in ["hon", "hennes", "henne", "kvinnan"]])
    
    # Avoid division by zero
    if male_pronouns + female_pronouns > 0:
        gender_ratio = male_pronouns / (female_pronouns + 1) # +1 to avoid zero division
        if gender_ratio > 3 or (female_pronouns > 0 and gender_ratio < 0.33):
            warnings.append(f"Könsobalans i pronomen (ratio: {gender_ratio:.2f}) - Kan indikera ensidigt perspektiv.")

    sensitive_terms = ["politik", "religion", "ras", "kön", "sexuell orientering"]
    if any(term in text.lower() for term in sensitive_terms):
        warnings.append("Text innehåller potentiellt känsliga ämnen - överväg etiska implikationer och målgruppsanpassning.")
    return warnings

def get_cefr_model():
    # Dummy training data to create a pre-trained model instance.
    # In a real application, this would be loaded from a file or a proper training pipeline.
    a1_text = "Jag heter Anna. Jag är 10 år."
    a2_text = "I går gick jag till skolan. Jag lärde mig engelska."
    b1_text = "Jag tycker att klimatförändringar är ett stort problem."
    b2_text = "Trots att teknologin utvecklas snabbt, finns det fortfarande utmaningar."
    
    training_data = [
        {"text": a1_text, "lix": textstat.lix(a1_text), "vocab_match": 95, "avg_depth": 1.5, "teacher_rating": "A1"},
        {"text": a2_text, "lix": textstat.lix(a2_text), "vocab_match": 85, "avg_depth": 2.0, "teacher_rating": "A2"},
        {"text": b1_text, "lix": textstat.lix(b1_text), "vocab_match": 70, "avg_depth": 3.0, "teacher_rating": "B1"},
        {"text": b2_text, "lix": textstat.lix(b2_text), "vocab_match": 60, "avg_depth": 3.5, "teacher_rating": "B2"}
    ]
    
    X = [[item["lix"], item["vocab_match"], item.get("avg_depth", 0)] for item in training_data]
    y = [item["teacher_rating"] for item in training_data]
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

# Load the model once when the module is imported
CEFR_MODEL = get_cefr_model()

def classify_text(text):
    """Classifies a given text and returns its CEFR level, an explanation, and warnings."""
    if not FREQ_LIST:
        return {"level": "Error", "explanation": "Frequency list not available.", "warnings": ["Could not connect to word frequency source."]}

    lix = textstat.lix(text)
    doc = nlp(text)
    words = [token.text.lower() for token in doc if token.is_alpha]
    
    if not words:
        return {"level": "N/A", "explanation": "Text contains no words to analyze.", "warnings": []}

    # Calculate percentage of words that are considered basic (A1/A2)
    low_freq_count = sum(1 for w in words if FREQ_LIST.get(w, 'C1') in ['A1', 'A2'])
    low_freq_percent = (low_freq_count / len(words)) * 100

    # Calculate average syntax depth
    depths = [max((len(list(token.subtree)) for token in sent if token.dep_ != 'ROOT'), default=1) for sent in doc.sents]
    avg_depth = sum(depths) / len(depths) if depths else 0

    # Use the pre-trained model to predict the level
    features = [[lix, low_freq_percent, avg_depth]]
    level = CEFR_MODEL.predict(features)[0]
    
    explanation = f"Beräknad CEFR-nivå: {level}. Analys baseras på LIX ({lix:.2f}), andel basvokabulär ({low_freq_percent:.1f}%), och meningsstruktur (syntaxdjup {avg_depth:.1f})."
    warnings = detect_potential_bias(text)
    
    return {"level": level, "explanation": explanation, "warnings": warnings}
