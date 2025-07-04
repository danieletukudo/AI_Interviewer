import json
import time
import re

class OpenAIClient:
    def __init__(self, api_key, base_url):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def create_completion(self, model, messages):
        return self.client.chat.completions.create(model=model, messages=messages)

class InterviewAI:
    def __init__(self, client):
        self.client = client

    def generate_questions(self, job_role):
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
            json_str = raw_response.strip()
            if '```' in json_str:
                json_str = json_str.split('```')[1].strip()
                if json_str.startswith('json'):
                    json_str = json_str[4:].strip()
            questions = json.loads(json_str)
            return questions[:5]
        except Exception as e:
            # fallback
            return [
                f"What makes you a strong candidate for this {job_role} position?",
                "Tell me about a challenging project you worked on recently.",
                "How do you approach learning new technologies?",
                "Describe your experience with team collaboration.",
                "What are your career goals?"
            ]

    def evaluate_interview(self, job_role, interview_data):
        prompt = f"""
        As an expert hiring manager, evaluate this candidate for a {job_role} position.
        Here are their interview responses:
        {'-' * 40}
        """ + "\n".join([
            f"Q{i+1}: {response['question']}\nA: {response['response']}\n"
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
            try:
                evaluation = json.loads(raw_response)
            except json.JSONDecodeError:
                json_match = re.search(r'```json\s*(.*?)\s*```', raw_response, re.DOTALL)
                if json_match:
                    evaluation = json.loads(json_match.group(1))
                else:
                    json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                    if json_match:
                        evaluation = json.loads(json_match.group(0))
                    else:
                        raise ValueError("No JSON found in response")
            return evaluation
        except Exception as e:
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
