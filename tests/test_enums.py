import unittest
from enums import Suit


class TestSuit(unittest.TestCase):
    def test_suit_values(self):
        """Test that all suits have the correct symbol values."""
        self.assertEqual(Suit.HEARTS.value, "♥")
        self.assertEqual(Suit.DIAMONDS.value, "♦")
        self.assertEqual(Suit.CLUBS.value, "♣")
        self.assertEqual(Suit.SPADES.value, "♠")

    def test_suit_enum_behavior(self):
        """Test that the enum works as expected."""
        self.assertIsInstance(Suit.HEARTS, Suit)
        self.assertEqual(list(Suit), [Suit.HEARTS, Suit.DIAMONDS, Suit.CLUBS, Suit.SPADES])
        self.assertEqual(Suit("♥"), Suit.HEARTS)


if __name__ == '__main__':
    unittest.main()