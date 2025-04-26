from game import MafiaGame
import json
import random

allSame = False

if allSame:
    mafia_game = MafiaGame("openai")
else:
    llm_names = 2 * ["openai"] + 2 * ["gemini"] + 2 * ["grok"] + 2 * ["claude"] + 2 * ["deepseek"]
    random.shuffle(llm_names)
    mafia_game = MafiaGame.from_llm_list(llm_names)

number_of_games = 1
games_total_record = []
for _ in range(number_of_games):
    mafia_game.run()
    games_total_record.append(mafia_game.game_data)

with open("game_results.json", "w") as json_file:
    json.dump(games_total_record, json_file, indent=4)