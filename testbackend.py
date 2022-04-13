import deepdiff
import json
import requests
import base64

#url = "http://localhost:8090/"
url = "https://aqueous-peak-70993.herokuapp.com/"

def doGet(path, headers={}, withAuth=()):
    if withAuth:
        (id, password) = withAuth
        headers['Authorization'] = makeAuthHeader(id, password)
    res = requests.get(url + path, headers=headers)
    if res.ok:
        try:
            return res.json()
        except:
            return res.text
    else:
        return res.text

def doPost(path, payload, withAuth=()):
    headers = {'Content-type': 'application/json'}
    if withAuth:
        (id, password) = withAuth
        headers['Authorization'] = makeAuthHeader(id, password)
    res = requests.post(url + path, data=payload, headers=headers)
    if res.ok:
        return res.json()
    else:
        return res.text

def equals(a, b):
    return deepdiff.DeepDiff(a, b) == {}

def makeAuthHeader(id, password):
    credentials = base64.b64encode((id + ":" + password).encode()).decode()
    return "Basic " + credentials

requests.post(url + "user/reset")

r = doGet("user/get-all")
assert len(r) == 0


# Add user Joe
newUser = json.dumps({
    "id": None,
    "version": None,
    "name": "Joe",
    "password":"joes-password"
})
userFromDb = doPost("user/add", newUser)
assert userFromDb['name'] == "Joe"
assert userFromDb['password'] == "joes-password"
idJoe = userFromDb['id']

# Try to add user Joe again
error = doPost("user/add", json.dumps({
    "id": None,
    "version": None,
    "name": "Joe",
    "password":"other-password"
}))
assert error == "Cannot insert user. User with name Joe already exists."

# Read user Joe
user = doGet("user/get/" + idJoe, withAuth=(idJoe, "joes-password"))
assert equals(user, userFromDb)

# Get user Joe by name
userId = doGet("user/get-by-name/Joe")
assert userId == idJoe

# Get user Joe by different spelling
userId = doGet("user/get-by-name/joe")
assert userId == idJoe


# Add user with greek letters
newUser = json.dumps({
    "id": None,
    "version": None,
    "name": "λambdα",
    "password": "my-password"
})
addedUser = doPost("user/add", newUser)
assert addedUser['name'] == "λambdα"
assert addedUser['password'] == "my-password"
id = addedUser['id']
userId = doGet("user/get-by-name/λambdα")
assert userId == id


# Get user with greek letters with different spelling
userId = doGet("user/get-by-name/lamBDa")
assert userId == id

# Try to get user that does not exist by name
error = doGet("user/get-by-name/notexistingname")
assert error == "User not found."

# Add user with maximum length name
newUser = json.dumps({
    "id": None,
    "version": None,
    "name": "abcdefghijklmnop",
    "password": "my-password"
})
addedUser = doPost("user/add", newUser)
assert addedUser['name'] == "abcdefghijklmnop"
assert addedUser['password'] == "my-password"
id = addedUser['id']
user = doGet("user/get-by-name/abcdefghijklmnop", withAuth=(id, "my-password"))

# Try to add user with too long name
newUser = json.dumps({
    "id": None,
    "version": None,
    "name": "abcdefghijklmnopq",
    "password": "my-password"
})
error = doPost("user/add", newUser)
assert error == "Invalid user name."


# Read non existing user
error = doGet("user/get/gibtsnicht", withAuth=(idJoe, "joes-password"))
assert error == "User with id = gibtsnicht not found."

# Try to add Joe again
newUser = json.dumps({
    "id": None,
    "version": None,
    "name": "Joe",
    "password":"joes-password"
})
error = doPost("user/add", newUser)
assert error == "Cannot insert user. User with name Joe already exists."


# Add user John
newUser = json.dumps({
    "id": None,
    "version": None,
    "name": "John",
    "password":"johns-password"
})
userFromDb = doPost("user/add", newUser)
assert userFromDb['name'] == "John"
assert userFromDb['password'] == "johns-password"
idJohn = userFromDb['id']

# Read user John
user = doGet("user/get/" + idJohn, withAuth=(idJohn, "johns-password"))
assert equals(user, userFromDb)

# Try to update John's Password without Authentication
user = doGet("user/get/" + idJohn, withAuth=(idJohn, "johns-password"))
user['password'] = "johns-new-password"
error = doPost("user/update/" + idJohn, json.dumps(user))
assert error == "Authentication header is missing."

# Try to update John's Password with wrong password
user = doGet("user/get/" + idJohn, withAuth=(idJohn, "johns-password"))
user['password'] = "johns-new-password"
error = doPost("user/update/" + idJohn, json.dumps(user), withAuth=(idJohn, "joes-password"))
assert error == "Wrong credentials."

# Update John's Password
user = doGet("user/get/" + idJohn, withAuth=(idJohn, "johns-password"))
user['password'] = "johns-new-password"
updatedJohn = doPost("user/update/" + idJohn, json.dumps(user), withAuth=(idJohn, "johns-password"))
assert updatedJohn['id'] == idJohn
assert updatedJohn['version'] != user['version']
assert updatedJohn['name'] == "John"
assert updatedJohn['password'] == "johns-new-password"

# Try to update again with outdated version
user['password'] = 'johns-password'
error = doPost("user/update/" + idJohn, json.dumps(user), withAuth=(idJohn, "johns-new-password"))
assert error == "The user does not exist or the version is outdated."
