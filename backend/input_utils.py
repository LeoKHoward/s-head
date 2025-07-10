from typing import List, Tuple, Optional
from backend.models import Card
from collections import Counter


class InputUtils:
    def __init__(self, game):
        self.game = game

    def parse_card_value(self, val: str) -> int | None:
        val = val.lower()
        value_map = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
            '7': 7, '8': 8, '9': 9, '10': 10,
            'j': 11, 'q': 12, 'k': 13, 'a': 14
        }
        return value_map.get(val)

    def parse_face_up_choice(self, input_str: str, cards: List[Card]) -> Tuple[List[Card], List[Card]]:
        input_str = input_str.strip().lower()

        if ' ' in input_str:
            tokens = input_str.split()
        else:
            tokens = []
            i = 0
            while i < len(input_str):
                if i < len(input_str) - 1 and input_str[i:i + 2] == "10":
                    tokens.append("10")
                    i += 2
                else:
                    tokens.append(input_str[i])
                    i += 1

        if len(tokens) != 3:
            print(f"Expected exactly 3 card values, got {len(tokens)}.")
            return [], []

        chosen_values = []
        for val in tokens:
            parsed_val = self.parse_card_value(val)
            if parsed_val is None:
                print(f"Invalid card value '{val}'.")
                return [], []
            chosen_values.append(parsed_val)

        available_values = [card.value for card in cards]
        temp_available = available_values.copy()
        for val in chosen_values:
            if val not in temp_available:
                print(f"Card value '{val}' not available in your cards.")
                return [], []
            temp_available.remove(val)

        face_up = []
        used_indices = set()
        for val in chosen_values:
            for i, card in enumerate(cards):
                if i not in used_indices and card.value == val:
                    face_up.append(card)
                    used_indices.add(i)
                    break

        hand = [card for i, card in enumerate(cards) if i not in used_indices]
        return face_up, hand

    def handle_player_input(self, playable_sets: List[List[Card]]) -> Optional[List[Card]]:
        while True:
            choice = input(
                "Choose cards to play (or 'tp' for tactical pickup, 'help' for assistance): ").strip().lower()
            if choice == "tp":
                print("You performed a TACTICAL PICKUP!")
                return None
            if choice == "help":
                print("\nHELP:")
                print("Enter card values to play (e.g. '7 7', '10', 'aa')")
                print("Valid values: 2-10, j (Jack), q (Queen), k (King), a (Ace)")
                print("Enter 'tp' to pick up the pile tactically")
                print("You must play cards >= pile's top value or special cards (2, 7, 8, 10)")
                print(f"Your playable sets: {[', '.join(str(card) for card in s) for s in playable_sets]}")
                continue

            if ' ' in choice:
                tokens = choice.split()
            else:
                tokens = []
                i = 0
                while i < len(choice):
                    if i < len(choice) - 1 and choice[i:i + 2] == "10":
                        tokens.append("10")
                        i += 2
                    else:
                        tokens.append(choice[i])
                        i += 1

            try:
                values = [self.parse_card_value(t) for t in tokens]
                if None in values:
                    raise KeyError(tokens[values.index(None)])
            except KeyError as e:
                print(
                    f"Invalid card value '{e.args[0]}'. Enter valid card values (e.g. '7 7', 'aa'), 'tp', or 'help'")
                continue

            input_counter = Counter(values)
            for s in playable_sets:
                set_counter = Counter(card.value for card in s)
                if input_counter == set_counter:
                    return s

            print(
                f"No playable set matches '{' '.join(tokens)}'. Enter valid card values, 'tp', or 'help'")
