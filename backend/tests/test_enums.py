import unittest
from backend.enums import Suit


class TestEnums(unittest.TestCase):
    def test_suit_values(self):
        """Test that Suit enum has correct values."""
        self.assertEqual(Suit.HEARTS.value, "♥")
        self.assertEqual(Suit.DIAMONDS.value, "♦")
        self.assertEqual(Suit.CLUBS.value, "♣")
        self.assertEqual(Suit.SPADES.value, "♠")

    def test_suit_members(self):
        """Test that Suit enum contains exactly the expected members."""
        expected_suits = ["HEARTS", "DIAMONDS", "CLUBS", "SPADES"]
        actual_suits = [suit.name for suit in Suit]
        self.assertEqual(actual_suits, expected_suits)
        self.assertEqual(len(Suit), 4)

    def test_suit_immutability(self):
        """Test that Suit enum values cannot be modified."""
        with self.assertRaises(AttributeError):
            Suit.HEARTS.value = "X"
