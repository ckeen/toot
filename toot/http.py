from requests import Request, Session
from toot.exceptions import NotFoundError, ApiError
from toot.logging import log_request, log_response
from toot import config

def send_request(request, allow_redirects=True):
    log_request(request)

    with Session() as session:
        session.proxies.update(config.get_proxy())
        prepared = session.prepare_request(request)
        response = session.send(prepared, allow_redirects=allow_redirects)

    log_response(response)

    return response


def _get_error_message(response):
    """Attempt to extract an error message from response body"""
    try:
        data = response.json()
        if "error_description" in data:
            return data['error_description']
        if "error" in data:
            return data['error']
    except Exception:
        pass

    return "Unknown error"


def process_response(response):
    if not response.ok:
        error = _get_error_message(response)

        if response.status_code == 404:
            raise NotFoundError(error)

        raise ApiError(error)

    return response


def get(app, user, url, params=None):
    url = app.base_url + url
    headers = {"Authorization": "Bearer " + user.access_token}

    request = Request('GET', url, headers, params=params)
    response = send_request(request)

    return process_response(response)


def anon_get(url, params=None):
    request = Request('GET', url, None, params=params)
    response = send_request(request)

    return process_response(response)


def post(app, user, url, data=None, files=None, allow_redirects=True):
    url = app.base_url + url
    headers = {"Authorization": "Bearer " + user.access_token}

    request = Request('POST', url, headers, files, data)
    response = send_request(request, allow_redirects)

    return process_response(response)


def anon_post(url, data=None, files=None, allow_redirects=True):
    request = Request('POST', url, {}, files, data)
    response = send_request(request, allow_redirects)

    return process_response(response)
