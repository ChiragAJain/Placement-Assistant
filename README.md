# 🤖 Personalized Placement Assistant

An intelligent web application that uses the Gemini 2.5 Pro API to analyze your resume against a job description, providing detailed feedback.<br>
_[Note: This is built by Gemini Pro 2.5 as an experiment to test its capability to build full-fledge web application with human tweaks to refine it further.]_


## ✨ Features

* **AI-Powered Analysis:** Leverages Google's Gemini 2.5 Pro for a nuanced understanding of job roles and resumes.
* **Comprehensive Feedback:** Get a match score, interview and hiring probabilities, strength/gap analysis, and tailored advice.
* **Company Assessment:** Evaluates the company profile separately from the role match based on public knowledge.
* **Smart Caching:** Avoids redundant API calls by caching results for identical inputs, saving time and potential costs.
* **Simple Web Interface:** Easy-to-use UI for uploading documents and viewing results instantly.


## 🛠️ Tech Stack

* **Backend:** Python 3.12 with Flask
* **AI Model:** Google Gemini 2.5 Pro API
* **Frontend:** HTML, CSS, Vanilla JavaScript

## 🚀 Setup and Installation

Follow these steps to get the application running locally on your machine.

### 1. Prerequisites

* Python 3.12 or higher
* A Google Gemini API Key

### 2. Clone the Repository

```bash
git clone https://github.com/ChiragAJain/Placement-Assistant
cd Placement-Assistant
```

### 3. Set Up Environment Variables

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

**Note:** `.env` is in `.gitignore` and will not be committed. Keep your API key safe!
