import deepdiff
import json
import requests
import base64
from utils import doGet, doPost, doDelete, equals
from const import URL



requests.post(URL + "user/reset")

r = doGet("user/get-all")
assert len(r) == 0


print("Add user Joe")
newUser = json.dumps({
    "id": None,
    "version": None,
    "name": "Joe",
    "password":"joes-password"
})
userFromDb = doPost("user/add", newUser)
assert userFromDb['name'] == "Joe"
assert userFromDb['password'] == None
idJoe = userFromDb['id']

print("Try to add user Joe again")
error = doPost("user/add", json.dumps({
    "id": None,
    "version": None,
    "name": "Joe",
    "password":"other-password"
}))
assert error == "The user name already exists."

print("Read user Joe")
user = doGet("user/get/" + idJoe, withAuth=(idJoe, "joes-password"))
assert equals(user, userFromDb)

print("Get user Joe by name")
userId = doGet("user/get-by-name/Joe")
assert userId == idJoe

print("Get user Joe by different spelling")
userId = doGet("user/get-by-name/joe")
assert userId == idJoe


print("Add user with greek letters")
newUser = json.dumps({
    "id": None,
    "version": None,
    "name": "λambdα",
    "password": "my-password"
})
addedUser = doPost("user/add", newUser)
assert addedUser['name'] == "λambdα"
assert addedUser['password'] == None
id = addedUser['id']
userId = doGet("user/get-by-name/λambdα")
assert userId == id


print("Get user with greek letters with different spelling")
userId = doGet("user/get-by-name/lamBDa")
assert userId == id

print("Try to get user that does not exist by name")
error = doGet("user/get-by-name/notexistingname")
assert error == "User not found."

print("Add user with maximum length name")
newUser = json.dumps({
    "id": None,
    "version": None,
    "name": "abcdefghijklmnop",
    "password": "my-password"
})
addedUser = doPost("user/add", newUser)
assert addedUser['name'] == "abcdefghijklmnop"
assert addedUser['password'] == None
id = addedUser['id']
user = doGet("user/get-by-name/abcdefghijklmnop")

print("Try to add user with too long name")
newUser = json.dumps({
    "id": None,
    "version": None,
    "name": "abcdefghijklmnopq",
    "password": "my-password"
})
error = doPost("user/add", newUser)
assert error == "Invalid user name."

print("Add user with minimum length name")
newUser = json.dumps({
    "id": None,
    "version": None,
    "name": "abc",
    "password": "my-password"
})
addedUser = doPost("user/add", newUser)
assert addedUser['name'] == "abc"
assert addedUser['password'] == None
id = addedUser['id']
user = doGet("user/get-by-name/abc")

print("Try to add user with too short name")
newUser = json.dumps({
    "id": None,
    "version": None,
    "name": "ab",
    "password": "my-password"
})
error = doPost("user/add", newUser)
assert error == "Invalid user name."

print("Read non existing user")
error = doGet("user/get/gibtsnicht", withAuth=(idJoe, "joes-password"), expectError=True)
assert error == "User not found."

print("Try to add Joe again")
newUser = json.dumps({
    "id": None,
    "version": None,
    "name": "Joe",
    "password":"joes-password"
})
error = doPost("user/add", newUser)
assert error == "The user name already exists."


print("Add user John")
newUser = json.dumps({
    "id": None,
    "version": None,
    "name": "John",
    "password":"johns-password"
})
userFromDb = doPost("user/add", newUser)
assert userFromDb['name'] == "John"
assert userFromDb['password'] == None
idJohn = userFromDb['id']

print("Read user John")
user = doGet("user/get/" + idJohn, withAuth=(idJohn, "johns-password"))
assert equals(user, userFromDb)

print("Try to update John's Password without Authentication")
user = doGet("user/get/" + idJohn, withAuth=(idJohn, "johns-password"))
user['password'] = "johns-new-password"
error = doPost("user/update/" + idJohn, json.dumps(user))
assert error == "Authentication header is missing."

print("Try to update John's Password with wrong password")
user = doGet("user/get/" + idJohn, withAuth=(idJohn, "johns-password"))
user['password'] = "johns-new-password"
error = doPost("user/update/" + idJohn, json.dumps(user), withAuth=(idJohn, "joes-password"))
assert error == "Wrong credentials."

print("Update John's Password")
user = doGet("user/get/" + idJohn, withAuth=(idJohn, "johns-password"))
user['password'] = "johns-new-password"
updatedJohn = doPost("user/update/" + idJohn, json.dumps(user), withAuth=(idJohn, "johns-password"))
assert updatedJohn['id'] == idJohn
assert updatedJohn['version'] != user['version']
assert updatedJohn['name'] == "John"
assert updatedJohn['password'] == None

