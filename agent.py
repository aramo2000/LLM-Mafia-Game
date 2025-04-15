import random
from typing import List
import config
import prompts_constants
from token_utils import count_openai_input_tokens, count_openai_output_tokens


class Agent:
    def __init__(self, llm_name: str, player_name: str, player_role: str, mafia_player_indices: List[int], don_index: int = None):
        self.llm_name = llm_name  # Store LLM name
        self.player_name = player_name
        self.role = player_role
        self.status = "alive"  # Default status is alive
        self.input_tokens_used = 0
        self.output_tokens_used = 0
        self.votes = []
        self.statements = []
        self.investigations = []

        if self.role in ["mafia", "don"]:
            self.mafia_players = [f"player_{i}" for i in mafia_player_indices]
            self.don = f"player_{don_index}" if don_index is not None else "Unknown"
        else:
            self.mafia_players = []
            self.don = None

    def get_player_info(self):
        # Return a dictionary with the player's information
        return {
            "player_id": self.player_name,
            "role": self.role,
            "status": self.status,
            "llm_name": self.llm_name  # This ensures the LLM name is tracked
        }

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        if self.llm_name == "openai":
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            input_tokens = count_openai_input_tokens(messages, model=config.OPENAI_MODEL)
            llm_response = config.OPENAI_CLIENT.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=messages,
                temperature=0.3,
            )
            output_text = llm_response.choices[0].message.content.strip()
            output_tokens = count_openai_output_tokens(output_text, model=config.OPENAI_MODEL)

            self.input_tokens_used += input_tokens
            self.output_tokens_used += output_tokens
            return output_text
        else:
            raise NotImplementedError(f"LLM {self.llm_name} not supported yet.")

    def _build_system_prompt(self):
        rules = prompts_constants.SYSTEM_PROMPTS["rules"]
        role_prompt = prompts_constants.SYSTEM_PROMPTS.get(self.role, "")

        mafia_prompt = ""
        if self.role in ["mafia", "don"]:
            mafia_list = ", ".join(self.mafia_players)
            mafia_prompt += f"\nYou are part of the Mafia. The Don is {self.don}. The other mafia players are: {mafia_list}."

        return f"{rules}\n\n{role_prompt}\n\nYou are {self.player_name}. Your role is {self.role}.{mafia_prompt}"

    def speak_opinion(self, game_log: str) -> str:
        system_prompt = self._build_system_prompt()
        investigation_history = ""
        if self.role == "detective" and self.investigations:
            investigation_history = "Here is your investigation history:\n" + "\n".join(self.investigations) + "\n"

        user_prompt = (
            f"Here is what happened in the game so far:\n{game_log}\n\n"
            f"{investigation_history}"
            f"As {self.player_name} (role: {self.role}), please express your thoughts and suspicions about who could be Mafia. "
            "Consider your role and any relevant interactions you've had. Your reason should be logical and persuasive.\n"
            "Return only your statement.The statement should be brief and not exceed 3-4 sentences in length to keep it concise.\n"
        )
        statement = self._call_llm(system_prompt, user_prompt)
        self.statements.append({
            "player_id": self.player_name,
            "statement": statement
        })
        return statement

    def vote_day(self, game_log: str, nominees: list[int], past_votes: str = "") -> tuple:
        nominee_names = [f"player_{i}" for i in nominees]
        system_prompt = self._build_system_prompt()
        user_prompt = (
            f"Here is what happened in the game so far:\n{game_log}\n\n"
            f"The following players are nominated for elimination: {', '.join(nominee_names)}.\n"
            f"Past votes and reasons:\n{past_votes}\n\n"
            "Choose who you want to eliminate or vote for no one.\n"
            "First provide the player you want to vote for (or 'no one'). Then provide your reason on the next line.\n"
            "Format: player_# or 'no one'\n\"Reason\"\n"
        )
        response = self._call_llm(system_prompt, user_prompt)

        try:
            lines = response.split("\n", 1)
            vote_choice = lines[0].strip()
            reason = lines[1].strip() if len(lines) > 1 else "No reason provided"

            self.votes.append({
                "player_id": self.player_name,
                "vote": vote_choice,
                "reason": reason
            })

            if vote_choice.lower() == "no one":
                return -1, reason

            if vote_choice.lower().startswith("player_"):
                try:
                    voted_player = int(vote_choice.replace("player_", "").strip())
                    return voted_player, reason
                except ValueError:
                    print(f"[vote_day error] Invalid player format: {vote_choice}")
                    return nominees[0], reason
            else:
                print(f"[vote_day error] Invalid vote format: {vote_choice}")
                return nominees[0], reason

        except Exception as e:
            print(f"[vote_day error] {e}")
            return nominees[0], "Fallback vote due to parsing error."

    def investigate(self, game_log: str, alive_players: list[int]) -> int:
        possible_targets = [p for p in alive_players if f"player_{p}" != self.player_name]
        system_prompt = self._build_system_prompt()
        user_prompt = (
            f"Here is what happened in the game so far:\n{game_log}\n\n"
            "You are the Detective. Choose one player to investigate tonight.\n"
            f"The investigation you did so far: \n{self.investigations}"
            f"Alive players: {', '.join(f'player_{i}' for i in possible_targets)}\n"
            "Return only their name in this format: player_#"
        )
        response = self._call_llm(system_prompt, user_prompt)
        try:
            investigated_player = int(response.replace("player_", "").strip())
            return investigated_player
        except:
            return random.choice(possible_targets)

    def decide_kill(self, game_log: str, candidates: list[int], mafia_votes: list[tuple] = None) -> int:
        possible_targets = [f"player_{i}" for i in candidates]
        system_prompt = self._build_system_prompt()
        user_prompt = (
            f"Here is what happened in the game so far:\n{game_log}\n\n"
            f"As part of the mafia, you must choose who to kill tonight.\n"
            f"Candidates: {', '.join(possible_targets)}\n"
            "Return only one player name in this format: player_#"
        )

        if mafia_votes:
            vote_summary = "Mafia votes:\n" + "\n".join([f"player_{voter} voted for player_{target}" for voter, target in mafia_votes])
            user_prompt += f"\n\n{vote_summary}\n\nDon, based on these votes, please decide the final target. You are free to choose a player not in the other Mafia votes"

        response = self._call_llm(system_prompt, user_prompt)
        try:
            return int(response.replace("player_", "").strip())
        except:
            return candidates[0]
