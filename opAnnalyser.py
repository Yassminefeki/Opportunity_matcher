import json
import re
import requests
import PyPDF2

from io import BytesIO
from typing import List, Dict, Any

class OpportunityAnalyzer:
    """
    A class to analyze scraped opportunities, filter for student-specific ones,
    extract key information from text and PDFs, and match them against a user's profile.
    """
    def __init__(self, opportunities_file='uss_opportunities.json'):
        """
        Initializes the analyzer with a JSON file of scraped opportunities.

        Args:
            opportunities_file (str): The path to the JSON file containing opportunities.
        """
        self.opportunities = self.load_opportunities(opportunities_file)
        self.student_opportunities = []
        self.analyzed_opportunities = []
        
    def load_opportunities(self, filename):
        """
        Loads opportunities from a specified JSON file.

        Args:
            filename (str): The name of the JSON file.

        Returns:
            list: A list of opportunities, or an empty list if loading fails.
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✓ Loaded {len(data)} opportunities from {filename}")
            return data
        except FileNotFoundError:
            print(f"Error: File {filename} not found")
            return []
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {filename}")
            return []
    
    def is_student_opportunity(self, description, title, subtitle):
        """
        Determines if an opportunity is relevant to students based on keywords.

        Args:
            description (str): The description of the opportunity.
            title (str): The title of the opportunity.
            subtitle (str): The subtitle of the opportunity.

        Returns:
            bool: True if the opportunity is likely for students, False otherwise.
        """
        student_keywords = [
            'student', 'étudiant', 'étudiante', 'undergraduate', 'graduate',
            'master', 'doctorat', 'phd', 'licence', 'bachelor', 'élève',
            'academic', 'université', 'university', 'scholarship', 'bourse',
            'mobility', 'mobilité', 'exchange', 'échange', 'formation',
            'training', 'internship', 'stage'
        ]
        
        text = f"{description} {title} {subtitle}".lower()
        return any(keyword in text for keyword in student_keywords)
    
    def filter_student_opportunities(self):
        """
        Filters the loaded opportunities to find those relevant to students.
        """
        print("\n" + "=" * 70)
        print("FILTERING STUDENT OPPORTUNITIES")
        print("=" * 70)
        
        self.student_opportunities = []
        
        for opp in self.opportunities:
            if self.is_student_opportunity(
                opp.get('description', ''), 
                opp.get('title', ''), 
                opp.get('subtitle', '')
            ):
                self.student_opportunities.append(opp)
                print(f"✓ Student opportunity: {opp.get('title', 'Untitled')}")
        
        print(f"\n📊 Found {len(self.student_opportunities)} student opportunities")
        print(f"   out of {len(self.opportunities)} total opportunities")
        
        return self.student_opportunities
    
    def extract_pdf_text(self, pdf_url):
        """
        Downloads a PDF from a URL and extracts its text content.

        Args:
            pdf_url (str): The URL of the PDF file.

        Returns:
            str: The extracted text from the PDF, or an empty string if extraction fails.
        """
        try:
            print(f"      📄 Downloading PDF...")
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            pdf_file = BytesIO(response.content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text += page.extract_text() + "\n"
            
            print(f"      ✓ Extracted {len(text)} characters from {len(pdf_reader.pages)} pages")
            return text
        except Exception as e:
            print(f"      ✗ Error extracting PDF: {e}")
            return ""
    
    def extract_fields_of_study(self, text):
        """
        Extracts potential fields of study from a given text using keywords and patterns.

        Args:
            text (str): The text to analyze.

        Returns:
            list: A list of unique fields of study found in the text.
        """
        fields = set()
        
        # A predefined list of common academic fields
        field_keywords = [
            'engineering', 'ingénierie', 'computer science', 'informatique',
            'medicine', 'médecine', 'business', 'management', 'économie', 'economics',
            'law', 'droit', 'mathematics', 'mathématiques', 'physics', 'physique',
            'chemistry', 'chimie', 'biology', 'biologie', 'architecture',
            'arts', 'humanities', 'sciences sociales', 'social sciences',
            'psychology', 'psychologie', 'education', 'éducation',
            'environmental', 'environnement', 'agriculture', 'agronomie',
            'data science', 'artificial intelligence', 'intelligence artificielle',
            'cybersecurity', 'cybersécurité', 'finance', 'accounting', 'comptabilité',
            'marketing', 'communication', 'journalism', 'journalisme',
            'nursing', 'soins infirmiers', 'pharmacy', 'pharmacie'
        ]
        
        text_lower = text.lower()
        
        for field in field_keywords:
            if field in text_lower:
                fields.add(field.title())
        
        # Regular expression patterns for more specific extraction
        patterns = [
            r'(?:field|domain|domaine|spécialit|area)[s]?[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'(?:study|études|filière)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                field = match.group(1).strip()
                if 3 < len(field) < 50:
                    fields.add(field)
        
        return list(fields)
    
    def extract_duration(self, text):
        """
        Extracts the duration of the opportunity from the text.

        Args:
            text (str): The text to analyze.

        Returns:
            str: The extracted duration or "Not specified".
        """
        duration_patterns = [
            r'(\d+)\s*(?:mois|months?)',
            r'(\d+)\s*(?:ans?|years?)',
            r'(\d+)\s*(?:semaines?|weeks?)',
            r'(?:duration|durée)[:\s]*([^\n.]{1,100})',
            r'(?:for|pendant)[:\s]+(\d+\s*(?:months?|years?|mois|ans?))',
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        return "Not specified"
    
    def extract_period(self, text):
        """
        Extracts the application period or deadline from the text.

        Args:
            text (str): The text to analyze.

        Returns:
            str: The extracted period or "Not specified".
        """
        period_patterns = [
            r'(?:deadline|date limite|application deadline)[:\s]*([^\n.]{1,100})',
            r'(?:period|période|dates?)[:\s]*([^\n.]{1,100})',
            r'(?:from|du|de)\s+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}',
            r'(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{1,2},?\s+\d{4}',
            r'(?:until|jusqu|avant|before)[:\s]+([^\n.]{1,80})',
        ]
        
        for pattern in period_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        return "Not specified"
    
    def extract_level(self, text):
        """
        Extracts the academic level (e.g., Bachelor, Master, PhD) from the text.

        Args:
            text (str): The text to analyze.

        Returns:
            list: A list of academic levels or ["All levels"] if none are specified.
        """
        levels = []
        
        level_keywords = {
            'Bachelor': ['bachelor', 'licence', 'undergraduate', 'L3', 'first degree', 'bac+3'],
            'Master': ['master', 'graduate', 'M1', 'M2', 'postgraduate', 'bac+5'],
            'PhD': ['phd', 'doctorat', 'doctoral', 'doctorate', 'ph.d', 'bac+8', 'third cycle']
        }
        
        text_lower = text.lower()
        
        for level, keywords in level_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                levels.append(level)
        
        return levels if levels else ["All levels"]
    
    def extract_requirements(self, text):
        """
        Extracts application requirements from the text.

        Args:
            text (str): The text to analyze.

        Returns:
            list: A list of extracted requirements.
        """
        requirements = []
        
        req_patterns = [
            r'(?:requirements?|required|requise?|conditions?)[:\s]*([^\n.]{10,200})',
            r'(?:eligibility|éligibilité|eligible)[:\s]*([^\n.]{10,200})',
            r'(?:must have|doit avoir|must be|doit être)[:\s]*([^\n.]{10,200})',
            r'(?:criteria|critères)[:\s]*([^\n.]{10,200})',
        ]
        
        seen = set()
        for pattern in req_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                req = match.group(0).strip()
                if req.lower() not in seen and len(req) > 15:
                    requirements.append(req)
                    seen.add(req.lower())
        
        return requirements[:10]  # Limit to the top 10 requirements
    
    def analyze_opportunity(self, opportunity):
        """
        Performs a comprehensive analysis of a single opportunity.

        Args:
            opportunity (dict): The opportunity to analyze.

        Returns:
            dict: A dictionary with the extracted and analyzed information.
        """
        print(f"\n📋 Analyzing: {opportunity.get('title', 'Untitled')}")
        
        analysis = {
            'title': opportunity.get('title', ''),
            'subtitle': opportunity.get('subtitle', ''),
            'url': opportunity.get('url', ''),
            'description': opportunity.get('description', ''),
            'fields_of_study': [],
            'duration': '',
            'period': '',
            'level': [],
            'requirements': [],
            'attachments': opportunity.get('attachments', []),
            'pdf_analysis': []
        }
        
        # Combine text from all available sources
        all_text = f"{opportunity.get('description', '')}\n{opportunity.get('title', '')}\n{opportunity.get('subtitle', '')}\n"
        
        # Analyze text from any PDF attachments
        for attachment in opportunity.get('attachments', []):
            if '.pdf' in attachment['url'].lower():
                print(f"   📎 Analyzing attachment: {attachment['name']}")
                pdf_text = self.extract_pdf_text(attachment['url'])
                
                if pdf_text:
                    analysis['pdf_analysis'].append({
                        'name': attachment['name'],
                        'url': attachment['url'],
                        'text_length': len(pdf_text)
                    })
                    all_text += f"\n{pdf_text}"
        
        # Extract structured information from the combined text
        analysis['fields_of_study'] = self.extract_fields_of_study(all_text)
        analysis['duration'] = self.extract_duration(all_text)
        analysis['period'] = self.extract_period(all_text)
        analysis['level'] = self.extract_level(all_text)
        analysis['requirements'] = self.extract_requirements(all_text)
        
        print(f"   ✓ Fields: {', '.join(analysis['fields_of_study']) if analysis['fields_of_study'] else 'None found'}")
        print(f"   ✓ Level: {', '.join(analysis['level'])}")
        print(f"   ✓ Duration: {analysis['duration']}")
        print(f"   ✓ Period: {analysis['period']}")
        
        return analysis
    
    def analyze_all_student_opportunities(self):
        """
        Analyzes all the opportunities that have been filtered for students.
        """
        print("\n" + "=" * 70)
        print("ANALYZING STUDENT OPPORTUNITIES")
        print("=" * 70)
        
        self.analyzed_opportunities = []
        
        for i, opp in enumerate(self.student_opportunities, 1):
            print(f"\n[{i}/{len(self.student_opportunities)}]")
            try:
                analysis = self.analyze_opportunity(opp)
                self.analyzed_opportunities.append(analysis)
            except Exception as e:
                print(f"   ✗ Error analyzing opportunity: {e}")
        
        print(f"\n✓ Successfully analyzed {len(self.analyzed_opportunities)} opportunities")
        return self.analyzed_opportunities
    
    def match_with_profile(self, user_profile):
        """
        Matches the analyzed opportunities against a user's profile.

        Args:
            user_profile (dict): A dictionary representing the user's academic profile.

        Returns:
            list: A sorted list of matched opportunities with scores and reasons.
        """
        print("\n" + "=" * 70)
        print("MATCHING OPPORTUNITIES WITH YOUR PROFILE")
        print("=" * 70)
        print(f"Your Profile:")
        print(f"  Level: {user_profile.get('level', 'Not specified')}")
        print(f"  Fields: {', '.join(user_profile.get('fields', []))}")
        print()
        
        matched = []
        
        for opp in self.analyzed_opportunities:
            score = 0
            reasons = []
            
            # Match by academic level
            user_level = user_profile.get('level', '')
            if user_level in opp['level']:
                score += 5
                reasons.append(f"✓ Level match: {user_level}")
            elif "All levels" in opp['level']:
                score += 2
                reasons.append("✓ Open to all levels")
            
            # Match by fields of study
            user_fields = [f.lower() for f in user_profile.get('fields', [])]
            opp_fields = [f.lower() for f in opp['fields_of_study']]
            
            field_matches = 0
            for user_field in user_fields:
                for opp_field in opp_fields:
                    if user_field in opp_field or opp_field in user_field:
                        score += 3
                        field_matches += 1
                        reasons.append(f"✓ Field match: {opp_field.title()}")
                        break
            
            if field_matches > 1:
                score += 2
                reasons.append(f"✓ Multiple field matches ({field_matches})")
            
            if score > 0:
                opp['match_score'] = score
                opp['match_reasons'] = reasons
                matched.append(opp)
                print(f"✓ Match found: {opp['title']} (Score: {score})")
        
        # Sort matches by score in descending order
        matched.sort(key=lambda x: x['match_score'], reverse=True)
        
        print(f"\n📊 Found {len(matched)} matching opportunities")
        return matched
    
    def save_results(self, data, filename):
        """
        Saves a list of dictionaries to a JSON file.

        Args:
            data (list): The data to save.
            filename (str): The name of the file to save to.
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 Saved to {filename}")
    
    def print_top_matches(self, matched_opportunities, top_n=5):
        """
        Prints a summary of the top N matched opportunities.

        Args:
            matched_opportunities (list): The list of matched opportunities.
            top_n (int): The number of top matches to print.
        """
        print("\n" + "=" * 70)
        print(f"🎯 TOP {min(top_n, len(matched_opportunities))} MATCHED OPPORTUNITIES")
        print("=" * 70)
        
        for i, opp in enumerate(matched_opportunities[:top_n], 1):
            print(f"\n{i}. {opp['title']}")
            print(f"   {'─' * 66}")
            print(f"   📊 Match Score: {opp['match_score']}")
            print(f"   🎓 Level: {', '.join(opp['level'])}")
            print(f"   📚 Fields: {', '.join(opp['fields_of_study'][:3]) if opp['fields_of_study'] else 'Not specified'}")
            print(f"   ⏱️  Duration: {opp['duration']}")
            print(f"   📅 Period: {opp['period']}")
            print(f"   🔗 URL: {opp['url']}")
            print(f"\n   Match Reasons:")
            for reason in opp['match_reasons']:
                print(f"      • {reason}")


