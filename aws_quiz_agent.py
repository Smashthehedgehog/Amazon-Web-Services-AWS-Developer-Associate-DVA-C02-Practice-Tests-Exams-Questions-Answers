import os
import json
import csv
from openai import OpenAI
from typing import List, Dict, Any
import PyPDF2
from pathlib import Path
import logging
import re
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AWSQuizAgent:
    """
    An OpenAI agent that can read AWS Certified Developer Slides and provide
    explanations for quiz questions.
    """
    
    def __init__(self, openai_api_key: str, pdf_path: str = "AWS Certified Developer Slides v40.pdf"):
        """
        Initialize the AWS Quiz Agent.
        
        Args:
            openai_api_key: Your OpenAI API key
            pdf_path: Path to the AWS slides PDF
        """
        self.openai_api_key = openai_api_key
        self.pdf_path = pdf_path
        self.knowledge_base = ""
        self.questions_data = []
        
        # Set up OpenAI client
        self.client = OpenAI(api_key=openai_api_key)
        
        # Initialize knowledge base
        self._extract_knowledge_from_pdf()
        self._load_questions()
    
    def _extract_knowledge_from_pdf(self):
        """
        Extract text content from the AWS slides PDF and store it in knowledge base.
        """
        try:
            logger.info(f"Extracting knowledge from PDF: {self.pdf_path}")
            
            # Use PyPDF2 to extract text
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = []
                
                for page in pdf_reader.pages:
                    text_content.append(page.extract_text())
                
                self.knowledge_base = "\n".join(text_content)
                logger.info(f"Successfully extracted text from {len(pdf_reader.pages)} pages using PyPDF2")
            
            # Clean up the extracted text
            self.knowledge_base = self._clean_text(self.knowledge_base)
            
        except Exception as e:
            logger.error(f"Error extracting knowledge from PDF: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and format the extracted text for better processing.
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers
        text = re.sub(r'\b\d+\s*of\s*\d+\b', '', text)
        
        # Remove common PDF artifacts
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}]', ' ', text)
        
        return text.strip()
    
    def _load_questions(self):
        """
        Load questions from the CSV file.
        """
        csv_path = "aws_developer_associate_questions.csv"
        
        if not os.path.exists(csv_path):
            logger.warning(f"CSV file {csv_path} not found. Please run extract_questions.py first.")
            return
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    question_data = {
                        'question': row['QUESTION'],
                        'answer_choices': json.loads(row['ANSWER_CHOICES']),
                        'correct_answers': json.loads(row['ANSWERS'])
                    }
                    self.questions_data.append(question_data)
            
            logger.info(f"Loaded {len(self.questions_data)} questions from CSV")
            
        except Exception as e:
            logger.error(f"Error loading questions from CSV: {e}")
    
    def get_explanation_for_question(self, question_index: int = None, question_text: str = None) -> Dict[str, Any]:
        """
        Get a detailed explanation for a specific question.
        
        Args:
            question_index: Index of the question in the loaded data
            question_text: Text of the question to explain
            
        Returns:
            Dictionary containing explanation and analysis
        """
        if question_index is not None and question_index < len(self.questions_data):
            question_data = self.questions_data[question_index]
        elif question_text:
            # Find question by text
            question_data = None
            for q in self.questions_data:
                if question_text.lower() in q['question'].lower():
                    question_data = q
                    break
            if not question_data:
                return {"error": "Question not found"}
        else:
            return {"error": "Please provide either question_index or question_text"}
        
        # Create the prompt for OpenAI
        prompt = self._create_explanation_prompt(question_data)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert AWS Certified Developer Associate instructor. 
                        You have comprehensive knowledge of AWS services and best practices. 
                        Your task is to explain why certain answers are correct and why others are incorrect 
                        based on AWS documentation and best practices."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            explanation = response.choices[0].message.content
            
            return {
                "question": question_data['question'],
                "answer_choices": question_data['answer_choices'],
                "correct_answers": question_data['correct_answers'],
                "explanation": explanation
            }
            
        except Exception as e:
            logger.error(f"Error getting explanation from OpenAI: {e}")
            return {"error": f"Failed to get explanation: {e}"}
    
    def _create_explanation_prompt(self, question_data: Dict[str, Any]) -> str:
        """
        Create a detailed prompt for explaining the question.
        """
        prompt = f"""
        Based on your knowledge of AWS Certified Developer Associate concepts, please explain the following question:

        QUESTION: {question_data['question']}

        ANSWER CHOICES:
        """
        
        for i, choice in enumerate(question_data['answer_choices'], 1):
            prompt += f"{i}. {choice}\n"
        
        prompt += f"""
        CORRECT ANSWERS: {', '.join(question_data['correct_answers'])}

        Please provide a detailed explanation that includes:
        1. Why the correct answers are right (with specific AWS concepts and best practices)
        2. Why the incorrect answers are wrong (with explanations of misconceptions or incorrect assumptions)
        3. Key AWS concepts and services mentioned in the question
        4. Real-world scenarios where this knowledge would be applied
        5. Any relevant AWS documentation or best practices that support the correct answers

        Make your explanation comprehensive but easy to understand for someone studying for the AWS Developer Associate exam.
        """
        
        return prompt
    
    def get_question_by_topic(self, topic: str) -> List[Dict[str, Any]]:
        """
        Get questions related to a specific AWS topic.
        
        Args:
            topic: AWS topic (e.g., 'S3', 'Lambda', 'DynamoDB')
            
        Returns:
            List of questions related to the topic
        """
        related_questions = []
        
        for i, question_data in enumerate(self.questions_data):
            if topic.lower() in question_data['question'].lower():
                question_data['index'] = i
                related_questions.append(question_data)
        
        return related_questions
    
    def create_study_session(self, num_questions: int = 5, topic: str = None) -> List[Dict[str, Any]]:
        """
        Create a study session with explanations for multiple questions.
        
        Args:
            num_questions: Number of questions to include
            topic: Optional topic filter
            
        Returns:
            List of questions with explanations
        """
        if topic:
            available_questions = self.get_question_by_topic(topic)
        else:
            available_questions = [{"index": i, **q} for i, q in enumerate(self.questions_data)]
        
        # Limit to requested number
        selected_questions = available_questions[:num_questions]
        
        session_questions = []
        for q in selected_questions:
            explanation = self.get_explanation_for_question(question_index=q['index'])
            session_questions.append(explanation)
        
        return session_questions
    
    def save_explanations_to_file(self, filename: str = "aws_explanations.json"):
        """
        Save all question explanations to a JSON file.
        """
        all_explanations = []
        
        for i in range(len(self.questions_data)):
            logger.info(f"Processing question {i+1}/{len(self.questions_data)}")
            explanation = self.get_explanation_for_question(question_index=i)
            all_explanations.append(explanation)
            
            # Add a small delay to avoid rate limiting
            import time
            time.sleep(1)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_explanations, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(all_explanations)} explanations to {filename}")

    def test_api_connection(self) -> Dict[str, Any]:
        """
        Test the API connection with gpt-4o model.
        
        Returns:
            Dictionary with test results
        """
        try:
            logger.info("Testing gpt-4o model...")
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": "Hello, this is a test message. Please respond with 'Test successful'."
                    }
                ],
                max_tokens=50
            )
            
            result = {
                "status": "success",
                "response": response.choices[0].message.content
            }
            logger.info("✓ gpt-4o - Test successful")
            
        except Exception as e:
            result = {
                "status": "failed",
                "error": str(e)
            }
            logger.error(f"✗ gpt-4o - Test failed: {str(e)}")
        
        return {"gpt-4o": result}

def main():
    """
    Example usage of the AWS Quiz Agent.
    """
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # You'll need to set your OpenAI API key
    openai_api_key = os.getenv('OPENAI_API_KEY')
    print(openai_api_key)
    
    # Initialize the agent
    agent = AWSQuizAgent(openai_api_key)
    
    # First, test the API connection
    print("Testing API connection with gpt-4o...")
    test_results = agent.test_api_connection()
    print(json.dumps(test_results, indent=2))
    
    # Check if gpt-4o is working
    if test_results["gpt-4o"]["status"] != "success":
        print("gpt-4o model is not working. Please check your API key and network connection.")
        return
    
    print("gpt-4o model is working!")
    
    # Example: Get explanation for a specific question
    print("\nGetting explanation for question 0...")
    explanation = agent.get_explanation_for_question(question_index=0)
    print(json.dumps(explanation, indent=2))
    
    # Example: Get questions by topic
    s3_questions = agent.get_question_by_topic("S3")
    print(f"Found {len(s3_questions)} questions about S3")
    
    # Example: Create a study session
    study_session = agent.create_study_session(num_questions=3, topic="Lambda")
    print(f"Created study session with {len(study_session)} Lambda questions")

if __name__ == "__main__":
    main() 