import globalVar
import requests
import json

URL_TRAIN = "/train"
URL_BASE = "http://localhost:8082"
URL_JOIN = "/joinGame?playerId=1&gameId=123"
URL_MAKEGAME = "/makeGame"
URL_MOVE = "/move"

#ovde pre battle u false
isTrainMode = True

def initializeGame():
    data = {
        "playerId": globalVar.PLAYER_ID,
        "playerSpot": 1
    }

    url = URL_BASE
    if isTrainMode:
        url += URL_TRAIN 
    url += URL_MAKEGAME

    #dobijanje podataka
    request = requests.post(url=url,json = data)
    globalVar.gameStateJSON = json.loads(request.text)
    globalVar.gameId = globalVar.gameStateJSON["gameId"]


def getData():
    pass

def createURL(moveType):
    url = URL_BASE
    if isTrainMode:
        url += URL_TRAIN
    url += "/" + moveType
    return url
    
def moveBee(direction, numberOfTiles):
    move = {
        "gameId": globalVar.gameId,
        "playerId": globalVar.PLAYER_ID,
        "direction": direction,
        "distance": numberOfTiles
    }
    request = requests.post(url=createURL("move"),json=move)
    gameState = json.loads(request.text)
    return gameState

def convertNectarToHoney(ammountOfHoney):
    honey ={
        "gameId": globalVar.gameId,
        "playerId": globalVar.PLAYER_ID,
        "amountOfHoneyToMake": ammountOfHoney
    }
    request = requests.post(url=createURL("convertNectarToHoney"),json=honey)
    gameState = json.loads(request.text)
    return gameState

def feedBeeWithNectar(ammountOfNectar):
    nectar ={
        "gameId": globalVar.gameId,
        "playerId": globalVar.PLAYER_ID,
        "amountOfNectarToFeedWith": ammountOfNectar
    }
    request = requests.post(url=createURL("feedBeeWithNectar"),json=nectar)
    gameState = json.loads(request.text)
    return gameState

def skipATurn():
    nectar ={
        "gameId": globalVar.gameId,
        "playerId": globalVar.PLAYER_ID
    }
    request = requests.post(url=createURL("skipATurn"),json=nectar)
    gameState = json.loads(request.text)
    return gameState
        

