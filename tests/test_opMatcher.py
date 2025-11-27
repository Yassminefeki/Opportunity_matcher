import unittest
import json
from opMatcher import CVOpportunityMatcher
import os

class TestCVOpportunityMatcher(unittest.TestCase):

    def setUp(self):
        # Create a dummy opportunities file for testing
        self.test_opportunities = [
            {
                "title": "Software Engineering Intern",
                "description": "Python, Java, SQL",
                "level": ["Bachelor", "Master"],
                "fields_of_study": ["Computer Science"]
            },
            {
                "title": "Data Science Internship",
                "description": "Machine Learning, Python, R",
                "level": ["Master", "PhD"],
                "fields_of_study": ["Data Science", "Computer Science"]
            }
        ]
        with open('test_analyzed_opportunities.json', 'w') as f:
            json.dump(self.test_opportunities, f)

        # Create a dummy CV file
        self.cv_content = """
        John Doe
        Master in Computer Science

        Skills: Python, Machine Learning, Deep Learning
        """
        with open('test_cv.txt', 'w') as f:
            f.write(self.cv_content)

        self.matcher = CVOpportunityMatcher('test_analyzed_opportunities.json', use_embeddings=False)

    def test_cv_loading_and_analysis(self):
        self.assertTrue(self.matcher.load_cv('test_cv.txt'))
        self.assertIn('Python', self.matcher.cv_profile['skills'])
        self.assertIn('Machine Learning', self.matcher.cv_profile['skills'])

    def test_matching(self):
        self.matcher.load_cv('test_cv.txt')
        matched_opps = self.matcher.match_opportunities()
        self.assertEqual(len(matched_opps), 2)
        # The Data Science internship should have a higher score
        self.assertEqual(matched_opps[0]['title'], "Data Science Internship")

    def tearDown(self):
        os.remove('test_analyzed_opportunities.json')
        os.remove('test_cv.txt')

if __name__ == '__main__':
    unittest.main()
