from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy.orm import Session
from models.models import ReadingText, ComprehensionAttempt, Student, TeacherOverride, Dialogue
from ai_module.regression_model import DialogueAnalyzer
from utils.csv_parser import load_texts_from_csv
from app import Session as DBSession
import csv
import io

# ARTI-koppling: Blueprint för lärarfunktioner

teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/teacher/dashboard')
def dashboard():
    """
    Visar klassövergripande analys.
    """
    db_session = DBSession()
    students = db_session.query(Student).all()
    attempts = db_session.query(ComprehensionAttempt).all()

    analytics = {
        'total_students': len(students),
        'total_attempts': len(attempts),
        'average_score': sum(a.score for a in attempts) / len(attempts) if attempts else 0,
        'cefr_distribution': {}
    }

    for student in students:
        level = student.current_cefr_level
        analytics['cefr_distribution'][level] = analytics['cefr_distribution'].get(level, 0) + 1

    db_session.close()
    return render_template('teacher_dashboard.html', analytics=analytics)

@teacher_bp.route('/teacher/upload_texts', methods=['GET', 'POST'])
def upload_texts():
    """
    Ladda upp nya texter via CSV.
    """
    if request.method == 'POST':
        file = request.files['file']
        if file:
            # Läs CSV från fil
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_input = csv.reader(stream)
            # För enkelhet, spara som ny CSV-fil och ladda
            with open('uploaded_texts.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for row in csv_input:
                    writer.writerow(row)

            db_session = DBSession()
            load_texts_from_csv('uploaded_texts.csv', db_session)
            db_session.close()
            return "Texter uppladdade framgångsrikt."

    return render_template('upload_texts.html')

@teacher_bp.route('/teacher/reports')
def reports():
    """
    Exportera studentframstegsrapporter.
    """
    db_session = DBSession()
    students = db_session.query(Student).all()
    report_data = []
    for student in students:
        attempts = db_session.query(ComprehensionAttempt).filter_by(student_id=student.id).all()
        report_data.append({
            'student_id': student.id,
            'class_id': student.class_id,
            'current_level': student.current_cefr_level,
            'attempts': len(attempts),
            'average_score': sum(a.score for a in attempts) / len(attempts) if attempts else 0
        })
    db_session.close()
    return render_template('reports.html', report_data=report_data)

@teacher_bp.route('/teacher/override/<int:student_id>', methods=['GET', 'POST'])
def override(student_id):
    """
    Manuell överskrivning av AI-rekommendationer.
    """
    if request.method == 'POST':
        teacher_id = request.form['teacher_id']
        reason = request.form['reason']

        db_session = DBSession()
        override = TeacherOverride(
            teacher_id=teacher_id,
            student_id=student_id,
            override_reason=reason
        )
        db_session.add(override)
        db_session.commit()
        db_session.close()
        return "Överskrivning sparad."

    return render_template('override.html', student_id=student_id)

@teacher_bp.route('/teacher/flag_bias/<text_id>', methods=['POST'])
def flag_bias(text_id):
    """
    Flagga texter för bias-granskning.
    """
    db_session = DBSession()
    text = db_session.query(ReadingText).filter_by(text_id=text_id).first()
    if text:
        text.bias_flags = request.form['flags']
        db_session.commit()
    db_session.close()
    return "Text flaggad för bias."

@teacher_bp.route('/teacher/class_digest/<class_id>')
def class_digest(class_id):
    """
    Provide digest of themes, paradoxes, and humility statements.
    """
    db_session = DBSession()
    dialogues = db_session.query(Dialogue).join(Student).filter(Student.class_id == class_id).all()
    
    analyzer = DialogueAnalyzer()
    themes = analyzer.cluster_themes(dialogues)
    paradoxes, humility_statements = analyzer.detect_paradoxes_and_humility(dialogues)
    
    digest = {
        'themes': themes,
        'paradoxes': paradoxes[:5],  # Top 5
        'humility_statements': humility_statements[:5]
    }
    db_session.close()
    return render_template('class_digest.html', digest=digest)

@teacher_bp.route('/teacher/socratic_questions/<class_id>')
def socratic_questions(class_id):
    """
    Generate Socratic questions based on divergences/convergences.
    """
    db_session = DBSession()
    dialogues = db_session.query(Dialogue).join(Student).filter(Student.class_id == class_id).all()
    
    analyzer = DialogueAnalyzer()
    themes = analyzer.cluster_themes(dialogues)
    
    # Find convergences and divergences based on cluster sizes
    topics = [d.topic for d in dialogues]
    unique_topics = list(set(topics))
    convergences = []
    divergences = []
    for topic in unique_topics:
        count = topics.count(topic)
        if count > 1:
            convergences.append(f"Many students discussed {topic} ({count} times)")
        else:
            divergences.append(f"Unique perspective on {topic}")
    
    questions = analyzer.generate_socratic_questions(themes, divergences, convergences)
    
    db_session.close()
    return render_template('socratic_questions.html', questions=questions)