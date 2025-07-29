# Jobby - AI-Powered Job Hunting Assistant

An intelligent job hunting assistant that utilizes AI to help you find opportunities, create customized CVs, and generate personalized motivational letters.

## 🚀 Features

- **AI-Powered Job Search**: Uses Gemini API to analyze job descriptions and match them with your profile
- **Automated Job Scraping**: Selenium-based web scraping to gather job opportunities from multiple platforms
- **Customized CV Generation**: AI-driven CV creation tailored to specific job requirements
- **Motivational Letter Creator**: Personalized cover letters generated using AI 
- **Interactive Web Interface**: User-friendly Streamlit frontend for easy interaction

## 🛠️ Tech Stack

### Document and Web Parsing
python-docx>=0.8.11
PyPDF2>=3.0.0
googlesearch-python>=1.2.3
requests>=2.31.0
beautifulsoup4>=4.12.0

### Backend
selenium>=4.14.0         
google-generativeai>=0.3.2  


### Frontend
- **Streamlit**: Modern web application framework for Python
- **HTML/CSS**: Custom styling and layout

## 📋 Prerequisites

Before running this project, make sure you have:

- Python 3.8 or higher installed
- Google Gemini API key
- Chrome/Chromium browser (for Selenium)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/jobby.git
   cd jobby
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## 📦 Project Structure

## 🎯 Usage

### Starting the Application

1. **Activate your virtual environment**
   ```bash
   # Windows
   venv\Scripts\activate
   ```

2. **Run the Streamlit app**
   ```bash
   streamlit run app/main.py
   ```

3. **Open your browser**
   Navigate to `http://localhost:8501`

