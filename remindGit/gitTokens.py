import requests
from remindGit.settings import CLIENT_ID, CLIENT_SECRET


def get_access_tokens(code):
    """
    :param code: code is acquired when a user authorizes our GitHub application
    which later will be used to get the access token for further API hits
    :return: JSON with token, scope and type of the token
    """
    url = 'https://github.com/login/oauth/access_token'
    body = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'redirect_uri': 'http://localhost:8000/',
    }
    headers = {'content-type': 'application/json'}
    req = requests.post(url, data=body, headers=headers)
    return req.text
