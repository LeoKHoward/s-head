import unittest

from enums import Suit
from game_logic import CardGame
from models import Card, Player


class TestGameLogic(unittest.TestCase):
    def setUp(self):
        """Set up a fresh game instance for each test."""
        self.game = CardGame()
        self.game.deck = self.game.create_deck()
        self.game.players = [Player("ME"), Player("COMPUTER")]
        self.player = self.game.players[0]
        self.computer = self.game.players[1]

    def test_create_deck(self):
        """Test deck creation (52 cards, all unique)."""
        deck = self.game.create_deck()
        self.assertEqual(len(deck), 52)
        self.assertEqual(len(set(deck)), 52)  # All cards unique
        values = [card.value for card in deck]
        suits = [card.suit for card in deck]
        self.assertEqual(sorted(values), [2] * 4 + [3] * 4 + [4] * 4 + [5] * 4 + [6] * 4 + [7] * 4 +
                         [8] * 4 + [9] * 4 + [10] * 4 + [11] * 4 + [12] * 4 + [13] * 4 + [14] * 4)
        self.assertEqual(len([s for s in suits if s == Suit.HEARTS]), 13)

    def test_deal_cards(self):
        """Test card dealing to players."""
        self.game.deal_cards()
        for player in self.game.players:
            self.assertEqual(len(player.hand), 3)
            self.assertEqual(len(player.face_up), 3)
            self.assertEqual(len(player.face_down), 3)
        self.assertEqual(len(self.game.deck), 52 - 18)  # 2 players * 9 cards

    def test_group_cards_by_value(self):
        """Test grouping cards by value."""
        cards = [Card(7, Suit.HEARTS), Card(7, Suit.SPADES), Card(10, Suit.CLUBS)]
        groups = self.game.card_utils.group_cards_by_value(cards)
        self.assertEqual(len(groups), 2)
        self.assertEqual(len(groups[7]), 2)
        self.assertEqual(len(groups[10]), 1)

    def test_get_pile_top_value_for_comparison(self):
        """Test getting pile top value, skipping special cards."""
        self.game.pile = [Card(5, Suit.HEARTS), Card(8, Suit.SPADES), Card(10, Suit.CLUBS)]
        self.assertEqual(self.game.card_utils.get_pile_top_value_for_comparison(self.game.pile), 5)
        self.game.pile = [Card(8, Suit.SPADES)]
        self.assertEqual(self.game.card_utils.get_pile_top_value_for_comparison(self.game.pile), None)
        self.game.pile = []
        self.assertEqual(self.game.card_utils.get_pile_top_value_for_comparison(self.game.pile), None)

    def test_can_play_cards_hand_phase(self):
        """Test card play validation in hand phase."""
        self.player.hand = [Card(7, Suit.HEARTS), Card(7, Suit.SPADES), Card(10, Suit.CLUBS)]
        self.game.pile = [Card(5, Suit.DIAMONDS)]

        # Same value, >= pile
        self.assertTrue(self.game.card_utils.can_play_cards([Card(7, Suit.HEARTS), Card(7, Suit.SPADES)]))
        # Special card (10)
        self.assertTrue(self.game.card_utils.can_play_cards([Card(10, Suit.CLUBS)]))
        # Invalid: different values
        self.assertFalse(self.game.card_utils.can_play_cards([Card(7, Suit.HEARTS), Card(10, Suit.CLUBS)]))
        # Valid: 7 is a special card, playable on Ace
        self.game.pile = [Card(14, Suit.HEARTS)]
        self.assertTrue(self.game.card_utils.can_play_cards([Card(7, Suit.HEARTS)]))

    def test_can_play_cards_face_up_phase(self):
        """Test card play validation in face-up phase."""
        self.player.hand = []
        self.player.face_up = [Card(7, Suit.HEARTS), Card(10, Suit.CLUBS), Card(14, Suit.SPADES)]
        self.game.pile = [Card(5, Suit.DIAMONDS)]

        # Mixed values with special card (10)
        self.assertTrue(self.game.card_utils.can_play_cards([Card(10, Suit.CLUBS), Card(14, Suit.SPADES)]))
        # Non-special cards >= pile
        self.assertTrue(self.game.card_utils.can_play_cards([Card(7, Suit.HEARTS), Card(14, Suit.SPADES)]))
        # Valid: 7 is a special card, playable on King
        self.game.pile = [Card(13, Suit.HEARTS)]
        self.assertTrue(self.game.card_utils.can_play_cards([Card(7, Suit.HEARTS)]))

    def test_can_play_nothing_card(self):
        """Test playing nothing card (8) with non-8 card."""
        self.player.hand = [Card(8, Suit.HEARTS), Card(7, Suit.SPADES)]
        self.game.pile = [Card(10, Suit.CLUBS)]
        self.assertTrue(self.game.card_utils.can_play_cards([Card(8, Suit.HEARTS), Card(7, Suit.SPADES)]))
        self.player.hand = [Card(8, Suit.HEARTS), Card(6, Suit.SPADES)]
        self.game.pile = [Card(14, Suit.HEARTS), Card(10, Suit.CLUBS)]
        self.assertFalse(self.game.card_utils.can_play_cards([Card(8, Suit.HEARTS), Card(6, Suit.SPADES)]))

    def test_play_cards_burn(self):
        """Test pile burning with 10 or four-of-a-kind."""
        self.player.hand = [Card(10, Suit.CLUBS)]
        self.assertTrue(self.game.card_utils.play_cards(self.player, [Card(10, Suit.CLUBS)]))
        self.assertEqual(self.game.pile, [])
        self.assertEqual(self.player.hand, [])

        self.game.pile = [Card(7, Suit.HEARTS), Card(7, Suit.SPADES), Card(7, Suit.CLUBS)]
        self.player.hand = [Card(7, Suit.DIAMONDS)]
        self.assertTrue(self.game.card_utils.play_cards(self.player, [Card(7, Suit.DIAMONDS)]))
        self.assertEqual(self.game.pile, [])

    def test_draw_card(self):
        """Test drawing cards to restore hand to 3."""
        self.player.hand = [Card(2, Suit.HEARTS)]
        self.game.deck = [Card(3, Suit.CLUBS), Card(4, Suit.SPADES)]
        self.game.draw_card(self.player)
        self.assertEqual(len(self.player.hand), 3)
        self.assertEqual(len(self.game.deck), 0)

    def test_parse_card_value(self):
        """Test parsing card value input."""
        self.assertEqual(self.game.input_utils.parse_card_value("a"), 14)
        self.assertEqual(self.game.input_utils.parse_card_value("10"), 10)
        self.assertEqual(self.game.input_utils.parse_card_value("j"), 11)
        self.assertIsNone(self.game.input_utils.parse_card_value("x"))

    def test_check_game_over(self):
        """Test game over condition."""
        self.player.hand = []
        self.player.face_up = []
        self.player.face_down = []
        self.computer.hand = [Card(2, Suit.HEARTS)]  # Ensure other player has cards
        self.assertTrue(self.game.check_game_over())
        self.assertEqual(self.game.winner, self.player)

        self.player.hand = [Card(2, Suit.HEARTS)]
        self.assertFalse(self.game.check_game_over())
        self.assertIsNone(self.game.winner)

    def test_choose_ai_setup_cards(self):
        """Test AI setup phase prioritises special cards (10, 8) and high-value cards."""
        player = Player("COMPUTER")
        player.hand = [Card(10, Suit.SPADES), Card(11, Suit.SPADES), Card(12, Suit.HEARTS)]
        player.face_up = [Card(8, Suit.SPADES), Card(2, Suit.HEARTS), Card(5, Suit.HEARTS)]
        self.game.ai_logic.choose_ai_setup_cards(player)
        expected_face_up_values = {8, 10, 12}  # 8♠, 10♠, Q♥
        actual_face_up_values = {card.value for card in player.face_up}
        self.assertEqual(actual_face_up_values, expected_face_up_values)
        self.assertEqual(len(player.face_up), 3)
        self.assertEqual(len(player.hand), 3)


if __name__ == '__main__':
    unittest.main()
