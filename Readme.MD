# AI Interview System

This repository contains two versions of an AI-powered interview system: a text-based and an audio-based interviewer.

## Overview

The system uses Gemini AI to conduct automated job interviews, generate relevant questions based on the job role, and provide comprehensive evaluations of candidates' responses.

## Files

1. `Text_AI_interview.py` - Text-based interview system
2. `Audio_AI_interview.py` - Audio-based interview system with speech recognition

## Features

- Dynamic question generation based on job role
- Comprehensive candidate evaluation
- JSON-formatted results storage
- Multiple evaluation criteria:
  - Technical competency
  - Problem-solving abilities
  - Communication skills
  - Experience level
  - Cultural fit

### Audio Interview Specific Features
- Voice interaction using Google Text-to-Speech
- Speech recognition for verbal responses
- Intelligent pause detection (waits for 2 seconds of silence)
- Natural conversation flow

### Text Interview Specific Features
- Command-line interface
- Text-based input/output
- Streamlined interaction

## Requirements

```bash
pip install -r requirements.txt
```

Required packages:
- openai
- gTTS (Google Text-to-Speech)
- SpeechRecognition
- pyaudio
- playsound
- json

## Setup

1. Install the required packages
2. Set up your Gemini API key
3. Choose the appropriate interview system (Text or Audio)

## Usage

### Text-based Interview:
```bash
python Text_AI_interview.py
```

### Audio-based Interview:
```bash
python Audio_AI_interview.py
```

Follow the prompts to:
1. Enter the job role
2. Answer interview questions
3. Receive evaluation and feedback

## Output

The system generates:
- Real-time feedback
- Comprehensive evaluation
- JSON file with interview results including:
  - Questions and responses
  - Evaluation scores
  - Strengths and areas for improvement
  - Hiring recommendation
  - Detailed feedback

## File Naming

Results are saved as: `interview_results_YYYYMMDD_HHMMSS.json`

## Configuration

### Audio Settings
- Pause threshold: 2 seconds
- Phrase threshold: 0.3 seconds
- Non-speaking duration: 1 second

### Interview Format
- 5 questions per interview
- Mix of technical and behavioral questions
- Role-specific content

## Error Handling

- Fallback question generation
- Speech recognition retry mechanism
- JSON parsing error handling
- Comprehensive error messages

## Notes

- Audio interview requires a working microphone
- Internet connection required for:
  - Speech recognition
  - Text-to-speech
  - AI model access
- Results are stored locally in JSON format

## Web UI (Modern Product Page)

The project now includes a modern web UI served directly from Flask.

### How to Use

1. Rename the `frontend` folder to `static` in your project root (so Flask can serve the files).
2. Run the Flask backend:
   ```bash
   python app.py
   ```
3. Open your browser and go to [let sessionId = null;
let questionIndex = 0;
let mediaRecorder;
let audioChunks = [];

const setupDiv = document.getElementById('setup');
const interviewDiv = document.getElementById('interview');
const resultDiv = document.getElementById('result');
const questionText = document.getElementById('question-text');
const questionAudio = document.getElementById('question-audio');
const recordBtn = document.getElementById('record-btn');
const stopBtn = document.getElementById('stop-btn');
const answerAudio = document.getElementById('answer-audio');
const submitBtn = document.getElementById('submit-btn');

document.getElementById('start-btn').onclick = async () => {
  const jobRole = document.getElementById('job-role').value.trim();
  if (!jobRole) return alert('Please enter a job role!');
  const res = await fetch('/start_interview', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ job_role: jobRole })
  });
  const data = await res.json();
  if (data.error) return alert(data.error);
  sessionId = data.session_id;
  questionIndex = data.question_index;
  questionText.textContent = data.question_text;
  questionAudio.src = data.question_audio_url;
  setupDiv.style.display = 'none';
  interviewDiv.style.display = '';
  resultDiv.style.display = 'none';
  answerAudio.style.display = 'none';
  submitBtn.disabled = true;
};

recordBtn.onclick = async () => {
  audioChunks = [];
  answerAudio.style.display = 'none';
  submitBtn.disabled = true;
  recordBtn.disabled = true;
  stopBtn.disabled = false;
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  mediaRecorder.start();
  mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
  mediaRecorder.onstop = () => {
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
    answerAudio.src = URL.createObjectURL(audioBlob);
    answerAudio.style.display = '';
    submitBtn.disabled = false;
    stream.getTracks().forEach(track => track.stop());
  };
};

stopBtn.onclick = () => {
  recordBtn.disabled = false;
  stopBtn.disabled = true;
  mediaRecorder.stop();
};

submitBtn.onclick = async () => {
  submitBtn.disabled = true;
  const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
  const formData = new FormData();
  formData.append('session_id', sessionId);
  formData.append('question_index', questionIndex);
  formData.append('audio', audioBlob, 'answer.wav');
  const res = await fetch('/submit_answer', { method: 'POST', body: formData });
  const data = await res.json();
  if (data.result) {
    interviewDiv.style.display = 'none';
    resultDiv.style.display = '';
    resultDiv.innerHTML = formatResult(data.result);
  } else {
    questionIndex = data.question_index;
    questionText.textContent = data.question_text;
    questionAudio.src = data.question_audio_url;
    answerAudio.style.display = 'none';
    submitBtn.disabled = true;
  }
};

function formatResult(result) {
  let html = `<h2>Interview Results</h2>`;
  html += `<h3>Job Role: ${result.job_role}</h3>`;
  html += `<h4>Questions & Answers</h4><ul>`;
  result.answers.forEach((qa, i) => {
    html += `<li><b>Q${i+1}:</b> ${qa.question}<br><b>Your answer:</b> ${qa.response}</li>`;
  });
  html += `</ul>`;
  html += `<h4>Evaluation</h4><ul>`;
  for (const [k, v] of Object.entries(result.evaluation)) {
    html += `<li><b>${k.replace(/_/g, ' ')}:</b> ${Array.isArray(v) ? v.join(', ') : v}</li>`;
  }
  html += `</ul>`;
  return html;
} http://localhost:5000](http://localhost:5000)
4. Use the product page to start an audio interview and view results interactively.

All static files (HTML, CSS, JS) are now served from the `static` folder.

