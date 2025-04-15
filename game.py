import random
import json
from agent import Agent


class MafiaGame:
    def __init__(self, llm_name: str):
        self.num_players = 10
        self.players = []
        self.roles = ["civilian"] * 6 + ["detective"] + ["mafia"] * 2 + ["don"]
        random.shuffle(self.roles)
        self.llm_name = llm_name
        self.night_count = 0
        self.day_count = 0
        self.game_log = "**Mafia Game Starts**\n"
        self.opinion_log = ""
        self.votes_log = ""
        self.winner_log = ""
        self.alive = [True] * self.num_players

        mafia_indices = [i for i, role in enumerate(self.roles) if role == "mafia"]
        don_index = next(i for i, role in enumerate(self.roles) if role == "don")

        for i, role in enumerate(self.roles):
            if role in ["mafia", "don"]:
                self.players.append(Agent(
                    llm_name=llm_name,
                    player_name=f"player_{i}",
                    player_role=role,
                    mafia_player_indices=mafia_indices,
                    don_index=don_index
                ))
            else:
                self.players.append(Agent(
                    llm_name=llm_name,
                    player_name=f"player_{i}",
                    player_role=role,
                    mafia_player_indices=[]
                ))

        # Initialize game data storage
        self.game_data = {
            "game_details": {
                "start_time": "2025-04-14T10:00:00Z",
                "players": [],
                "mafia_players": [],
                "detective_player": "",
                "game_log": [],
                "game_outcome": {}
            }
        }
        self._initialize_players()

    def _initialize_players(self):
        # Initialize player details for the game
        for i, player in enumerate(self.players):
            player_data = player.get_player_info()
            self.game_data["game_details"]["players"].append(player_data)

        # Track mafia players and detective player
        mafia_players = [player.player_name for player in self.players if player.role in ["mafia", "don"]]
        self.game_data["game_details"]["mafia_players"] = mafia_players
        self.game_data["game_details"]["detective_player"] = next(
            (player.player_name for player in self.players if player.role == "detective"), None)

    def get_alive_players(self):
        return [i for i, alive in enumerate(self.alive) if alive]

    def night_phase(self):
        self.night_count += 1
        alive_players = self.get_alive_players()
        alive_mafia = [i for i in alive_players if self.roles[i] in ["mafia", "don"]]
        alive_civilians = [i for i in alive_players if self.roles[i] not in ["mafia", "don"]]

        mafia_votes = []

        # Mafia members vote
        for i in alive_mafia:
            vote = self.players[i].decide_kill(self.game_log, alive_players)
            mafia_votes.append((i, vote))

        # Decide final target
        don_alive = any(self.roles[i] == "don" for i in alive_mafia)
        if don_alive:
            don_index = next(i for i in alive_mafia if self.roles[i] == "don")
            final_target = self.players[don_index].decide_kill(
                self.game_log,
                alive_players,
                mafia_votes=mafia_votes  # Pass mafia votes to Don
            )
        else:
            # Mafia majority vote logic
            vote_counts = {}
            for _, vote in mafia_votes:
                vote_counts[vote] = vote_counts.get(vote, 0) + 1

            max_votes = max(vote_counts.values())
            top_choices = [v for v, count in vote_counts.items() if count == max_votes]
            final_target = random.choice(top_choices)

        # Detective investigates
        detective_index = next((i for i in alive_players if self.roles[i] == "detective"), None)
        investigation_result = None
        if detective_index is not None:
            investigate_target = self.players[detective_index].investigate(self.game_log, alive_players)
            is_mafia = self.roles[investigate_target] in ["mafia", "don"]
            self.players[detective_index].investigations.append(
                f"player_{investigate_target} - Mafia: {is_mafia}"
            )
            investigation_result = {
                f"player_{detective_index}": {
                    "investigated": f"player_{investigate_target}",
                    "result": is_mafia
                }
            }

        self.alive[final_target] = False
        self.game_log += f"\nNight {self.night_count}: Mafia killed player_{final_target}"
        self.players[final_target].status = "dead"  # Update player status to "dead"

        # Optional: update game_data["game_log"] if you're logging JSON format
        if hasattr(self, "game_data"):
            self.game_data["game_details"]["game_log"].append({
                "night": self.night_count,
                "mafia_kill": f"player_{final_target}",
                "detective_investigation": investigation_result or {}
            })

    import random

    def day_phase(self):
        self.day_count += 1
        alive_players = self.get_alive_players()

        self.game_log += f"\n\nDay {self.day_count} Begins"
        self.game_data["game_details"]["game_log"].append({
            "day": self.day_count,
            "events": []  # Initialize events list for the day
        })

        # Randomly select the first speaker for the opinion phase
        random_start_player = random.choice(alive_players)
        start_index = alive_players.index(random_start_player)
        # Rotate the list to start from the random player
        alive_players = alive_players[start_index:] + alive_players[:start_index]

        # Each player gives a statement and logs it as an event
        for i in alive_players:
            statement = self.players[i].speak_opinion(self.game_log)
            self.opinion_log += f"\nplayer_{i} says: {statement}"
            self.game_log += f"\nplayer_{i} says: {statement}"
            # Add the player's statement to the day's events
            self.game_data["game_details"]["game_log"][-1]["events"].append({
                "player_id": f"player_{i}",
                "statement": statement
            })

        vote_counts = {n: 0 for n in alive_players}
        no_one_votes = 0
        votes_and_reasons = []  # To store votes and reasons for visibility

        # Randomly select the first voter for the voting phase
        random_start_player = random.choice(alive_players)
        start_index = alive_players.index(random_start_player)
        # Rotate the list to start from the random player
        alive_players = alive_players[start_index:] + alive_players[:start_index]

        for i in alive_players:
            # Before voting, show past votes and reasons
            past_votes = "\n".join([f"player_{voter} voted for player_{target} - Reason: {reason}"
                                    for voter, target, reason in votes_and_reasons])
            vote, reason = self.players[i].vote_day(self.game_log, alive_players, past_votes)
            if vote == -1:  # Vote to 'no one'
                no_one_votes += 1
                vote_statement_with_reason = f"player_{i} voted to eliminate no one - Reason: {reason}"
            else:
                vote_counts[vote] += 1
                vote_statement_with_reason = f"player_{i} voted to eliminate player_{vote} - Reason: {reason}"

            # Store the current vote and reason
            votes_and_reasons.append((i, vote, reason))

            self.votes_log += f"\n{vote_statement_with_reason}"
            self.game_log += f"\n{vote_statement_with_reason}"

            # Add voting actions to the day's events
            self.game_data["game_details"]["game_log"][-1]["events"].append({
                "player_id": f"player_{i}",
                "vote": f"player_{vote}" if vote != -1 else "no one",
                "reason": reason
            })

        most_votes_player = max(vote_counts, key=vote_counts.get)
        most_votes_count = vote_counts[most_votes_player]

        if most_votes_count <= no_one_votes:  # No one should be eliminated
            self.game_log += "\nNo elimination this round."
            self.game_data["game_details"]["game_log"][-1]["elimination"] = "no elimination this round"
        else:
            self.alive[most_votes_player] = False
            self.game_log += f"\nDay: player_{most_votes_player} was voted out by the town/players of the game"
            self.players[most_votes_player].status = "dead"  # Update player status to "dead"
            self.game_data["game_details"]["game_log"][-1]["elimination"] = f"player_{most_votes_player} was voted out"

    def check_win_condition(self):
        alive_roles = [self.roles[i] for i in self.get_alive_players()]
        mafia_count = sum(1 for r in alive_roles if r in ["mafia", "don"])
        good_count = len(alive_roles) - mafia_count

        if mafia_count == 0:
            self.winner_log = "Good players win!"
            self.game_log += f"\n\n{self.winner_log}"
            self.game_data["game_details"]["game_outcome"] = {
                "winner": "Good players win!",
                "reason": "All Mafia members were eliminated."
            }
            return True
        elif mafia_count >= good_count:
            self.winner_log = "Mafia wins!"
            self.game_log += f"\n\n{self.winner_log}"
            self.game_data["game_details"]["game_outcome"] = {
                "winner": "Mafia wins!",
                "reason": "Mafia outnumbered the good players."
            }
            return True
        return False

    def run(self) -> str:
        while not self.check_win_condition():
            print(self.game_log)
            self.night_phase()
            if self.check_win_condition():
                break
            self.day_phase()
        print("\n--- Game Over ---")

        # Save the game data to a JSON file
        with open('game_results.json', 'w') as json_file:
            # Ensure player status is updated (alive or dead) before saving
            for i, player in enumerate(self.players):
                # Update the player's status based on whether they're alive or dead
                if self.alive[i]:
                    player.status = "alive"
                else:
                    player.status = "dead"

                # Add player status, role, and LLM name to the final data
                self.game_data["game_details"]["players"][i]["status"] = player.status
                self.game_data["game_details"]["players"][i]["llm_name"] = player.llm_name

            # Write the updated game data to the JSON file
            json.dump(self.game_data, json_file, indent=4)

        return self.game_log

