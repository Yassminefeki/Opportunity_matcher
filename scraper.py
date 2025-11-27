import requests
from bs4 import BeautifulSoup
import json
import time
import os
from urllib.parse import urljoin

class USSOpportunitiesScraper:
    """
    A class to scrape scholarship and opportunity information from the Université de Sousse (USS) website.

    This scraper navigates through the news pages, extracts opportunity details,
    and saves the information to JSON and CSV files. It's designed to be run
    periodically to collect new opportunities without duplicating existing ones.
    """
    def __init__(self):
        """
        Initializes the scraper by setting up URLs, page limits, and loading existing data.
        """
        self.base_url = "https://uss.rnu.tn"
        self.news_url = f"{self.base_url}/news/international"
        self.total_pages = 21  # Total number of pages to scrape
        self.opportunities = []  # List to hold newly scraped opportunities
        self.existing_opportunities = self.load_existing()  # Load already scraped opportunities
        self.existing_urls = {opp['url'] for opp in self.existing_opportunities}  # A set of URLs for quick lookup

    def load_existing(self):
        """
        Loads previously scraped opportunities from a JSON file to prevent duplicates.

        Returns:
            list: A list of dictionaries, where each dictionary represents an opportunity.
                  Returns an empty list if the file doesn't exist or is empty.
        """
        if os.path.exists('uss_opportunities.json'):
            try:
                with open('uss_opportunities.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("Warning: Could not load existing JSON file. Starting fresh.")
                return []
        return []
        
    def get_page(self, url, retries=3):
        """
        Fetches the content of a URL with a specified number of retries in case of failure.

        Args:
            url (str): The URL to fetch.
            retries (int): The number of times to retry fetching the URL.

        Returns:
            requests.Response: The response object if the request is successful, otherwise None.
        """
        for attempt in range(retries):
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()  # Raise an exception for bad status codes
                return response
            except requests.RequestException as e:
                print(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(2)  # Wait before retrying
                else:
                    return None
    
    def scrape_opportunity_details(self, opportunity_url):
        """
        Scrapes detailed information from a single opportunity page.

        Args:
            opportunity_url (str): The URL of the opportunity detail page.

        Returns:
            dict: A dictionary containing the scraped details (title, subtitle, description, attachments),
                  or None if scraping fails.
        """
        print(f"  Scraping details from: {opportunity_url}")
        
        response = self.get_page(opportunity_url)
        if not response:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        details = {
            'url': opportunity_url,
            'title': '',
            'subtitle': '',
            'description': '',
            'attachments': []
        }
        
        # Extract the main title
        title_elem = soup.find('span', class_='top-title')
        if title_elem:
            details['title'] = title_elem.get_text(strip=True)
        
        # Extract the subtitle (usually in an h2 tag)
        h2_elem = soup.find('h2')
        if h2_elem:
            details['subtitle'] = h2_elem.get_text(strip=True)
        
        # Find the description section and extract its content
        desc_h3 = soup.find('h3', string=lambda text: text and 'Description' in text)
        if desc_h3:
            description_parts = []
            for sibling in desc_h3.find_next_siblings():
                if sibling.name == 'h3':  # Stop if another section starts
                    break
                text = sibling.get_text(strip=True)
                if text:
                    description_parts.append(text)
            details['description'] = ' '.join(description_parts)
        
        # Find and collect links to attachments (PDF, DOC, etc.)
        attachment_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx']
        
        for elem in soup.find_all(['a', 'div']):
            # Check for attachment links in 'href' attributes
            if elem.name == 'a' and elem.get('href'):
                href = elem.get('href')
                if any(ext in href.lower() for ext in attachment_extensions):
                    full_url = urljoin(self.base_url, href)
                    attachment_name = elem.get_text(strip=True) or os.path.basename(href)
                    details['attachments'].append({
                        'name': attachment_name,
                        'url': full_url
                    })
            
            # Check for attachment links in 'data-field-name' attributes
            if elem.get('data-field-name'):
                field_name = elem.get('data-field-name')
                if any(ext in field_name.lower() for ext in attachment_extensions):
                    link = elem.find('a')
                    if link and link.get('href'):
                        full_url = urljoin(self.base_url, link.get('href'))
                        details['attachments'].append({
                            'name': field_name,
                            'url': full_url
                        })
        
        return details
    
    def scrape_page(self, page_num):
        """
        Scrapes all the opportunity links from a given page number.

        Args:
            page_num (int): The page number to scrape.
        """
        url = f"{self.news_url}?page={page_num}"
        print(f"\nScraping page {page_num}: {url}")
        
        response = self.get_page(url)
        if not response:
            print(f"Failed to fetch page {page_num}")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all containers that hold opportunity links
        containers = soup.find_all('div', class_='col-lg-3 col-sm-6')
        
        print(f"Found {len(containers)} opportunities on page {page_num}")
        
        for idx, container in enumerate(containers, 1):
            link = container.find('a', href=True)

            if link:
                opportunity_url = urljoin(self.base_url, link['href'])

                # Scrape only if it's a new opportunity and a valid details page
                if 'news_details' in opportunity_url and opportunity_url not in self.existing_urls:
                    details = self.scrape_opportunity_details(opportunity_url)

                    if details:
                        self.opportunities.append(details)
                        print(f"    ✓ New opportunity {idx}: {details['title']}")

                    time.sleep(1)  # A small delay to be respectful to the server
                elif 'news_details' in opportunity_url:
                    print(f"    - Already scraped opportunity {idx}: {opportunity_url}")
    
    def scrape_all(self):
        """
        Iterates through all pages and scrapes the opportunities.
        """
        print(f"Starting to scrape {self.total_pages} pages...")
        print("=" * 60)
        
        for page in range(1, self.total_pages + 1):
            self.scrape_page(page)
            time.sleep(2)  # A delay between scraping pages
        
        print("\n" + "=" * 60)
        print(f"Scraping completed! Total new opportunities scraped: {len(self.opportunities)}")
    
    def save_to_json(self, filename='uss_opportunities.json'):
        """
        Saves the scraped opportunities to a JSON file.

        Args:
            filename (str): The name of the JSON file to save to.
        """
        all_opportunities = self.existing_opportunities + self.opportunities
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_opportunities, f, ensure_ascii=False, indent=2)
        print(f"\nData saved to {filename}")
    
    def save_to_csv(self, filename='uss_opportunities.csv'):
        """
        Saves the scraped opportunities to a CSV file.

        Args:
            filename (str): The name of the CSV file to save to.
        """
        import csv

        all_opportunities = self.existing_opportunities + self.opportunities

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if not all_opportunities:
                return

            writer = csv.writer(f)
            writer.writerow(['URL', 'Title', 'Subtitle', 'Description', 'Attachments'])

            for opp in all_opportunities:
                # Format attachments for CSV
                attachments_str = ' | '.join([f"{att['name']}: {att['url']}" for att in opp['attachments']])
                writer.writerow([
                    opp['url'],
                    opp['title'],
                    opp['subtitle'],
                    opp['description'],
                    attachments_str
                ])

        print(f"Data saved to {filename}")


# Main execution block
if __name__ == "__main__":
    scraper = USSOpportunitiesScraper()
    
    # Start the scraping process
    scraper.scrape_all()
    
    # Save the results
    scraper.save_to_json()
    scraper.save_to_csv()
    
    # Display a summary of the scraping session
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"New opportunities scraped: {len(scraper.opportunities)}")
    print(f"Total opportunities in database: {len(scraper.existing_opportunities) + len(scraper.opportunities)}")

    if scraper.opportunities:
        print(f"\nFirst new opportunity example:")
        first = scraper.opportunities[0]
        print(f"  Title: {first['title']}")
        print(f"  Subtitle: {first['subtitle']}")
        print(f"  Description: {first['description'][:100]}...")
        print(f"  Attachments: {len(first['attachments'])}")
        print(f"  URL: {first['url']}")
