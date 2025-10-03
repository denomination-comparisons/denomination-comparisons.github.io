from flask import Blueprint, request, jsonify, current_app
from flask_socketio import emit, join_room
from .. import socketio
# Placeholder for Groq API
# from groq import Groq

ai_chat = Blueprint('ai_chat', __name__)

@ai_chat.route('/converse', methods=['POST'])
def converse():
    user_input = request.json.get('input', '')
    # Placeholder: simulate LLM response
    # client = Groq(api_key=current_app.config.get('GROQ_API_KEY'))
    # response = client.chat.completions.create(
    #     model="mixtral-8x7b-32768",
    #     messages=[{"role": "user", "content": f"Respond in Swedish for language practice: {user_input}"}]
    # )
    # ai_response = response.choices[0].message.content
    ai_response = f"Simulated AI response to: {user_input}"  # Placeholder
    return jsonify({'response': ai_response})

@socketio.on('join_peer')
def join_peer(data):
    group_id = data.get('group_id')
    join_room(group_id)
    # AI tutor joins: emit simulated response
    ai_response = "Welcome to the peer group! AI tutor here to help with Swedish practice."
    socketio.emit('tutor_response', {'response': ai_response}, room=group_id)

@socketio.on('peer_message')
def peer_message(data):
    group_id = data.get('group_id')
    message = data.get('message')
    # Simulate AI tutor response
    ai_response = f"AI Tutor: Responding to '{message}' in Swedish context."
    socketio.emit('tutor_response', {'response': ai_response}, room=group_id)