import deepdiff
from copy import deepcopy
import json
import requests
import base64
from utils import doGet, doPost, doDelete, equals, equalsInAnyOrder
from const import URL

def itemsEqual(item1, item2):
    return item1["id"] == item2["id"] \
       and item1["version"] == item2["version"] \
       and item1["name"] == item2["name"] \
       and item1["createdBy"] == item2["createdBy"] \
       and item1["modifiedBy"] == item2["modifiedBy"] \
       and item1["boughtBy"] == item2["boughtBy"] \
       and item1["stateChangedBy"] == item2["stateChangedBy"]

def itemListsEqual(items1, items2):
    if len(items1) != len(items2):
        return False
    for i in range(len(items1)):
        item1 = items1[i]
        item2 = items2[i]
        if not itemsEqual(item1, item2):
            return False
    return True


def enrichedShoppingListsEqual(enrichedShoppingList1, enrichedShoppingList2):
    return enrichedShoppingList1["id"] == enrichedShoppingList2["id"] \
      and  enrichedShoppingList1["version"] == enrichedShoppingList2["version"] \
      and  enrichedShoppingList1["name"] == enrichedShoppingList2["name"] \
      and  enrichedShoppingList1["owner"] == enrichedShoppingList2["owner"] \
      and  equalsInAnyOrder(enrichedShoppingList1["members"], enrichedShoppingList2["members"]) \
      and  equalsInAnyOrder(enrichedShoppingList1["invitedUsers"], enrichedShoppingList2["invitedUsers"]) \
      and itemListsEqual(enrichedShoppingList1["items"], enrichedShoppingList2["items"])

def enrichedShoppingListsEqualButVersionsDiffer(enrichedShoppingList1, enrichedShoppingList2):
    return enrichedShoppingList1["id"] == enrichedShoppingList2["id"] \
      and  enrichedShoppingList1["version"] != enrichedShoppingList2["version"] \
      and  enrichedShoppingList1["name"] == enrichedShoppingList2["name"] \
      and  enrichedShoppingList1["owner"] == enrichedShoppingList2["owner"] \
      and  equalsInAnyOrder(enrichedShoppingList1["members"], enrichedShoppingList2["members"]) \
      and  equalsInAnyOrder(enrichedShoppingList1["invitedUsers"], enrichedShoppingList2["invitedUsers"]) \
      and itemListsEqual(enrichedShoppingList1["items"], enrichedShoppingList2["items"])

def shoppingListsEqualButVersionsDiffer(enrichedShoppingList1, enrichedShoppingList2):
    return enrichedShoppingList1["id"] == enrichedShoppingList2["id"] \
      and  enrichedShoppingList1["version"] != enrichedShoppingList2["version"] \
      and  enrichedShoppingList1["name"] == enrichedShoppingList2["name"] \
      and  enrichedShoppingList1["owner"] == enrichedShoppingList2["owner"]


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
expected["items"] = []
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


print("Jack adds an item.")
item = json.dumps({
    "id": "", 
    "version": "",
    "name": "Bananen",
    "createdBy": "",
    "modifiedBy": "",
    "boughtBy": "",
    "stateChangedBy": "",
})
enrichedShoppingList = doPost("shopping-list/add-item/" + jacksShoppingList["id"], item, withAuth=jacksAuth)
items = enrichedShoppingList["items"]
assert len(items) == 1
item = items[0]
assert item["name"] == "Bananen"
assert item["createdBy"] == jack["id"]
assert item["modifiedBy"] == jack["id"]
assert item["boughtBy"] == None
assert item["stateChangedBy"] == jack["id"]

print("Joe tries to add an item.")
item = json.dumps({
    "id": "", 
    "version": "",
    "name": "Äpfel",
    "createdBy": "",
    "modifiedBy": "",
    "boughtBy": "",
    "stateChangedBy": "",
})
error = doPost("shopping-list/add-item/" + jacksShoppingList["id"], item, withAuth=joesAuth)
assert error == "ShoppingList not found."

print("Jack reads the enriched shopping list and finds that the number of items has not changed.")
enrichedShoppingList = doGet("shopping-list/get-enriched/" + jacksShoppingList["id"], withAuth=jacksAuth)
assert len(enrichedShoppingList["items"]) == 1

