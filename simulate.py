from game import MafiaGame
import json
import random

allSame = False

if allSame:
    mafia_game = MafiaGame("deepseek") #openai/gemini/grok working    -    claude/deepseek not working as expected with the prompts
    mafia_game.run()
else:
    llm_names = 2 * ["openai"] + 2 * ["gemini"] + 2 * ["grok"] + 2 * ["claude"] + 2 * ["deepseek"]
    random.shuffle(llm_names)
    mafia_game = MafiaGame.from_llm_list(llm_names)
    mafia_game.run()

with open("results.json", "w") as json_file:
    json.dump(mafia_game.game_data, json_file, indent=4)

# Joseph to test why claude and deepseek are not following orders from prompts. ok bro