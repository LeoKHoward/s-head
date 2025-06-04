from typing import List, Optional
from backend.models import Card, Player
from backend.card_utils import CardUtils


class AILogic:
    def __init__(self, game):
        self.game = game
        self.card_utils = CardUtils(self.game)

    def choose_ai_setup_cards(self, player: Player):
        # Combine all available cards (hand + face_up)
        combined = player.hand + player.face_up

        # Group cards by value for easier selection
        value_groups = self.card_utils.group_cards_by_value(combined)
        high_value_threshold = 9

        prioritised_cards = []

        # Prioritise 8s and 10s (special cards)
        for value in [8, 10]:
            if value in value_groups:
                prioritised_cards.extend(value_groups[value])
                # Remove from value_groups to avoid reprocessing
                del value_groups[value]

        # Add sets of high-value cards (9 or higher) - prioritize larger sets
        if len(prioritised_cards) < 3:
            for value, cards in sorted(value_groups.items(), key=lambda x: (-len(x[1]), -x[0])):
                if value >= high_value_threshold and len(cards) >= 2:
                    needed = 3 - len(prioritised_cards)
                    prioritised_cards.extend(cards[:needed])
                    if len(prioritised_cards) >= 3:
                        break

        # Add single high-value cards if still needed
        if len(prioritised_cards) < 3:
            for value, cards in sorted(value_groups.items(), key=lambda x: -x[0]):
                if value >= high_value_threshold:
                    needed = 3 - len(prioritised_cards)
                    prioritised_cards.extend(cards[:needed])
                    if len(prioritised_cards) >= 3:
                        break

        # Add sets of 2s or 7s (special low cards)
        if len(prioritised_cards) < 3:
            for value, cards in sorted(value_groups.items(), key=lambda x: (-len(x[1]), x[0])):
                if value in [2, 7] and len(cards) >= 2:
                    needed = 3 - len(prioritised_cards)
                    prioritised_cards.extend(cards[:needed])
                    if len(prioritised_cards) >= 3:
                        break

        # Fill remaining slots with highest-value cards
        if len(prioritised_cards) < 3:
            remaining = [card for card in combined if card not in prioritised_cards]
            remaining.sort(key=lambda c: c.value, reverse=True)
            needed = 3 - len(prioritised_cards)
            prioritised_cards.extend(remaining[:needed])

        # Select exactly 3 cards for face-up (no more, no less)
        face_up_cards = prioritised_cards[:3]

        # Create hand from remaining cards
        hand_cards = [card for card in combined if card not in face_up_cards]

        # Update player's cards
        player.face_up = face_up_cards
        player.hand = hand_cards

    def get_best_ai_play(self, player: Player, playable_sets: List[List[Card]]) -> Optional[List[Card]]:
        non_eights = [s for s in playable_sets if s[0].value != 8]
        eights = [s for s in playable_sets if s[0].value == 8]

        if len(player.hand) <= 3 and eights:
            return min(eights, key=lambda s: len(s))

        if non_eights:
            return min(non_eights, key=lambda s: s[0].value)

        if eights:
            return min(eights, key=lambda s: len(s))

        return None

    def computer_choose_playable_set(self, playable_sets: List[List[Card]], top_pile_value: int,
                                     player: Optional[Player] = None) -> Optional[List[Card]]:
        if not playable_sets:
            return None

        # Check if any opponent has exactly one face-down card
        opponent_one_face_down = False
        for p in self.game.players:
            if p != player and len(p.face_down) == 1 and not p.hand and not p.face_up:
                opponent_one_face_down = True
                break

        # Separate special and non-special sets
        non_special = [s for s in playable_sets if s[0].value not in [2, 7, 8, 10]]
        special_no_eights = [s for s in playable_sets if s[0].value in [2, 7, 10]]
        eights = [s for s in playable_sets if s[0].value == 8]

        # Filter non-special sets to meet or exceed pile value
        valid_non_special = [s for s in non_special if self.card_utils._base_card_value(s[0]) >= top_pile_value]

        # Check for four-of-a-kind burn opportunity
        if len(self.game.pile) >= 3:
            last_three = self.game.pile[-3:]
            if all(card.value == last_three[0].value for card in last_three):
                matching_sets = [s for s in valid_non_special if s[0].value == last_three[0].value]
                if matching_sets:
                    return min(matching_sets, key=len)

        # Strategy based on game state
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
