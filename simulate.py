from game import MafiaGame
import json
import random

number_of_games = 1
allSame = False

if allSame:
    mafia_game = MafiaGame("openai")
else:
    llm_names = 2 * ["openai"] + 2 * ["gemini"] + 2 * ["grok"] + 2 * ["claude"] + 2 * ["deepseek"]
    # llm_names = 10 * ["openai"]
    random.shuffle(llm_names)
    mafia_game = MafiaGame.from_llm_list(llm_names)
games_total_record = []
for i in range(number_of_games):
    if i != 0:
        with open("games_total_record_IO.json", "r") as file:
            games_total_record = json.load(file)
    mafia_game.run()
    games_total_record.append(mafia_game.game_data)
    with open("games_total_record_IO.json", "w") as file:
        json.dump(games_total_record, file, indent=4)