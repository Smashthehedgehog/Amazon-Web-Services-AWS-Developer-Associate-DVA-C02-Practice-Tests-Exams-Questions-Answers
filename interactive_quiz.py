#!/usr/bin/env python3
"""
Interactive AWS Quiz Agent - A command-line interface for the AWS Quiz Agent.
"""

import os
import json
import sys
from aws_quiz_agent import AWSQuizAgent

def print_banner():
    """Print a welcome banner."""
    print("=" * 60)
    print("🚀 AWS Certified Developer Associate Quiz Agent")
    print("=" * 60)
    print("This agent can explain AWS quiz questions using knowledge from the slides.")
    print("=" * 60)

def get_api_key():
    """Get OpenAI API key from user or environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ OpenAI API key not found in environment variables.")
        print("Please set your OpenAI API key:")
        print("   Windows: set OPENAI_API_KEY=your_key_here")
        print("   Linux/Mac: export OPENAI_API_KEY=your_key_here")
        print("\nOr enter it now (it won't be saved):")
        api_key = input("OpenAI API Key: ").strip()
        
        if not api_key:
            print("❌ API key is required. Exiting.")
            sys.exit(1)
    
    return api_key

def show_menu():
    """Show the main menu options."""
    print("\n📋 Available Options:")
    print("1. 📖 Get explanation for a specific question")
    print("2. 🔍 Find questions by topic")
    print("3. 📚 Create a study session")
    print("4. 💾 Save all explanations to file")
    print("5. 📊 Show question statistics")
    print("6. ❓ Get help")
    print("0. 🚪 Exit")
    print("-" * 40)

def get_question_explanation(agent):
    """Get explanation for a specific question."""
    print("\n📖 Get Question Explanation")
    print("-" * 30)
    
    # Show available options
    print("How would you like to select a question?")
    print("1. By question number")
    print("2. By searching question text")
    
    choice = input("\nEnter your choice (1-2): ").strip()
    
    if choice == "1":
        try:
            question_num = int(input("Enter question number (1-385): ")) - 1
            if 0 <= question_num < len(agent.questions_data):
                explanation = agent.get_explanation_for_question(question_index=question_num)
                display_explanation(explanation)
            else:
                print(f"❌ Question number must be between 1 and {len(agent.questions_data)}")
        except ValueError:
            print("❌ Please enter a valid number")
    
    elif choice == "2":
        search_term = input("Enter search term: ").strip()
        if search_term:
            explanation = agent.get_explanation_for_question(question_text=search_term)
            if "error" not in explanation:
                display_explanation(explanation)
            else:
                print(f"❌ No questions found containing '{search_term}'")
        else:
            print("❌ Please enter a search term")

def find_questions_by_topic(agent):
    """Find questions by topic."""
    print("\n🔍 Find Questions by Topic")
    print("-" * 30)
    
    # Common AWS topics
    common_topics = [
        "S3", "Lambda", "DynamoDB", "EC2", "RDS", "API Gateway", 
        "CloudFormation", "IAM", "VPC", "ElastiCache", "SQS", "SNS",
        "CloudWatch", "CodeDeploy", "Elastic Beanstalk", "KMS"
    ]
    
    print("Common AWS topics:")
    for i, topic in enumerate(common_topics, 1):
        print(f"{i:2d}. {topic}")
    
    print("\nOr enter a custom topic:")
    topic = input("Enter topic: ").strip()
    
    if topic:
        questions = agent.get_question_by_topic(topic)
        if questions:
            print(f"\n✅ Found {len(questions)} questions about '{topic}':")
            for i, q in enumerate(questions[:10], 1):  # Show first 10
                print(f"{i}. {q['question'][:80]}...")
            
            if len(questions) > 10:
                print(f"... and {len(questions) - 10} more")
            
            # Ask if user wants explanation for any of these
            if questions:
                try:
                    choice = int(input(f"\nEnter question number (1-{min(10, len(questions))}) for explanation, or 0 to skip: "))
                    if 1 <= choice <= len(questions):
                        explanation = agent.get_explanation_for_question(question_index=questions[choice-1]['index'])
                        display_explanation(explanation)
                except ValueError:
                    pass
        else:
            print(f"❌ No questions found for topic '{topic}'")

def create_study_session(agent):
    """Create a study session."""
    print("\n📚 Create Study Session")
    print("-" * 30)
    
    try:
        num_questions = int(input("Number of questions (1-20): "))
        num_questions = max(1, min(20, num_questions))
    except ValueError:
        num_questions = 5
    
    topic = input("Topic (optional, press Enter to skip): ").strip()
    topic = topic if topic else None
    
    print(f"\n🔄 Creating study session with {num_questions} questions...")
    if topic:
        print(f"Topic: {topic}")
    
    session = agent.create_study_session(num_questions=num_questions, topic=topic)
    
    print(f"\n✅ Study session created with {len(session)} questions!")
    
    for i, explanation in enumerate(session, 1):
        print(f"\n{'='*50}")
        print(f"Question {i}/{len(session)}")
        print(f"{'='*50}")
        display_explanation(explanation, show_full=False)
        
        if i < len(session):
            input("\nPress Enter for next question...")

def save_explanations(agent):
    """Save all explanations to file."""
    print("\n💾 Save All Explanations")
    print("-" * 30)
    
    filename = input("Filename (default: aws_explanations.json): ").strip()
    if not filename:
        filename = "aws_explanations.json"
    
    if not filename.endswith('.json'):
        filename += '.json'
    
    print(f"\n🔄 Saving explanations to {filename}...")
    print("This may take a while and will use OpenAI API calls.")
    
    confirm = input("Continue? (y/N): ").strip().lower()
    if confirm == 'y':
        try:
            agent.save_explanations_to_file(filename)
            print(f"✅ Explanations saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving explanations: {e}")
    else:
        print("❌ Operation cancelled")

def show_statistics(agent):
    """Show question statistics."""
    print("\n📊 Question Statistics")
    print("-" * 30)
    
    total_questions = len(agent.questions_data)
    print(f"Total questions: {total_questions}")
    
    # Count questions by topic
    topics = {}
    for q in agent.questions_data:
        question_lower = q['question'].lower()
        for topic in ['s3', 'lambda', 'dynamodb', 'ec2', 'rds', 'api gateway', 'cloudformation', 'iam', 'vpc']:
            if topic in question_lower:
                topics[topic] = topics.get(topic, 0) + 1
    
    print("\nQuestions by topic:")
    for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True):
        print(f"  {topic.title()}: {count}")
    
    # Count questions by number of correct answers
    single_answer = sum(1 for q in agent.questions_data if len(q['correct_answers']) == 1)
    multiple_answer = total_questions - single_answer
    
    print(f"\nQuestion types:")
    print(f"  Single answer: {single_answer}")
    print(f"  Multiple answer: {multiple_answer}")

def display_explanation(explanation, show_full=True):
    """Display a question explanation in a formatted way."""
    if "error" in explanation:
        print(f"❌ Error: {explanation['error']}")
        return
    
    print(f"\n{'='*60}")
    print("📝 QUESTION:")
    print(f"{'='*60}")
    print(explanation['question'])
    
    print(f"\n{'='*60}")
    print("📋 ANSWER CHOICES:")
    print(f"{'='*60}")
    for i, choice in enumerate(explanation['answer_choices'], 1):
        if choice in explanation['correct_answers']:
            print(f"{i}. ✅ {choice}")
        else:
            print(f"{i}. ❌ {choice}")
    
    print(f"\n{'='*60}")
    print("🎯 CORRECT ANSWERS:")
    print(f"{'='*60}")
    for answer in explanation['correct_answers']:
        print(f"✅ {answer}")
    
    if show_full:
        print(f"\n{'='*60}")
        print("📚 EXPLANATION:")
        print(f"{'='*60}")
        print(explanation['explanation'])

def show_help():
    """Show help information."""
    print("\n❓ Help")
    print("-" * 30)
    print("This AWS Quiz Agent helps you understand AWS Certified Developer Associate questions.")
    print("\nFeatures:")
    print("• Get detailed explanations for any question")
    print("• Find questions by AWS service/topic")
    print("• Create custom study sessions")
    print("• Save all explanations for offline study")
    print("\nTips:")
    print("• Use specific topics like 'S3', 'Lambda', 'DynamoDB' for better results")
    print("• The agent uses GPT-4 for explanations, so API calls will be charged")
    print("• Explanations are based on AWS best practices and documentation")

def main():
    """Main interactive loop."""
    print_banner()
    
    # Get API key
    api_key = get_api_key()
    
    try:
        # Initialize agent
        print("\n🔄 Initializing AWS Quiz Agent...")
        agent = AWSQuizAgent(api_key)
        print("✅ Agent initialized successfully!")
        
        # Main loop
        while True:
            show_menu()
            choice = input("Enter your choice (0-6): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                get_question_explanation(agent)
            elif choice == "2":
                find_questions_by_topic(agent)
            elif choice == "3":
                create_study_session(agent)
            elif choice == "4":
                save_explanations(agent)
            elif choice == "5":
                show_statistics(agent)
            elif choice == "6":
                show_help()
            else:
                print("❌ Invalid choice. Please try again.")
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your API key and try again.")

if __name__ == "__main__":
    main() 