import json

# This script performs a simple analysis of the scraped opportunities
# to count how many are relevant to students based on a list of keywords.

# Load the scraped opportunities from the JSON file
with open('uss_opportunities.json', 'r', encoding='utf-8') as f:
    opportunities = json.load(f)

print(f"Total opportunities loaded: {len(opportunities)}")

# Define a list of keywords to identify student-related opportunities
student_keywords = [
    'student', 'étudiant', 'étudiante', 'undergraduate', 'graduate',
    'master', 'doctorat', 'phd', 'licence', 'bachelor', 'élève',
    'academic', 'université', 'university', 'scholarship', 'bourse',
    'mobility', 'mobilité', 'exchange', 'échange', 'formation',
    'training', 'internship', 'stage'
]

student_count = 0
# Iterate through each opportunity to check for student-related keywords
for opp in opportunities:
    # Combine the text from title, subtitle, and description for a comprehensive search
    description = opp.get('description', '').lower()
    title = opp.get('title', '').lower()
    subtitle = opp.get('subtitle', '').lower()
    text = f"{description} {title} {subtitle}"
    
    # If any of the keywords are found in the text, increment the counter
    if any(keyword in text for keyword in student_keywords):
        student_count += 1

print(f"Number of opportunities identified as relevant for students: {student_count}")
