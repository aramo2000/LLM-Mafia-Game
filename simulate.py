from game import MafiaGame
import json
import random

allSame = True

if allSame:
    mafia_game = MafiaGame("gemini")
    mafia_game.run()
else:
    llm_names = 2 * ["openai"] + 2 * ["gemini"] + 2 * ["grok"] + 2 * ["claude"] + 2 * ["deepseek"]
    random.shuffle(llm_names)
    mafia_game = MafiaGame.from_llm_list(llm_names)
    mafia_game.run()

with open("results.json", "w") as json_file:
    json.dump(mafia_game.game_data, json_file, indent=4)