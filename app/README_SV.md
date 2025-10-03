# Läsförståelse App för Svenska som Andraspråk

Denna Flask-applikation är utformad för att hjälpa IM-programmets elever (ålder 15-16) att förbättra sin läsförståelse i svenska genom adaptiv AI-stöd.

## Funktioner

- **Studentgränssnitt**: Visa texter, få rekommendationer baserat på prestanda, vokabulärhjälp och journal för reflektioner.
- **Lärargränssnitt**: Ladda upp texter, visa analyser, exportera rapporter och överskrida AI-rekommendationer.
- **AI-integration**: Använder regression för att rekommendera nästa textnivå baserat på tidigare prestanda.
- **Säkerhet**: GDPR-kompatibel, inga externa tjänster.

## Installation

1. Klona eller ladda ner projektet.
2. Installera beroenden:
   ```
   pip install -r requirements.txt
   ```
3. Kör appen:
   ```
   python app.py
   ```
4. Öppna http://localhost:5000 i din webbläsare.

## Användning

- **För Elever**: Logga in och börja läsa texter. AI:n anpassar svårighetsgraden.
- **För Lärare**: Använd lärarpanelen för att hantera texter och se klassframsteg.

## Tekniska Detaljer

- **Databas**: SQLite för enkelhet.
- **UI**: Bootstrap 5 för responsiv design.
- **AI**: Scikit-learn för regression.
- **Språk**: Svenska genom hela gränssnittet.

## Deployment för Skolor

För skolmiljöer med restriktioner:
- Kör lokalt på skolservrar.
- Säkerställ att inga externa API:er används.
- Testa på skolans nätverk för kompatibilitet.

## ARTI-Kopplingar

Varje AI-beslut är märkt med ARTI-koncept för utbildningsändamål, t.ex. regression och övervakat lärande.

## Nya Funktioner (Uppdatering)
- TextProcessor-klass för modulär bearbetning av texter (PDF/text)
- AI-integrering för textmodifiering och analys
- Batch-bearbetning av läromedel
- Förbättrad UI med filuppladdning och realtidsförhandsvisningar

## Exempel på Användning
### Bearbeta ett läromedel
python ../../run.py generate-gy25 input.txt output.md --book "Tatueraren i Auschwitz" --options cefr=B1,source_crit=true

### Anpassa text för CEFR-nivå
Använd verktyget "Text-anpassningsverktyg" i appen för att modifiera texter till specifika nivåer.

### Generera källkritiska frågor
Ladda upp en text och använd "Source Criticism Helper" för att få frågor.

## Licens

Denna app är utvecklad för utbildningsändamål. Kontakta utvecklaren för användning.