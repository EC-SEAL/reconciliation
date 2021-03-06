import base64
import os

# Base Properties file path
PROPERTIES_FILE = "server.properties"

# Application root directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Default directory for application data
DEFAULT_DATA_DIR = "data/"

# API autoloader root package name
API_ROOT_PACKAGE = 'api'

# Directory where the API autoloader must look for files to load
API_DIR = './' + API_ROOT_PACKAGE

# Directory where the class autoloader must look for files to load
COMP_DIR = ROOT_DIR + "/" + "lib" + "/" + "comparators"

# Directory where the class autoloader must look for files to load
PROC_DIR = ROOT_DIR + "/" + "lib" + "/" + "processors"

# Generate a volatile secure encryption key to use if no env key is passed
ENCRYPTION_KEY = base64.b64encode(os.urandom(16))
# TODO: check if randomness is real in docker, and if real, check if enough, as it might block execution
