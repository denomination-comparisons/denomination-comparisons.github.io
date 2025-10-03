from flask import Blueprint, render_template, request, jsonify
from app.tools.text_processor import TextProcessor
# from app.models.models import SpeakingExercise, db

speaking = Blueprint('speaking', __name__)
tp = TextProcessor()

@speaking.route('/exercise/<int:assignment_id>', methods=['GET', 'POST'])
def speaking_exercise(assignment_id):
    if request.method == 'POST':
        # Handle audio upload (placeholder)
        audio_file = request.files.get('audio')
        target_text = request.form.get('target_text')
        if audio_file:
            # Save and analyze
            audio_path = f"static/audio/{audio_file.filename}"
            audio_file.save(audio_path)
            wer, feedback = tp.analyze_pronunciation(audio_path, target_text)
            # exercise = SpeakingExercise(assignment_id=assignment_id, audio_url=audio_path, transcript="Simulated", pronunciation_score=1-wer)
            # db.session.add(exercise)
            # db.session.commit()
            return jsonify({'wer': wer, 'feedback': feedback})
    return render_template('speaking/exercise.html', assignment_id=assignment_id)

@speaking.route('/voice_to_text', methods=['POST'])
def voice_to_text():
    # Placeholder for voice-to-text processing (use Web Speech API on client-side)
    # For server-side, could use Google Speech-to-Text or similar
    transcript = request.json.get('transcript', '')
    # Process transcript for dyslexia-friendly output or correction
    corrected = tp.correct_text(transcript)  # Assume method exists
    return jsonify({'original': transcript, 'corrected': corrected})