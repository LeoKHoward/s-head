import random
from typing import List, Optional
from enums import Suit
from models import Card, Player
from card_utils import CardUtils
from ai_logic import AILogic
from input_utils import InputUtils


class CardGame:
    def __init__(self):
        self.deck: List[Card] = []
        self.players: List[Player] = []
        self.pile: List[Card] = []
        self.current_player = 0
        self.game_over = None
        self.winner: Optional[Player] = None
        self.card_utils = CardUtils(self)
        self.ai_logic = AILogic(self)
        self.input_utils = InputUtils(self)

    def create_deck(self) -> List[Card]:
        return self.card_utils.create_deck()

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

    def draw_card(self, player: Player):
        new_hand = player.hand.copy()
        while len(new_hand) < 3 and self.deck:
            new_hand.append(self.deck.pop())
        player.hand = new_hand

    def player_must_pickup_pile(self, player: Player):
        print(f"{player.name} picks up the pile!")
        new_hand = player.hand + self.pile
        self.pile = []
        player.hand = new_hand

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

        pile_display = self.pile[-5:] if len(self.pile) > 3 else self.pile
        print(f"\nPile ({len(self.pile)}): {pile_display}")
        if self.pile:
            print(f"Top pile value: {self.card_utils.get_top_pile_value()}")
        print(f"Deck remaining: {len(self.deck)}")

    def check_game_over(self) -> bool:
        players_with_no_cards = [player for player in self.players if not player.has_cards()]
        if len(players_with_no_cards) == 1:
            self.game_over = True
            self.winner = players_with_no_cards[0]
            return True
        self.game_over = False
        self.winner = None
        return False

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

                    value_str = input("Choose 3 card values to place face-up: ").strip()
                    face_up, hand = self.input_utils.parse_face_up_choice(value_str, combined)

                    if face_up and hand:
                        player.face_up = face_up
                        player.hand = hand
                        break
                    else:
                        value_parts = value_str.replace(" ", "")
                        if len(value_parts) < 3 or len(value_parts) > 5:
                            print("Please enter exactly 3 card values!")
                        else:
                            for i in range(0, len(value_parts), 1):
                                val = value_parts[i]
                                if val == '1' and i + 1 < len(value_parts) and value_parts[i:i + 2] == "10":
                                    val = "10"
                                    i += 1
                                if val not in self.card_utils.FACE_VALUES:
                                    print(f"Invalid card value '{val}'. Try again.")
                                    break
                                elif self.input_utils.parse_card_value(val) not in [card.value for card in combined]:
                                    print(f"Card value '{val}' not available in your cards! Try again!")
                                    break
            else:
                self.ai_logic.choose_ai_setup_cards(player)

            player.face_up.sort(key=lambda card: card.value)
            print(f"After setup - Hand: {player.hand}, Face-up: {player.face_up}")

    def player_turn(self, player: Player) -> bool:
        print(f"\n{player.name}'s turn:")

        if player.can_play_from_face_down():
            if not hasattr(player, 'face_down_positions'):
                player.face_down_positions = list(range(1, len(player.face_down) + 1))

            print(f"Face-down cards available: {len(player.face_down)}")
            valid_positions = player.face_down_positions

            if player.name == "COMPUTER":
                choice = random.choice(valid_positions)
                chosen_index = player.face_down_positions.index(choice)
                chosen_cards = [player.face_down[chosen_index]]
                print(f"{player.name} plays: {chosen_cards}")
                if self.card_utils.can_play_cards(chosen_cards):
                    player.face_down_positions.remove(choice)
                    another_turn = self.card_utils.play_cards(player, chosen_cards)
                    self.draw_card(player)
                    return another_turn
                else:
                    print(f"{chosen_cards[0]} cannot be played. {player.name} must pick up the pile.")
                    player.face_down_positions.remove(choice)
                    player.face_down.pop(chosen_index)
                    self.player_must_pickup_pile(player)
                    self.draw_card(player)
                    return False
            else:
                prompt = f"Choose a face-down card ({', '.join(map(str, valid_positions))}): "
                while True:
                    choice = input(prompt).strip()
                    if choice.isdigit() and int(choice) in valid_positions:
                        chosen_index = player.face_down_positions.index(int(choice))
                        chosen_cards = [player.face_down[chosen_index]]
                        print(f"You played: {chosen_cards}")
                        if self.card_utils.can_play_cards(chosen_cards):
                            player.face_down_positions.remove(int(choice))
                            another_turn = self.card_utils.play_cards(player, chosen_cards)
                            self.draw_card(player)
                            return another_turn
                        else:
                            print(f"{chosen_cards[0]} cannot be played. You must pick up the pile.")
                            player.face_down_positions.remove(int(choice))
                            player.face_down.pop(chosen_index)
                            self.player_must_pickup_pile(player)
                            self.draw_card(player)
                            return False
                    print(f"Invalid choice. Please enter a number from {', '.join(map(str, valid_positions))}")

        playable_sets = self.card_utils.get_playable_cards(player)
        if not playable_sets:
            print(f"{player.name} has no playable cards and must pick up the pile.")
            self.player_must_pickup_pile(player)
            self.draw_card(player)
            return False

        top_value = self.card_utils.get_top_pile_value()
        if player.name == "ME" and player.hand:
            can_play = False
            has_eight = False
            for s in playable_sets:
                if any(card.value in [2, 7, 10] for card in s):
                    can_play = True
                    break
                elif any(card.value == 8 for card in s):
                    has_eight = True
                    underlying_value = self.card_utils.get_pile_top_value_for_comparison(
                        self.pile[:-1]) or 0 if self.pile else 0
                    follow_cards = [card for card in player.hand if card not in s]
                    for follow_card in follow_cards:
                        if follow_card.value in [2, 7, 8, 10] or self.card_utils._base_card_value(
                                follow_card) >= underlying_value:
                            can_play = True
                            break
                    if can_play:
                        break
                elif all(self.card_utils._base_card_value(card) >= top_value for card in s):
                    can_play = True
                    break
                elif len(s) >= 4 and all(card.value == s[0].value for card in s):
                    can_play = True
                    break

            if not can_play and has_eight:
                print(
                    "Your only playable card is an 8, but you have no valid follow-up card. You must pick up the pile.")
                self.player_must_pickup_pile(player)
                self.draw_card(player)
                return False

        if player.name == "COMPUTER":
            chosen_cards = self.ai_logic.computer_choose_playable_set(playable_sets, top_value, player)
            if chosen_cards:
                print(f"{player.name} plays: {chosen_cards}")
                another_turn = self.card_utils.play_cards(player, chosen_cards)
                self.draw_card(player)
                return another_turn
            else:
                print(f"{player.name} has no playable cards and must pick up the pile.")
                self.player_must_pickup_pile(player)
                self.draw_card(player)
                return False

        chosen_cards = self.input_utils.handle_player_input(playable_sets)
        if chosen_cards:
            print(f"You played: {chosen_cards}")
            another_turn = self.card_utils.play_cards(player, chosen_cards)
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
