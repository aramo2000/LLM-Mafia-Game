from game import MafiaGame
import json
import random
from pprint import pprint
from collections import Counter
from utils import retry


def validate_llms_and_roles(llms_lists, roles_tuples, number_of_games):
    target_detective = number_of_games // 5
    target_don = number_of_games // 5
    target_mafia = (2 * number_of_games) // 5
    target_civilian = (6 * number_of_games) // 5

    llm_role_counts = {llm: {"detective": 0, "don": 0, "mafia": 0, "civilian": 0} for llm in
                       set([llm for sublist in llms_lists for llm in sublist])}

    for game_idx in range(number_of_games):
        llms = llms_lists[game_idx]
        roles = roles_tuples[game_idx]

        llm_counter = Counter(llms)
        for llm, count in llm_counter.items():
            assert count == 2, f"LLM '{llm}' is not used exactly twice in game {game_idx + 1}!"

        role_counter = Counter(zip(llms, roles))
        for (llm, role), count in role_counter.items():
            if role == 'detective':
                llm_role_counts[llm]["detective"] += count
            elif role == 'don':
                llm_role_counts[llm]["don"] += count
            elif role == 'mafia':
                llm_role_counts[llm]["mafia"] += count
            elif role == 'civilian':
                llm_role_counts[llm]["civilian"] += count

    for llm, counts in llm_role_counts.items():
        assert counts[
                   "detective"] == target_detective, f"LLM '{llm}' was assigned detective role {counts['detective']} times, expected {target_detective}!"
        assert counts[
                   "don"] == target_don, f"LLM '{llm}' was assigned don role {counts['don']} times, expected {target_don}!"
        assert counts[
                   "mafia"] == target_mafia, f"LLM '{llm}' was assigned mafia role {counts['mafia']} times, expected {target_mafia}!"
        assert counts[
                   "civilian"] == target_civilian, f"LLM '{llm}' was assigned civilian role {counts['civilian']} times, expected {target_civilian}!"
    return True


@retry()
def run_single_mafia_same(llm_name: str):
    game = MafiaGame(llm_name)
    game.run()
    return game.game_data


@retry()
def run_single_mafia_different(llm_names: list, preassigned_roles: list):
    game = MafiaGame.from_llm_list(llm_names, preassigned_roles)
    game.run()
    return game.game_data


def run_games_same_llm(llm_name: str, number_of_games: int, json_name: str):
    games_total_record = []
    for i in range(number_of_games):
        game_data = run_single_mafia_same(llm_name)
        if i != 0:
            with open(json_name, "r") as file:
                games_total_record = json.load(file)
        games_total_record.append(game_data)
        with open(json_name, "w") as file:
            json.dump(games_total_record, file, indent=4)
    return games_total_record


all_roles = []
all_llms = []


def run_games_different_llms(number_of_games: int, json_name: str):
    llms = ["openai", "gemini", "grok", "claude", "deepseek"]

    target_detective = number_of_games // 5
    target_don = number_of_games // 5
    target_mafia = (2 * number_of_games) // 5
    target_civilian = (6 * number_of_games) // 5

    role_counts = {
        llm: {"detective": target_detective, "don": target_don, "mafia": target_mafia, "civilian": target_civilian} for
        llm in llms}

    all_assigned_llms = []
    games_total_record = []

    for game_idx in range(number_of_games):
        while True:
            try:
                temp_role_counts = {llm: role_counts[llm].copy() for llm in llms}
                players = []
                for llm in llms:
                    players.append(llm)
                    players.append(llm)

                random.shuffle(players)

                assigned_llms = []

                def pick_player(role, candidates):
                    for idx, llm in enumerate(candidates):
                        if temp_role_counts[llm][role] > 0:
                            return idx, llm
                    return None, None

                candidates = players.copy()

                idx, llm = pick_player("detective", candidates)
                assert llm is not None, "No available LLM for Detective!"
                assigned_llms.append(llm)
                temp_role_counts[llm]["detective"] -= 1
                candidates.pop(idx)

                idx, llm = pick_player("don", candidates)
                assert llm is not None, "No available LLM for Don!"
                assigned_llms.append(llm)
                temp_role_counts[llm]["don"] -= 1
                candidates.pop(idx)

                for _ in range(2):
                    idx, llm = pick_player("mafia", candidates)
                    assert llm is not None, "No available LLM for Mafia!"
                    assigned_llms.append(llm)
                    temp_role_counts[llm]["mafia"] -= 1
                    candidates.pop(idx)

                for _ in range(6):
                    idx, llm = pick_player("civilian", candidates)
                    assert llm is not None, "No available LLM for Civilian!"
                    assigned_llms.append(llm)
                    temp_role_counts[llm]["civilian"] -= 1
                    candidates.pop(idx)

                role_counts = temp_role_counts
                all_assigned_llms.append(assigned_llms)
                print(assigned_llms)
                break
            except AssertionError as e:
                print(f"⚠️ Retry because of game {game_idx + 1} due to assignment issue: {e}")
    pprint(role_counts)

    for llms_row in all_assigned_llms:
        roles = ["detective", "don", "mafia", "mafia", "civilian", "civilian", "civilian", "civilian", "civilian",
                 "civilian"]
        game_data = run_single_mafia_different(llm_names=llms_row, preassigned_roles=roles)
        games_total_record.append(game_data)
        with open(json_name, "w") as file:
            json.dump(games_total_record, file, indent=4)


run_games_different_llms(10, "different_4.json")
run_games_same_llm(llm_name="openai", number_of_games=1, json_name="mafia_same_10s_1.json")