# Main execution block
if __name__ == "__main__":
    try:
        # Define a user profile for matching
        user_profile = {
            'level': 'Master',
            'fields': [
                'Computer Science',
                'Data Science',
                'Artificial Intelligence',
                'Engineering'
            ]
        }

        # Initialize the analyzer with the scraped data
        analyzer = OpportunityAnalyzer('uss_opportunities.json')

        # Step 1: Filter for student-relevant opportunities
        student_opps = analyzer.filter_student_opportunities()
        analyzer.save_results(student_opps, 'student_opportunities.json')

        # Step 2: Analyze the filtered opportunities
        analyzed = analyzer.analyze_all_student_opportunities()
        analyzer.save_results(analyzed, 'analyzed_opportunities.json')

        # Step 3: Match the analyzed opportunities with the user profile
        matched = analyzer.match_with_profile(user_profile)
        analyzer.save_results(matched, 'matched_opportunities.json')

        # Step 4: Display a summary of the top matches
        analyzer.print_top_matches(matched, top_n=10)

        print("\n" + "=" * 70)
        print("✅ PROCESS COMPLETE")
        print("=" * 70)
        print(f"📁 Files created:")
        print(f"   • student_opportunities.json - All student opportunities")
        print(f"   • analyzed_opportunities.json - With extracted requirements")
        print(f"   • matched_opportunities.json - Matched with your profile")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
