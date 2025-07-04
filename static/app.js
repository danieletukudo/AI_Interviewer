let sessionId = null;
let questionIndex = 0;
let mediaRecorder;
let audioChunks = [];
let conversation = [];

const setupDiv = document.getElementById('setup');
const interviewDiv = document.getElementById('interview');
const resultDiv = document.getElementById('result');
const questionText = document.getElementById('question-text');
const questionAudio = document.getElementById('question-audio');
const recordBtn = document.getElementById('record-btn');
const stopBtn = document.getElementById('stop-btn');
const answerAudio = document.getElementById('answer-audio');
const submitBtn = document.getElementById('submit-btn');
const convoDiv = document.getElementById('convo');

function updateConversation() {
  convoDiv.innerHTML = conversation.map(item => {
    if (item.type === 'question') {
      return `<div class="q"><b>Question ${item.index+1}:</b> ${item.text}</div>`;
    } else if (item.type === 'answer') {
      return `<div class="a"><b>You said:</b> ${item.text}</div>`;
    } else if (item.type === 'status') {
      return `<div class="status">${item.text}</div>`;
    }
    return '';
  }).join('');
}

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
  conversation = [{type: 'question', index: questionIndex, text: data.question_text}];
  updateConversation();
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
  conversation.push({type: 'status', text: 'Listening... (speak your response, I\'ll wait for you to finish)'});
  updateConversation();
  try {
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
  } catch (err) {
    alert('Microphone access denied or not supported.');
    recordBtn.disabled = false;
    stopBtn.disabled = true;
  }
};

stopBtn.onclick = () => {
  recordBtn.disabled = false;
  stopBtn.disabled = true;
  mediaRecorder.stop();
};

submitBtn.onclick = async () => {
  submitBtn.disabled = true;
  conversation.push({type: 'status', text: 'Processing your response...'});
  updateConversation();
  const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
  const formData = new FormData();
  formData.append('session_id', sessionId);
  formData.append('question_index', questionIndex);
  formData.append('audio', audioBlob, 'answer.wav');
  const res = await fetch('/submit_answer', { method: 'POST', body: formData });
  const data = await res.json();
  // Show transcript
  if (data.transcript) {
    conversation.push({type: 'answer', text: data.transcript});
  }
  // Next question or result
  if (data.result) {
    interviewDiv.style.display = 'none';
    resultDiv.style.display = '';
    resultDiv.innerHTML = formatResult(data.result);
  } else {
    questionIndex = data.question_index;
    conversation.push({type: 'question', index: questionIndex, text: data.question_text});
    updateConversation();
    questionText.textContent = data.question_text;
    questionAudio.src = data.question_audio_url;
    answerAudio.style.display = 'none';
    submitBtn.disabled = true;
  }
  // Remove status
  conversation = conversation.filter(item => item.type !== 'status');
  updateConversation();
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
}