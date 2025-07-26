import os
import json
import hashlib # Import the hashing library
import google.generativeai as genai
import google.api_core.exceptions
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Configure the Gemini API with the key from the environment variables
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
except KeyError:
    # If the key is not found, raise an error to alert the user
    raise KeyError("GEMINI_API_KEY not found. Please set it in your .env file.")

# Initialize the Flask application
app = Flask(__name__)

# --- Simple In-Memory Cache ---
# A dictionary to store the results of previous API calls.
ANALYSIS_CACHE = {}

# --- Helper Functions ---
def clean_json_response(response_text):
    """
    Cleans the Gemini API response to extract the JSON object.
    The API might return the JSON string wrapped in ```json ... ```.
    """
    json_start = response_text.find('```json')
    if json_start != -1:
        # Adjust start position to be after '```json\n'
        json_start += 7
        json_end = response_text.rfind('```')
        if json_end != -1:
            # Extract the JSON string
            json_str = response_text[json_start:json_end].strip()
            return json_str
    # If no JSON block is found, assume the whole response is the JSON string
    return response_text.strip()


# --- API Routes ---
@app.route('/')
def index():
    """
    Renders the main HTML page for testing the application.
    """
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze_placement():
    """
    The core API endpoint to analyze a resume against a job description.
    """
    # --- 1. Receive and Validate Input ---
    if 'resume' not in request.files or not request.form.get('job_description'):
        return jsonify({"error": "Resume file or job description is missing."}), 400
    
    resume_file = request.files['resume']
    job_description = request.form.get('job_description')
    
    # --- 2. Implement Caching Logic ---
    resume_content = resume_file.read()
    resume_file.seek(0)
    
    cache_key = hashlib.sha256(resume_content + job_description.encode('utf-8')).hexdigest()

    if cache_key in ANALYSIS_CACHE:
        print(f"✅ Cache HIT! Serving stored result for key: {cache_key[:10]}...")
        return jsonify(ANALYSIS_CACHE[cache_key])
    
    print(f"❌ Cache MISS! Calling Gemini API for key: {cache_key[:10]}...")
    
    # --- 3. Define the Detailed Prompt for Gemini ---
    # This prompt is updated with 'hiring_probability' and 'company_assessment'.
    prompt = """
    You are an expert career advisor for the tech and finance sectors in India.
    Your task is to analyze the provided undergraduate resume against the job description and return a detailed analysis in a structured JSON format.
    Context: The student is in the final year and the JD company has arrived for placements. 
    Note: Based on current industry requirement, A summary is not necessary for Entry-level jobs as there isn't much to summarise for an undergraduate student in comparison to an experienced individual.

    **Job Description:**
    {job_description}

    **My Resume:**
    [Resume PDF is provided as a file]

    Please provide the following in a structured JSON format with the specified keys:
    1.  `recommendation`: A clear "Apply" or "Don't Apply" verdict for this specific ROLE.
    2.  `match_score`: An integer percentage (0-100) of how well the resume matches the job description.
    3.  `interview_chance`: A qualitative assessment ('High', 'Medium', or 'Low') of the chance of passing the initial screening for an interview.
    4.  `hiring_probability`: A qualitative assessment ('High', 'Medium', or 'Low') of the overall probability of getting hired for this role if the interview process goes well.
    5.  `company_assessment`: An object containing an assessment of the COMPANY itself. It should include:
        * `verdict`: A recommendation like 'Recommended Company' or 'Apply with Caution'.
        * `summary`: A brief summary of the company's reputation, work culture, and growth prospects based on public knowledge.
    6.  `summary`: A brief overall summary explaining your recommendation, match score, and probabilities.
    7.  `strengths`: A list of strings identifying skills/experiences that are a strong match. Try to infer tech stack from projects if not mentioned explicitly in the resume.
    8.  `gaps`: A list of strings identifying key qualifications that are missing or not prominent on the resume.
    9.  `preparation_feedback`: If "Apply", an object with detailed advice on technical skills, soft skills, and potential interview questions.
    10. `resume_improvement_suggestions`: A list of specific suggestions to tailor the resume for this job.
    """

    # --- 4. Call Gemini API (only if not found in cache) ---
    try:
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        formatted_prompt = prompt.format(job_description=job_description)

        contents = [
            formatted_prompt,
            {"mime_type": "application/pdf", "data": resume_content}
        ]

        response = model.generate_content(contents)
        
        # --- 5. Process and Store the Result ---
        cleaned_json_str = clean_json_response(response.text)
        analysis_result = json.loads(cleaned_json_str)
        
        ANALYSIS_CACHE[cache_key] = analysis_result
        
        return jsonify(analysis_result)

    # --- 6. Handle Specific Errors ---
    except google.api_core.exceptions.ResourceExhausted as e:
        print(f"Rate limit exceeded: {e}")
        return jsonify({
            "error": "API rate limit exceeded.",
            "details": "You've made too many requests in a short period. Please wait a minute and try again."
        }), 429
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "Failed to process the request.", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)