print("John adds an item.")
item = json.dumps({
    "id": "", 
    "version": "",
    "name": "Birnen",
    "createdBy": "",
    "modifiedBy": "",
    "boughtBy": "",
    "stateChangedBy": "",
})
enrichedShoppingList = doPost("shopping-list/add-item/" + jacksShoppingList["id"], item, withAuth=johnsAuth)
items = enrichedShoppingList["items"]
assert len(items) == 2
item = items[1]
assert item["name"] == "Birnen"
assert item["createdBy"] == john["id"]
assert item["modifiedBy"] == john["id"]
assert item["boughtBy"] == None
assert item["stateChangedBy"] == john["id"]
oldEnrichedShoppingList = enrichedShoppingList

print("Jack removes John's item.")
enrichedShoppingList = doPost("shopping-list/remove-item/" + jacksShoppingList["id"], json.dumps(oldEnrichedShoppingList["items"][1]), withAuth=jacksAuth)
assert len(enrichedShoppingList["items"]) == 1
expected = deepcopy(oldEnrichedShoppingList)
expected["items"] = [oldEnrichedShoppingList["items"][0]]
assert enrichedShoppingListsEqualButVersionsDiffer(enrichedShoppingList, expected)

print("Jack tries to add an item with too long name.")
item = json.dumps({
    "id": "", 
    "version": "",
    "name": "123456789012345678901234567890123",
    "createdBy": "",
    "modifiedBy": "",
    "boughtBy": "",
    "stateChangedBy": "",
})
error = doPost("shopping-list/add-item/" + jacksShoppingList["id"], item, withAuth=jacksAuth)
assert error == "Invalid name."
enrichedShoppingList = doGet("shopping-list/get-enriched/" + jacksShoppingList["id"], withAuth=jacksAuth)
assert len(enrichedShoppingList["items"]) == 1

print("Jack tries to add an item with too short name.")
item = json.dumps({
    "id": "", 
    "version": "",
    "name": "",
    "createdBy": "",
    "modifiedBy": "",
    "boughtBy": "",
    "stateChangedBy": "",
})
error = doPost("shopping-list/add-item/" + jacksShoppingList["id"], item, withAuth=jacksAuth)
assert error == "Invalid name."
enrichedShoppingList = doGet("shopping-list/get-enriched/" + jacksShoppingList["id"], withAuth=jacksAuth)
assert len(enrichedShoppingList["items"]) == 1

print("Jack adds an item with maximal length name.")
item = json.dumps({
    "id": "", 
    "version": "",
    "name": "12345678901234567890123456789012",
    "createdBy": "",
    "modifiedBy": "",
    "boughtBy": "",
    "stateChangedBy": "",
})
enrichedShoppingList = doPost("shopping-list/add-item/" + jacksShoppingList["id"], item, withAuth=jacksAuth)
assert len(enrichedShoppingList["items"]) == 2
enrichedShoppingList = doGet("shopping-list/get-enriched/" + jacksShoppingList["id"], withAuth=jacksAuth)
assert len(enrichedShoppingList["items"]) == 2

print("Jack adds an item with minimal length name.")
item = json.dumps({
    "id": "", 
    "version": "",
    "name": "1",
    "createdBy": "",
    "modifiedBy": "",
    "boughtBy": "",
    "stateChangedBy": "",
})
enrichedShoppingList = doPost("shopping-list/add-item/" + jacksShoppingList["id"], item, withAuth=jacksAuth)
assert len(enrichedShoppingList["items"]) == 3
enrichedShoppingList = doGet("shopping-list/get-enriched/" + jacksShoppingList["id"], withAuth=jacksAuth)
assert len(enrichedShoppingList["items"]) == 3

print("John reads Jack's shopping list.")
oldEnrichedShoppingList = enrichedShoppingList
enrichedShoppingList = doGet("shopping-list/get-enriched/" + jacksShoppingList["id"], withAuth=johnsAuth)
assert enrichedShoppingListsEqual(enrichedShoppingList, oldEnrichedShoppingList)


print("Jack creates a new shopping list.")
newShoppingList = json.dumps({
    "id": None,
    "version": None,
    "name": "Our shopping list",
    "owner": None,
})
newShoppingList = doPost("shopping-list/add", newShoppingList, withAuth=jacksAuth)
assert newShoppingList["name"] == "Our shopping list"

