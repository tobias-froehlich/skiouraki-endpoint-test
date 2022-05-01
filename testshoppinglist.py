import deepdiff
import json
import requests
import base64
from utils import doGet, doPost, doDelete, equals, equalsInAnyOrder
from const import URL

requests.post(URL + "user/reset")
r = doGet("user/get-all")
assert len(r) == 0

john = json.dumps({
    "id": None,
    "version": None,
    "name": "John",
    "password": "johns-password"
})
john = doPost("user/add", john)
johnsAuth = (john["id"], "johns-password")

joe = json.dumps({
    "id": None,
    "version": None,
    "name": "Joe",
    "password": "joes-password"
})
joe = doPost("user/add", joe)
joesAuth = (joe["id"], "joes-password")

jack = json.dumps({
    "id": None,
    "version": None,
    "name": "Jack",
    "password": "jacks-password",
})
jack = doPost("user/add", jack)
jacksAuth = (jack["id"], "jacks-password")


print("John adds a shopping list.")
newShoppingList = json.dumps({
    "id": None,
    "version": None,
    "name": "John's shopping list",
    "owner": None,
})
addedShoppingList = doPost("shopping-list/add", newShoppingList, withAuth=johnsAuth)
assert addedShoppingList["name"] == "John's shopping list"

print("John reads his shopping list.")
fromDb = doGet("shopping-list/get/" + addedShoppingList["id"], withAuth=johnsAuth)
assert equals(fromDb, addedShoppingList)

print("Joe tries to read John's shopping list.")
error = doGet("shopping-list/get/" + addedShoppingList["id"], withAuth=joesAuth)
assert error == "Not authorized."

print("John renames his shopping list.")
shoppingList = json.dumps({
    "id": addedShoppingList["id"],
    "version": addedShoppingList["version"],
    "name": "John's renamed shopping list",
    "owner": john["id"],
})
renamedShoppingList = doPost("shopping-list/rename", shoppingList, withAuth=johnsAuth)
assert renamedShoppingList["id"] == addedShoppingList["id"]
assert renamedShoppingList["version"] != addedShoppingList["version"]
assert renamedShoppingList["name"] == "John's renamed shopping list"
assert renamedShoppingList["owner"] == john["id"]

print("Joe tries to rename John's shopping list.")
shoppingList = json.dumps({
    "id": renamedShoppingList["id"],
    "version": renamedShoppingList["version"],
    "name": "Joe's renamed shopping list",
    "owner": john["id"],
})
error = doPost("shopping-list/rename", shoppingList, withAuth=joesAuth, expectError=True)
assert error == "Cannot rename ShoppingList."

print("Joe tries to rename John's shopping list with predenting it is his.")
shoppingList = json.dumps({
    "id": renamedShoppingList["id"],
    "version": renamedShoppingList["version"],
    "name": "Joe's renamed shopping list",
    "owner": joe["id"],
})
error = doPost("shopping-list/rename", shoppingList, withAuth=joesAuth, expectError=True)
assert error == "Cannot rename ShoppingList."

print("John reads his shopping list again.")
fromDb = doGet("shopping-list/get/" + addedShoppingList["id"], withAuth=johnsAuth)
assert equals(fromDb, renamedShoppingList)

print("John reads all his own shopping lists, which is just the one.")
johnsShoppingLists = doGet("shopping-list/get-own", withAuth=johnsAuth)
assert equalsInAnyOrder(johnsShoppingLists, [renamedShoppingList,])

print("Joe reads all his own shopping lists, which is none.")
joesShoppingLists = doGet("shopping-list/get-own", withAuth=joesAuth)
assert equalsInAnyOrder(joesShoppingLists, [])


print("Joe adds two shopping lists.")
newShoppingList = json.dumps({
    "id": None,
    "version": None,
    "name": "Joe's 1. shopping list",
    "owner": None,
})
joesFirstShoppingList = doPost("shopping-list/add", newShoppingList, withAuth=joesAuth)
assert joesFirstShoppingList["name"] == "Joe's 1. shopping list"
newShoppingList = json.dumps({
    "id": None,
    "version": None,
    "name": "Joe's 2. shopping list",
    "owner": None,
})
joesSecondShoppingList = doPost("shopping-list/add", newShoppingList, withAuth=joesAuth)
assert joesSecondShoppingList["name"] == "Joe's 2. shopping list"

print("Joe reads his own shopping lists, which are two now.")
joesShoppingLists = doGet("shopping-list/get-own", withAuth=joesAuth)
assert equalsInAnyOrder(joesShoppingLists, [joesSecondShoppingList, joesFirstShoppingList])

