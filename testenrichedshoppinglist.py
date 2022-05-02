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

