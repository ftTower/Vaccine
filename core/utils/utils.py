import argparse
from   utils.ainsi import *

def init():
     #! ARGUMENT
    parser = argparse.ArgumentParser(description="Vaccine: SQL Injection Detection Tool")
    parser.add_argument("url", help="The target URL to test for SQL injection.")
    parser.add_argument("-o", "--output", dest="output_file", default="vaccine_results.txt",
                        help="Archive file to store results. Defaults to 'vaccine_results.txt'.")
    parser.add_argument("-X", "--method", dest="request_method", default="GET",
                        choices=["GET", "POST"], help="HTTP request method (GET or POST). Defaults to GET.")

    args = parser.parse_args()    
    target_url = args.url
    output_file = args.output_file
    request_method = args.request_method.upper()

    #! PRINT ARGUMENT
    print(f"\n{colored('             VACCINE             ', BLACK, BG_BRIGHT_WHITE, BOLD)}")
    print(f"{colored('   URL   : ', BLACK, BG_WHITE, BOLD)}" 
          + f"  {colored(target_url, RED, styles=BOLD)}")
    print(f"{colored(' OUTFILE : ', BLACK, BG_WHITE, BOLD )}"
          + f"  {colored(output_file, RED, styles=BOLD)}")
    print(f"{colored('  METHOD : ', BLACK, BG_WHITE, BOLD )}"
          + f"  {colored(request_method, RED, styles=BOLD)}\n")
    
    return target_url, output_file, request_method


def write_scrapped_data(scrapped_data, output_file, target_url):
      import json
      import os
      import requests
      from bs4 import BeautifulSoup

      if output_file == "vaccine_results.txt":
            try:
                  response = requests.get(target_url)
                  response.raise_for_status()
                  soup = BeautifulSoup(response.text, "html.parser")
                  page_title = soup.title.string.strip() if soup.title else "untitled"
                  output_file = f"{page_title}.txt"
            except Exception as e:
                  print(f"Error fetching page title: {e}")
                  output_file = "untitled.txt"

      # Ensure the data folder exists
      data_folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../data/")
      os.makedirs(data_folder_path, exist_ok=True)
      
      # Write the scrapped data to the file
      path = os.path.join(data_folder_path, output_file)
      with open(path, "w") as f:
            f.write(json.dumps(scrapped_data, indent=4, ensure_ascii=False))
            f.write("\n\n")
      
      return output_file

    