import json
import numpy as np
from typing import List, Dict, Any
import re
from pathlib import Path

# Import libraries for parsing different CV file formats
import PyPDF2
import docx
from io import BytesIO

# Import libraries for text similarity matching
# Method 1: TF-IDF for basic keyword matching (fast and simple)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Method 2: Sentence Transformers for advanced semantic matching (more accurate)
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("⚠️  sentence-transformers not installed. Using TF-IDF for matching.")
    print("   To install it, run: pip install sentence-transformers")


class CVOpportunityMatcher:
    """
    A class to match a user's CV against a list of analyzed job or scholarship opportunities.
    It supports both TF-IDF and sentence embedding-based similarity calculations.
    """
    def __init__(self, opportunities_file='analyzed_opportunities.json', use_embeddings=True):
        """
        Initializes the matcher.

        Args:
            opportunities_file (str): Path to the JSON file with analyzed opportunities.
            use_embeddings (bool): If True, uses sentence transformers for semantic matching.
                                   If False or not available, falls back to TF-IDF.
        """
        self.opportunities = self.load_opportunities(opportunities_file)
        self.cv_text = ""
        self.cv_profile = {}
        
        self.use_embeddings = use_embeddings and EMBEDDINGS_AVAILABLE
        
        if self.use_embeddings:
            print("🤖 Loading Sentence Transformer model for semantic matching...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')  # A fast and effective model
            print("✓ Model loaded successfully!")
        else:
            print("📊 Using TF-IDF for keyword-based matching.")
            self.vectorizer = TfidfVectorizer(
                max_features=500,
                stop_words='english',
                ngram_range=(1, 2)
            )
    
    def load_opportunities(self, filename):
        """
        Loads the analyzed opportunities from a JSON file.
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✓ Loaded {len(data)} opportunities from {filename}")
            return data
        except FileNotFoundError:
            print(f"Error: {filename} not found.")
            return []
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Extracts all text from a PDF file.
        """
        try:
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error reading PDF file: {e}")
            return ""
    
    def extract_text_from_docx(self, docx_path):
        """
        Extracts all text from a DOCX file.
        """
        try:
            doc = docx.Document(docx_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            print(f"Error reading DOCX file: {e}")
            return ""
    
    def load_cv(self, cv_path):
        """
        Loads and extracts text from a CV file (supports PDF, DOCX, TXT).
        """
        print(f"\n📄 Loading CV from: {cv_path}")
        
        path = Path(cv_path)
        
        if not path.exists():
            print(f"❌ File not found: {cv_path}")
            return False
        
        if path.suffix.lower() == '.pdf':
            self.cv_text = self.extract_text_from_pdf(cv_path)
        elif path.suffix.lower() in ['.docx', '.doc']:
            self.cv_text = self.extract_text_from_docx(cv_path)
        elif path.suffix.lower() == '.txt':
            with open(cv_path, 'r', encoding='utf-8') as f:
                self.cv_text = f.read()
        else:
            print(f"❌ Unsupported file format: {path.suffix}")
            return False
        
        if self.cv_text:
            print(f"✓ Extracted {len(self.cv_text)} characters from your CV.")
            self.analyze_cv()
            return True
        else:
            print("❌ Could not extract any text from the CV.")
            return False
    
    def analyze_cv(self):
        """
        Analyzes the extracted CV text to build a profile of skills, education, etc.
        """
        print("\n🔍 Analyzing your CV to build a profile...")
        
        self.cv_profile = {
            'skills': self.extract_skills(self.cv_text),
            'education': self.extract_education(self.cv_text),
            'experience': self.extract_experience(self.cv_text),
            'languages': self.extract_languages(self.cv_text),
            'keywords': self.extract_keywords(self.cv_text)
        }
        
        print(f"   ✓ Identified {len(self.cv_profile['skills'])} unique skills.")
        print(f"   ✓ Found {len(self.cv_profile['education'])} education entries.")
        print(f"   ✓ Detected {len(self.cv_profile['languages'])} languages.")
    
    def extract_skills(self, text):
        """
        Extracts technical and professional skills from the CV text.
        """
        skill_patterns = [
            r'\b(?:Python|Java|C\+\+|JavaScript|TypeScript|React|Node\.js|Django|Flask)\b',
            r'\b(?:Machine Learning|Deep Learning|AI|Data Science|Big Data)\b',
            r'\b(?:SQL|MongoDB|PostgreSQL|MySQL|NoSQL)\b',
            r'\b(?:AWS|Azure|GCP|Docker|Kubernetes|Git)\b',
            r'\b(?:TensorFlow|PyTorch|Scikit-learn|Pandas|NumPy)\b',
            r'\b(?:HTML|CSS|REST API|GraphQL|Microservices)\b',
        ]
        
        skills = []
        for pattern in skill_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            skills.extend([match.group(0) for match in matches])
        
        return list(set(skills))
    
    def extract_education(self, text):
        """
        Extracts education history (degrees) from the CV text.
        """
        degree_patterns = [
            r'(?:Bachelor|Licence|BSc|B\.Sc)[^\n]{0,100}',
            r'(?:Master|MSc|M\.Sc|MBA)[^\n]{0,100}',
            r'(?:PhD|Doctorat|Doctorate)[^\n]{0,100}',
        ]
        
        education = []
        for pattern in degree_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            education.extend([match.group(0).strip() for match in matches])
        
        return education
    
    def extract_experience(self, text):
        """
        Extracts work experience (job titles) from the CV text.
        """
        exp_patterns = [
            r'(?:Developer|Engineer|Scientist|Analyst|Manager|Consultant)[^\n]{0,100}',
            r'(?:Intern|Stage|Internship)[^\n]{0,100}',
        ]
        
        experience = []
        for pattern in exp_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            experience.extend([match.group(0).strip() for match in matches])
        
        return experience[:10]
    
    def extract_languages(self, text):
        """
        Extracts spoken languages from the CV text.
        """
        lang_patterns = [
            r'\b(?:English|French|Français|Spanish|German|Arabic|Arabe|Italian|Chinese)\b',
        ]
        
        languages = []
        for pattern in lang_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            languages.extend([match.group(0) for match in matches])
        
        return list(set(languages))
    
    def extract_keywords(self, text):
        """
        Extracts the most frequent and relevant keywords from the CV text.
        """
        words = re.findall(r'\b[A-Za-z]{4,}\b', text.lower())
        stop_words = {'with', 'from', 'have', 'this', 'that', 'were', 'been', 'have'}
        keywords = [w for w in words if w not in stop_words]
        
        from collections import Counter
        return [word for word, count in Counter(keywords).most_common(50)]
    
    def get_opportunity_text(self, opportunity):
        """
        Combines all relevant fields of an opportunity into a single string for matching.
        """
        parts = [
            opportunity.get('title', ''),
            opportunity.get('subtitle', ''),
            opportunity.get('description', ''),
            ' '.join(opportunity.get('fields_of_study', [])),
            ' '.join(opportunity.get('level', [])),
            ' '.join(opportunity.get('requirements', [])),
        ]
        return ' '.join(filter(None, parts))
    
    def calculate_similarity_tfidf(self, cv_text, opportunities):
        """
        Calculates similarity scores using the TF-IDF method.
        """
        print("\n📊 Calculating keyword-based similarities (TF-IDF)...")
        
        opp_texts = [self.get_opportunity_text(opp) for opp in opportunities]
        all_docs = [cv_text] + opp_texts
        
        tfidf_matrix = self.vectorizer.fit_transform(all_docs)
        
        cv_vector = tfidf_matrix[0:1]
        opp_vectors = tfidf_matrix[1:]
        
        similarities = cosine_similarity(cv_vector, opp_vectors)[0]
        
        return similarities
    
    def calculate_similarity_embeddings(self, cv_text, opportunities):
        """
        Calculates similarity scores using sentence embeddings for semantic understanding.
        """
        print("\n🤖 Calculating semantic similarities with embeddings...")
        
        opp_texts = [self.get_opportunity_text(opp) for opp in opportunities]
        
        print("   Encoding your CV...")
        cv_embedding = self.model.encode([cv_text])[0]
        
        print(f"   Encoding {len(opp_texts)} opportunities...")
        opp_embeddings = self.model.encode(opp_texts, show_progress_bar=True)
        
        similarities = cosine_similarity([cv_embedding], opp_embeddings)[0]
        
        return similarities
    
    def match_opportunities(self):
        """
        Orchestrates the matching process between the loaded CV and opportunities.
        """
        if not self.cv_text:
            print("❌ Please load a CV first using the load_cv() method.")
            return []
        
        print("\n" + "=" * 70)
        print("🎯 MATCHING YOUR CV WITH OPPORTUNITIES")
        print("=" * 70)
        
        if self.use_embeddings:
            similarities = self.calculate_similarity_embeddings(self.cv_text, self.opportunities)
        else:
            similarities = self.calculate_similarity_tfidf(self.cv_text, self.opportunities)
        
        matched = []
        for i, opp in enumerate(self.opportunities):
            opp_copy = opp.copy()
            opp_copy['similarity_score'] = similarities[i].item()
            opp_copy['similarity_percentage'] = round(similarities[i].item() * 100, 2)
            matched.append(opp_copy)
        
        matched.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        print(f"✓ Calculated similarity scores for {len(matched)} opportunities.")
        
        return matched
    
    def print_top_matches(self, matched_opportunities, top_n=10):
        """
        Prints a summary of the top N matched opportunities.
        """
        print("\n" + "=" * 70)
        print(f"🏆 TOP {min(top_n, len(matched_opportunities))} MATCHES FOR YOUR CV")
        print("=" * 70)
        
        for i, opp in enumerate(matched_opportunities[:top_n], 1):
            print(f"\n{i}. {opp['title']}")
            print(f"   {'─' * 66}")
            print(f"   🎯 Match Score: {opp['similarity_percentage']}%")
            print(f"   🎓 Level: {', '.join(opp.get('level', ['Not specified']))}")
            print(f"   📚 Fields: {', '.join(opp.get('fields_of_study', ['Not specified'])[:3])}")
            print(f"   ⏱️  Duration: {opp.get('duration', 'Not specified')}")
            print(f"   📅 Period: {opp.get('period', 'Not specified')}")
            print(f"   🔗 URL: {opp.get('url', '')}")
            
            if self.cv_profile.get('skills'):
                matching_skills = []
                opp_text = self.get_opportunity_text(opp).lower()
                for skill in self.cv_profile['skills']:
                    if skill.lower() in opp_text:
                        matching_skills.append(skill)
                
                if matching_skills:
                    print(f"   ✓ Matching Skills: {', '.join(matching_skills[:5])}")
    
    def save_results(self, matched_opportunities, filename='cv_matched_opportunities.json'):
        """
        Saves the list of matched opportunities to a JSON file.
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(matched_opportunities, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Results saved to {filename}")
    
    def generate_cv_summary(self):
        """
        Generates and prints a summary of the analyzed CV profile.
        """
        print("\n" + "=" * 70)
        print("📋 YOUR CV SUMMARY")
        print("=" * 70)
        
        print(f"\n🎓 Education:")
        for edu in self.cv_profile.get('education', [])[:3]:
            print(f"   • {edu}")
        
        print(f"\n💼 Top Skills:")
        for skill in self.cv_profile.get('skills', [])[:10]:
            print(f"   • {skill}")
        
        print(f"\n🌍 Languages:")
        for lang in self.cv_profile.get('languages', []):
            print(f"   • {lang}")
        
        print(f"\n📊 CV Statistics:")
        print(f"   • Total length: {len(self.cv_text)} characters")
        print(f"   • Skills found: {len(self.cv_profile.get('skills', []))}")
        print(f"   • Experience entries: {len(self.cv_profile.get('experience', []))}")


# Main execution block
if __name__ == "__main__":
    # Initialize the matcher
    matcher = CVOpportunityMatcher(
        opportunities_file='analyzed_opportunities.json',
        use_embeddings=True  # Set to False to use the simpler TF-IDF method
    )
    
    # --- IMPORTANT ---
    # Change this to the path of your CV file
    cv_path = "CV_Yassmine_Fki.pdf" 
    # -----------------
    
    if matcher.load_cv(cv_path):
        # Display a summary of the parsed CV
        matcher.generate_cv_summary()
        
        # Run the matching process
        matched = matcher.match_opportunities()
        
        # Print the top N best matches
        matcher.print_top_matches(matched, top_n=15)
        
        # Save the full list of matches to a file
        matcher.save_results(matched)
        
        print("\n" + "=" * 70)
        print("✅ MATCHING COMPLETE")
        print("=" * 70)
        print(f"📁 Results have been saved to cv_matched_opportunities.json")
        if matched:
            print(f"🎯 The top match for your CV is: '{matched[0]['title']}' with a {matched[0]['similarity_percentage']}% score.")
    else:
        print("\n❌ Failed to load and process the CV. Please check the file path and format.")