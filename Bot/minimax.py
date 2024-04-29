import globalVar
from helper import *
from evaluate import eval
import copy

def startAI():
    #ako smo u kosnici
    if (getPlayerCoordinates(globalVar.gameStateJSON) == [0, 0] and globalVar.ourPlayer == 1) or (getPlayerCoordinates(globalVar.gameStateJSON) == [26, 8] and globalVar.ourPlayer == 2):
        convertNum = tryFeedBee(globalVar.gameStateJSON, globalVar.ourPlayer)
        if convertNum != 0:
            return "feedBeeWithNectar", convertNum
        convertNum = tryConvert(globalVar.gameStateJSON, globalVar.ourPlayer)
        if convertNum != 0:
            return "convertNectarToHoney", convertNum
    if trySkip(globalVar.gameStateJSON, globalVar.ourPlayer):
        return "skipATurn",0
    #proci kroz sve akcije
    bestMove = findBestMove()
    print(bestMove)
    return "move", bestMove

def trySkip(currentState, playerNum):
    player = currentState["player" + str(globalVar.opponentPlayer)]
    if playerNum == globalVar.ourPlayer:
        player = currentState["player" + str(globalVar.ourPlayer)]
    if not isInHive(player):
        if player["energy"] < 7:
            return True

def tryFeedBee(currentState, playerNum):
    player = currentState["player" + str(playerNum)]
    currentNectar = player["nectar"]
    currentEnergy = player["energy"]
    if currentEnergy > 70 or currentNectar < 5:
        return 0
    # energy = currentEnergy
    # nectar = currentNectar
    # convertNum = 0
    # toConvert = 0
    # while energy < 100 and nectar > 0:
    #     convertNum += toConvert
    #     toConvert = nectar%20
    #     if toConvert == 0:
    #         toConvert = 20
    #     energy += toConvert*2
    #     nectar -= toConvert
    convertNum = (100 - currentEnergy)//2
    return convertNum

def tryConvert(currentState, playerNum):
    player = currentState["player" + str(playerNum)]
    return player["nectar"]//20

def evaluateTileNumber(x, y, direction, currentState, player, depth):
    bestNumberOfTiles = -1
    countTiles = 1

    if player == globalVar.ourPlayer:
        bestScore = float("inf") #tezi minimumu

        while True:
            countTiles += 1
            new_x, new_y = calculateNextStep(x, y, direction) #nova pozicija

            #provera tipa tile
            tileContent = checkTileType(new_x, new_y, currentState)
            if tileContent == None or currentState["player" + str(player)]["energy"] < 7: #ako je los tile
                break

            #funkcija koja menja current state
            if new_x in currentState["tiles"] and new_y in currentState["tiles"][new_x]:
                tile = currentState["tiles"][new_x][new_y]
                newCurrentState = copy.deepcopy(currentState)
                newCurrentState = changeCurrentState(newCurrentState, tile, player, new_x, new_y)
            else:
                tile = globalVar.gameStateJSON["map"]["tiles"][new_x][new_y]
                newCurrentState = copy.deepcopy(currentState)
                newCurrentState = changeCurrentState(newCurrentState, tile, player)

            result = miniMax(float("-inf"), float("inf"), depth-1, globalVar.opponentPlayer, newCurrentState) + eval(newCurrentState, player)
            if countTiles <= 3:
                result += (4 - countTiles)*550

            if result < bestScore:
                if currentState["player"+str(player)]["energy"] > bestNumberOfTiles*2+3:
                    bestScore = result
                    bestNumberOfTiles = countTiles

            x = new_x
            y = new_y

    else:
        bestScore = float("-inf") #tezi maksimumu

        while True:
            countTiles += 1
            new_x, new_y = calculateNextStep(x, y, direction) #nova pozicija

            #provera tipa tile
            tileContent = checkTileType(new_x, new_y, currentState)
            if tileContent == None or currentState["player" + str(player)]["energy"] < 7: #ako je los tile
                break

            #funkcija koja menja current state
            if new_x in currentState["tiles"] and new_y in currentState["tiles"][new_x]:
                tile = currentState["tiles"][new_x][new_y]
                newCurrentState = copy.deepcopy(currentState)
                newCurrentState = changeCurrentState(newCurrentState, tile, player, new_x, new_y)
            else:
                tile = globalVar.gameStateJSON["map"]["tiles"][new_x][new_y]
                newCurrentState = copy.deepcopy(currentState)
                newCurrentState = changeCurrentState(newCurrentState, tile, player)

            #inace evaluacija trenutnog stanja i zvanje minimax
            result = miniMax(float("-inf"), float("inf"), depth-1, globalVar.ourPlayer, newCurrentState) + eval(newCurrentState, player)
            if countTiles <= 3:
                result -= (4 - countTiles)*550
            if result > bestScore:
                if currentState["player"+str(player)]["energy"] > bestNumberOfTiles*2+3:
                    bestScore = result
                    bestNumberOfTiles = countTiles

            x = new_x
            y = new_y

    return bestNumberOfTiles, bestScore


