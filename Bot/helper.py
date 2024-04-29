import globalVar

def getPlayerCoordinates(currentState):
    player = currentState["player" + str(globalVar.ourPlayer)]
    return [player['x'], player['y']]

def getOpponentCoordinates(currentState):
    player = currentState["player" + str(globalVar.opponentPlayer)]
    return [player['x'], player['y']]


def getMoves(currentState, playerNum):
    xy = getOpponentCoordinates(currentState)
    
    if (playerNum == globalVar.ourPlayer):
        xy = getPlayerCoordinates(currentState)

    if (xy[0] % 2 == 0):
        return [[xy[0]-1, xy[1]-1, "q"], [xy[0]-2, xy[1], "w"], [xy[0]-1, xy[1], "e"], [xy[0]+1, xy[1], "d"], [xy[0]+2, xy[1], "s"], [xy[0]+1, xy[1]-1, "a"]]
    else:
        return [[xy[0]-1, xy[1], "q"], [xy[0]-2, xy[1], "w"], [xy[0]-1, xy[1]+1, "e"], [xy[0]+1, xy[1]+1, "d"], [xy[0]+2, xy[1], "s"], [xy[0]+1, xy[1], "a"]]

def calculateNextStep(x, y, direction):
    match direction:
        case "w": return x-2, y
        case "s": return x+2, y

    if x % 2 == 0:
        match direction:
            case "q": return x-1, y-1
            case "e": return x-1, y
            case "d": return x+1, y
            case "a": return x+1, y-1
    else:
        match direction:
            case "q": return x-1, y
            case "e": return x-1, y+1
            case "d": return x+1, y+1
            case "a": return x+1, y

#proverava da li ima jos cvetova na mapi
def noMoreFlowers(currentState):
    for tiles in globalVar.gameStateJSON["map"]["tiles"]:
        for tile in tiles:
            if (tile["row"] not in currentState["tiles"]) or ((tile["row"] in currentState["tiles"]) and tile["column"] not in currentState["tiles"][tile["row"]]):
                if (tile["tileContent"]["itemType"] in globalVar.FLOWERS):
                    return False
    return True

def checkTileType(x, y, currentState):
    if (x < 0 or x > 26) or (x % 2 == 0 and (y > 8 or y < 0)) or (x % 2 == 1 and (y > 7 or y < 0)):
        return None
    
    if ([x, y] == [globalVar.gameStateJSON["player"+str(globalVar.opponentPlayer)]["hiveX"], globalVar.gameStateJSON["player"+str(globalVar.opponentPlayer)]["hiveY"]]):
        return None

    tileContent = globalVar.gameStateJSON["map"]["tiles"][x][y]["tileContent"]
    if x in currentState["tiles"] and y in currentState["tiles"][x]:
        tileContent = currentState["tiles"][x][y]
    
    if tileContent["itemType"] == "POND" or tileContent["itemType"] == "HOLE":
        return None
    
    if [x, y] == getOpponentCoordinates(currentState):
        return None
    
    return tileContent

def makeCurrentState():
    newCurrentState = {
        "player1": {
            "x" : globalVar.gameStateJSON["player1"]["x"],
            "y" : globalVar.gameStateJSON["player1"]["y"],
            "energy" : globalVar.gameStateJSON["player1"]["energy"],
            "nectar": globalVar.gameStateJSON["player1"]["nectar"],
            "score": globalVar.gameStateJSON["player1"]["score"],
            "honey": globalVar.gameStateJSON["player1"]["honey"],
            "frozen": globalVar.gameStateJSON["player1"]["frozen"]
        },
        "player2": {
            "x" : globalVar.gameStateJSON["player2"]["x"],
            "y" : globalVar.gameStateJSON["player2"]["y"],
            "energy" : globalVar.gameStateJSON["player2"]["energy"],
            "nectar": globalVar.gameStateJSON["player2"]["nectar"],
            "score": globalVar.gameStateJSON["player2"]["score"],
            "honey": globalVar.gameStateJSON["player2"]["honey"],
            "frozen": globalVar.gameStateJSON["player2"]["frozen"]
        },
        "tiles": { 
        }
    }
    return newCurrentState


def changeCurrentState(currentState, tile, playerNum, x = -1, y = -1):
    if "row" in tile:
        x = tile["row"]
        y = tile["column"]
        itemType = tile["tileContent"]["itemType"]
        numOfItems = tile["tileContent"]["numOfItems"]
    else:
        itemType = tile["itemType"]
        numOfItems = tile["numOfItems"]
    
    # provera koji je igrac
    player = "player" + str(globalVar.ourPlayer)
    opponent = "player"+ str(globalVar.opponentPlayer)
    if playerNum == globalVar.opponentPlayer:
        player = "player"+str(globalVar.opponentPlayer)
        opponent = "player"+str(globalVar.ourPlayer)

    #pomera igraca na tile
    currentState[player]["x"] = x
    currentState[player]["y"] = y
    currentState[player]["energy"] -= 2
    
    currentNectar = currentState[player]["nectar"]
    currentEnergy = currentState[player]["energy"]

    emptyContent = {
        "itemType" : "EMPTY",
        "numOfItems" : 0
    }

    if itemType in globalVar.FLOWERS or itemType in globalVar.BOOSTERS:
        if currentNectar < 100:
            if currentState["tiles"] == {}:
                currentState["tiles"][x] = {}
            if x not in currentState["tiles"]:
                currentState["tiles"][x] = {}
            currentState["tiles"][x][y] = emptyContent

            #dodaje score koliko je zapravo dobio nectara
            pointsToAdd = numOfItems
            if (currentNectar + numOfItems) > 100:
                pointsToAdd = numOfItems - (currentNectar + numOfItems - 100)
            currentState[player]["nectar"] += pointsToAdd
            currentState[player]["score"] += pointsToAdd

    else:
        match itemType:
            case "FREEZE":#100 p
                currentState[opponent]["frozen"]=True
                if currentState["tiles"] == {}:
                    currentState["tiles"][x] = {}
                if x not in currentState["tiles"]:
                    currentState["tiles"][x] = {}
                currentState["tiles"][x][y] = emptyContent
                currentState[player]["score"] += 100

            case "MINUS_FIFTY_PCT_ENERGY":#50 p
                currentState[opponent]["energy"] = currentState[opponent]["energy"]/2
                if currentState["tiles"] == {}:
                    currentState["tiles"][x] = {}
                if x not in currentState["tiles"]:
                    currentState["tiles"][x] = {}
                currentState["tiles"][x][y] = emptyContent
                currentState[player]["score"] += 50

            case "SUPER_HONEY":#150 p
                if currentState["tiles"] == {}:
                    currentState["tiles"][x] = {}
                if x not in currentState["tiles"]:
                    currentState["tiles"][x] = {}
                currentState["tiles"][x][y] = emptyContent
                currentState[player]["score"] += 150
                currentState[player]["honey"] += 5

            case "ENERGY":
                if currentEnergy < 100:
                    if currentState["tiles"] == {}:
                        currentState["tiles"][x] = {}
                    if x not in currentState["tiles"]:
                        currentState["tiles"][x] = {}
                    currentState["tiles"][x][y] = emptyContent
                pointsToAdd = numOfItems
                if (currentEnergy+numOfItems) > 100:
                    pointsToAdd = numOfItems - (currentEnergy + numOfItems - 100)
                currentState[player]["energy"] += pointsToAdd
                currentState[player]["score"] += pointsToAdd
                
    return currentState

def isInHive(player):
    if (player["x"]==0 and player["y"]==0) or (player["x"]==26 and player["y"]==8):
        return True
  
    return False
