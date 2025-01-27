import requests
from bs4 import BeautifulSoup
import os
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def get_abstract_with_selenium(driver, abstract_url):
    try:
        driver.get(abstract_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        abstract_element = driver.find_element(By.ID, "abstract")
        if not abstract_element.text.strip():
            # Try finding the abstract in another way if the ID method fails
            possible_abstracts = driver.find_elements(By.XPATH, "//*[contains(text(), 'Abstract')]/following-sibling::*")
            for element in possible_abstracts:
                if element.text.strip():
                    return element.text.strip()
        return abstract_element.text.strip()
    except Exception as e:
        print(f"Selenium error: {e} for URL: {abstract_url}")
    return None

def get_abstract(session, abstract_url, driver):
    methods = [
        lambda: get_abstract_with_requests(session, abstract_url),
        lambda: get_abstract_with_selenium(driver, abstract_url)
    ]
    
    for method in methods:
        abstract = method()
        if abstract:
            return abstract
    
    print(f"Failed to get abstract for {abstract_url} using all methods")
    return None

def get_abstract_with_requests(session, abstract_url):
    try:
        response = session.get(abstract_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try different possible locations/structures for the abstract
        abstract_div = soup.find('div', id='abstract')
        if abstract_div and abstract_div.text.strip():
            return abstract_div.text.strip()
        
        # Fallback to searching by other possible div classes or ids
        abstract_div = soup.find('div', class_='abstract')
        if abstract_div and abstract_div.text.strip():
            return abstract_div.text.strip()
        
        # Attempt to find abstract using regular expressions
        abstract_text = re.search(r'Abstract[:.\s]+(.*?)\n', soup.text, re.DOTALL | re.IGNORECASE)
        if abstract_text:
            return abstract_text.group(1).strip()
        
    except requests.RequestException as e:
        print(f"Requests error: {e} for URL: {abstract_url}")
    return None

def save_abstract(abstract, save_path):
    try:
        with open(save_path, 'w', encoding='utf-8') as file:
            file.write(abstract)
        print(f"Saved abstract: {save_path}")
        return True
    except IOError as e:
        print(f"Failed to save abstract: {save_path}")
        print(f"Error: {e}")
    return False

def download_abstracts(npapers=10,save_directory="CVPR2024_abstracts",base_url="https://openaccess.thecvf.com/CVPR2024?day=all"):
    
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    driver = setup_driver()
    
    try:
        response = session.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        paper_titles = soup.find_all('dt', class_='ptitle')
        
        if not paper_titles:
            print("No paper titles found. The page structure might have changed.")
            return
        
        print(f"Found {len(paper_titles)} paper titles")
        
        count = 0
        for title in paper_titles:
            if count >= npapers:
                break
            link = title.find('a')
            if link:
                abstract_url = "https://openaccess.thecvf.com/" + link.get('href')
                paper_title = link.text.strip()
                sanitized_title = sanitize_filename(paper_title)
                print(f"Fetching abstract for: {paper_title}")
                abstract = get_abstract(session, abstract_url, driver)
                if abstract:
                    save_path = os.path.join(save_directory, f"{sanitized_title}.txt")
                    save_abstract(abstract, save_path)
                    count += 1
                else:
                    print(f"Couldn't find abstract for: {paper_title}")
                    print(f"URL: {abstract_url}")
            else:
                print(f"No link found for paper: {title.text.strip()}")
            time.sleep(1)
        
        print("Download complete.")
        
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()


def download_paper(paper_title,save_directory="CVPR_papers",base_url = "https://openaccess.thecvf.com/CVPR2024?day=all"):
    #download document
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    paper_title=paper_title.replace("_",":")
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
        
    filename = re.sub(r'[^\w\-_\. ]', '_', paper_title) + '.pdf'
    filename =  os.path.join(save_directory, filename)
    
    if os.path.isfile(filename):
        print("paper already in directory")
        return filename
    else:
        print(filename)

    # Get the main page
    response = session.get(base_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the link to the paper
    paper_link = None
    for dt in soup.find_all('dt', class_='ptitle'):
        if paper_title.lower() in dt.text.strip().lower():
            paper_link = dt.find('a')['href']
            break

    if not paper_link:
        print(f"Paper '{paper_title}' not found.")
        return

    # Get the paper's page
    paper_url = f"https://openaccess.thecvf.com/{paper_link}"
    response = session.get(paper_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the PDF link
    pdf_link = soup.find('a', text='pdf')
    if not pdf_link:
        print(f"PDF link for '{paper_title}' not found.")
        return

    pdf_url = f"https://openaccess.thecvf.com/{pdf_link['href']}"

    # Download the PDF
    response = session.get(pdf_url)
    response.raise_for_status()
    
    # Save the PDF
    
    with open(filename, 'wb') as f:
        f.write(response.content)

    print(f"Successfully downloaded '{filename}'")
    return filename

    