#uvek ulazi iz naseg i to je prvi potez
def findBestMove():
    bestMove = [] #smer, broj koraka
    minVal = float("inf") #mi smo igrac koji tezi minimalnim vrednostima 
    for x, y, direction in getMoves(globalVar.gameStateJSON, globalVar.ourPlayer):
        #provera jel moze da ide ovamo
        currentState = makeCurrentState()
        tileContent = checkTileType(x, y, currentState)
        if tileContent == None:
            continue

        #funkcija koja menja current state
        currentState = changeCurrentState(currentState, globalVar.gameStateJSON["map"]["tiles"][x][y], globalVar.ourPlayer)

        #evaluirati trenutno i pozvati minimax
        result = miniMax(float("-inf"), float("inf"), globalVar.DEPTH-1, globalVar.opponentPlayer, currentState) + eval(currentState, globalVar.ourPlayer)
        if result < minVal:
            minVal = result
            bestMove = [direction, 1]

        #bestNumberOfTiles i Score
        bestNumberOfTiles, bestScore = evaluateTileNumber(x, y, direction, currentState, globalVar.ourPlayer, globalVar.DEPTH)
        #proveriti da li je ovo dobijeno bolje od najboljeg ako jeste sacuvati
        if bestScore < minVal:
            if currentState["player"+str(globalVar.ourPlayer)]["energy"] > bestNumberOfTiles*2+3:
                minVal = bestScore
                bestMove = [direction, bestNumberOfTiles]

    return bestMove
   

