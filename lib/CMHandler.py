from lib.Tools import load_json_file
from lib.dto.MsMetadata import MsMetadata


class CMHandler:

    def __init__(self, cache_path, source_url=""):
        self.microservices_url = source_url
        self.cache_path = cache_path
        self.microservices = None

    def _fetch_microservices(self):
        # TODO: here, read it from the CM url, keep a cache for resilience,
        #  update cache only if file can be parsed
        ms_dicts = load_json_file(self.cache_path)
        self.microservices = []
        for ms in ms_dicts:
            self.microservices.append(MsMetadata().unmarshall(ms))

    def get_microservices(self):
        self._fetch_microservices()
        return self.microservices

    def get_microservice_by_id(self, msId):
        self._fetch_microservices()
        for ms in self.microservices:
            if ms.msId == msId:
                return ms
        return None

    def get_microservice_by_api(self, apiClass, apiCall=None):
        self._fetch_microservices()
        for ms in self.microservices:
            for api_item in ms.publishedAPI:
                if api_item.apiClass == apiClass:
                    # If search didn't specify a call, it's enough to find the class
                    if not apiCall:
                        return ms
                    # Check if the call is defined
                    elif api_item.apiCall == apiCall:
                        return ms
        return None
