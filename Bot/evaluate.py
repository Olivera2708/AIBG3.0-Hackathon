import globalVar
from helper import *
import copy

def valueInTile(currentState, playerNum):
    player = currentState["player" + str(playerNum)]

    if playerNum == globalVar.ourPlayer:
        x, y = getPlayerCoordinates(currentState)
    else:
        x, y = getOpponentCoordinates(currentState)
    opponentPlayer = currentState["player" + str(globalVar.opponentPlayer)]

    tileValue = globalVar.gameStateJSON["map"]["tiles"][x][y]["tileContent"]

    match tileValue["itemType"]:
        case "ENERGY":
            if player["energy"] + 20 > 100:
                addedEnergy = 20 - (player["energy"] + 20) % 100
            else:
                addedEnergy = 20
            return addedEnergy
        case "BOOSTER_NECTAR_30_PCT": 
            if player["nectar"] * 1.3 > 100:
                addedNectar = 100 - player["nectar"]
            else:
                addedNectar = 100 - player["nectar"] * 1.3
            return addedNectar
        case "BOOSTER_NECTAR_50_PCT":
            if player["nectar"] * 1.5 > 100:
                addedNectar = 100 - player["nectar"]
            else:
                addedNectar = 100 - player["nectar"] * 1.5
            return addedNectar
        case "BOOSTER_NECTAR_100_PCT":
            if player["nectar"] * 2 > 100:
                addedNectar = 100 - player["nectar"]
            else:
                addedNectar = 100 - player["nectar"] * 2
            return addedNectar
        case "HIVE": 
            return 20
        case "EMPTY":
            return -35
        case "MINUS_FIFTY_PCT_ENERGY": 
            return 150
        case "SUPER_HONEY": 
            return 250
        case "FREEZE":
            return 200
        case _:
            if player["nectar"] + tileValue["numOfItems"] > 100:
                addedNectar = tileValue["numOfItems"] - (player["nectar"] + tileValue["numOfItems"]) % 100
            else:
                addedNectar = tileValue["numOfItems"]
            return addedNectar
 
        
def distanceHive(currentState, playerNum):
    player = currentState["player" + str(playerNum)]
    x = player["x"]
    y = player["y"]

    hiveX = globalVar.gameStateJSON["player"+str(globalVar.opponentPlayer)]["hiveX"]
    hiveY = globalVar.gameStateJSON["player"+str(globalVar.opponentPlayer)]["hiveY"]

    energy = player["energy"]
    if (energy <= 0):
        energy = 1
    return (hiveX + hiveY - x - y)/energy*100


def movingDirections(currentState, playerNum):
    moves = getMoves(currentState, playerNum)
    player = "player" + str(playerNum)

    myState = copy.deepcopy(currentState)
    
    score1 = myState[player]["score"]
    nectar1 = currentState[player]["nectar"]
    moveCounter = 0
    eng = 0
    for move in moves:
        x = move[0]
        y = move[1]
        direction = move[2]
        energy = currentState[player]["energy"]
        while True:
            if checkTileType(x, y, currentState) != None:

                if x in myState["tiles"] and y in myState["tiles"][x]:
                    tile = myState["tiles"][x][y]
                else:
                    tile = globalVar.gameStateJSON["map"]["tiles"][x][y]

                myState = changeCurrentState(myState, tile, playerNum, x, y) #dodati u helper
                x, y = calculateNextStep(x, y, direction)
                myState[player]["x"] = x
                myState[player]["y"] = y
                moveCounter += 1
                energy -= 2
                if energy < 7:
                    break
            else:
                break
        eng += energy
    score2 = myState[player]["score"]
    nectar2 = currentState[player]["nectar"]
    if moveCounter == 0 or score1 == score2:
        return 0
    return (score2 - score1) // 10 + (nectar2-nectar1) // 5

def numOfFree(currentState, playerNum):
    # playerNum = getCurrentPlayerNum(currentState)
    moves = getMoves(currentState, playerNum)
    score = 0
    for move in moves:
        if not checkTileType(move[0], move[1], currentState):
            score += 10
    return score

def numOfSkip(playerNum):
    player = globalVar.gameStateJSON["player" + str(playerNum)]
    if player["numOfSkipATurnUsed"] == 146:
        return -10000
    return 0

def isHive(currentState, playerNum):
    player = currentState["player" + str(playerNum)]
    if playerNum == globalVar.ourPlayer:
        x, y = getPlayerCoordinates(currentState)
    else:
        x, y = getOpponentCoordinates(currentState)
    if ((x == 0 and y == 0) or (x == 26 and y == 8)) and player["nectar"] > 75:
        return 600
    return 0

def eval(currentState, playerNum):
    player = currentState["player" + str(playerNum)]
    ret = 0
    if player["nectar"] != 100:
        ret += valueInTile(currentState, playerNum)
    ret += movingDirections(currentState, playerNum)
    ret += numOfFree(currentState, playerNum)
    ret += numOfSkip(playerNum)
    ret += isHive(currentState, playerNum)
    if (player["energy"] < 50):
        ret += distanceHive(currentState, playerNum)
    if player["energy"] < 7:
        ret = -10000

    if globalVar.ourPlayer == playerNum:
        return -ret
    return ret