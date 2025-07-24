from selenium import webdriver

import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service

from utils.conf import *
from utils.ainsi import *

def setup_driver():
    chrome_options = Options()
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    return driver

def extract_data(driver):
    data = {}
    try :
        data['title'] = driver.title
        
        paragraphs = driver.find_elements(By.TAG_NAME, 'p')
        data['paragraphs'] = [p.text for p in paragraphs if p.text.strip()]
        
        links = driver.find_elements(By.TAG_NAME, 'a')
        data['links'] = [{'text': link.text.strip(), 'href':link.get_attribute('href')}
                         for link in links if link.get_attribute('href') and link.text.strip()]
        
    except Exception as e:
        print(f"Erreur lors de l'extraction des données : {e}")
        data['error'] = str(e)
    return data

def simple_crawler(start_url, max_pages=10, domain_whitelist=None):
    driver = setup_driver()
    visited_url = set()
    urls_to_visit = [start_url]
    scraped_data = {}
    
    if domain_whitelist is None:
        from urllib.parse import urlparse
        parsed_url = urlparse(start_url)
        domain_whitelist = {parsed_url.netloc}
        
    print(f"{colored('🔴 Crawling:  ', RED, styles=BOLD)}{colored(start_url, CYAN, styles=BLINK)}")
    
    
    while urls_to_visit and len(visited_url) < max_pages:
        current_url = urls_to_visit.pop(0)
        
        if current_url in visited_url:
            continue
        
        visited_url.add(current_url)
        
        try:
            driver.get(current_url)
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            data = extract_data(driver)
            scraped_data[current_url] = data
            print(f"{colored('🟡 Crawling: ', YELLOW, styles=BOLD):<20} {colored(current_url, CYAN, styles=BOLD):<60} {colored('Title:', WHITE)} {colored(data.get('title', 'N/A'), GREEN, styles=BOLD):<40}")
            
            
            for link_info in data.get('links', []):
                href = link_info.get('href')
                if href:
                    from urllib.parse import urljoin, urlparse
                    absolute_url = urljoin(current_url, href)
                    parsed_link_url = urlparse(absolute_url)
                    
                    if parsed_link_url.netloc in domain_whitelist and \
                        absolute_url not in visited_url and \
                        absolute_url not in urls_to_visit and \
                            absolute_url.startswith('http'):
                        urls_to_visit.append(absolute_url)
                        
                time.sleep(requested_delay)
                
        except Exception as e:
            print(f"Erreur lors de la visite de {current_url}")
            scraped_data[current_url] = {'error': str(e)}
        finally:
            pass
    
     
    print(erase_lines(len(scraped_data) + 3))
    print(
        f"{colored('🟢 Crawling: ', WHITE, styles=BOLD)} "
        f"{colored('Found ', CYAN, styles=BOLD)}"
        f"{colored(str(len(scraped_data)), YELLOW, styles=BOLD)} "
        f"{colored('URLs from the initial URL.', CYAN, styles=BOLD)}\n"
    )
        
    driver.quit()    
    return scraped_data