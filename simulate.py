from game import MafiaGame
import json
import random

allSame = True

if allSame:
    mafia_game = MafiaGame("openai") #openai/gemini/grok working    -    claude/deepseek not working as expected with the prompts
else:
    llm_names = 2 * ["openai"] + 2 * ["gemini"] + 2 * ["grok"] + 2 * ["claude"] + 2 * ["deepseek"]
    random.shuffle(llm_names)
    mafia_game = MafiaGame.from_llm_list(llm_names)

number_of_games = 2
games_total_record = []
for i in range(number_of_games):
    if i != 0:
        with open("games_total_record.json", "r") as file:
            games_total_record = json.load(file)
    mafia_game.run()
    games_total_record.append(mafia_game.game_data)
    with open("games_total_record.json", "w") as file:
        json.dump(games_total_record, file, indent=4)