print("Jack invites John to this shopping list and John accepts.")
invitedUsers = doPost("shopping-list/invite/" + newShoppingList["id"] + "/" + john["id"], None, withAuth=jacksAuth)
assert invitedUsers == [john]
doPost("shopping-list/accept-invitation/" + newShoppingList["id"], None, withAuth=johnsAuth)
shoppingList = doGet("shopping-list/get/" + newShoppingList["id"], withAuth=johnsAuth)
assert shoppingListsEqualButVersionsDiffer(shoppingList, newShoppingList)

print("Jack adds an item to the new shopping list.")
item = json.dumps({
    "id": "", 
    "version": "",
    "name": "1",
    "createdBy": "",
    "modifiedBy": "",
    "boughtBy": "",
    "stateChangedBy": "",
})
enrichedShoppingList = doPost("shopping-list/add-item/" + newShoppingList["id"], item, withAuth=jacksAuth)
assert len(enrichedShoppingList["items"]) == 1
item = enrichedShoppingList["items"][0]


print("Joe tries to set the item to bought.")
error = doPost("shopping-list/set-bought/" + newShoppingList["id"], json.dumps(item), withAuth=joesAuth)
assert error == "ShoppingList not found."
enrichedShoppingList = doGet("shopping-list/get-enriched/" + newShoppingList["id"], withAuth=jacksAuth)
assert len(enrichedShoppingList["items"]) == 1
item = enrichedShoppingList["items"][0]
assert item["boughtBy"] == None
assert item["stateChangedBy"] == jack["id"]


print("Jack sets the item to bought.")
enrichedShoppingList = doPost("shopping-list/set-bought/" + newShoppingList["id"], json.dumps(item), withAuth=jacksAuth)
assert len(enrichedShoppingList["items"]) == 1
item = enrichedShoppingList["items"][0]
assert item["boughtBy"] == jack["id"]
assert item["stateChangedBy"] == jack["id"]

print("John tries to set the item to bought again.")
error = doPost("shopping-list/set-bought/" + newShoppingList["id"], json.dumps(item), withAuth=johnsAuth)
assert error == "Cannot set ShoppingListItem to state bought."
enrichedShoppingList = doGet("shopping-list/get-enriched/" + newShoppingList["id"], withAuth=jacksAuth)
assert len(enrichedShoppingList["items"]) == 1
item = enrichedShoppingList["items"][0]
assert item["boughtBy"] == jack["id"]
assert item["stateChangedBy"] == jack["id"]

print("Joe tries to set the item to unbought.")
error = doPost("shopping-list/set-unbought/" + newShoppingList["id"], json.dumps(item), withAuth=joesAuth)
assert error == "ShoppingList not found."
enrichedShoppingList = doGet("shopping-list/get-enriched/" + newShoppingList["id"], withAuth=jacksAuth)
assert len(enrichedShoppingList["items"]) == 1
item = enrichedShoppingList["items"][0]
assert item["boughtBy"] == jack["id"]
assert item["stateChangedBy"] == jack["id"]

print("John sets the item to unbought.")
enrichedShoppingList = doPost("shopping-list/set-unbought/" + newShoppingList["id"], json.dumps(item), withAuth=johnsAuth)
assert len(enrichedShoppingList["items"]) == 1
item = enrichedShoppingList["items"][0]
assert item["boughtBy"] == None
assert item["stateChangedBy"] == john["id"]

print("Jack tries to set the item to unbought again.")
error = doPost("shopping-list/set-unbought/" + newShoppingList["id"], json.dumps(item), withAuth=jacksAuth)
assert error == "Cannot set ShoppingListItem to state unbought."
enrichedShoppingList = doGet("shopping-list/get-enriched/" + newShoppingList["id"], withAuth=jacksAuth)
assert len(enrichedShoppingList["items"]) == 1
item = enrichedShoppingList["items"][0]
assert item["boughtBy"] == None
assert item["stateChangedBy"] == john["id"]



print("Jack deletes his user account.")
deletedUser = doDelete("user/delete/" + jack["id"], withAuth=jacksAuth)

print("John tries to read Jack's shopping list.")
error = doGet("shopping-list/get-enriched/" + jacksShoppingList["id"], withAuth=johnsAuth)
assert error == "ShoppingList not found."
