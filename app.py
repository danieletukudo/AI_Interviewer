"""
Flask backend for real-time, browser-based AI audio interview system.
"""

import json
import os
import uuid
import tempfile
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from gtts import gTTS
import speech_recognition as sr
import subprocess
import glob

# Import your AI logic (modularize if needed)
from ai_logic import InterviewAI, OpenAIClient  # Ensure these are importable

app = Flask(__name__, static_folder='static')
CORS(app)

sessions = {}

# Set up your OpenAI/Gemini client
api_key = "YOUR_API_KEY"
base_url = "YOUR_BASE_URL"
client = OpenAIClient(api_key, base_url)

RESULT_DIR = os.path.join(os.path.dirname(__file__), 'Result')
AUDIO_SCRIPT = os.path.join(os.path.dirname(__file__), 'Audio_AI_interview.py')

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/start_interview', methods=['POST'])
def start_interview():
    data = request.get_json()
    job_role = data.get('job_role')
    if not job_role:
        return jsonify({'error': 'Job role is required.'}), 400

    interview_ai = InterviewAI(client)
    questions = interview_ai.generate_questions(job_role)
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        'job_role': job_role,
        'questions': questions,
        'answers': [],
        'current_index': 0
    }

    # Generate TTS for first question
    question_text = questions[0]
    audio_filename = f"{session_id}_q0.mp3"
    tts = gTTS(text=question_text, lang='en')
    tts.save(os.path.join('static', audio_filename))

    return jsonify({
        'session_id': session_id,
        'question_index': 0,
        'question_text': question_text,
        'question_audio_url': f'/static/{audio_filename}'
    })

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    session_id = request.form.get('session_id')
    question_index = int(request.form.get('question_index', 0))
    audio_file = request.files.get('audio')

    if not session_id or session_id not in sessions:
        return jsonify({'error': 'Invalid session.'}), 400
    if not audio_file:
        return jsonify({'error': 'No audio file provided.'}), 400

    # Save audio temporarily and transcribe
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
        audio_file.save(temp_audio.name)
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_audio.name) as source:
            audio = recognizer.record(source)
            try:
                response_text = recognizer.recognize_google(audio)
            except Exception as e:
                response_text = ""
        os.remove(temp_audio.name)

    # Store answer
    session = sessions[session_id]
    session['answers'].append({
        'question': session['questions'][question_index],
        'response': response_text
    })
    session['current_index'] += 1

    # Next question or finish
    if session['current_index'] < len(session['questions']):
        next_index = session['current_index']
        question_text = session['questions'][next_index]
        audio_filename = f"{session_id}_q{next_index}.mp3"
        tts = gTTS(text=question_text, lang='en')
        tts.save(os.path.join('static', audio_filename))
        return jsonify({
            'question_index': next_index,
            'question_text': question_text,
            'question_audio_url': f'/static/{audio_filename}',
            'transcript': response_text
        })
    else:
        # Evaluate and return results
        interview_ai = InterviewAI(client)
        evaluation = interview_ai.evaluate_interview(session['job_role'], session['answers'])
        result = {
            'job_role': session['job_role'],
            'questions': session['questions'],
            'answers': session['answers'],
            'evaluation': evaluation
        }
        filename = f"Result/interview_results_{session_id}.json"
        with open(filename, "w") as f:
            json.dump(result, f, indent=2)
        del sessions[session_id]
        return jsonify({'result': result, 'transcript': response_text})

@app.route('/run_interview', methods=['POST'])
def run_interview():
    data = request.get_json()
    job_role = data.get('job_role')
    if not job_role:
        return jsonify({'error': 'Job role is required.'}), 400

    # Run the interview script (blocking, uses server's mic/speaker)
    try:
        subprocess.run(['python3', AUDIO_SCRIPT], input=f"{job_role}\n", text=True, check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Interview failed.', 'details': str(e)}), 500

    # Find the latest result file
    result_files = sorted(glob.glob(os.path.join(RESULT_DIR, 'interview_results_*.json')), reverse=True)
    if not result_files:
        return jsonify({'error': 'No result file found.'}), 500
    with open(result_files[0], 'r') as f:
        result_data = json.load(f)
    return jsonify(result_data)

if __name__ == '__main__':
    app.run(debug=True)