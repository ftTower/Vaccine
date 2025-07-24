
from utils.ainsi import *

class Table_obj:
    def __init__(self, name, columns_name, columns_info):
        self.name = name
        self.columns_name = columns_name
        self.columns_info = columns_info

    def __str__(self):
        return f"==================================\nTable Name: {self.name}\nColumns: {', '.join(self.columns_name)}\n\n{self.columns_info}\n==================================\n"        

class Success_obj:
    def __init__(self,success = None ,db_type=None, version=None, tables=None, payloads=None):
        self.success = success
        self.db_type = db_type
        self.version = version
        self.tables = tables
        self.payloads = payloads
        
    def __str__(self):
        return (
                    f"Database Type: {self.db_type}\n"
                    f"Version: {self.version}\n\n"
                    f"Payloads:\n" +
                    "\n".join([f"  - {payload}" for payload in self.payloads]) +
                    f"\n\n------Stolen Tables------\n" +
                    "\n".join([str(table) for table in self.tables])
                )
        
        
    
        