def miniMax(alpha, beta, depth, player, currentState):
    if depth == 0 or isEnd(currentState, depth):
        return eval(currentState, player) #potrebno vratiti vrednost koliko je dobro

    if player == globalVar.ourPlayer:
        minVal = float("inf")

        doneSomething = False

        if (getPlayerCoordinates(currentState) == [0, 0] and globalVar.ourPlayer == 1) or (getPlayerCoordinates(currentState) == [26, 8] and globalVar.ourPlayer == 2):
            convertNum = tryFeedBee(currentState, player)
            if convertNum != 0:
                doneSomething = True
                newCurrentState = copy.deepcopy(currentState)
                newCurrentState["player"+str(player)]["energy"] += convertNum * 2
                newCurrentState["player"+str(player)]["nectar"] -= convertNum

                result = miniMax(alpha, beta, depth-1, globalVar.opponentPlayer, newCurrentState) + eval(newCurrentState, player)
                minVal = min(result, minVal)
            else:
                convertNum = tryConvert(currentState, player)
                if convertNum != 0:
                    doneSomething = True
                    newCurrentState = copy.deepcopy(currentState)
                    newCurrentState["player"+str(player)]["honey"] += convertNum
                    newCurrentState["player"+str(player)]["nectar"] -= convertNum*20

                    result = miniMax(alpha, beta, depth-1, globalVar.opponentPlayer, newCurrentState) + eval(newCurrentState, player)
                    minVal = min(result, minVal)

        if not doneSomething:
            if trySkip(currentState, player):
                newCurrentState = copy.deepcopy(currentState)
                newCurrentState["player"+str(player)]["energy"] += 5

                result = miniMax(alpha, beta, depth-1, globalVar.opponentPlayer, newCurrentState) + eval(newCurrentState, player)
                minVal = min(result, minVal)
            
            else:
                for x, y, direction in getMoves(currentState, globalVar.ourPlayer):
                    #provera jel moze da ide ovamo
                    tileContent = checkTileType(x, y, currentState)
                    if tileContent == None:
                        continue

                    #funkcija koja menja current state
                    if x in currentState["tiles"] and y in currentState["tiles"][x]:
                        tile = currentState["tiles"][x][y]
                        newCurrentState = copy.deepcopy(currentState)
                        newCurrentState = changeCurrentState(newCurrentState, tile, player, x, y)
                    else:
                        tile = globalVar.gameStateJSON["map"]["tiles"][x][y]
                        newCurrentState = copy.deepcopy(currentState)
                        newCurrentState = changeCurrentState(newCurrentState, tile, player)

                    #evaluirati trenutno i pozvati minimax
                    result = miniMax(alpha, beta, depth-1, globalVar.opponentPlayer, newCurrentState) + eval(newCurrentState, player)
                    
                    minVal = min(result, minVal)
                    # beta = min(beta, result)
                    # if beta <= alpha:
                    #     continue

                    #bestNumberOfTiles i Score
                    _, bestScore = evaluateTileNumber(x, y, direction, newCurrentState, globalVar.ourPlayer, depth)

                    #proveriti da li je ovo dobijeno bolje od najboljeg ako jeste sacuvati
                    minVal = min(bestScore, minVal)

        return minVal
    
    else:
        maxVal = float("-inf")

        doneSomething = False

        if (getOpponentCoordinates(currentState) == [0, 0]) or (getOpponentCoordinates(currentState) == [26, 8]):
            convertNum = tryFeedBee(currentState, player)
            if convertNum != 0:
                doneSomething = True
                newCurrentState = copy.deepcopy(currentState)
                newCurrentState["player"+str(player)]["energy"]+=convertNum*2
                newCurrentState["player"+str(player)]["nectar"]-=convertNum

                result = miniMax(alpha, beta, depth-1, globalVar.ourPlayer, currentState) + eval(currentState, player)
                maxVal = max(result, maxVal)

            else:
                convertNum = tryConvert(currentState, player)
                if convertNum != 0:
                    doneSomething = True
                    newCurrentState = copy.deepcopy(currentState)
                    newCurrentState["player"+str(player)]["honey"] += convertNum
                    newCurrentState["player"+str(player)]["nectar"] -= convertNum*20

                    result = miniMax(alpha, beta, depth-1, globalVar.ourPlayer, currentState) + eval(currentState, player)
                    maxVal = max(result, maxVal)
        
        if not doneSomething:
            if trySkip(currentState, player):
                newCurrentState = copy.deepcopy(currentState)
                newCurrentState["player"+str(player)]["energy"]+=5

                result = miniMax(alpha, beta, depth-1, globalVar.ourPlayer, currentState) + eval(currentState, player)
                maxVal = max(result, maxVal)
            
            else:
                for x, y, direction in getMoves(currentState, globalVar.opponentPlayer):
                    #provera jel moze da ide ovamo
                    tileContent = checkTileType(x, y, currentState)
                    if tileContent == None:
                        continue

                    #funkcija koja menja current state
                    if x in currentState["tiles"] and y in currentState["tiles"][x]:
                        tile = currentState["tiles"][x][y]
                        newCurrentState = copy.deepcopy(currentState)
                        newCurrentState = changeCurrentState(newCurrentState, tile, player, x, y)
                    else:
                        tile = globalVar.gameStateJSON["map"]["tiles"][x][y]
                        newCurrentState = copy.deepcopy(currentState)
                        newCurrentState = changeCurrentState(newCurrentState, tile, player)

                    #evaluirati trenutno i pozvati minimax
                    result = miniMax(alpha, beta, depth-1, globalVar.ourPlayer, newCurrentState) + eval(newCurrentState, player)
                    maxVal = max(result, maxVal)
                    # alpha = max(alpha, result)
                    # if beta <= alpha:
                    #     continue

                    #bestNumberOfTiles i Score
                    _, bestScore = evaluateTileNumber(x, y, direction, newCurrentState, globalVar.opponentPlayer, depth)

                    #proveriti da li je ovo dobijeno bolje od najboljeg ako jeste sacuvati
                    maxVal = max(maxVal, bestScore)

        return maxVal

def isEnd(currentState, depth):
    #maksimalan broj poteza je 500, dakle treba nam brojac poteza
    if globalVar.gameStateJSON["numOfMove"] + depth/2 >= 300:
        return True
    
    #na mapi nema vise cveca
    if noMoreFlowers(currentState):
        return True

    #maksimalan broj skipATurn je 150
    if globalVar.gameStateJSON["player1"]["numOfSkipATurnUsed"] >= 150 or globalVar.gameStateJSON["player1"]["numOfSkipATurnUsed"] >= 150:
        return True

    return False