print("Jack adds three shopping lists.")
newShoppingList = json.dumps({
    "id": None,
    "version": None,
    "name": "Jack's 1. shopping list",
    "owner": None,
})
jacksFirstShoppingList = doPost("shopping-list/add", newShoppingList, withAuth=jacksAuth)
assert jacksFirstShoppingList["name"] == "Jack's 1. shopping list"
newShoppingList = json.dumps({
    "id": None,
    "version": None,
    "name": "Jack's 2. shopping list",
    "owner": None,
})
jacksSecondShoppingList = doPost("shopping-list/add", newShoppingList, withAuth=jacksAuth)
assert jacksSecondShoppingList["name"] == "Jack's 2. shopping list"
newShoppingList = json.dumps({
    "id": None,
    "version": None,
    "name": "Jack's 3. shopping list",
    "owner": None,
})
jacksThirdShoppingList = doPost("shopping-list/add", newShoppingList, withAuth=jacksAuth)
assert jacksThirdShoppingList["name"] == "Jack's 3. shopping list"

print("Jack reads all his own shopping lists, which are three.")
jacksOwnShoppingLists = doGet("shopping-list/get-own", withAuth=jacksAuth)
assert equalsInAnyOrder(jacksOwnShoppingLists, [jacksFirstShoppingList, jacksSecondShoppingList, jacksThirdShoppingList])

print("John tries to delete Jack's third shopping list.")
error = doDelete("shopping-list/delete/" + jacksThirdShoppingList["id"], withAuth=johnsAuth, expectError=True)
assert error == "ShoppingList not found."

print("Jack assures that he has still all three.")
jacksOwnShoppingLists = doGet("shopping-list/get-own", withAuth=jacksAuth)
assert equalsInAnyOrder(jacksOwnShoppingLists, [jacksFirstShoppingList, jacksSecondShoppingList, jacksThirdShoppingList])


print("Jack deletes the third shopping list.")
doDelete("shopping-list/delete/" + jacksThirdShoppingList["id"], withAuth=jacksAuth)

print("Jack assures that he now has only two.")
jacksOwnShoppingLists = doGet("shopping-list/get-own", withAuth=jacksAuth)
assert equalsInAnyOrder(jacksOwnShoppingLists, [jacksFirstShoppingList, jacksSecondShoppingList])

print("Jack tries to invite a user that does not exist.")
error = doPost("shopping-list/invite/" + jacksFirstShoppingList["id"] + "/" + "notexisting-id", None, withAuth=jacksAuth, expectError=True)
assert error == "User not found."

print("Jack tries to invite John to a shopping list that does not exist.")
error  = doPost("shopping-list/invite/" + "notexisting-id" + "/" + john["id"], None, withAuth=jacksAuth, expectError=True)
assert error == "ShoppingList not found."

print("Joe tries to invite John to Jack's first shopping list.")
error = doPost("shopping-list/invite/" + jacksFirstShoppingList["id"] + "/" + john["id"], None, withAuth=joesAuth)
assert error == "ShoppingList not found."

print("John tries to read Jack's first shopping list.")
error = doGet("shopping-list/get/" + jacksFirstShoppingList["id"], withAuth=johnsAuth, expectError=True)
assert error == "Not authorized."

print("Jack invites john to his first shopping list.")
invitedUsers = doPost("shopping-list/invite/" + jacksFirstShoppingList["id"] + "/" + john["id"], None, withAuth=jacksAuth)
assert equalsInAnyOrder(invitedUsers, [john])

print("Jack reads the invited users of his first shopping list.")
invitedUsers = doGet("shopping-list/get-invitations-by-shopping-list/" + jacksFirstShoppingList["id"], withAuth=jacksAuth)
assert equalsInAnyOrder(invitedUsers, [john])

print("Joe tries to read the invited users of Jack's first shopping list.")
invitedUsers = doGet("shopping-list/get-invitations-by-shopping-list/" + jacksFirstShoppingList["id"], withAuth=joesAuth)
assert equalsInAnyOrder(invitedUsers, [])

print("John tries to read Jack's first shopping list.")
error = doGet("shopping-list/get/" + jacksFirstShoppingList["id"], withAuth=johnsAuth)
assert error == "Not authorized."

print("John accepts the invitation.")
result = doPost("shopping-list/accept-invitation/" + jacksFirstShoppingList["id"], None, withAuth=johnsAuth)
assert result == "ok"

