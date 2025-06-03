import random
from typing import List, Dict, Tuple, Optional
from enums import Suit
from models import Card, Player
from itertools import combinations
from collections import Counter


class CardGame:
    FACE_VALUES = {
        'a': 14, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
        '7': 7, '8': 8, '9': 9, '10': 10, 't': 10,
        'j': 11, 'q': 12, 'k': 13
    }

    def __init__(self):
        self.deck: List[Card] = []
        self.players: List[Player] = []
        self.pile: List[Card] = []
        self.current_player = 0
        self.game_over = None
        self.winner: Optional[Player] = None

    def create_deck(self) -> List[Card]:
        return [Card(value, suit) for suit in Suit for value in range(2, 15)]

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def deal_cards(self):
        self.deck = self.create_deck()
        self.shuffle_deck()
        self.players = [Player("ME"), Player("COMPUTER")]
        for player in self.players:
            player.face_down = [self.deck.pop() for _ in range(3)]
            player.face_up = [self.deck.pop() for _ in range(3)]
            player.hand = [self.deck.pop() for _ in range(3)]

    @staticmethod
    def group_cards_by_value(cards: List[Card]) -> Dict[int, List[Card]]:
        groups = {}
        for card in cards:
            groups.setdefault(card.value, []).append(card)
        return groups

    @staticmethod
    def get_pile_top_value_for_comparison(pile: list) -> int | None:
        """
        Returns the value of the top card in the pile for comparison.
        Skips special cards like 7, 8 see-through, 10 see-under).
        """
        for card in reversed(pile):
            if card.value not in [7, 8, 10]:
                return card.value
        return None

    def _base_card_value(self, card: Card) -> int:
        """
        Returns the standard value of a card.
        """
        if card.value in (2, 10):
            return 0
        return card.value

    def get_top_pile_value(self) -> int:
        return self.get_pile_top_value_for_comparison(self.pile) or 0

    def can_play_cards(self, cards: List[Card]) -> bool:
        if not cards:
            return False

        pile_value = self.get_top_pile_value()
        # Hand phase: handle sets with 8s or same-value cards
        if self.players[self.current_player].hand:
            # If all cards are 8s, they are always playable
            if all(card.value == 8 for card in cards):
                return True
            # If includes 8s, allow one non-8 card that is special or >= underlying pile value
            if any(card.value == 8 for card in cards):
                non_eights = [card for card in cards if card.value != 8]
                if len(non_eights) <= 1:  # Allow at most one non-8 card
                    underlying_value = self.get_pile_top_value_for_comparison(self.pile[:-1]) or 0 if self.pile else 0
                    return not non_eights or (non_eights[0].value in [2, 5, 7, 8, 10] or self._base_card_value(
                        non_eights[0]) >= underlying_value)
                return False
            # Otherwise, all cards must be same value and either special or >= pile_value
            if not all(card.value == cards[0].value for card in cards):
                return False
            card_value = self._base_card_value(cards[0])
            return cards[0].value in [2, 7, 8, 10] or card_value >= pile_value

        # Face-up phase: allow mixed values, but all non-special cards must be >= pile_value
        has_special = False
        for card in cards:
            card_value = self._base_card_value(card)
            if card.value in [2, 7, 8, 10]:
                has_special = True
            elif card_value < pile_value:
                return False
        return has_special or all(self._base_card_value(card) >= pile_value for card in cards)

    def find_playable_combinations(self, cards: List[Card]) -> List[List[Card]]:
        playable = []
        # Hand phase: only same-value combinations
        if self.players[self.current_player].hand:
            groups = self.group_cards_by_value(cards)
            for group_cards in groups.values():
                if self.can_play_cards([group_cards[0]]):
                    playable.append([group_cards[0]])
                for count in range(2, len(group_cards) + 1):
                    combo = group_cards[:count]
                    if self.can_play_cards(combo):
                        playable.append(combo)
        # Face-up phase: allow all combinations of 1 or more cards
        elif self.players[self.current_player].face_up:
            for r in range(1, len(cards) + 1):
                for combo in combinations(cards, r):
                    if self.can_play_cards(list(combo)):
                        playable.append(list(combo))
        return playable

    def choose_ai_setup_cards(self, player: Player):
        combined = player.hand + player.face_up
        groups = self.group_cards_by_value(combined)
        # Sort groups by size (descending) and then by value (descending)
        sorted_groups = sorted(groups.values(), key=lambda g: (len(g), max(c.value for c in g)), reverse=True)

        face_up_cards = []
        used_indices = set()

        # Step 1: Take the highest-value group among the largest groups
        if sorted_groups:
            max_size = max(len(g) for g in sorted_groups)
            largest_groups = [g for g in sorted_groups if len(g) == max_size]
            highest_value_group = max(largest_groups, key=lambda g: max(c.value for c in g))
            face_up_cards.extend(highest_value_group)
            for card in highest_value_group:
                used_indices.add(combined.index(card))

        # Step 2: Fill remaining slots (up to 3) with special cards or highest-value cards
        if len(face_up_cards) < 3:
            target_value = max(c.value for c in face_up_cards) if face_up_cards else None
            remaining_cards = [card for i, card in enumerate(combined) if i not in used_indices]

            # Prioritize special cards (2, 7, 8, 10)
            special_cards = [card for card in remaining_cards if card.value in [2, 7, 8, 10]]
            special_cards.sort(key=lambda c: c.value)  # Prefer lower-value special cards
            while len(face_up_cards) < 3 and special_cards:
                face_up_cards.append(special_cards.pop(0))
                used_indices.add(combined.index(face_up_cards[-1]))

            # If still need more cards, prioritize highest-value cards
            if len(face_up_cards) < 3:
                remaining_cards = [card for i, card in enumerate(combined) if i not in used_indices]
                remaining_cards.sort(key=lambda c: c.value, reverse=True)  # Prefer higher values

                for card in remaining_cards:
                    if len(face_up_cards) < 3:
                        face_up_cards.append(card)
                        used_indices.add(combined.index(card))
                    else:
                        break

        player.face_up = face_up_cards
        player.hand = [card for i, card in enumerate(combined) if i not in used_indices]

    def parse_face_up_choice(self, input_str: str, combined: List[Card]) -> Tuple[List[Card], List[Card]]:
        # Normalize input: strip and lowercase
        input_str = input_str.strip().lower()

        # Split on spaces if present, otherwise treat as single token
        if ' ' in input_str:
            tokens = input_str.split()
        else:
            tokens = [input_str]

        # Expand tokens to handle repeated values (e.g., "44" -> ["4", "4"], "qq" -> ["q", "q"])
        expanded_tokens = []
        valid_single_chars = set("23456789tjqka")
        for token in tokens:
            if token == "10":
                expanded_tokens.append("10")
            else:
                i = 0
                while i < len(token):
                    if i < len(token) - 1 and token[i:i + 2] == "10":
                        expanded_tokens.append("10")
                        i += 2
                    elif token[i] in valid_single_chars:
                        expanded_tokens.append(token[i])
                        i += 1
                    else:
                        print(f"Invalid card value in '{token}'.")
                        return [], []

        # Validate exactly 3 values
        if len(expanded_tokens) != 3:
            print(f"Expected exactly 3 card values, got {len(expanded_tokens)}.")
            return [], []

        # Map input values to numeric values using parse_card_value
        chosen_values = []
        for val in expanded_tokens:
            parsed_val = self.parse_card_value(val)
            if parsed_val is None:
                print(f"Invalid card value '{val}'.")
                return [], []
            chosen_values.append(parsed_val)

        # Check if all chosen values exist in combined cards
        available_values = [card.value for card in combined]
        temp_available = available_values.copy()  # Copy to track used values
        for val in chosen_values:
            if val not in temp_available:
                print(f"Card value '{val}' not available in your cards.")
                return [], []
            temp_available.remove(val)  # Ensure each card is used only once

        # Assign cards to face-up and hand
        face_up = []
        used_indices = set()
        for val in chosen_values:
            for i, card in enumerate(combined):
                if i not in used_indices and card.value == val:
                    face_up.append(card)
                    used_indices.add(i)
                    break

        hand = [card for i, card in enumerate(combined) if i not in used_indices]
        return face_up, hand

    def get_best_ai_play(self, player: Player, playable_sets: List[List[Card]]) -> Optional[List[Card]]:
        non_eights = [s for s in playable_sets if s[0].value != 8]
        eights = [s for s in playable_sets if s[0].value == 8]

        if len(player.hand) <= 3 and eights:
            return min(eights, key=lambda s: s[0].value)

        if non_eights:
            return min(non_eights, key=lambda s: s[0].value)

        if eights:
            return min(eights, key=lambda s: s[0].value)

        return None

    def computer_choose_playable_set(self, playable_sets: List[List[Card]], top_pile_value: int,
                                     player: Optional[Player] = None) -> Optional[List[Card]]:
        if not playable_sets:
            return None

        # Check if any opponent has exactly one face-down card
        opponent_one_face_down = False
        for p in self.players:
            if p != player and len(p.face_down) == 1 and not p.hand and not p.face_up:
                opponent_one_face_down = True
                break

        # Separate special and non-special sets
        non_special = [s for s in playable_sets if s[0].value not in [2, 7, 8, 10]]
        special_no_eights = [s for s in playable_sets if s[0].value in [2, 7, 10]]
        eights = [s for s in playable_sets if s[0].value == 8]

        # Filter non-special sets to ensure they meet or exceed the pile value
        valid_non_special = [s for s in non_special if self._base_card_value(s[0]) >= top_pile_value]

        # Check for four-of-a-kind opportunity to burn the pile
        if len(self.pile) >= 3:
            last_three = self.pile[-3:]
            if all(card.value == last_three[0].value for card in last_three):
                # Check if we have a card matching the pile's value
                matching_sets = [s for s in valid_non_special if s[0].value == last_three[0].value]
                if matching_sets:
                    return min(matching_sets, key=len)  # Play smallest set to complete four-of-a-kind

        # Existing logic continues...
        if opponent_one_face_down and valid_non_special:
            return max(valid_non_special, key=lambda s: (s[0].value, len(s)))

        if player and len(player.hand) <= 3 and eights:
            return min(eights, key=len)

        if top_pile_value == 14 and any(s[0].value == 7 for s in special_no_eights):
            sevens = [s for s in special_no_eights if s[0].value == 7]
            return min(sevens, key=len)

        if top_pile_value >= 10 and any(s[0].value == 2 for s in special_no_eights):
            twos = [s for s in special_no_eights if s[0].value == 2]
            return min(twos, key=len)

        if top_pile_value <= 9 and valid_non_special:
            return min(valid_non_special, key=lambda s: (s[0].value, len(s)))

        if player and len(player.hand) > 10 and valid_non_special:
            return max(valid_non_special, key=len)

        if valid_non_special:
            return min(valid_non_special, key=lambda s: (s[0].value, -len(s)))

        if special_no_eights:
            return min(special_no_eights, key=lambda s: s[0].value)

        if eights:
            return min(eights, key=len)

        return None

    def handle_player_input(self, playable_sets: List[List[Card]]) -> Optional[List[Card]]:
        while True:
            choice = input(
                "Choose set to play (e.g., '7 7' or '77' for two 7s, 'tp' to pick up pile): ").strip().lower()

            # Handle tactical pickup
            if choice == "tp":
                print("You chose to tactically pick up the pile.")
                return None

            # Handle input with or without spaces
            if ' ' in choice:
                tokens = choice.split()
            else:
                # Split space-less input into individual card values (e.g., "77" -> ["7", "7"], "aa" -> ["a", "a"])
                tokens = []
                i = 0
                while i < len(choice):
                    if i < len(choice) - 1 and choice[i:i + 2] == "10":
                        tokens.append("10")
                        i += 2
                    else:
                        tokens.append(choice[i])
                        i += 1

            # Try parsing as card values
            try:
                values = [self.parse_card_value(t) for t in tokens]
                if None in values:
                    raise KeyError(tokens[values.index(None)])
            except KeyError as e:
                print(
                    f"Invalid card value '{e.args[0]}'. Please enter valid card values (e.g., '7 7', 'aa') or 'tp' to pick up pile.")
                continue

            # Compare multiset of values against playable sets
            input_counter = Counter(values)
            for s in playable_sets:
                set_counter = Counter(card.value for card in s)
                if input_counter == set_counter:
                    return s

            # No match found
            print(
                f"No playable set matches '{' '.join(tokens)}'. Please enter valid card values or 'tp' to pick up pile.")

    def play_cards(self, player: Player, cards: List[Card]) -> bool:
        # Remove played cards from player's collections
        new_hand = [card for card in player.hand if card not in cards]
        for card in cards:
            if card in player.face_up:
                player.face_up.remove(card)
            elif card in player.face_down:
                player.face_down.remove(card)
        player.hand = new_hand

        self.pile.extend(cards)
        card_value = cards[-1].value  # Use last card for pile value and special checks

        # Check for burn-by-10 or burn-by-4-of-a-kind
        if card_value == 10:
            print(f"Pile burned! {len(self.pile)} cards removed.")
            self.pile = []
            return True

        # Check if last 4 cards on pile are of the same value
        if len(self.pile) >= 4:
            last_four = self.pile[-4:]
            if all(card.value == last_four[0].value for card in last_four):
                print(f"4 of a kind played! Pile burned! {len(self.pile)} cards removed.")
                self.pile = []
                return True

        if card_value == 8:
            return True

        return False

    def draw_card(self, player: Player):
        # Collect current hand and add new cards
        new_hand = player.hand.copy()
        while len(new_hand) < 3 and self.deck:
            new_hand.append(self.deck.pop())
        # Update hand using the property to ensure sorting
        player.hand = new_hand

    def player_must_pickup_pile(self, player: Player):
        print(f"{player.name} picks up the pile!")
        # Add pile cards to hand and clear pile
        new_hand = player.hand + self.pile
        self.pile = []
        # Update hand using the property to ensure sorting
        player.hand = new_hand

    def get_playable_cards(self, player: Player) -> List[List[Card]]:
        playable = []
        # Consider hand cards if available
        if player.hand:
            playable.extend(self.find_playable_combinations(player.hand))
        # Consider face-up cards only if hand is empty
        elif player.face_up:
            playable.extend(self.find_playable_combinations(player.face_up))
        # For face-down cards, skip combination check since they're chosen blindly
        return playable

    def display_game_state(self):
        print("\n" + "=" * 50)
        print("GAME STATE")
        print("=" * 50)

        for i, player in enumerate(self.players):
            current = " (CURRENT)" if i == self.current_player else ""
            print(f"\n{player.name}{current}:")
            print(f"  Hand ({len(player.hand)}): {player.hand if player.hand else 'Empty'}")
            print(f"  Face-up ({len(player.face_up)}): {player.face_up if player.face_up else 'Empty'}")
            face_down_str = '[Hidden] ' * len(player.face_down) if player.face_down else 'Empty'
            print(f"  Face-down ({len(player.face_down)}): {face_down_str}")

        pile_display = self.pile[-3:] if len(self.pile) > 3 else self.pile
        print(f"\nPile ({len(self.pile)}): {pile_display}")
        if self.pile:
            print(f"Top pile value: {self.get_top_pile_value()}")
        print(f"Deck remaining: {len(self.deck)}")

    def check_game_over(self) -> bool:
        for player in self.players:
            if not player.has_cards():
                self.game_over = True
                self.winner = player
                return True
        return False

    def parse_card_value(self, val: str) -> int | None:
        """Convert card value input (e.g., 'a', 'q', '10', 'j') to numeric value."""
        val = val.lower()
        value_map = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
            '7': 7, '8': 8, '9': 9, '10': 10,
            't': 10,
            'j': 11,
            'q': 12,
            'k': 13,
            'a': 14
        }
        return value_map.get(val)

    def setup_phase(self):
        print("SETUP PHASE: Players can swap cards between hand and face-up cards")

        for player in self.players:
            print(f"\n{player.name}'s turn to set up:")
            print(f"Hand: {player.hand}")
            print(f"Face-up: {player.face_up}")

            combined = player.hand + player.face_up
            combined_sorted_desc = sorted(combined, key=lambda c: c.value, reverse=True)

            if player.name == "ME":
                while True:
                    print("You have the following 6 cards to choose from:")
                    for idx, card in enumerate(combined_sorted_desc):
                        print(f"{idx + 1}: {card}")

                    value_str = input("Choose 3 card values to place face-up (e.g., '5 5 8' or '558'): ").strip()
                    face_up, hand = self.parse_face_up_choice(value_str, combined)

                    if face_up and hand:
                        player.face_up = face_up
                        player.hand = hand
                        break
                    else:
                        value_parts = value_str.replace(" ", "")  # Remove spaces for error message
                        if len(value_parts) < 3 or len(value_parts) > 5:  # Rough check for 3 values
                            print("Please enter exactly 3 card values (e.g., '5 5 8' or '558').")
                        else:
                            for i in range(0, len(value_parts), 1):
                                val = value_parts[i]
                                if val == '1' and i + 1 < len(value_parts) and value_parts[i:i + 2] == "10":
                                    val = "10"
                                    i += 1
                                if val not in self.FACE_VALUES:
                                    print(f"Invalid card value '{val}'. Try again.")
                                    break
                                elif self.parse_card_value(val) not in [card.value for card in combined]:
                                    print(f"Card value '{val}' not available in your cards. Try again.")
                                    break
            else:
                self.choose_ai_setup_cards(player)

            player.face_up.sort(key=lambda card: card.value)
            print(f"After setup - Hand: {player.hand}, Face-up: {player.face_up}")

    def player_turn(self, player: Player) -> bool:
        print(f"\n{player.name}'s turn:")

        # For face-down phase, always prompt to choose a card
        if player.can_play_from_face_down():
            if not hasattr(player, 'face_down_positions'):
                player.face_down_positions = list(range(1, len(player.face_down) + 1))

            print(f"Face-down cards available: {len(player.face_down)}")
            valid_positions = player.face_down_positions

            if player.name == "COMPUTER":
                # Computer randomly selects a face-down card
                import random
                choice = random.choice(valid_positions)
                chosen_index = player.face_down_positions.index(choice)
                chosen_cards = [player.face_down[chosen_index]]
                print(f"{player.name} plays: {chosen_cards}")
                if self.can_play_cards(chosen_cards):
                    player.face_down_positions.remove(choice)
                    another_turn = self.play_cards(player, chosen_cards)
                    self.draw_card(player)
                    return another_turn
                else:
                    print(f"{chosen_cards[0]} cannot be played. {player.name} must pick up the pile.")
                    player.face_down_positions.remove(choice)
                    player.face_down.pop(chosen_index)  # Remove the unplayable card
                    self.player_must_pickup_pile(player)
                    self.draw_card(player)
                    return False
            else:
                # Human player prompt
                prompt = f"Choose a face-down card ({', '.join(map(str, valid_positions))}): "
                while True:
                    choice = input(prompt).strip()
                    if choice.isdigit() and int(choice) in valid_positions:
                        chosen_index = player.face_down_positions.index(int(choice))
                        chosen_cards = [player.face_down[chosen_index]]
                        print(f"You played: {chosen_cards}")
                        if self.can_play_cards(chosen_cards):
                            player.face_down_positions.remove(int(choice))
                            another_turn = self.play_cards(player, chosen_cards)
                            self.draw_card(player)
                            return another_turn
                        else:
                            print(f"{chosen_cards[0]} cannot be played. You must pick up the pile.")
                            player.face_down_positions.remove(int(choice))
                            player.face_down.pop(chosen_index)  # Remove the unplayable card
                            self.player_must_pickup_pile(player)
                            self.draw_card(player)
                            return False
                    print(f"Invalid choice. Please enter a number from {', '.join(map(str, valid_positions))}")

        playable_sets = self.get_playable_cards(player)
        if not playable_sets:
            print(f"{player.name} has no playable cards and must pick up the pile.")
            self.player_must_pickup_pile(player)
            self.draw_card(player)
            return False

        top_value = self.get_top_pile_value()
        if player.name == "ME" and player.hand:
            # Check if the only playable sets involve 8s with no valid follow-up
            can_play = False
            has_eight = False
            for s in playable_sets:
                if any(card.value in [2, 7, 10] for card in s):  # Special cards that reset or burn
                    can_play = True
                    break
                elif any(card.value == 8 for card in s):
                    has_eight = True
                    # Check for a follow-up card in hand
                    underlying_value = self.get_pile_top_value_for_comparison(self.pile[:-1]) or 0 if self.pile else 0
                    follow_cards = [card for card in player.hand if card not in s]
                    for follow_card in follow_cards:
                        if follow_card.value in [2, 7, 8, 10] or self._base_card_value(
                                follow_card) >= underlying_value:
                            can_play = True
                            break
                    if can_play:
                        break
                elif all(self._base_card_value(card) >= top_value for card in s):  # Normal cards beating pile
                    can_play = True
                    break
                elif len(s) >= 4 and all(card.value == s[0].value for card in s):  # Four-of-a-kind burns
                    can_play = True
                    break

            # If only 8s are playable but no valid follow-up, force pile pickup
            if not can_play and has_eight:
                print(
                    "Your only playable card is an 8, but you have no valid follow-up card. You must pick up the pile.")
                self.player_must_pickup_pile(player)
                self.draw_card(player)
                return False

        if player.name == "COMPUTER":
            chosen_cards = self.computer_choose_playable_set(playable_sets, top_value, player)
            if chosen_cards:
                print(f"{player.name} plays: {chosen_cards}")
                another_turn = self.play_cards(player, chosen_cards)
                self.draw_card(player)
                return another_turn
            else:
                print(f"{player.name} has no playable cards and must pick up the pile.")
                self.player_must_pickup_pile(player)
                self.draw_card(player)
                return False

        # Display playable sets for human player
        # print("Playable sets:")
        # for i, s in enumerate(playable_sets, 1):
        #     print(f"{i}. {s}")
        chosen_cards = self.handle_player_input(playable_sets)
        if chosen_cards:
            print(f"You played: {chosen_cards}")
            another_turn = self.play_cards(player, chosen_cards)
            self.draw_card(player)
            return another_turn
        print("You chose to pick up the pile.")
        self.player_must_pickup_pile(player)
        self.draw_card(player)
        return False

    def play_game(self):
        self.deal_cards()
        self.setup_phase()
        while not self.game_over:
            self.display_game_state()
            player = self.players[self.current_player]
            another_turn = self.player_turn(player)

            if self.check_game_over():
                break

            if not another_turn:
                self.current_player = (self.current_player + 1) % len(self.players)

        print(f"\nGame Over! Winner is {self.winner.name}!")
