# AI Web Search Agent

A Flask-based web application that allows users to perform bulk web searches and extract relevant information using AI. The application supports multiple search APIs and AI-powered information extraction.

### You can find the link to the Loom Video here: [loom.com](https://www.loom.com/share/e80f8b46da7f4badb7cc0ed5cce402f6?sid=89232b8b-6014-4af1-99c8-6ae3783f11d4)
 - It shows the usage and results of a basic web search

## Features

- **File Upload**: 
  - Support for CSV and Excel files (.csv, .xls, .xlsx)
  - Automatic file type detection and validation
  - Clean data display in tabular format

- **Search API Options**:
  - Google SERP API (requires API key)
  - DuckDuckGo API (free, unlimited usage)

- **AI-Powered Extraction**:
  - Uses Grok AI for intelligent information extraction
  - Supports template-based prompts with variable substitution
  - Generates structured JSON responses and summaries

- **Results Management**:
  - Display results alongside original data
  - Download results as CSV
  - Clean formatting and presentation

## Setup Instructions

1. **Create Virtual Environment**:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure API Keys**:
- Get SERP API key from [SerpApi](https://serpapi.com/)
- Get Grok AI API key from [x.ai](https://x.ai/)

## Running the Application

1. **Start the Flask Server**:
```bash
python app.py
```

2. **Access the Web Interface**:
- Open browser and navigate to `http://127.0.0.1:5555`

## Usage Guide

1. **Upload Data File**:
- Click "Choose File" and select your CSV/Excel file
- Click "Upload" to load the data

2. **Configure Search**:
- Select search API (SERP or DuckDuckGo)
- Enter API keys if using SERP API
- Enter your prompt template (e.g., "find offices for {company} in India")

3. **Process Results**:
- Click "Submit" to start processing
- View results in the right panel
- Download results using the "Download Results" button

## Requirements

- Python 3.8+
- See requirements.txt for package dependencies

## Notes

- SERP API has usage limits
- DuckDuckGo API is free but may have rate limiting
- Large files may take longer to process
- Ensure proper internet connectivity for API calls