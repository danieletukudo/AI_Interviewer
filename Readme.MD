
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

