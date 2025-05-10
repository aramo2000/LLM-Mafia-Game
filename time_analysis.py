import os
import json
from typing import Dict
from statistics import mean


def mafia_vs_civilian_response_times(folder_name: str, output_json: str) -> Dict:
    llm_durations = {}
    for file_name in os.listdir(folder_name):
        if file_name.endswith('.json'):
            full_path = os.path.join(folder_name, file_name)
            with open(full_path, 'r') as file:
                games = json.load(file)
            for game in games:
                for player in game['game_details']['players']:
                    llm = player['llm_name']
                    role = player['role']
                    durations = player.get('opinion_speech_generation_durations', [])

                    if llm not in llm_durations:
                        llm_durations[llm] = {'mafia': [], 'civilian': []}

                    if role in ['mafia', 'don']:
                        llm_durations[llm]['mafia'].extend(durations)
                    elif role in ['civilian', 'detective']:
                        llm_durations[llm]['civilian'].extend(durations)
    result = {}
    for llm, role_durations in llm_durations.items():
        mafia_times = role_durations['mafia']
        civilian_times = role_durations['civilian']
        result[llm] = {
            "avg_mafia_response_time": round(mean(mafia_times), 2) if mafia_times else 0,
            "avg_civilian_response_time": round(mean(civilian_times), 2) if civilian_times else 0,
            "num_mafia_statements": len(mafia_times),
            "num_civilian_statements": len(civilian_times)
        }
    with open(output_json, 'w') as f:
        json.dump(result, f, indent=4)
    return result
