import api
import globalVar
from minimax import startAI
import time


if __name__ == "__main__":
    api.initializeGame()
    print(globalVar.gameId)

    while True:
        start = time.time()
        moveType, bestMove = startAI()
        match moveType:
            case "move":
                globalVar.gameStateJSON = api.moveBee(bestMove[0], bestMove[1])
            case "feedBeeWithNectar":
                globalVar.gameStateJSON = api.feedBeeWithNectar(bestMove)
            case "convertNectarToHoney":
                globalVar.gameStateJSON = api.convertNectarToHoney(bestMove)
            case "skipATurn":
                globalVar.gameStateJSON = api.skipATurn()
        end = time.time()
        print(f"Time -> {end-start} -> {moveType}")
        if (globalVar.gameStateJSON["winnerTeamName"] != None):
            print(globalVar.gameStateJSON)
            break