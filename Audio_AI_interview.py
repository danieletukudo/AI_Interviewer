"""
A voice-based AI interviewer system that conducts job interviews through speech interaction.
This module handles speech recognition, text-to-speech conversion, and interview management.
"""

import json
from openai import OpenAI
import os
from typing import List, Dict
import time
import re
from gtts import gTTS
import speech_recognition as sr
from playsound import playsound

class OpenAIClient:
    """
    A wrapper class for OpenAI API interactions.
    
    Attributes:
        client (OpenAI): The OpenAI client instance for API calls.
    """
    
    def __init__(self, api_key, base_url):
        """
        Initialize the OpenAI client.
        
        Args:
            api_key (str): API key for authentication
            base_url (str): Base URL for API endpoints
        """
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def create_completion(self, model, messages):
        """
        Create a chat completion using the OpenAI API.
        
        Args:
            model (str): The model to use for completion
            messages (list): List of message dictionaries
            
        Returns:
            OpenAI completion response
        """
        return self.client.chat.completions.create(model=model, messages=messages)

class VoiceInterface:
    """
    Handles all voice-related interactions including speech recognition and synthesis.
    
    Attributes:
        recognizer (sr.Recognizer): Speech recognition instance
    """
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 2  # Wait for 2 seconds of silence
        self.recognizer.phrase_threshold = 0.3  # Minimum seconds of speaking to activate
        self.recognizer.non_speaking_duration = 1  # Time of silence to mark the end
    
    def speak(self, text):
        """
        Convert text to speech and play it.
        
        Args:
            text (str): Text to be converted to speech
            
        Side effects:
            Creates and plays a temporary audio file
        """
        try:
            tts = gTTS(text=text, lang='en', tld='com')
            temp_file = "temp_speech.mp3"
            tts.save(temp_file)
            playsound(temp_file)
            os.remove(temp_file)
        except Exception as e:
            print(f"Error in speech synthesis: {e}")

    def listen(self):
        """
        Listen for and recognize speech input from the user.
        
        Returns:
            str: Recognized text from speech, or None if recognition fails
            
        Side effects:
            Prints status messages during listening process
        """
        try:
            with sr.Microphone() as source:
                print("Listening... (speak your response, I'll wait for you to finish)")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen until there's a significant pause
                audio = self.recognizer.listen(source, 
                                            timeout=None,  # No timeout for starting to speak
                                            phrase_time_limit=None)  # No limit on response length
                
                print("Processing your response...")
                text = self.recognizer.recognize_google(audio)
                print(f"You said: {text}")
                return text
                
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that. Please try again.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None

