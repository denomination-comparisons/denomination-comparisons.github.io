from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name_hash = Column(String(255), nullable=False)  # För GDPR, hash av namn
    class_id = Column(String(50), nullable=False)
    current_cefr_level = Column(String(10), default='A1')  # CEFR-nivå

    # Relationer
    attempts = relationship("ComprehensionAttempt", back_populates="student")
    reflections = relationship("Reflection", back_populates="student")
    overrides = relationship("TeacherOverride", back_populates="student")
    dialogues = relationship("Dialogue", back_populates="student")

class ReadingText(db.Model):
    __tablename__ = 'texts'
    text_id = Column(String(50), primary_key=True)
    source = Column(String(255), nullable=False)  # Källa för transparens
    title = Column(String(255), nullable=False)
    cefr_level = Column(String(10), nullable=False)
    word_count = Column(Integer, nullable=False)
    theme = Column(String(100))
    bias_flags = Column(String(255))  # Flaggor för bias, t.ex. 'kön,ålder'
    full_text = Column(Text, nullable=False)

    # Relationer
    attempts = relationship("ComprehensionAttempt", back_populates="text")
    reflections = relationship("Reflection", back_populates="text")

class ComprehensionAttempt(db.Model):
    __tablename__ = 'comprehension_attempts'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    text_id = Column(String(50), ForeignKey('texts.text_id'), nullable=False)
    score = Column(Float, nullable=False)  # Poäng 0-100
    time_spent = Column(Integer, nullable=False)  # Tid i sekunder
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationer
    student = relationship("Student", back_populates="attempts")
    text = relationship("ReadingText", back_populates="attempts")

class Reflection(db.Model):
    __tablename__ = 'reflections'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    text_id = Column(String(50), ForeignKey('texts.text_id'), nullable=False)
    journal_entry = Column(Text, nullable=False)  # AI Collaboration Journal
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationer
    student = relationship("Student", back_populates="reflections")
    text = relationship("ReadingText", back_populates="reflections")

class TeacherOverride(db.Model):
    __tablename__ = 'teacher_overrides'
    id = Column(Integer, primary_key=True)
    teacher_id = Column(String(50), nullable=False)  # Lärar-ID
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    override_reason = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationer
    student = relationship("Student", back_populates="overrides")

class Dialogue(db.Model):
    __tablename__ = 'dialogues'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    topic = Column(String(255), nullable=False)  # Theological topic
    messages = Column(Text, nullable=False)  # JSON list of messages
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationer
    student = relationship("Student", back_populates="dialogues")

class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(String(50), default='student')  # 'student' or 'teacher'

class ReadingAssignment(db.Model):
    __tablename__ = 'reading_assignments'
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)  # JSON string for texts/questions/strategies
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    teacher = relationship("User", backref="assignments")

class StudentResponse(db.Model):
    __tablename__ = 'student_responses'
    id = Column(Integer, primary_key=True)
    assignment_id = Column(Integer, ForeignKey('reading_assignments.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    answers = Column(Text, nullable=False)  # JSON of answers
    strategies = Column(Text, nullable=False)  # JSON of selected strategies
    self_assessment = Column(Integer, nullable=False)  # Score 1-5
    submitted_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    assignment = relationship("ReadingAssignment", backref="responses")
    student = relationship("User", backref="responses")

class AIFeedback(db.Model):
    __tablename__ = 'ai_feedbacks'
    id = Column(Integer, primary_key=True)
    response_id = Column(Integer, ForeignKey('student_responses.id'), nullable=False)
    comprehension_score = Column(Float, nullable=False)
    recommendations = Column(Text, nullable=False)
    cefr_level = Column(String(10), nullable=False)  # e.g., 'B1'
    generated_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    response = relationship("StudentResponse", backref="feedback")

class WritingAssignment(db.Model):
    __tablename__ = 'writing_assignments'
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    example_novella = Column(Text, nullable=True)  # JSON or text of example
    elements = Column(Text, nullable=False)  # JSON: {'undertext': True, 'stil': 'komiskt', etc.}
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    teacher = relationship("User", backref="writing_assignments")

class StudentWriting(db.Model):
    __tablename__ = 'student_writings'
    id = Column(Integer, primary_key=True)
    assignment_id = Column(Integer, ForeignKey('writing_assignments.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    elements_used = Column(Text, nullable=False)  # JSON of elements
    self_assessment = Column(Integer, nullable=False)  # 1-5
    submitted_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    assignment = relationship("WritingAssignment", backref="writings")
    student = relationship("User", backref="writings")

class WritingFeedback(db.Model):
    __tablename__ = 'writing_feedbacks'
    id = Column(Integer, primary_key=True)
    writing_id = Column(Integer, ForeignKey('student_writings.id'), nullable=False)
    element_scores = Column(Text, nullable=False)  # JSON: {'undertext': 0.8, 'stil': 0.7}
    recommendations = Column(Text, nullable=False)
    cefr_level = Column(String(10), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    writing = relationship("StudentWriting", backref="feedback")

class SpeakingExercise(db.Model):
    __tablename__ = 'speaking_exercises'
    id = Column(Integer, primary_key=True)
    assignment_id = Column(Integer, ForeignKey('writing_assignments.id'), nullable=False)  # Link to writing for integrated tasks
    audio_url = Column(String(255), nullable=True)  # Stored in cloud (e.g., S3)
    transcript = Column(Text, nullable=True)
    pronunciation_score = Column(Float, nullable=True)  # AI-computed
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    assignment = relationship("WritingAssignment", backref="speaking_exercises")

class PeerGroup(db.Model):
    __tablename__ = 'peer_groups'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    creator = relationship("User", backref="peer_groups")

class VRCert(db.Model):
    __tablename__ = 'vr_certs'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    cert_hash = Column(String(66), nullable=True)  # Placeholder for blockchain hash
    cefr_level = Column(String(10), nullable=False)  # e.g., 'B1'
    issued_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    student = relationship("User", backref="vr_certs")

class UserConsent(db.Model):
    __tablename__ = 'user_consents'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    ai_data_use = Column(Boolean, default=False)
    consent_given_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    user = relationship("User", backref="consents")