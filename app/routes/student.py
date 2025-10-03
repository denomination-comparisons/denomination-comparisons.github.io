from flask import Blueprint, render_template, request, redirect, url_for, session as flask_session
from sqlalchemy.orm import Session
from models.models import ReadingText, ComprehensionAttempt, Reflection, Student, Dialogue
from ai_module.regression_model import TextRecommender, explain_recommendation, DialogueAnalyzer
from app import Session as DBSession
import json
import datetime
import logging

# ARTI-koppling: Blueprint för studentfunktioner, modular design för testbarhet

student_bp = Blueprint('student', __name__)
recommender = TextRecommender()

@student_bp.route('/student/dashboard/<int:student_id>')
def dashboard(student_id):
    """
    Visar studentens framsteg och rekommenderade texter.
    """
    db_session = DBSession()
    student = db_session.query(Student).filter_by(id=student_id).first()
    if not student:
        return "Elev hittades inte.", 404

    # Hämta senaste försök
    attempts = db_session.query(ComprehensionAttempt).filter_by(student_id=student_id).all()
    progress = {
        'current_level': student.current_cefr_level,
        'attempts_count': len(attempts),
        'average_score': sum(a.score for a in attempts) / len(attempts) if attempts else 0
    }

    # Rekommendera nästa text (exempel)
    if attempts:
        last_attempt = attempts[-1]
        recommended_level = recommender.recommend_next_level(
            student_id, last_attempt.text_id, last_attempt.score, last_attempt.time_spent, db_session
        )
    else:
        recommended_level = 'A1'

    db_session.close()
    return render_template('student_dashboard.html', progress=progress, recommended_level=recommended_level)

@student_bp.route('/student/text/<text_id>')
def show_text(text_id):
    """
    Visar en text för läsning.
    """
    db_session = DBSession()
    text = db_session.query(ReadingText).filter_by(text_id=text_id).first()
    if not text:
        return "Text hittades inte.", 404

    # Kontrollera bias
    bias_warning = recommender.detect_bias(text)

    db_session.close()
    return render_template('show_text.html', text=text, bias_warning=bias_warning)

@student_bp.route('/student/complete/<text_id>', methods=['POST'])
def complete_text(text_id):
    """
    Sparar comprehension-försök.
    """
    db_session = DBSession()
    student_id = request.form['student_id']
    score = float(request.form['score'])
    time_spent = int(request.form['time_spent'])

    attempt = ComprehensionAttempt(
        student_id=student_id,
        text_id=text_id,
        score=score,
        time_spent=time_spent
    )
    db_session.add(attempt)
    db_session.commit()

    # Uppdatera studentnivå om nödvändigt
    student = db_session.query(Student).filter_by(id=student_id).first()
    if score > 80:
        # Enkel logik för nivåökning
        levels = ['A1', 'A2', 'B1', 'B2', 'C1']
        current_index = levels.index(student.current_cefr_level)
        if current_index < len(levels) - 1:
            student.current_cefr_level = levels[current_index + 1]
            db_session.commit()

    db_session.close()
    return redirect(url_for('student.dashboard', student_id=student_id))

@student_bp.route('/student/journal/<int:student_id>')
def journal(student_id):
    """
    Visar och lägger till journalanteckningar.
    """
    db_session = DBSession()
    reflections = db_session.query(Reflection).filter_by(student_id=student_id).all()
    db_session.close()
    return render_template('journal.html', reflections=reflections)

@student_bp.route('/student/add_reflection/<int:student_id>', methods=['POST'])
def add_reflection(student_id):
    """
    Lägger till en ny journalanteckning.
    """
    db_session = DBSession()
    text_id = request.form['text_id']
    entry = request.form['entry']

    reflection = Reflection(
        student_id=student_id,
        text_id=text_id,
        journal_entry=entry
    )
    db_session.add(reflection)
    db_session.commit()
    db_session.close()
    return redirect(url_for('student.journal', student_id=student_id))

@student_bp.route('/student/start_dialogue/<int:student_id>', methods=['GET', 'POST'])
def start_dialogue(student_id):
    """
    Start a new theological dialogue.
    """
    if request.method == 'POST':
        topic = request.form['topic']
        db_session = DBSession()
        dialogue = Dialogue(
            student_id=student_id,
            topic=topic,
            messages='[]'  # Empty JSON list
        )
        db_session.add(dialogue)
        db_session.commit()
        dialogue_id = dialogue.id
        db_session.close()
        return redirect(url_for('student.dialogue', student_id=student_id, dialogue_id=dialogue_id))
    return render_template('start_dialogue.html')

@student_bp.route('/student/dialogue/<int:student_id>/<int:dialogue_id>', methods=['GET', 'POST'])
def dialogue(student_id, dialogue_id):
    """
    View and add to a dialogue.
    """
    db_session = DBSession()
    dialogue = db_session.query(Dialogue).filter_by(id=dialogue_id, student_id=student_id).first()
    if not dialogue:
        db_session.close()
        return "Dialogue not found.", 404

    import json
    messages = json.loads(dialogue.messages) if dialogue.messages else []

    if request.method == 'POST':
        user_message = request.form['message']
        # Here, integrate with AI for response (simplified for now)
        ai_response = "AI response to: " + user_message  # Placeholder
        analyzer = DialogueAnalyzer()
        if not analyzer.check_neutrality(ai_response):
            ai_response += " (Note: This response has been flagged for potential bias and reviewed for neutrality.)"
        messages.append({'user': user_message, 'ai': ai_response, 'timestamp': str(datetime.utcnow())})
        dialogue.messages = json.dumps(messages)
        db_session.commit()
        logging.info(f"Dialogue {dialogue_id}: Added message with neutrality check.")

    db_session.close()
    return render_template('dialogue.html', dialogue=dialogue, messages=messages)

@student_bp.route('/student/shared_board/<class_id>')
def shared_board(class_id):
    """
    View aggregated dialogues for the class.
    """
    db_session = DBSession()
    dialogues = db_session.query(Dialogue).join(Student).filter(Student.class_id == class_id).all()
    # Convert to Markdown or JSON for display
    shared_content = []
    for d in dialogues:
        import json
        messages = json.loads(d.messages) if d.messages else []
        shared_content.append(f"# Topic: {d.topic}\n\n" + "\n".join([f"**Student:** {m['user']}\n**AI:** {m['ai']}" for m in messages]))
    shared_markdown = "\n\n---\n\n".join(shared_content)
    db_session.close()
    return render_template('shared_board.html', shared_markdown=shared_markdown)