import unittest
from enums import Suit
from models import Card, Player


class TestModels(unittest.TestCase):
    def test_card_initialisation(self):
        """Test Card class initialisation and string representation."""
        card = Card(14, Suit.HEARTS)
        self.assertEqual(card.value, 14)
        self.assertEqual(card.suit, Suit.HEARTS)
        self.assertEqual(str(card), "A♥")
        self.assertEqual(repr(card), "A♥")

    def test_card_equality(self):
        """Test Card equality comparison."""
        card1 = Card(10, Suit.SPADES)
        card2 = Card(10, Suit.SPADES)
        card3 = Card(10, Suit.HEARTS)
        card4 = Card(9, Suit.SPADES)
        self.assertEqual(card1, card2)
        self.assertNotEqual(card1, card3)
        self.assertNotEqual(card1, card4)
        self.assertNotEqual(card1, None)

    def test_player_initialisation(self):
        """Test Player initialisation."""
        player = Player("TestPlayer")
        self.assertEqual(player.name, "TestPlayer")
        self.assertEqual(player.hand, [])
        self.assertEqual(player.face_up, [])
        self.assertEqual(player.face_down, [])
        self.assertEqual(player.total_cards(), 0)
        self.assertFalse(player.has_cards())

    def test_player_hand_sorting(self):
        """Test Player hand sorting via property setter."""
        player = Player("TestPlayer")
        cards = [Card(5, Suit.HEARTS), Card(10, Suit.CLUBS), Card(2, Suit.SPADES)]
        player.hand = cards
        expected = [Card(2, Suit.SPADES), Card(5, Suit.HEARTS), Card(10, Suit.CLUBS)]
        self.assertEqual(player.hand, expected)

    def test_player_card_counts(self):
        """Test Player card counting and phase checks."""
        player = Player("TestPlayer")
        player.hand = [Card(2, Suit.HEARTS)]
        player.face_up = [Card(3, Suit.CLUBS)]
        player.face_down = [Card(4, Suit.SPADES)]
        self.assertEqual(player.total_cards(), 3)
        self.assertTrue(player.has_cards())
        self.assertTrue(player.can_play_from_hand())
        self.assertFalse(player.can_play_from_face_up())
        self.assertFalse(player.can_play_from_face_down())

        player.hand = []
        self.assertTrue(player.can_play_from_face_up())
        self.assertFalse(player.can_play_from_face_down())

        player.face_up = []
        self.assertTrue(player.can_play_from_face_down())
