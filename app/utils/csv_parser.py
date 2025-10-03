import csv
import os
from sqlalchemy.orm import Session
from models.models import Text

# ARTI-koppling: Här använder vi CSV-parsering för att ladda texter
# Detta är ett exempel på databehandling för att mata in data i modellen

def load_texts_from_csv(csv_file_path, session: Session):
    """
    Laddar texter från en CSV-fil och lägger till dem i databasen.
    CSV-format: text_id,source,title,cefr_level,theme,excerpt,full_text
    """
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"CSV-filen {csv_file_path} finns inte.")

    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Kontrollera att alla nödvändiga fält finns
            required_fields = ['text_id', 'source', 'title', 'cefr_level', 'theme', 'excerpt', 'full_text']
            if not all(field in row for field in required_fields):
                print(f"Hoppar över rad: saknar fält {row}")
                continue

            # Skapa Text-objekt
            text = Text(
                text_id=row['text_id'],
                source=row['source'],
                title=row['title'],
                cefr_level=row['cefr_level'],
                word_count=len(row['full_text'].split()),  # Beräkna ordantal
                theme=row['theme'],
                bias_flags='',  # Kan fyllas i senare
                full_text=row['full_text']
            )

            # Lägg till i databasen
            session.add(text)
        session.commit()
        print(f"Laddade {reader.line_num - 1} texter från CSV.")

# Exempel på användning
if __name__ == '__main__':
    # Detta är för testning
    from app import Session
    session = Session()
    load_texts_from_csv('sample_texts.csv', session)