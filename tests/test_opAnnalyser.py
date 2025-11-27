import unittest
import json
from opAnnalyser import OpportunityAnalyzer

class TestOpportunityAnalyzer(unittest.TestCase):

    def setUp(self):
        # Create a dummy opportunities file for testing
        self.test_opportunities = [
            {
                "title": "PhD Scholarship in AI",
                "description": "An opportunity for graduate students in computer science.",
                "subtitle": "Fully funded PhD",
                "url": "http://test.com/phd"
            },
            {
                "title": "Marketing Internship",
                "description": "A summer internship for undergraduate students.",
                "subtitle": "Internship for students",
                "url": "http://test.com/intern"
            },
            {
                "title": "Senior Developer Position",
                "description": "A full-time job for experienced developers.",
                "subtitle": "Job offer",
                "url": "http://test.com/job"
            }
        ]
        with open('test_opportunities.json', 'w') as f:
            json.dump(self.test_opportunities, f)

        self.analyzer = OpportunityAnalyzer('test_opportunities.json')

    def test_filter_student_opportunities(self):
        student_opps = self.analyzer.filter_student_opportunities()
        self.assertEqual(len(student_opps), 2)
        self.assertEqual(student_opps[0]['title'], "PhD Scholarship in AI")
        self.assertEqual(student_opps[1]['title'], "Marketing Internship")

    def tearDown(self):
        import os
        os.remove('test_opportunities.json')

if __name__ == '__main__':
    unittest.main()
