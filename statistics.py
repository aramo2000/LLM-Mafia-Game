import json
from typing import List, Dict



def llms_vote_stats(game_records: List[Dict], llms_used: List[str]) -> dict :
    stats = {llm_name:{"civilian_correct_votes":0, "got_civilian_votes_as_mafia":0, "civilian_no_one":0} for llm_name in llms_used}

    for game in game_records:
        players_info = {player["player_id"]:player for player in game["game_details"]["players"]}
        mafia_names = [player["player_id"] for player in game["game_details"]["players"] if player["role"] in {"mafia","don"}]
        for log in game["game_details"]["game_log"]:
            if "day" in log:
                for event in log["events"]:
                    if "vote" in event:
                        voter_name = event["player_id"]
                        voted_on_name = event["vote"]

                        if voted_on_name in mafia_names and players_info[voter_name]["role"] == "civilian" and event["vote"] != "no one":
                            stats[players_info[voter_name]["llm_name"]]["civilian_correct_votes"] +=1
                            stats[players_info[voted_on_name]["llm_name"]]["got_civilian_votes_as_mafia"] +=1

                        if players_info[voter_name]["role"] == "civilian" and event["vote"] == "no one":
                            stats[players_info[voter_name]["llm_name"]]["civilian_no_one"] += 1

    return stats




with open("results.json", "r") as file:
    games_total_record = json.load(file)

print(llms_vote_stats(games_total_record, ["openai","claude", "gemini", "deepseek","grok"]))