class InterviewAI:
    """
    Main class handling the interview process including question generation,
    response collection, and evaluation.
    
    Attributes:
        client (OpenAIClient): Instance of OpenAIClient for API interactions
    """
    
    def __init__(self, client):
        self.client = client
        self.voice = VoiceInterface()

    def generate_questions(self, job_role: str) -> List[str]:
        """
        Generate interview questions based on the job role.
        
        Args:
            job_role (str): The position being interviewed for
            
        Returns:
            List[str]: List of 5 interview questions
            
        Raises:
            Exception: If question generation fails
        """
        prompt = f"""
        Generate 5 unique interview questions for a {job_role} position.
        Mix of:
        - Technical skills for {job_role}
        - Problem-solving scenarios
        - System design (if applicable)
        - Team collaboration
        - Past experience
        
        Make questions specific to {job_role} and avoid generic questions.
        Please make the questions short and small, I mean do not make it too long
        Format your response as a JSON array of questions only:
        ["question1", "question2", "question3", "question4", "question5"]
        """
        
        try:
            response = self.client.create_completion(
                model="gemini-2.0-flash-exp",
                messages=[{
                    "role": "user", 
                    "content": prompt + f"\nTimestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                }]
            )
            
            raw_response = response.choices[0].message.content
            
            # Clean up the response to extract just the JSON array
            # Remove any markdown formatting or extra text
            json_str = raw_response.strip()
            if '```' in json_str:
                json_str = json_str.split('```')[1].strip()
                if json_str.startswith('json'):
                    json_str = json_str[4:].strip()
            
            # Parse the JSON array
            questions = json.loads(json_str)
            
            # Ensure we have exactly 5 questions
            if len(questions) > 5:
                questions = questions[:5]
            elif len(questions) < 5:
                raise ValueError("Not enough questions generated")
                
            return questions
            
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            # Generate dynamic questions instead of using fallback
            return self.generate_dynamic_questions(job_role)
    
    def generate_dynamic_questions(self, job_role: str) -> List[str]:
        """
        Fallback method to generate questions if primary method fails.
        
        Args:
            job_role (str): The position being interviewed for
            
        Returns:
            List[str]: List of 5 interview questions
            
        Raises:
            Exception: If unable to generate questions
        """
        # Try a simpler prompt as a backup
        prompt = f"List 5 interview questions for a {job_role} position. Return only the questions as a JSON array. Please make the questions short and small, I mean do not make it too long"
        
        try:
            response = self.client.create_completion(
                model="gemini-2.0-flash-exp",
                messages=[{
                    "role": "user", 
                    "content": prompt
                }]
            )
            
            raw_response = response.choices[0].message.content
            
            # Try to extract a JSON array from the response
            questions = json.loads(raw_response)
            return questions[:5] if len(questions) >= 5 else [
                f"What makes you a strong candidate for this {job_role} position?",
                "Tell me about a challenging project you worked on recently.",
                "How do you approach learning new technologies?",
                "Describe your experience with team collaboration.",
                "What are your career goals?"
            ]
            
        except:
            # If all else fails, raise an error
            raise Exception("Unable to generate interview questions. Please try again.")

    def evaluate_interview(self, job_role: str, interview_data: List[Dict]) -> Dict:
        """
        Evaluate candidate responses and generate comprehensive feedback.
        
        Args:
            job_role (str): The position being interviewed for
            interview_data (List[Dict]): List of question-response pairs
            
        Returns:
            Dict: Structured evaluation including scores and feedback
        """
        # Construct a comprehensive evaluation prompt
        prompt = f"""
        As an expert hiring manager, evaluate this candidate for a {job_role} position.
        
        Here are their interview responses:
        
        {'-' * 40}
        """ + "\n".join([
            f"Q{i+1}: {response['question']}\n"
            f"A: {response['response']}\n"
            for i, response in enumerate(interview_data)
        ]) + f"""
        {'-' * 40}

        Provide a structured evaluation in this exact JSON format:
        {{
            "overall_score": <number between 1-10>,
            "technical_competency": <number between 1-10>,
            "problem_solving": <number between 1-10>,
            "communication": <number between 1-10>,
            "experience_level": <number between 1-10>,
            "cultural_fit": <number between 1-10>,
            "strengths": ["strength1", "strength2"],
            "areas_for_improvement": ["area1", "area2"],
            "hiring_recommendation": "<strong yes/yes/maybe/no>",
            "detailed_feedback": "<your comprehensive evaluation>"
        }}

        Ensure your response is valid JSON and includes all fields.
        """

        try:
            response = self.client.create_completion(
                model="gemini-2.0-flash-exp",
                messages=[{"role": "user", "content": prompt}]
            )
            
            raw_response = response.choices[0].message.content
            
            # Try to extract JSON from the response
            try:
                # First, try direct JSON parsing
                evaluation = json.loads(raw_response)
            except json.JSONDecodeError:
                # If that fails, try to extract JSON from markdown or text
                try:
                    # Look for JSON between triple backticks
                    json_match = re.search(r'```json\s*(.*?)\s*```', raw_response, re.DOTALL)
                    if json_match:
                        evaluation = json.loads(json_match.group(1))
                    else:
                        # Try to find JSON-like content between curly braces
                        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                        if json_match:
                            evaluation = json.loads(json_match.group(0))
                        else:
                            raise ValueError("No JSON found in response")
                except:
                    print("\nDebug - Raw response from API:")
                    print(raw_response)
                    raise
            
            # Validate required fields
            required_fields = [
                "overall_score", "technical_competency", "problem_solving",
                "communication", "experience_level", "cultural_fit",
                "strengths", "areas_for_improvement", "hiring_recommendation",
                "detailed_feedback"
            ]
            
            for field in required_fields:
                if field not in evaluation:
                    evaluation[field] = "Not provided" if field != "overall_score" else 5
            
            return evaluation
            
        except Exception as e:
            print(f"\nDebug - Error occurred: {str(e)}")
            # Return a structured fallback response
            return {
                "overall_score": 5,
                "technical_competency": 5,
                "problem_solving": 5,
                "communication": 5,
                "experience_level": 5,
                "cultural_fit": 5,
                "strengths": ["Unable to determine strengths"],
                "areas_for_improvement": ["Unable to determine areas for improvement"],
                "hiring_recommendation": "maybe",
                "detailed_feedback": f"Error processing evaluation: {str(e)}"
            }

    def run_interview(self, job_role: str):
        """
        Execute the complete interview process from start to finish.
        
        Args:
            job_role (str): The position being interviewed for
            
        Side effects:
            - Prints interview progress and results
            - Saves results to a JSON file
        """
        print(f"\nStarting interview for {job_role} position...")
        self.voice.speak(f"Welcome to the interview for the {job_role} position. I will ask you questions, and you can respond verbally.")
        time.sleep(1)
        
        try:
            questions = self.generate_questions(job_role)
            if not questions:
                raise Exception("Failed to generate questions")
                
            interview_responses = []
            
            for i, question in enumerate(questions, 1):
                print(f"\nQuestion {i}: {question}")
                self.voice.speak(question)
                
                # Get verbal response
                response = None
                while response is None:
                    response = self.voice.listen()
                    if response is None:
                        self.voice.speak("I didn't catch that. Could you please repeat your answer?")
                
                interview_responses.append({
                    "question": question,
                    "response": response
                })
                
                # Brief pause between questions
                time.sleep(1)
            
         
      
            self.voice.speak("The interview is now complete. Thank you for your time.")
            print("\nAnalyzing responses...")
            
            evaluation = self.evaluate_interview(job_role, interview_responses)
            
            # Display and speak results
            print("\nInterview Evaluation:")
     
            print(f"Overall Score: {evaluation.get('overall_score')}/10")
            print("\nDetailed Feedback:")
         
            print(evaluation.get('detailed_feedback'))
            
            if 'strengths' in evaluation:
                print("\nStrengths:")
                strengths_text = "Your key strengths are: " + ", ".join(evaluation['strengths'])
                print(strengths_text)
             
            
            if 'areas_for_improvement' in evaluation:
                print("\nAreas for Improvement:")
                improvement_text = "Areas for improvement: " + ", ".join(evaluation['areas_for_improvement'])
                print(improvement_text)
              
            
            if 'hiring_recommendation' in evaluation:
                recommendation = f"My hiring recommendation is: {evaluation['hiring_recommendation']}"
                print(f"\nHiring Recommendation: {evaluation['hiring_recommendation']}")
            
            # Save results
            results = {
                "job_role": job_role,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "interview_responses": interview_responses,
                "evaluation": evaluation
            }
            
            filename = f"Result/interview_results_{time.strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w") as f:
                json.dump(results, f, indent=2)
            
            print(f"\nResults saved to {filename}")
        
                
        except Exception as e:
            print(f"\nError during interview: {str(e)}")
            self.voice.speak("I apologize, but there was an error during the interview. Please try again.")

if __name__ == '__main__':
    api_key = "AIzaSyCMV1RzXC62lSyDxqcqlky-p1UzHqH2XEw"
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
    client = OpenAIClient(api_key, base_url)

    interview_ai = InterviewAI(client)
    job_role = input("Enter the job role: ")
    interview_ai.run_interview(job_role)
