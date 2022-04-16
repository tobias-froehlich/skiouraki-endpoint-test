import deepdiff
import json
import requests
import base64
from const import URL

def doGet(path, headers={}, withAuth=(), expectError=False):
    if withAuth:
        (id, password) = withAuth
        if not expectError:
            headers['Authorization'] = makeAuthHeader(id, 'wrong-password')
            error = requests.get(URL + path, headers=headers).text
            assert error == "Wrong credentials."
            headers['Authorization'] = makeAuthHeader('wrong-id', password)
            error = requests.get(URL + path, headers=headers).text
            assert error == "Wrong credentials."
        headers['Authorization'] = makeAuthHeader(id, password)
    res = requests.get(URL + path, headers=headers)
    if res.ok:
        try:
            return res.json()
        except:
            return res.text
    else:
        return res.text


def doPost(path, payload, withAuth=(), expectError=False):
    headers = {'Content-type': 'application/json'}
    if withAuth:
        (id, password) = withAuth
        if not expectError:
            headers['Authorization'] = makeAuthHeader(id, 'wrong-password')
            error = requests.post(URL + path, data=payload, headers=headers).text
            assert error == "Wrong credentials."
            headers['Authorization'] = makeAuthHeader('wrong-id', password)
            error = requests.post(URL + path, data=payload, headers=headers).text
            assert error == "Wrong credentials."
        headers['Authorization'] = makeAuthHeader(id, password)
    res = requests.post(URL + path, data=payload, headers=headers)
    if res.ok:
        return res.json()
    else:
        return res.text

def doDelete(path, headers={}, withAuth=(), expectError=False):
    if withAuth:
        (id, password) = withAuth
        if not expectError:
            headers['Authorization'] = makeAuthHeader(id, 'wrong-password')
            error = requests.delete(URL + path, headers=headers).text
            assert error == "Wrong credentials."
            headers['Authorization'] = makeAuthHeader('wrong-id', password)
            error = requests.delete(URL + path, headers=headers).text
            assert error == "Wrong credentials."
        headers['Authorization'] = makeAuthHeader(id, password)
    res = requests.delete(URL + path, headers=headers)
    if res.ok:
        try:
            return res.json()
        except:
            return res.text
    else:
        return res.text


def equals(a, b):
    return deepdiff.DeepDiff(a, b) == {}

def makeAuthHeader(id, password):
    credentials = base64.b64encode((id + ":" + password).encode()).decode()
    return "Basic " + credentials

