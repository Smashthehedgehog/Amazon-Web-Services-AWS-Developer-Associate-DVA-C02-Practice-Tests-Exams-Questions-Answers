# AWS Certified Developer Associate Quiz Agent

An intelligent OpenAI-powered agent that can read AWS Certified Developer Slides and provide detailed explanations for quiz questions.

## 🚀 Features

- **PDF Knowledge Extraction**: Automatically extracts knowledge from AWS slides PDF
- **Question Explanations**: Provides detailed explanations for why answers are correct/incorrect
- **Topic-based Search**: Find questions by AWS service or topic
- **Study Sessions**: Create custom study sessions with multiple questions
- **Interactive Interface**: User-friendly command-line interface
- **Offline Storage**: Save explanations to JSON files for offline study

## 📋 Prerequisites

1. **Python 3.8+** installed on your system
2. **OpenAI API Key** (you can get one from [OpenAI Platform](https://platform.openai.com/))
3. **AWS Certified Developer Slides PDF** (should be named "AWS Certified Developer Slides v40.pdf")

## 🛠️ Installation

### Step 1: Clone or Download Files
Make sure you have all the required files in your directory:
- `aws_quiz_agent.py` - Main agent class
- `interactive_quiz.py` - Interactive interface
- `extract_questions.py` - Question extraction script
- `requirements.txt` - Python dependencies
- `README.md` - Original AWS questions
- `AWS Certified Developer Slides v40.pdf` - AWS slides

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Set Up OpenAI API Key
Set your OpenAI API key as an environment variable:

**Windows:**
```cmd
set OPENAI_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY=your_api_key_here
```

**Or add it to your system environment variables permanently.**

### Step 4: Extract Questions (First Time Only)
Run the question extraction script to create the CSV file:
```bash
python extract_questions.py
```

This will create `aws_developer_associate_questions.csv` with all the questions from the README.

## 🎯 Usage

### Quick Start
Run the interactive interface:
```bash
python interactive_quiz.py
```

### Programmatic Usage
```python
from aws_quiz_agent import AWSQuizAgent

# Initialize the agent
agent = AWSQuizAgent("your_openai_api_key")

# Get explanation for a specific question
explanation = agent.get_explanation_for_question(question_index=0)
print(explanation)

# Find questions by topic
s3_questions = agent.get_question_by_topic("S3")
print(f"Found {len(s3_questions)} S3 questions")

# Create a study session
study_session = agent.create_study_session(num_questions=5, topic="Lambda")
```

## 📖 Available Commands

When using the interactive interface, you can:

1. **📖 Get explanation for a specific question**
   - By question number (1-385)
   - By searching question text

2. **🔍 Find questions by topic**
   - Search by AWS service (S3, Lambda, DynamoDB, etc.)
   - Get explanations for found questions

3. **📚 Create a study session**
   - Choose number of questions (1-20)
   - Optional topic filter
   - Step-through explanations

4. **💾 Save all explanations to file**
   - Generate JSON file with all explanations
   - Useful for offline study

5. **📊 Show question statistics**
   - Total question count
   - Questions by topic
   - Single vs multiple answer questions

6. **❓ Get help**
   - Usage tips and information

## 🔧 Configuration

### Customizing the Agent

You can modify the agent behavior by editing `aws_quiz_agent.py`:

- **Model Selection**: Change `model="gpt-4"` to use different OpenAI models
- **Temperature**: Adjust `temperature=0.3` for more/less creative responses
- **Max Tokens**: Modify `max_tokens=1500` for longer/shorter explanations

### PDF Processing

The agent supports two PDF processing libraries:
- **PyMuPDF** (recommended) - Better for complex PDFs
- **PyPDF2** (fallback) - Basic PDF text extraction

## 💡 Tips for Best Results

1. **Use Specific Topics**: Search for specific AWS services like "S3", "Lambda", "DynamoDB" for better results
2. **API Costs**: The agent uses GPT-4, so be mindful of API costs for large study sessions
3. **Offline Study**: Use the "Save explanations" feature to create offline study materials
4. **Question Numbers**: Questions are numbered 1-385, matching the original README order

## 🐛 Troubleshooting

### Common Issues

1. **"Python was not found"**
   - Install Python 3.8+ from [python.org](https://python.org)
   - Make sure Python is in your PATH

2. **"OpenAI API key not found"**
   - Set the OPENAI_API_KEY environment variable
   - Or enter it when prompted

3. **"PDF file not found"**
   - Ensure "AWS Certified Developer Slides v40.pdf" is in the same directory
   - Check the filename matches exactly

4. **"CSV file not found"**
   - Run `python extract_questions.py` first to create the CSV

5. **Import errors**
   - Install dependencies: `pip install -r requirements.txt`
   - Make sure you're using Python 3.8+

### API Rate Limits

If you encounter rate limit errors:
- The agent includes a 1-second delay between API calls
- For large datasets, consider processing in smaller batches
- Check your OpenAI account usage limits

## 📁 File Structure

```
your-directory/
├── aws_quiz_agent.py          # Main agent class
├── interactive_quiz.py        # Interactive interface
├── extract_questions.py       # Question extraction script
├── requirements.txt           # Python dependencies
├── README.md                  # Original AWS questions
├── AWS Certified Developer Slides v40.pdf  # AWS slides
├── aws_developer_associate_questions.csv   # Generated questions (after running extract_questions.py)
└── aws_explanations.json      # Generated explanations (optional)
```

## 🤝 Contributing

Feel free to improve the agent by:
- Adding more AWS topics and services
- Improving PDF text extraction
- Enhancing the explanation prompts
- Adding new features

## 📄 License

This project is for educational purposes. Make sure to comply with OpenAI's terms of service and AWS documentation usage guidelines.

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your OpenAI API key is valid
3. Ensure all dependencies are installed
4. Check that the PDF file is accessible and readable 