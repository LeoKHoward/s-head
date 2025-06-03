# Shithead Card Game

## Overview

Shithead is a multiplayer card game (implemented here for two players: a human player and a computer opponent) where the
goal is to be the first to play all your cards.

The game uses a standard 52-card deck and involves strategy, luck and tactical card play.

Players progress through three phases: hand, face-up and face-down, with special cards and burning mechanics adding
complexity.

---

## Game Setup

### Deck

- A standard 52-card deck is used (no jokers)
- Cards ranked from 2 (lowest) to Ace (highest, value 14)
- Suits are irrelevant for gameplay

### Players

- Two players:
    - **ME** (human)
    - **COMPUTER** (AI)

### Dealing

- Each player receives 9 cards:
    - 3 face-down (hidden on table)
    - 3 face-up (visible on top of face-down cards)
    - 3 in hand (held privately)

### Setup Phase

- Players may swap cards between their hand and face-up piles to optimise their strategy
- The human player selects 3 card values to place face-up (e.g. `5 5 8`)
- The computer automatically selects face-up cards, prioritising high-value sets or special cards

### Starting the Game

- The remaining deck forms the draw pile
- The human player goes first

---

## Gameplay Rules

### Objective

Be the first player to play all cards from their hand, face-up and face-down piles.

### Turn Structure

- Players take turns playing cards to the pile following these rules:

#### Playing Cards

- Players must play one or more cards valid based on the pile’s top card
- **Hand Phase**: Played cards must have the same value (e.g. two 7s)
- **Face-Up Phase**: Mixed-value cards allowed, provided all non-special cards meet or exceed the pile’s top value
- **Face-Down Phase**: Players blindly select one face-down card to play

#### Drawing Cards

- After playing, if the player’s hand has fewer than 3 cards and the deck isn’t empty, they draw cards to restore their
  hand to 3

#### Picking Up the Pile

- If a player cannot or chooses not to play valid cards, they must pick up the entire pile, adding it to their hand
- Human player may opt for a tactical pickup by entering `tp`

#### End of Turn

- If a player plays a card that burns the pile or plays a **nothing card** (8), they take another turn
- Otherwise, the turn passes to the next player

---

## Card Values and Comparisons

### Standard Values

- Cards ranked as: 2 (2), 3 (3), …, 10 (10), Jack (11), Queen (12), King (13), Ace (14)

### Playable Cards

- **Hand Phase**: Played cards must be same value and either:
    - Special cards (2, 7, **nothing card** (8), 10), always playable
    - Non-special cards with value ≥ pile top value
- **Face-Up Phase**: Mixed-value cards allowed, all non-special cards ≥ pile top value
- A **nothing card** (8) can be played with one non-8 card, which must be special or match underlying pile value (
  ignoring the 8)

---

## Special Cards

- **2 (Reset):** Playable anytime; resets pile, allowing any card next
- **7 (Mirror):** Can be played on any card **except a nothing card (8) or a 10**. When played, the pile’s top value for
  the next turn is determined by the card beneath the 7, effectively "mirroring" that value. The next card played must
  be equal to or higher than that underlying card (or a special card)
- **8 (Nothing Card):** Always playable; pile’s top value determined by card beneath it; grants another turn
- **10 (Burn):** Playable anytime; burns the pile (clears it); grants another turn

---

## Burning the Pile

The pile is burned (cleared) in these cases:

- Four-of-a-Kind: If the last four cards played have the same value (e.g. four Kings)
- 10 Played: Playing a 10 burns the pile

Burning the pile grants the player another turn.

---

## Game Phases

### Hand Phase

- Players play from their hand using same-value sets
- If no valid cards can be played, the player picks up the pile

### Face-Up Phase

- When hand is empty, players play from face-up cards

### Face-Down Phase

- When hand and face-up piles are empty, players play face-down cards blindly
- A chosen face-down card is revealed and played if valid
- If invalid, player picks up the pile as well as the unplayable card

---

## Winning the Game

The game ends when a player has no cards left in hand, face-up, or face-down piles. The first to do so wins.

---

## Additional Notes

- **Tactical Pickup:** Human player can choose to pick up the pile by entering `tp` even if playable cards exist
- **8 with No Follow-Up:** If the only playable card is a **nothing card** (8) but no valid follow-up card exists, the
  player must pick up the pile
- **AI Strategy:**
    - Prioritises high-value or special cards during setup
    - Plays low-value cards, special cards, or completes four-of-a-kinds to burn the pile, especially when advantageous

---

## How to Play

- Ensure Python 3.8+ is installed and project files are in a directory
- Run the game using:

  ```bash
  python main.py