print("Try to update again with outdated version")
user['password'] = 'johns-password'
error = doPost("user/update/" + idJohn, json.dumps(user), withAuth=(idJohn, "johns-new-password"))
assert error == "The version is outdated."
oldJohn = doGet("user/get/" + idJohn, withAuth=(idJohn, "johns-new-password"))
assert equals(oldJohn, updatedJohn)

print("Update John's password with maximum length password")
user = doGet("user/get/" + idJohn, withAuth=(idJohn, "johns-new-password"))
user['password'] = "01234567890123456789012345678901"
updatedJohn = doPost("user/update/" + idJohn, json.dumps(user), withAuth=(idJohn, "johns-new-password"))
assert updatedJohn['id'] == idJohn
assert updatedJohn['version'] != user['version']
assert updatedJohn['name'] == "John"
assert updatedJohn['password'] == None
user = doGet("user/get/" + idJohn, withAuth=(idJohn, "0123456789012345678901234567890"));

print("Try to update John's password with too long password")
user = doGet("user/get/" + idJohn, withAuth=(idJohn, "01234567890123456789012345678901"))
user['password'] = "012345678901234567890123456789012"
error = doPost("user/update/" + idJohn, json.dumps(user), withAuth=(idJohn, "01234567890123456789012345678901"))
assert error == "Invalid password."

print("Update John's password with minimum length password")
user = doGet("user/get/" + idJohn, withAuth=(idJohn, "01234567890123456789012345678901"))
user['password'] = "0123"
updatedJohn = doPost("user/update/" + idJohn, json.dumps(user), withAuth=(idJohn, "01234567890123456789012345678901"))
assert updatedJohn['id'] == idJohn
assert updatedJohn['version'] != user['version']
assert updatedJohn['name'] == "John"
assert updatedJohn['password'] == None
user = doGet("user/get/" + idJohn, withAuth=(idJohn, "0123456789012345678901234567890"));

print("Try to update John's password with too short password")
user = doGet("user/get/" + idJohn, withAuth=(idJohn, "0123"))
user['password'] = "012"
error = doPost("user/update/" + idJohn, json.dumps(user), withAuth=(idJohn, "0123"))
assert error == "Invalid password."



print("Add user with Password with colon.")
newUser = json.dumps({
    "id": None,
    "version": None,
    "name": "Jimmy",
    "password":"jimmys:password"
})
userFromDb = doPost("user/add", newUser)
assert userFromDb['name'] == "Jimmy"
assert userFromDb['password'] == None
idJimmy = userFromDb['id']

print("Read this User")
user = doGet("user/get/" + idJimmy, withAuth=(idJimmy, "jimmys:password"))
assert equals(user, userFromDb)

print("Update Jimmy's name")
newJimmy = json.dumps({
    "id": user['id'],
    "version": user['version'],
    "name": "Jummy",
    "password": "jimmys:password",
})
updatedJimmy = doPost("user/update/" + idJimmy, newJimmy, withAuth=(idJimmy, "jimmys:password"))

print("Read Jimmy with new name Jummy")
userId = doGet("user/get-by-name/Jummy")
assert userId == idJimmy

print("Update spelling of Jummys name")
newJummy = json.dumps({
  "id": idJimmy,
  "version": updatedJimmy["version"],
  "name": "jUMMY",
  "password": "jimmys:password",
})
updatedJummy = doPost("user/update/" + idJimmy, newJummy, withAuth=(idJimmy, "jimmys:password"))
assert updatedJummy["name"] == "jUMMY"
jummyFromDb = doGet("user/get/" + idJimmy, withAuth=(idJimmy, "jimmys:password"))
assert jummyFromDb["name"] == "jUMMY"

print("Delete John")
idJohn = updatedJohn["id"]
deletedUser = doDelete("user/delete/" + idJohn, withAuth=(idJohn, "0123"))
assert deletedUser["id"] == idJohn
assert deletedUser["name"] == "John"

print("Add John again")
newJohn = json.dumps({
  "id": None,
  "version": None,
  "name": "John",
  "password": "my-password",
})
addedUser = doPost("user/add/", newJohn)
assert addedUser["id"] != idJohn
assert addedUser["name"] == "John"
assert addedUser["password"] == None
userFromDb = doGet("user/get/" + addedUser["id"], withAuth=(addedUser["id"], "my-password"))
assert equals(addedUser, userFromDb)

