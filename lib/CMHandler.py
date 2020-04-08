import json
import logging
import os
from datetime import datetime, timedelta
from json import JSONDecodeError

from lib.Tools import load_json_file
from lib.dto.MsMetadata import MsMetadata


# Will handle access to the needed Config Manager files.
# Will keep a local copy of the file and only update
# if it successfully retrieved the new one
from lib.httpsig.HttpSig import HttpError, HttpConnectError
from lib.httpsig.HttpSigClient import HttpSigClient


class CMHandlerError(Exception):
    def __init__(self, message):
        self.message = message


class CMHandler:

    def __init__(self, cache_dir, ms_source_url=None, key=None, lifetime=600):
        self.microservices_url = ms_source_url
        self.cache_dir = cache_dir
        self.microservices = None
        # How many seconds between cache update attempts
        self.lifetime = lifetime
        self.httpsig = None
        if key:
            logging.info("Remote CM ms metadata query configured on " + ms_source_url)
            self.httpsig = HttpSigClient(key)
            self.httpsig.doValidateResponse(False)

    # Gets the content of a config file, from cache or remote
    def _get(self, file_path, remote_url=None):
        ret_dict = None
        logging.debug(f"Try to get CM metadata set from local file cache in {file_path}")
        # First, try to read locally
        if os.path.isfile(file_path) \
                and os.path.getsize(file_path) > 0:
            try:
                logging.debug("There is a file and has size")
                ret_dict = load_json_file(file_path)
                logging.debug(f"Read from file: {ret_dict}")
            except (OSError, JSONDecodeError, TypeError) as err:
                logging.warning(f"Error accessing file {file_path}: {err}")
        else:
            logging.debug("Not a file or empty")

        # If cache is outdated, fetch file (if we have a url and key)
        last_write = datetime.fromtimestamp(os.path.getmtime(file_path))
        threshold = datetime.now() - timedelta(seconds=self.lifetime)
        logging.debug(f"is cache outdated? {last_write} < {threshold} ?")
        if self.httpsig and last_write < threshold:
            res = None
            try:
                logging.debug(f"Fetching CM metadata set from {remote_url}")
                res = self.httpsig.get(remote_url)
                logging.debug(f"Fetched")
            except HttpError as err:
                logging.warning(f"Error fetching remote config file {remote_url}: {err}")
            except HttpConnectError as err:
                logging.error(f"Error fetching remote config file {remote_url}: {err}")

            # Parse the fetched file.
            if res and res.text:
                logging.debug(f"Fetched data is not empty: {res.text}")
                fetched_dict = None
                try:
                    logging.debug(f"Parsing data into json")
                    fetched_dict = json.loads(res.text)
                except (JSONDecodeError, TypeError) as err:
                    logging.warning(f"Error decoding fetched file {file_path} from {remote_url}: {err}")

                #  If successful, overwrite
                if fetched_dict:
                    logging.debug(f"Successfully parsed")
                    try:
                        logging.debug(f"Overwriting cache in {file_path}")
                        with open(file_path, 'w') as f:
                            f.write(res.text)
                    except (OSError, IOError) as err:
                        logging.warning(f"Error overwriting file {file_path}: {err}")
                    # Regardless of we were able to overwrite or not, return the fetched data
                    logging.debug(f"Overwritten")
                    ret_dict = fetched_dict

        # Return config set contents, or error if empty
        if not ret_dict:
            raise CMHandlerError("Requested config set not found or empty and could not be fetched remotely")
        return ret_dict

    def _fetch_microservices(self):
        ms_dicts = self._get(self.cache_dir + '/msMetadataList.json',
                             self.microservices_url)
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
