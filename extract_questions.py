import re
import os
import random
 
def parse_markdown(file_path):
    """
    Parse the Markdown file to extract questions, options, and answers.
 
    Args:
        file_path (str): Path to the Markdown file.
 
    Returns:
        list: A list of dictionaries containing questions, options, and answers.
    """
    questions = []
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
 
    # Regex to match questions, options, and answers
    question_blocks = re.findall(r'###\s*(.*?)(?=###|\Z)', content, re.DOTALL)

    for idx, block in enumerate(question_blocks):
        # Split block into question and options
        # Find where options start (first line with '- [')
        match = re.search(r'\n- \[', block)
        if match:
            question_text = block[:match.start()].strip()
            options_text = block[match.start():].strip()
            # Remove the '**[⬆ Back to Top]' line from options_text if present
            options_text = re.sub(r'^\s*\*\*\[⬆ Back to Top\]\(.*?\)\*\*\s*$', '', options_text, flags=re.MULTILINE)
        else:
            question_text = block.strip()
            options_text = ""
        
        # Extract and randomize options
        options = []
        correct_answers = []
        if options_text:
            # Extract all option lines with their markers
            all_option_matches = re.findall(r'- \[([ x])\]\s*(.+?)(?=\n- \[|\Z)', options_text, re.DOTALL)
            
            # Build options list and track which ones are correct
            for marker, option_text in all_option_matches:
                option_clean = option_text.strip()
                options.append(option_clean)
                if marker == 'x':
                    correct_answers.append(option_clean)
            
            # Shuffle options
            random.shuffle(options)
            
            # Find positions of correct answers in shuffled list
            correct_indices = [i for i, opt in enumerate(options) if opt in correct_answers]
            
            # Add letter prefixes to options (A, B, C, D, etc.)
            letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
            options = [f"{letters[i]}) {opt}" for i, opt in enumerate(options)]
            
            # Convert correct_answers to letters
            correct_answers = [letters[i] for i in correct_indices]
        
        questions.append({
            "question": question_text,
            "options": options,
            "answer": correct_answers
        })

    return questions


def run_quiz(questions):
    """
    Run the interactive quiz in the terminal.
 
    Args:
        questions (list): List of questions with options and answers.
    """
    print("\nWelcome to the Practice Exam!\n")
    score = 0
 
    for idx, q in enumerate(questions, start=1):
        print(f"{q['question']}")
        for option in q["options"]:
            print(option)
       
        # Check if the question requires multiple answers
        if len(q["answer"]) > 1:
            print(f"\nThis question requires {len(q['answer'])} answers. Separate your answers with commas (e.g., A,B).")
            user_answers = input("Your answers: ").strip().upper().replace(" ", "").split(",")
            if sorted(user_answers) == sorted(q["answer"]):
                print("✅ Correct!\n")
                score += 1
            else:
                print(f"❌ Incorrect. The correct answers are {', '.join(q['answer'])}.\n")
        else:
            # Single-answer question
            user_answer = input("\nYour answer: ").strip().upper()
           
            # Check answer
            if user_answer == q["answer"][0]:
                print("✅ Correct!\n")
                score += 1
            else:
                print(f"❌ Incorrect. The correct answer is {q['answer'][0]}.\n")
   
    # Final score
    print(f"Your final score is {score} / {len(questions)}.")
    if score <= 35:
        print("You suck ass nigga.")
    else:
        print("You tough big bro")

if __name__ == "__main__":
    questions = parse_markdown("README.md")
 
    # Run the quiz
    run_quiz(questions)