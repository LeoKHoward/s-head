from typing import List, Dict
from backend.enums import Suit
from backend.models import Card, Player
from itertools import combinations


class CardUtils:
    FACE_VALUES = {
        'a': 14, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
        '7': 7, '8': 8, '9': 9, '10': 10,
        'j': 11, 'q': 12, 'k': 13
    }

    def __init__(self, game):
        self.game = game

    def create_deck(self) -> List[Card]:
        return [Card(value, suit) for suit in Suit for value in range(2, 15)]

    @staticmethod
    def group_cards_by_value(cards: List[Card]) -> Dict[int, List[Card]]:
        groups = {}
        for card in cards:
            groups.setdefault(card.value, []).append(card)
        return groups

    @staticmethod
    def get_pile_top_value_for_comparison(pile: list) -> int | None:
        for card in reversed(pile):
            if card.value not in [7, 8, 10]:
                return card.value
        return None

    def _base_card_value(self, card: Card) -> int:
        if card.value in (2, 10):
            return 0
        return card.value

    def get_top_pile_value(self) -> int:
        return self.get_pile_top_value_for_comparison(self.game.pile) or 0

    def can_play_cards(self, cards: List[Card]) -> bool:
        if not cards:
            return False

        pile_value = self.get_top_pile_value()
        if self.game.players[self.game.current_player].hand:
            if all(card.value == 8 for card in cards):
                return True
            if any(card.value == 8 for card in cards):
                non_eights = [card for card in cards if card.value != 8]
                if len(non_eights) > 1:
                    return False
                underlying_value = self.get_pile_top_value_for_comparison(
                    self.game.pile[:-1]) or 0 if self.game.pile else 0
                return not non_eights or (
                        non_eights[0].value in [2, 7, 8, 10] or
                        self._base_card_value(non_eights[0]) >= underlying_value
                )
            if not all(card.value == cards[0].value for card in cards):
                return False
            card_value = self._base_card_value(cards[0])
            return cards[0].value in [2, 7, 8, 10] or card_value >= pile_value

        for card in cards:
            card_value = self._base_card_value(card)
            if card.value not in [2, 7, 8, 10] and card_value < pile_value:
                return False
        return True

    def find_playable_combinations(self, cards: List[Card]) -> List[List[Card]]:
        playable = []
        if self.game.players[self.game.current_player].hand:
            groups = self.group_cards_by_value(cards)
            for group_cards in groups.values():
                if self.can_play_cards([group_cards[0]]):
                    playable.append([group_cards[0]])
                for count in range(2, len(group_cards) + 1):
                    combo = group_cards[:count]
                    if self.can_play_cards(combo):
                        playable.append(combo)
        elif self.game.players[self.game.current_player].face_up:
            for r in range(1, len(cards) + 1):
                for combo in combinations(cards, r):
                    if self.can_play_cards(list(combo)):
                        playable.append(list(combo))
        return playable

    def get_playable_cards(self, player: Player) -> List[List[Card]]:
        playable = []
        if player.hand:
            playable.extend(self.find_playable_combinations(player.hand))
        elif player.face_up:
            playable.extend(self.find_playable_combinations(player.face_up))
        return playable

    def play_cards(self, player: Player, cards: List[Card]) -> bool:
        new_hand = [card for card in player.hand if card not in cards]
        for card in cards:
            if card in player.face_up:
                player.face_up.remove(card)
            elif card in player.face_down:
                player.face_down.remove(card)
        player.hand = new_hand

        self.game.pile.extend(cards)
        card_value = cards[-1].value

        if card_value == 10:
            print(f"Pile burned! {len(self.game.pile)} cards removed.")
            self.game.pile = []
            return True

        if len(self.game.pile) >= 4:
            last_four = self.game.pile[-4:]
            if all(card.value == last_four[0].value for card in last_four):
                print(f"4 of a kind played! Pile burned! {len(self.game.pile)} cards removed.")
                self.game.pile = []
                return True

        if card_value == 8:
            return True

        return False
