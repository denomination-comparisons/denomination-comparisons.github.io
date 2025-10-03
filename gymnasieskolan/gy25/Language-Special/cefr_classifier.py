import textstat
import spacy
import nltk
import requests
from io import StringIO
import csv
from sklearn.ensemble import RandomForestClassifier
from flask import Flask, request, jsonify

nltk.download('punkt')
nlp = spacy.load("sv_core_news_sm")

def load_frequency_list(url="https://raw.githubusercontent.com/spraakbanken/kelly-list/master/kelly.csv"):
    response = requests.get(url)
    reader = csv.reader(StringIO(response.text))
    freq_words = {row[0].lower(): row[1] for row in reader if len(row) > 1}
    return freq_words

def detect_potential_bias(text):
    doc = nlp(text)
    warnings = []
    modern_terms = ["smartphone", "internet", "sociala medier", "app", "dator", "mobil", "webb", "digital", "online"]
    has_modern_context = any(term in text.lower() for term in modern_terms)
    if not has_modern_context:
        warnings.append("Text saknar moderna referenser - kan kännas främmande för IM-elever")
    male_pronouns = len([t for t in doc if t.text.lower() in ["han", "hans", "honom", "mannen"]])
    female_pronouns = len([t for t in doc if t.text.lower() in ["hon", "hennes", "henne", "kvinnan"]])
    gender_ratio = male_pronouns / (female_pronouns + 1)
    if gender_ratio > 3 or gender_ratio < 0.33:
        warnings.append(f"Könsobalans i pronomen (ratio: {gender_ratio:.2f})")
    # Etiska flaggor för data-bias per ARTI (antagande: artikelbaserad bias)
    sensitive_terms = ["politik", "religion", "ras", "kön", "sexuell orientering"]
    if any(term in text.lower() for term in sensitive_terms):
        warnings.append("Text innehåller känsliga ämnen - överväg etiska implikationer")
    return warnings

def collect_teacher_labels(training_data):
    X = [[item["lix"], item["vocab_match"], item.get("avg_depth", 0)] for item in training_data]
    y = [item["teacher_rating"] for item in training_data]
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

def classify_cefr(text, freq_list, model=None):
    lix = textstat.lix(text)
    doc = nlp(text)
    words = [token.text.lower() for token in doc if token.is_alpha]
    low_freq_percent = sum(1 for w in words if freq_list.get(w, 'low') in ['A1', 'A2']) / len(words) * 100 if words else 0
    depths = [max((len(list(token.subtree)) for token in sent if token.dep_ != 'ROOT'), default=1) for sent in doc.sents]
    avg_depth = sum(depths) / len(depths) if depths else 0
    if model:
        level = model.predict([[lix, low_freq_percent, avg_depth]])[0]
    else:
        if lix < 25 and low_freq_percent > 95 and avg_depth < 2:
            level = "A1"
        elif lix < 35 and low_freq_percent > 85 and avg_depth < 3:
            level = "A2"
        elif lix < 45 and low_freq_percent > 75 and avg_depth < 4:
            level = "B1"
        else:
            level = "B2"
    explanation = f"{level}: LIX={lix:.2f}, Vokabulär-match={low_freq_percent:.1f}%, Syntaxdjup={avg_depth:.1f}"
    warnings = detect_potential_bias(text)
    if warnings:
        explanation += f" Varningar: {'; '.join(warnings)}"
    return {"level": level, "explanation": explanation, "warnings": warnings}

# Exempelanvändning
hafte_text = "Hur ofta pratar du och dina vänner om saker som ni har sett eller läst på internet? Jag pratar ofta med mina vänner om filmer och musik. Vi delar bilder på sociala medier."
a1_text = "Jag heter Anna. Jag är 10 år. Jag bor i Stockholm. Jag gillar att leka."
a2_text = "I går gick jag till skolan. Jag lärde mig engelska. Min lärare är snäll."
b1_text = "Jag tycker att klimatförändringar är ett stort problem. Vi måste minska användningen av fossila bränslen."
b2_text = "Trots att teknologin utvecklas snabbt, finns det fortfarande utmaningar inom artificiell intelligens och etik."

freq_list = load_frequency_list()
training_data = [
    {"text": a1_text, "lix": textstat.lix(a1_text), "vocab_match": 95, "avg_depth": 1.5, "teacher_rating": "A1"},
    {"text": a2_text, "lix": textstat.lix(a2_text), "vocab_match": 85, "avg_depth": 2.0, "teacher_rating": "A2"},
    {"text": hafte_text, "lix": textstat.lix(hafte_text), "vocab_match": 82, "avg_depth": 2.5, "teacher_rating": "A2"},
    {"text": b1_text, "lix": textstat.lix(b1_text), "vocab_match": 70, "avg_depth": 3.0, "teacher_rating": "B1"},
    {"text": b2_text, "lix": textstat.lix(b2_text), "vocab_match": 60, "avg_depth": 3.5, "teacher_rating": "B2"}
]
model = collect_teacher_labels(training_data)
print(classify_cefr(hafte_text, freq_list, model))

# Flask-integration
app = Flask(__name__)
@app.route('/classify', methods=['POST'])
def api_classify():
    data = request.get_json()
    text = data['text']
    result = classify_cefr(text, freq_list, model)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)