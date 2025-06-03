import unittest
from enums import Suit
from models import Card, Player


class TestCard(unittest.TestCase):
    def test_card_initialisation(self):
        """Test that cards are initialised correctly."""
        card = Card(10, Suit.HEARTS)
        self.assertEqual(card.value, 10)
        self.assertEqual(card.suit, Suit.HEARTS)

    def test_card_string_representation(self):
        """Test the string representation of cards."""
        self.assertEqual(str(Card(2, Suit.HEARTS)), "2♥")
        self.assertEqual(str(Card(10, Suit.DIAMONDS)), "10♦")
        self.assertEqual(str(Card(11, Suit.CLUBS)), "J♣")
        self.assertEqual(str(Card(12, Suit.SPADES)), "Q♠")
        self.assertEqual(str(Card(13, Suit.HEARTS)), "K♥")
        self.assertEqual(str(Card(14, Suit.DIAMONDS)), "A♦")

    def test_card_equality(self):
        """Test that card equality works correctly."""
        card1 = Card(10, Suit.HEARTS)
        card2 = Card(10, Suit.HEARTS)
        card3 = Card(10, Suit.DIAMONDS)
        card4 = Card(11, Suit.HEARTS)

        self.assertEqual(card1, card2)
        self.assertNotEqual(card1, card3)
        self.assertNotEqual(card1, card4)
        self.assertNotEqual(card1, "Not a card")


class TestPlayer(unittest.TestCase):
    def setUp(self):
        """Set up a player with some cards for testing."""
        self.player = Player("Test Player")
        self.cards = [
            Card(10, Suit.HEARTS),
            Card(2, Suit.DIAMONDS),
            Card(14, Suit.CLUBS),
            Card(7, Suit.SPADES)
        ]

    def test_player_initialisation(self):
        """Test that players are initialised correctly."""
        player = Player("Test Player")
        self.assertEqual(player.name, "Test Player")
        self.assertEqual(player.hand, [])
        self.assertEqual(player.face_up, [])
        self.assertEqual(player.face_down, [])

    def test_hand_property(self):
        """Test that the hand property sorts cards by value."""
        self.player.hand = self.cards
        expected_order = [
            Card(2, Suit.DIAMONDS),
            Card(7, Suit.SPADES),
            Card(10, Suit.HEARTS),
            Card(14, Suit.CLUBS)
        ]
        self.assertEqual(self.player.hand, expected_order)

    def test_total_cards(self):
        """Test that total_cards returns the correct count."""
        self.player.hand = self.cards[:2]
        self.player.face_up = self.cards[2:3]
        self.player.face_down = self.cards[3:]
        self.assertEqual(self.player.total_cards(), 4)

    def test_has_cards(self):
        """Test that has_cards returns the correct boolean."""
        self.assertFalse(self.player.has_cards())

        self.player.hand = [self.cards[0]]
        self.assertTrue(self.player.has_cards())

        self.player.hand = []
        self.player.face_up = [self.cards[0]]
        self.assertTrue(self.player.has_cards())

        self.player.face_up = []
        self.player.face_down = [self.cards[0]]
        self.assertTrue(self.player.has_cards())

    def test_can_play_methods(self):
        """Test the can_play_from_* methods."""
        # Empty player can't play from anywhere
        self.assertFalse(self.player.can_play_from_hand())
        self.assertFalse(self.player.can_play_from_face_up())
        self.assertFalse(self.player.can_play_from_face_down())

        # Player with hand can play from hand only
        self.player.hand = [self.cards[0]]
        self.assertTrue(self.player.can_play_from_hand())
        self.assertFalse(self.player.can_play_from_face_up())
        self.assertFalse(self.player.can_play_from_face_down())

        # Player with empty hand and face_up can play from face_up only
        self.player.hand = []
        self.player.face_up = [self.cards[0]]
        self.assertFalse(self.player.can_play_from_hand())
        self.assertTrue(self.player.can_play_from_face_up())
        self.assertFalse(self.player.can_play_from_face_down())

        # Player with empty hand and face_up can play from face_down only
        self.player.face_up = []
        self.player.face_down = [self.cards[0]]
        self.assertFalse(self.player.can_play_from_hand())
        self.assertFalse(self.player.can_play_from_face_up())
        self.assertTrue(self.player.can_play_from_face_down())


if __name__ == '__main__':
    unittest.main()