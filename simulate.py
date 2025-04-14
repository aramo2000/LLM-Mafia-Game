from game import MafiaGame

mafia_game = MafiaGame("openai")
game_log = mafia_game.run()
with open("game_total_record.txt", "w") as file:
    file.write(game_log)