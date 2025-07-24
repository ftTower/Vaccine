


class vuln_link:
    def __init__(self, identified_db, link, query_params, success):
        self.db = identified_db
        self.link = link
        self.query_params = query_params
        self.success = success
        
    def get_infos(self):
        self.db = getattr(self, 'db', None)
        self.link = getattr(self, 'link', None)
        self.query_params = getattr(self, 'query_params', None)
        self.success = getattr(self, 'success', None)
        return self.db, self.link, self.query_params, self.success