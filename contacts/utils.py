import pandas as pd
import requests
import csv
import time
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup

def process_linkedin_html(html_file_path):
    apollo_api_key = "jySvIbIbWEmF5AwKwNoAJg"  # Your Apollo API key

    # Function to clean a name
    def clean_name(name):
        unwanted_words = ["MBA", "CFA"]
        for word in unwanted_words:
            name = name.replace(word, "").strip()
        return name

    # Function to split the name into first and last names
    def split_name(name):
        parts = name.split()
        first_name = parts[0]
        last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
        return first_name, last_name

    # Load the HTML file
    with open(html_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(content, 'lxml')

    # Function to extract contact information
    def extract_contact_info(person):
        name_tag = person.find('div', class_='org-people-profile-card__profile-title')
        if not name_tag:
            return None

        name = name_tag.text.strip()
        name = clean_name(name)
        first_name, last_name = split_name(name)

        title_tag = person.find('div', class_='artdeco-entity-lockup__subtitle')
        title = title_tag.text.strip() if title_tag else 'N/A'

        profile_url_tag = person.find('a', class_='app-aware-link')
        profile_url = profile_url_tag['href'].split('?')[0] if profile_url_tag else 'N/A'

        return {
            'first_name': first_name,
            'last_name': last_name,
            'title': title,
            'linkedin_url': profile_url
        }

    # Find all the contact blocks
    contacts = soup.find_all('div', class_='artdeco-entity-lockup__content')

    # Extract information for each contact
    contact_list = []
    for contact in contacts:
        info = extract_contact_info(contact)
        if info:
            contact_list.append(info)

    # Save the collected information to a CSV file
    csv_file = 'Contacts.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['first_name', 'last_name', 'title', 'linkedin_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(contact_list)

    # Prepare Apollo input
    url = "https://api.apollo.io/api/v1/people/bulk_match"
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
        'X-Api-Key': apollo_api_key
    }

    # Setup session with retries
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    # Initialize the list to collect all matches
    all_matches = []

    # Process contacts in batches of 10 with rate limiting
    batch_size = 10
    max_batches_per_minute = 20
    requests_count = 0

    for i in range(0, len(contact_list), batch_size):
        batch = contact_list[i:i + batch_size]
        apollo_input = [{'first_name': contact['first_name'], 'last_name': contact['last_name'], 'linkedin_url': contact['linkedin_url']} for contact in batch]

        data = {
            "reveal_personal_emails": True,
            "details": apollo_input
        }

        try:
            response = session.post(url, headers=headers, json=data)
            requests_count += 1

            if response.status_code == 200:
                JSON_result = response.json()
                matches = JSON_result.get('matches', [])
                valid_matches = [match for match in matches if match is not None]
                all_matches.extend(valid_matches)
            else:
                print(f"Request failed with status code {response.status_code}")
                print(response.text)
        except requests.ConnectionError as e:
            print(f"Connection error: {e}")
        except requests.Timeout as e:
            print(f"Timeout error: {e}")
        except requests.RequestException as e:
            print(f"General error: {e}")

        # Pause for 60 seconds after max_batches_per_minute requests
        if requests_count >= max_batches_per_minute:
            print("Reached the maximum number of API calls per minute. Pausing for 60 seconds.")
            time.sleep(60)
            requests_count = 0

    # Save the JSON results directly to the CSV file
    output_csv_file = "Full_contacts.csv"

    # Extract field names from the JSON result dynamically
    fieldnames = set()
    for match in all_matches:
        if match:  # Ensure match is not None
            fieldnames.update(match.keys())

    # Write JSON data to CSV file
    with open(output_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for match in all_matches:
            if match:  # Ensure match is not None
                writer.writerow(match)

    print("CSV file generated successfully.")
    return contact_list, all_matches