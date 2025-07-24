import os

from utils.ainsi import *
from utils.objects.vuln_link import *
from utils.objects.success_obj import *

from GET.injection.union_based import *

def write_into_file(string, filepath):
    data_folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../data/")
    os.makedirs(data_folder_path, exist_ok=True)
    with open(data_folder_path + filepath, 'a') as file:
        file.write(string)
    

def get_injection(vuln_links, output_file):
    
    
    for vuln_link in vuln_links:
        try :
            identified_db, link, query_params, success = vuln_link.get_infos()
            parsed_url = urlparse(link)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
            print(f"🔴 {colored('Injection:', RED, styles=BOLD)} {colored(base_url, CYAN, styles=BOLD)}")
            
            if (identified_db.lower() == "mysql"):
                success = get_union_based_injection(query_params, base_url, identified_db)
                if (success.success == True):
                    print(f"{colored('🟢 Injection:', YELLOW, styles=BOLD)} {colored(identified_db, GREEN, styles=BLINK)} > {colored('UNION BASED', MAGENTA, styles=BOLD)} ✅")
                    write_into_file(str(success), output_file)
                else:
                    print(f"{colored('🔴 Injection:', YELLOW, styles=BOLD)} {colored(identified_db, GREEN, styles=BLINK)} > {colored('UNION BASED', MAGENTA, styles=BOLD)} ❌")
                
            
            # print(success)

        except Exception as e:
            print(f"{colored('ERROR INJECTION : ', RED, styles=UNDERLINE)} {e}")


    
        

