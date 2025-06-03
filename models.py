from enums import Suit
from typing import List


class Card:
    def __init__(self, value: int, suit: Suit):
        self.value = value  # 2-14 (where 11=J, 12=Q, 13=K, 14=A)
        self.suit = suit

    def __str__(self):
        value_names = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
        value_str = value_names.get(self.value, str(self.value))
        return f"{value_str}{self.suit.value}"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return isinstance(other, Card) and self.value == other.value and self.suit == other.suit


class Player:
    def __init__(self, name: str):
        self.name = name
        self._hand: List[Card] = []
        self.face_up: List[Card] = []
        self.face_down: List[Card] = []

    @property
    def hand(self) -> List[Card]:
        return self._hand

    @hand.setter
    def hand(self, cards: List[Card]):
        self._hand = sorted(cards, key=lambda card: card.value)

    def total_cards(self) -> int:
        return len(self.hand) + len(self.face_up) + len(self.face_down)

    def has_cards(self) -> bool:
        return self.total_cards() > 0

    def can_play_from_hand(self) -> bool:
        return len(self.hand) > 0

    def can_play_from_face_up(self) -> bool:
        return len(self.hand) == 0 and len(self.face_up) > 0

    def can_play_from_face_down(self) -> bool:
        return len(self.hand) == 0 and len(self.face_up) == 0 and len(self.face_down) > 0