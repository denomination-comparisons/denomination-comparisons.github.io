import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sqlalchemy.orm import Session
from models.models import ComprehensionAttempt, ReadingText, Student, Dialogue
import numpy as np
import json
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# ARTI-koppling: Här använder vi övervakat lärande (regression) för att förutsäga nästa textnivå
# Detta är ett exempel på maskininlärning för personaliserad utbildning

class TextRecommender:
    def __init__(self):
        self.model = LinearRegression()
        self.cefr_encoder = LabelEncoder()
        self.is_trained = False

    def prepare_data(self, session: Session):
        """
        Hämtar data från databasen för träning.
        """
        attempts = session.query(ComprehensionAttempt).all()
        data = []
        for attempt in attempts:
            student = session.query(Student).filter_by(id=attempt.student_id).first()
            text = session.query(ReadingText).filter_by(text_id=attempt.text_id).first()
            if student and text:
                # Kodifiera CEFR-nivåer
                cefr_encoded = self.cefr_encoder.fit_transform([text.cefr_level])[0]
                data.append({
                    'student_id': attempt.student_id,
                    'previous_cefr': cefr_encoded,
                    'score': attempt.score,
                    'time_spent': attempt.time_spent,
                    'next_cefr': cefr_encoded  # För enkelhet, använd samma som mål
                })
        return pd.DataFrame(data)

    def train(self, session: Session):
        """
        Tränar modellen på historiska data.
        """
        df = self.prepare_data(session)
        if len(df) < 10:  # Behöver minst 10 exempel
            print("Otillräckligt med data för träning.")
            return

        X = df[['student_id', 'previous_cefr', 'score', 'time_spent']]
        y = df['next_cefr']
        self.model.fit(X, y)
        self.is_trained = True
        print("Modellen är tränad.")

    def recommend_next_level(self, student_id, previous_text_id, score, time_spent, session: Session):
        """
        Förutsäger nästa CEFR-nivå baserat på prestanda.
        """
        if not self.is_trained:
            self.train(session)

        # Hämta tidigare text för kodifiering
        previous_text = session.query(ReadingText).filter_by(text_id=previous_text_id).first()
        if not previous_text:
            return 'A1'  # Standard

        previous_cefr_encoded = self.cefr_encoder.transform([previous_text.cefr_level])[0]

        # Förutsäg
        prediction = self.model.predict([[student_id, previous_cefr_encoded, score, time_spent]])
        predicted_index = int(round(prediction[0]))

        # Avkodifiera till CEFR-nivå
        cefr_levels = list(self.cefr_encoder.classes_)
        if 0 <= predicted_index < len(cefr_levels):
            return cefr_levels[predicted_index]
        else:
            return 'A1'  # Säkerhetsåtgärd

    def detect_bias(self, text: Text):
        """
        Enkel bias-detektion baserat på flaggor.
        """
        if text.bias_flags:
            return f"Varning: Texten kan innehålla bias gällande {text.bias_flags}."
        return "Ingen bias detekterad."

# ARTI-koppling: Detta är en transparent AI-modell som förklarar sina rekommendationer
def explain_recommendation(student_id, recommended_level, reason_data):
    """
    Förklarar varför en viss nivå rekommenderades.
    """
    explanation = f"Rekommendation för elev {student_id}: Nivå {recommended_level}. "
    explanation += f"Baserat på tidigare poäng: {reason_data['score']}, tid: {reason_data['time_spent']} sekunder."
    return explanation

class DialogueAnalyzer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self.cluster_model = KMeans(n_clusters=5, random_state=42)
        self.is_trained = False
        nltk.download('vader_lexicon', quiet=True)
        self.sia = SentimentIntensityAnalyzer()

    def extract_texts(self, dialogues):
        """
        Extract text from dialogues for clustering.
        """
        texts = []
        for d in dialogues:
            messages = json.loads(d.messages) if d.messages else []
            full_text = d.topic + ' ' + ' '.join([m['user'] + ' ' + m['ai'] for m in messages])
            texts.append(full_text)
        return texts

    def cluster_themes(self, dialogues):
        """
        Cluster dialogues into themes.
        """
        texts = self.extract_texts(dialogues)
        if len(texts) < 2:
            return ["General"]
        
        X = self.vectorizer.fit_transform(texts)
        clusters = self.cluster_model.fit_predict(X)
        
        # Group by cluster
        theme_groups = {}
        for i, cluster in enumerate(clusters):
            if cluster not in theme_groups:
                theme_groups[cluster] = []
            theme_groups[cluster].append(dialogues[i].topic)
        
        # Summarize themes
        themes = []
        for cluster, topics in theme_groups.items():
            common_theme = max(set(topics), key=topics.count) if topics else "Miscellaneous"
            themes.append(f"Theme {cluster}: {common_theme}")
        
        return themes

    def detect_paradoxes_and_humility(self, dialogues):
        """
        Detect paradoxes and humility statements.
        """
        paradoxes = []
        humility = []
        for d in dialogues:
            messages = json.loads(d.messages) if d.messages else []
            for m in messages:
                text = m['user'] + ' ' + m['ai']
                if any(word in text.lower() for word in ['paradox', 'contradiction', 'tension']):
                    paradoxes.append(text)
                if any(word in text.lower() for word in ['humble', 'uncertain', 'not sure', 'maybe']):
                    humility.append(text)
        return paradoxes, humility

    def generate_socratic_questions(self, themes, divergences, convergences):
        """
        Generate Socratic questions.
        """
        questions = []
        for theme in themes:
            questions.append(f"What do you think about {theme}? Why?")
        for div in divergences:
            questions.append(f"Why might {div} differ from the majority view?")
        for conv in convergences:
            questions.append(f"What common ground exists in {conv}?")
        return questions

    def check_neutrality(self, text):
        """
        Check if text is neutral using sentiment analysis.
        """
        sentiment = self.sia.polarity_scores(text)
        bias_score = abs(sentiment['compound'])
        return bias_score < 0.1  # Threshold for neutrality

    def ensure_diversity(self, dialogues):
        """
        Ensure diversity in themes.
        """
        topics = [d.topic for d in dialogues]
        unique_topics = set(topics)
        diversity_score = len(unique_topics) / len(dialogues) if dialogues else 0
        return diversity_score > 0.5  # At least 50% unique topics