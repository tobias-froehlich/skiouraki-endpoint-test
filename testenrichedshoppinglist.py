import deepdiff
from copy import deepcopy
import json
import requests
import base64
from utils import doGet, doPost, doDelete, equals, equalsInAnyOrder
from const import URL

def enrichedShoppingListsEqual(enrichedShoppingList1, enrichedShoppingList2):
    return enrichedShoppingList1["id"] == enrichedShoppingList2["id"] \
      and  enrichedShoppingList1["version"] == enrichedShoppingList2["version"] \
      and  enrichedShoppingList1["name"] == enrichedShoppingList2["name"] \
      and  enrichedShoppingList1["owner"] == enrichedShoppingList2["owner"] \
      and  equalsInAnyOrder(enrichedShoppingList1["members"], enrichedShoppingList2["members"]) \
      and  equalsInAnyOrder(enrichedShoppingList1["invitedUsers"], enrichedShoppingList2["invitedUsers"]) 

def enrichedShoppingListsEqualButVersionsDiffer(enrichedShoppingList1, enrichedShoppingList2):
    return enrichedShoppingList1["id"] == enrichedShoppingList2["id"] \
      and  enrichedShoppingList1["version"] != enrichedShoppingList2["version"] \
      and  enrichedShoppingList1["name"] == enrichedShoppingList2["name"] \
      and  enrichedShoppingList1["owner"] == enrichedShoppingList2["owner"] \
      and  equalsInAnyOrder(enrichedShoppingList1["members"], enrichedShoppingList2["members"]) \
      and  equalsInAnyOrder(enrichedShoppingList1["invitedUsers"], enrichedShoppingList2["invitedUsers"]) 


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


print("Jack adds a shopping list.")
newShoppingList = json.dumps({
    "id": None,
    "version": None,
    "name": "Jack's shopping list",
    "owner": None,
})
jacksShoppingList = doPost("shopping-list/add", newShoppingList, withAuth=jacksAuth)
assert jacksShoppingList["name"] == "Jack's shopping list"


print("Jack reads the enriched shopping list.")
enrichedShoppingList = doGet("shopping-list/get-enriched/" + jacksShoppingList["id"], withAuth=jacksAuth)
expected = deepcopy(jacksShoppingList)
expected["invitedUsers"] = []
expected["members"] = [jack]
assert enrichedShoppingListsEqual(enrichedShoppingList, expected)

print("Jack invites John to his shopping list.")
invitedUsers = doPost("shopping-list/invite/" + jacksShoppingList["id"] + "/" + john["id"], None, withAuth=jacksAuth)
assert equalsInAnyOrder(invitedUsers, [john])

print("Jack reads the enriched shopping list.")
old = enrichedShoppingList
enrichedShoppingList = doGet("shopping-list/get-enriched/" + jacksShoppingList["id"], withAuth=jacksAuth)
expected = deepcopy(old)
expected["invitedUsers"] = [john]
expected["members"] = [jack]
assert enrichedShoppingListsEqualButVersionsDiffer(enrichedShoppingList, expected)

print("Jack invites Joe to his shopping list.")
invitedUsers = doPost("shopping-list/invite/" + jacksShoppingList["id"] + "/" + joe["id"], None, withAuth=jacksAuth)
assert equalsInAnyOrder(invitedUsers, [john, joe])

print("John accepts the invitation.")
doPost("shopping-list/accept-invitation/" + jacksShoppingList["id"], None, withAuth=johnsAuth)

print("Joe tries to read the enriched shopping list.")
error = doGet("shopping-list/get-enriched/" + jacksShoppingList["id"], withAuth=joesAuth, expectError=True)
assert error == "ShoppingList not found."

print("John reads the enriched shopping list.")
old = enrichedShoppingList
enrichedShoppingList = doGet("shopping-list/get-enriched/" + jacksShoppingList["id"], withAuth=johnsAuth)
expected = deepcopy(old)
expected["invitedUsers"] = [joe]
expected["members"] = [jack, john]
assert enrichedShoppingListsEqualButVersionsDiffer(enrichedShoppingList, expected)



