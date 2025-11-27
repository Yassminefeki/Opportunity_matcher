# Opportunity Matcher

A comprehensive system for scraping, analyzing, and matching academic opportunities (scholarships, internships, exchanges) with student profiles based on their CVs.

## Overview

This project automates the process of finding relevant academic opportunities for students by:

1. **Scraping** opportunity data from university websites
2. **Analyzing** opportunities to extract key information (level, fields, requirements, etc.)
3. **Matching** student CVs against opportunities using advanced similarity algorithms

## Features

### 🔍 Web Scraping (`scraper.py`)
- Scrapes scholarship and opportunity information from Université de Sousse (USS) website
- Handles pagination and extracts detailed opportunity information
- Downloads and processes PDF attachments
- Saves data in both JSON and CSV formats
- Avoids duplicates by tracking existing opportunities

### 📊 Opportunity Analysis (`opAnnalyser.py`)
- Filters opportunities relevant to students using keyword detection
- Extracts structured information from opportunity descriptions and PDFs:
  - Academic levels (Bachelor, Master, PhD)
  - Fields of study
  - Duration and application periods
  - Eligibility requirements
- Downloads and analyzes PDF attachments for additional details

### 🎯 CV Matching (`opMatcher.py`)
- Supports CV upload in PDF, DOCX, or TXT formats
- Extracts skills, education, experience, and languages from CVs
- Uses advanced similarity matching:
  - TF-IDF for keyword-based matching
  - Sentence Transformers for semantic understanding (if available)
- Calculates match scores and provides detailed explanations
- Ranks opportunities by relevance to the user's profile

### 🧪 Testing (`tests/`)
- Unit tests for core functionality
- Test coverage for scraper, analyzer, and matcher components

## Project Structure

```
├── scraper.py              # Web scraping functionality
├── opAnnalyser.py          # Opportunity analysis and filtering
├── opMatcher.py            # CV matching with opportunities
├── test_analyzer.py        # Additional analysis utilities
├── tests/                  # Unit tests
│   ├── test_opAnnalyser.py
│   ├── test_opMatcher.py
│   └── test_scraper.py
├── analyzed_opportunities.json    # Processed opportunity data
├── student_opportunities.json     # Filtered student opportunities
├── cv_matched_opportunities.json  # Matched results for CV
├── uss_opportunities.json         # Raw scraped data
└── uss_opportunities.csv          # CSV export of opportunities
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Yassminefeki/Opportunity_matcher.git
cd Opportunity_matcher
```

2. Install required Python packages:
```bash
pip install requests beautifulsoup4 scikit-learn sentence-transformers PyPDF2 python-docx
```

## Usage

### 1. Scrape Opportunities
```bash
python scraper.py
```
This will scrape the latest opportunities from USS website and save them to `uss_opportunities.json`.

### 2. Analyze Opportunities
```bash
python opAnnalyser.py
```
Filters and analyzes opportunities, extracting structured information and saving to `analyzed_opportunities.json`.

### 3. Match with CV
```bash
python opMatcher.py
```
Loads a CV (default: `CV_Yassmine_Fki.pdf`) and matches it against analyzed opportunities, saving results to `cv_matched_opportunities.json`.

## Data Flow

1. **Scraping**: Raw HTML → Structured JSON with attachments
2. **Analysis**: JSON opportunities → Filtered student opportunities → Extracted metadata
3. **Matching**: CV text → Profile extraction → Similarity scoring → Ranked matches

## Technologies Used

- **Python** - Core programming language
- **BeautifulSoup** - HTML parsing and web scraping
- **Requests** - HTTP requests
- **PyPDF2** - PDF text extraction
- **scikit-learn** - TF-IDF vectorization and cosine similarity
- **Sentence Transformers** - Advanced semantic matching
- **python-docx** - DOCX file processing

## Future Development Plans

### 🚀 Frontend Development
- **Web Application**: Build a user-friendly web interface where students can:
  - Upload their CV (PDF/DOCX)
  - View matched opportunities with scores and explanations
  - Filter results by academic level, field, duration
  - Save favorite opportunities
  - Get personalized recommendations

- **Technologies**: React.js or Vue.js for frontend, with responsive design for mobile access

### 🗄️ Database Integration
- **Data Storage**: Implement a database to store:
  - Scraped opportunities with metadata
  - User profiles and CV data
  - Match history and user preferences
  - Analytics on opportunity popularity

- **Technologies**: PostgreSQL or MongoDB for data persistence, with SQLAlchemy or similar ORM

### 🔄 Additional Features
- **Real-time Updates**: Automated scraping with notifications for new opportunities
- **Multi-source Scraping**: Expand to other universities and scholarship platforms
- **Advanced Matching**: Incorporate user preferences, location, and budget constraints
- **API Development**: RESTful API for integration with other educational platforms
- **Machine Learning**: Improve matching accuracy with user feedback and reinforcement learning

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is open source and available under the [MIT License](LICENSE).

## Contact

For questions or collaboration opportunities, please reach out to the project maintainer.
