import unittest
from io import StringIO
from unittest.mock import patch

from enums import Suit
from game_logic import CardGame
from models import Card, Player


class TestGameIntegration(unittest.TestCase):
    def setUp(self):
        """Set up a game for testing."""
        self.game = CardGame()

    # @patch('builtins.input', return_value='2 7 10')
    # @patch('sys.stdout', new_callable=StringIO)
    # def test_setup_phase(self, mock_stdout, mock_input):
    #     """Test the setup phase of the game."""
    #     # Create a controlled deck - need to reverse order since we're using pop()
    #     self.game.deck = [
    #         # Face down cards (will be popped first)
    #         Card(9, Suit.SPADES),
    #         Card(8, Suit.CLUBS),
    #         Card(6, Suit.DIAMONDS),
    #         Card(5, Suit.HEARTS),
    #         Card(4, Suit.SPADES),
    #         Card(3, Suit.CLUBS),
    #         # Face up cards
    #         Card(9, Suit.DIAMONDS),
    #         Card(8, Suit.HEARTS),
    #         Card(6, Suit.SPADES),
    #         Card(5, Suit.CLUBS),
    #         Card(4, Suit.DIAMONDS),
    #         Card(3, Suit.HEARTS),
    #         # Hand cards
    #         Card(14, Suit.DIAMONDS),  # A
    #         Card(12, Suit.HEARTS),  # Q
    #         Card(11, Suit.SPADES),  # J
    #         Card(10, Suit.CLUBS),  # 10
    #         Card(7, Suit.DIAMONDS),  # 7
    #         Card(2, Suit.HEARTS),  # 2
    #     ]
    #
    #     # Initialize players
    #     self.game.players = [Player("ME"), Player("COMPUTER")]
    #
    #     # Deal initial cards manually to have control over what each player gets
    #     # Player 1 (ME) gets: hand=[2♥, 7♦, 10♣], face_up=[J♠, Q♥, A♦], face_down=[3♣, 4♠, 5♥]
    #     # Player 2 (COMPUTER) gets: hand=[3♥, 4♦, 5♣], face_up=[6♠, 8♥, 9♦], face_down=[6♦, 8♣, 9♠]
    #     for player in self.game.players:
    #         player.face_down = [self.game.deck.pop() for _ in range(3)]
    #         player.face_up = [self.game.deck.pop() for _ in range(3)]
    #         player.hand = [self.game.deck.pop() for _ in range(3)]
    #
    #     # Run setup phase
    #     self.game.setup_phase()
    #
    #     # Check that the human player's face up cards match the input
    #     human_face_up_values = [card.value for card in self.game.players[0].face_up]
    #     self.assertEqual(sorted(human_face_up_values), [2, 7, 10])
    #
    #     # Check that the computer player has face up cards
    #     self.assertEqual(len(self.game.players[1].face_up), 3)

    # @patch('builtins.input', return_value='1')
    # def test_handle_player_input(self, mock_input):
    #     """Test that handle_player_input processes input correctly."""
    #     playable_sets = [
    #         [Card(10, Suit.HEARTS)],
    #         [Card(7, Suit.DIAMONDS), Card(7, Suit.CLUBS)]
    #     ]
    #
    #     # Player chooses the first set
    #     chosen_set = self.game.handle_player_input(playable_sets)
    #     self.assertEqual(chosen_set, playable_sets[0])

    def test_computer_choose_playable_set(self):
        """Test that computer_choose_playable_set selects a valid set."""
        playable_sets = [
            [Card(10, Suit.HEARTS)],
            [Card(7, Suit.DIAMONDS), Card(7, Suit.CLUBS)],
            [Card(2, Suit.SPADES)]
        ]

        # Set up pile with a high value
        top_pile_value = 12

        # Computer should choose 2 to reset the pile
        chosen_set = self.game.computer_choose_playable_set(playable_sets, top_pile_value)
        self.assertEqual(chosen_set[0].value, 2)

        # Set up pile with a low value
        top_pile_value = 3

        # Computer should choose the lowest non-special card
        playable_sets = [
            [Card(5, Suit.HEARTS)],
            [Card(7, Suit.DIAMONDS)],
            [Card(10, Suit.CLUBS)]
        ]
        chosen_set = self.game.computer_choose_playable_set(playable_sets, top_pile_value)
        self.assertEqual(chosen_set[0].value, 5)

    def test_full_game_setup(self):
        """Test the complete game setup without user input."""
        # Test the deal_cards method which sets up the initial game state
        self.game.deal_cards()

        # Verify game state after dealing
        self.assertEqual(len(self.game.players), 2)
        self.assertEqual(self.game.players[0].name, "ME")
        self.assertEqual(self.game.players[1].name, "COMPUTER")

        # Verify each player has correct number of cards
        for player in self.game.players:
            self.assertEqual(len(player.hand), 3)
            self.assertEqual(len(player.face_up), 3)
            self.assertEqual(len(player.face_down), 3)
            self.assertEqual(player.total_cards(), 9)

        # Verify deck has remaining cards
        self.assertEqual(len(self.game.deck), 34)  # 52 - (2 players * 9 cards each)

    def test_ai_setup_cards(self):
        """Test the AI's card setup logic."""
        player = Player("COMPUTER")

        # Give the AI some cards to choose from
        player.hand = [
            Card(2, Suit.HEARTS),  # Special card
            Card(5, Suit.DIAMONDS),  # Regular card
            Card(8, Suit.CLUBS)  # Special card
        ]
        player.face_up = [
            Card(10, Suit.SPADES),  # Special card
            Card(12, Suit.HEARTS),  # High value
            Card(14, Suit.DIAMONDS)  # Highest value
        ]

        # Run AI setup
        self.game.choose_ai_setup_cards(player)

        # Verify the AI chose 3 face-up cards
        self.assertEqual(len(player.face_up), 3)
        self.assertEqual(len(player.hand), 3)

        # Verify total cards remain the same
        self.assertEqual(len(player.face_up) + len(player.hand), 6)

    def test_card_playing_mechanics(self):
        """Test the card playing mechanics."""
        # Set up a simple game state
        player = Player("Test Player")
        player.hand = [Card(5, Suit.HEARTS), Card(10, Suit.DIAMONDS)]

        # Test playing a regular card
        self.game.pile = [Card(3, Suit.SPADES)]
        another_turn = self.game.play_cards(player, [Card(5, Suit.HEARTS)])

        self.assertFalse(another_turn)  # Regular card doesn't give another turn
        self.assertEqual(len(player.hand), 1)
        self.assertEqual(len(self.game.pile), 2)
        self.assertEqual(self.game.pile[-1].value, 5)

        # Test playing a 10 (burn card)
        another_turn = self.game.play_cards(player, [Card(10, Suit.DIAMONDS)])

        self.assertTrue(another_turn)  # 10 gives another turn
        self.assertEqual(len(player.hand), 0)
        self.assertEqual(len(self.game.pile), 0)  # Pile should be burned

    def test_game_over_detection(self):
        """Test game over detection."""
        # Set up players
        player1 = Player("Player 1")
        player2 = Player("Player 2")
        self.game.players = [player1, player2]

        # Both players have cards - game should not be over
        player1.hand = [Card(5, Suit.HEARTS)]
        player2.hand = [Card(7, Suit.DIAMONDS)]

        self.assertFalse(self.game.check_game_over())
        self.assertIsNone(self.game.winner)

        # Player 1 runs out of all cards - game should be over
        player1.hand = []
        player1.face_up = []
        player1.face_down = []

        self.assertTrue(self.game.check_game_over())
        self.assertEqual(self.game.winner, player1)
        self.assertTrue(self.game.game_over)


if __name__ == '__main__':
    unittest.main()