print("John reads Jack's first shopping list.")
shoppingList = doGet("shopping-list/get/" + jacksFirstShoppingList["id"], withAuth=johnsAuth)
assert equals(shoppingList, jacksFirstShoppingList)

print("John tries to invite Joe to Jack's first shopping list.")
error = doPost("shopping-list/invite/" + jacksFirstShoppingList["id"] + "/" + joe["id"], None, withAuth=johnsAuth)
assert error == "Not authorized."

print("Joe tries to accept John's invitation.")
error = doPost("shopping-list/accept-invitation/" + jacksFirstShoppingList["id"], None, withAuth=joesAuth)
assert error == "Invitation not found."

print("Joe tries to read Jack's first shopping list.")
error = doGet("shopping-list/get/" + jacksFirstShoppingList["id"], withAuth=joesAuth, expectError=True)
assert error == "Not authorized."

print("Jack invites joe to his first shopping list.")
invitedUsers = doPost("shopping-list/invite/" + jacksFirstShoppingList["id"] + "/" + joe["id"], None, withAuth=jacksAuth)
assert equalsInAnyOrder(invitedUsers, [joe])

print("Jack deletes his user account.")
deletedUser = doDelete("user/delete/" + jack["id"], withAuth=jacksAuth)
assert equals(deletedUser, jack)

print("Joe tries to accept the invitation.")
error = doPost("shopping-list/accept-invitation/" + jacksFirstShoppingList["id"], None, withAuth=joesAuth)
assert error == "Invitation not found."

print("John tries to read Jack's first shopping list.")
error = doGet("shopping-list/get/" + jacksFirstShoppingList["id"], withAuth=johnsAuth, expectError=True)
assert error == "Not authorized."

print("Jack creates a new user account.")
jack = json.dumps({
    "id": None,
    "version": None,
    "name": "Jack",
    "password": "jacks-password",
})
jack = doPost("user/add", jack)
jacksAuth = (jack["id"], "jacks-password")

print("John creates a shopping list, invites Joe and he accepts.")
shoppingList = json.dumps({
    "id": None,
    "version": None,
    "name": "John's new shopping list",
    "owner": None,
})
johnsShoppingList = doPost("shopping-list/add", shoppingList, withAuth=johnsAuth)
assert johnsShoppingList["name"] == "John's new shopping list"
invitedUsers = doPost("shopping-list/invite/" + johnsShoppingList["id"] + "/" + joe["id"], None, withAuth=johnsAuth)
assert equalsInAnyOrder(invitedUsers, [joe])
doPost("shopping-list/accept-invitation/" + johnsShoppingList["id"], None, withAuth=joesAuth)
shoppingList = doGet("shopping-list/get/" + johnsShoppingList["id"], withAuth=joesAuth)
assert equals(shoppingList, johnsShoppingList)

print("Jack tries to remove Joe from John's shopping list.")
error = doPost("shopping-list/remove-user-from-shopping-list/" + johnsShoppingList["id"] + "/" + joe["id"], None, withAuth=jacksAuth, expectError=True)
print(error)
assert error == "Cannot leave ShoppingList."
shoppingList = doGet("shopping-list/get/" + johnsShoppingList["id"], withAuth=joesAuth)
assert equals(shoppingList, johnsShoppingList)

print("John removes Joe from that shopping list.")
members = doPost("shopping-list/remove-user-from-shopping-list/" + johnsShoppingList["id"] + "/" + joe["id"], None, withAuth=johnsAuth)
assert equalsInAnyOrder(members, [john])
error = doGet("shopping-list/get/" + johnsShoppingList["id"], withAuth=joesAuth, expectError=True)
assert error == "Not authorized."

print("John invites Joe again and he accepts again.")
invitedUsers = doPost("shopping-list/invite/" + johnsShoppingList["id"] + "/" + joe["id"], None, withAuth=johnsAuth)
assert equalsInAnyOrder(invitedUsers, [joe])
doPost("shopping-list/accept-invitation/" + johnsShoppingList["id"], None, withAuth=joesAuth)
shoppingList = doGet("shopping-list/get/" + johnsShoppingList["id"], withAuth=joesAuth)
assert equals(shoppingList, johnsShoppingList)

print("Joe leaves the shopping list.")
doPost("shopping-list/leave-shopping-list/" + johnsShoppingList["id"], None, withAuth=joesAuth)
error = doGet("shopping-list/get/" + johnsShoppingList["id"], withAuth=joesAuth, expectError=True)
assert error == "Not authorized."

