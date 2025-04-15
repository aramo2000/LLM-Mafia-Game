from game import MafiaGame
import json

# Initialize the game with the LLM name ("openai" or others)
mafia_game = MafiaGame("openai")
mafia_game.run()

with open("game_results.json", "w") as json_file:
    json.dump(mafia_game.game_data, json_file, indent=4)
