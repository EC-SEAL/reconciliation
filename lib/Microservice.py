

# Get SM ms_metadata object
from lib.CMHandler import CMHandler
from lib.SMHandler import SMHandler
from lib.dto.StatusResponse import StatusResponse

from flask import render_template


def session_manager_handler(data_dir, ms_metadata_url,
                            httpsig_private_key, cm_cache_lifetime,
                            httpsig_send_retries):
    cm = CMHandler(data_dir,
                   ms_source_url=ms_metadata_url,
                   key=httpsig_private_key,
                   lifetime=cm_cache_lifetime)
    sm = cm.get_microservice_by_api('SM')
    smh = SMHandler(sm,
                    key=httpsig_private_key,
                    retries=httpsig_send_retries,
                    validate=False)
    return smh


def redirect_return(sm_handler, url, status, origin, destination, message=""):

    result = StatusResponse()
    result.primaryCode = status
    result.secondaryCode = ""
    result.message = ""
    if message != "":
        result.message = message

    token = sm_handler.generateToken(origin, destination, result.json_marshall())
    print("Generated msToken: " + token + "<br/>\n")

    template = {
        'url': url,
        'token': token,
    }

    return render_template('msToken.html', template=template)
