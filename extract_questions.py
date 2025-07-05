import re
import csv
import json
import os
import logging
from openai import OpenAI
from typing import List, Dict, Any
import PyPDF2
from pathlib import Path
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
        
        # Set up OpenAI client
        self.client = OpenAI(api_key=openai_api_key)
        
        # Initialize knowledge base
        self._extract_knowledge_from_pdf()
    
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
    
    def get_explanation_for_question(self, question_data: Dict[str, Any]) -> str:
        """
        Get a detailed explanation for a specific question.
        
        Args:
            question_data: Dictionary containing question, answer_choices, and correct_answers
            
        Returns:
            String containing the explanation in JSON format
        """
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
                        based on AWS documentation and best practices.
                        
                        IMPORTANT: You must respond with a valid JSON dictionary in the format:
                        {"ANSWER_CHOICE_1": "explanation for choice 1", "ANSWER_CHOICE_2": "explanation for choice 2", ...}
                        
                        Do not include any other text, just the JSON dictionary."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            explanation_text = response.choices[0].message.content.strip()
            
            # Try to parse the response as JSON
            try:
                explanation_dict = json.loads(explanation_text)
                # Convert back to JSON string for storage
                return json.dumps(explanation_dict, ensure_ascii=False)
            except json.JSONDecodeError:
                # If parsing fails, return the raw text
                logger.warning(f"Failed to parse explanation as JSON: {explanation_text[:100]}...")
                return explanation_text
            
        except Exception as e:
            logger.error(f"Error getting explanation from OpenAI: {e}")
            return f"Failed to get explanation: {e}"
    
    def _create_explanation_prompt(self, question_data: Dict[str, Any]) -> str:
        """
        Create a detailed prompt for explaining the question.
        """
        prompt = f"""
        Based on your knowledge of AWS Certified Developer Associate concepts, please explain the following question:

        QUESTION: {question_data['QUESTION']}

        ANSWER CHOICES:
        """
        
        for i, choice in enumerate(question_data['ANSWER_CHOICES'], 1):
            prompt += f"{i}. {choice}\n"
        
        prompt += f"""
        CORRECT ANSWERS: {', '.join(question_data['ANSWERS'])}

        Please provide explanations for EACH answer choice in the following JSON format:
        {{
            "{question_data['ANSWER_CHOICES'][0]}": "explanation for why this choice is correct/incorrect",
            "{question_data['ANSWER_CHOICES'][1]}": "explanation for why this choice is correct/incorrect",
            ...
        }}

        Please provide a detailed explanation that includes:
        1. Why the correct answers are right (with specific AWS concepts and best practices)
        2. Why the incorrect answers are wrong (with explanations of misconceptions or incorrect assumptions)
        3. Key AWS concepts and services mentioned in the question
        4. Real-world scenarios where this knowledge would be applied
        5. Any relevant AWS documentation or best practices that support the correct answers

        Make your explanations comprehensive but easy to understand for someone studying for the AWS Developer Associate exam.
        
        IMPORTANT: Respond ONLY with the JSON dictionary, no other text.
        """
        
        return prompt

def extract_questions_from_readme(readme_file_path):
    """
    Extract questions from README.md file and return a list of dictionaries
    with QUESTION, ANSWER_CHOICES, ANSWERS, and EXPLANATIONS fields.
    """
    questions = []
    
    with open(readme_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Split content by question headers (lines starting with ###)
    question_sections = re.split(r'\n### ', content)
    print(f"Found {len(question_sections)} sections")
    
    for section in question_sections[1:]:  # Skip the first section (header)
        if not section.strip():
            continue
            
        # Split the section into lines
        lines = section.strip().split('\n')
        
        # The first line is the question
        question_text = lines[0].strip()
        
        # Skip if it's just a placeholder or empty
        if question_text.lower() == 'placeholder' or not question_text:
            continue
        
        answer_choices = []
        correct_answers = []
        
        # Process the remaining lines to find answer choices
        for line in lines[1:]:
            line = line.strip()
            
            # Skip empty lines and navigation links
            if not line or line.startswith('[⬆ Back to Top]') or line.startswith('**[⬆ Back to Top]'):
                continue
            
            # Check if this is an answer choice (starts with - [ ] or - [x])
            if line.startswith('- [ ]') or line.startswith('- [x]'):
                # Extract the choice text (remove the checkbox part)
                choice_text = line[5:].strip()
                
                # Add to answer choices
                answer_choices.append(choice_text)
                
                # If it's marked as correct (has [x]), add to correct answers
                if line.startswith('- [x]'):
                    correct_answers.append(choice_text)
        
        # Only add questions that have answer choices and correct answers
        if answer_choices and correct_answers:
            questions.append({
                'QUESTION': question_text,
                'ANSWER_CHOICES': answer_choices,
                'ANSWERS': correct_answers,
                'EXPLANATIONS': ''  # Will be filled later
            })
    
    return questions

def save_to_csv(questions, output_file_path):
    """
    Save questions to a CSV file with proper formatting for lists and explanations.
    """
    with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['QUESTION', 'ANSWER_CHOICES', 'ANSWERS', 'EXPLANATIONS']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for question in questions:
            # Convert lists to JSON strings for CSV storage
            row = {
                'QUESTION': question['QUESTION'],
                'ANSWER_CHOICES': json.dumps(question['ANSWER_CHOICES'], ensure_ascii=False),
                'ANSWERS': json.dumps(question['ANSWERS'], ensure_ascii=False),
                'EXPLANATIONS': question['EXPLANATIONS']
            }
            writer.writerow(row)

def main():
    """
    Main function to extract questions, generate explanations, and save to CSV.
    """
    # Load environment variables
    load_dotenv()
    
    # Get API key
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        print("Please set your OPENAI_API_KEY environment variable")
        return
    
    readme_file = 'README.md'
    output_file = 'aws_developer_associate_questions.csv'
    
    print("Extracting questions from README.md...")
    questions = extract_questions_from_readme(readme_file)
    
    print(f"Found {len(questions)} questions")
    
    # Initialize the AWS Quiz Agent
    print("Initializing AWS Quiz Agent...")
    agent = AWSQuizAgent(openai_api_key)
    
    # Generate explanations for each question
    print("Generating explanations for questions...")
    for i, question in enumerate(questions):
        print(f"Processing question {i+1}/{len(questions)}: {question['QUESTION'][:50]}...")
        
        try:
            explanation = agent.get_explanation_for_question(question)
            print(explanation)
            question['EXPLANATIONS'] = explanation
            
            # Add a small delay to avoid rate limiting
            import time
            time.sleep(1)
            
        except Exception as e:
            print(f"Error generating explanation for question {i+1}: {e}")
            question['EXPLANATIONS'] = f"Error: {e}"
    
    # Save to CSV
    print(f"Saving questions with explanations to {output_file}...")
    save_to_csv(questions, output_file)
    
    print(f"Questions saved to {output_file}")
    
    # Print a sample question for verification
    if questions:
        print("\nSample question with explanation:")
        print(f"Question: {questions[0]['QUESTION']}")
        print(f"Answer choices: {questions[0]['ANSWER_CHOICES']}")
        print(f"Correct answers: {questions[0]['ANSWERS']}")
        
        # Try to parse and display the explanation dictionary
        try:
            explanation_dict = json.loads(questions[0]['EXPLANATIONS'])
            print("Explanations:")
            for answer, explanation in explanation_dict.items():
                print(f"  {answer}: {explanation[:100]}...")
        except (json.JSONDecodeError, KeyError):
            print(f"Explanation: {questions[0]['EXPLANATIONS'][:200]}...")

if __name__ == "__main__":
    main() 