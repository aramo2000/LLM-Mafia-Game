from game import MafiaGame
import json
import random

allSame = False

if allSame:
    mafia_game = MafiaGame("grok") #openai/gemini/grok working    -    claude/deepseek not working as expected with the prompts
    mafia_game.run()
else:
    llm_names = 4 * ["openai"] + 3 * ["gemini"] + 3 * ["grok"]
    random.shuffle(llm_names)
    mafia_game = MafiaGame.from_llm_list(llm_names)
    mafia_game.run()

with open("results.json", "w") as json_file:
    json.dump(mafia_game.game_data, json_file, indent=4)




# To add last say after dying

# To provide the way that each player died previously during voting and some strategies for the players.
# Joseph to test why claude and deepseek are not following orders.
