import random
import os
import sys
from enum import Enum
from typing import Dict, List, Tuple, Optional

class PlayerColor(Enum):
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class GameStatus(Enum):
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"

class Player:
    def __init__(self, player_id: int, name: str = None):
        self.id = player_id
        self.name = name or f"Player {player_id}"
        self.position = 1
        self.moves_count = 0
        self.ladder_climbs = 0
        self.snake_slides = 0
        self.color = PlayerColor.BLUE if player_id == 1 else PlayerColor.YELLOW
    
    def move(self, dice_value: int) -> int:
        new_position = self.position + dice_value
        self.position = min(new_position, 100)
        self.moves_count += 1
        return self.position
    
    def reset_position(self):
        self.position = 1
        self.moves_count = 0
        self.ladder_climbs = 0
        self.snake_slides = 0
    
    def __str__(self) -> str:
        return f"{self.color.value}{self.name} (Position: {self.position}){PlayerColor.RESET.value}"

class Board:
    BOARD_SIZE = 100
    GRID_SIZE = 10
    SNAKES = {17: 7, 54: 34, 62: 42, 87: 36, 93: 71, 95: 80, 98: 79}
    LADDERS = {1: 38, 4: 14, 9: 31, 21: 42, 28: 84, 51: 67, 72: 91, 80: 99}
    
    def __init__(self):
        self.board_data = self._create_board()
    
    def _create_board(self) -> Dict[int, str]:
        board = {}
        for i in range(1, self.BOARD_SIZE + 1):
            if i in self.SNAKES:
                board[i] = 'snake'
            elif i in self.LADDERS:
                board[i] = 'ladder'
            else:
                board[i] = 'empty'
        return board
    
    def get_destination(self, position: int) -> Tuple[int, Optional[str]]:
        if position in self.SNAKES:
            return self.SNAKES[position], 'snake'
        elif position in self.LADDERS:
            return self.LADDERS[position], 'ladder'
        else:
            return position, None
    
    def is_valid_position(self, position: int) -> bool:
        return 1 <= position <= self.BOARD_SIZE
    
    def is_winning_position(self, position: int) -> bool:
        return position == self.BOARD_SIZE

class Game:
    def __init__(self, player1_name: str = None, player2_name: str = None):
        self.board = Board()
        self.player1 = Player(1, player1_name or "Player 1")
        self.player2 = Player(2, player2_name or "Player 2")
        self.current_player_id = 1
        self.status = GameStatus.RUNNING
        self.moves_history = []
        self.dice_rolls = []
    
    @property
    def current_player(self) -> Player:
        return self.player1 if self.current_player_id == 1 else self.player2
    
    @property
    def other_player(self) -> Player:
        return self.player2 if self.current_player_id == 1 else self.player1
    
    def roll_dice(self) -> int:
        dice_value = random.randint(1, 6)
        self.dice_rolls.append(dice_value)
        return dice_value
    
    def play_turn(self) -> Dict:
        turn_data = {
            'player': self.current_player.name,
            'player_id': self.current_player_id,
            'old_position': self.current_player.position,
            'dice_value': self.roll_dice(),
            'new_position': None,
            'final_position': None,
            'encounter': None,
            'message': ''
        }
        
        turn_data['new_position'] = self.current_player.move(turn_data['dice_value'])
        
        if turn_data['old_position'] + turn_data['dice_value'] > 100:
            turn_data['message'] = f"Rolled too high! Stay at position {turn_data['old_position']}"
            self.current_player.position = turn_data['old_position']
            turn_data['final_position'] = turn_data['old_position']
        else:
            destination, encounter_type = self.board.get_destination(turn_data['new_position'])
            
            if encounter_type == 'snake':
                self.current_player.snake_slides += 1
                turn_data['encounter'] = 'snake'
                turn_data['message'] = f"Landed on a snake! Slid down from {turn_data['new_position']} to {destination} 🐍"
                self.current_player.position = destination
            elif encounter_type == 'ladder':
                self.current_player.ladder_climbs += 1
                turn_data['encounter'] = 'ladder'
                turn_data['message'] = f"Landed on a ladder! Climbed up from {turn_data['new_position']} to {destination} 🪜"
                self.current_player.position = destination
            else:
                turn_data['message'] = f"Moved from {turn_data['old_position']} to {turn_data['new_position']}"
            
            turn_data['final_position'] = self.current_player.position
        
        self.moves_history.append(turn_data)
        
        if self.board.is_winning_position(self.current_player.position):
            self.status = GameStatus.FINISHED
            turn_data['message'] += f" 🎉 {self.current_player.name} WINS! 🎉"
        
        return turn_data
    
    def switch_player(self):
        self.current_player_id = 2 if self.current_player_id == 1 else 1
    
    def reset(self):
        self.player1.reset_position()
        self.player2.reset_position()
        self.current_player_id = 1
        self.status = GameStatus.RUNNING
        self.moves_history = []
        self.dice_rolls = []

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_welcome():
    print(f"\n{PlayerColor.BOLD.value}{PlayerColor.MAGENTA.value}")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "🎲 SNAKE AND LADDER GAME 🎲".center(78) + "║")
    print("║" + "Interactive Python Implementation".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    print(f"{PlayerColor.RESET.value}\n")

def play_game():
    clear_screen()
    display_welcome()
    
    print(f"{PlayerColor.BOLD.value}Enter Player Names:{PlayerColor.RESET.value}")
    player1_name = input("Player 1 name (press Enter for 'Player 1'): ").strip() or "Player 1"
    player2_name = input("Player 2 name (press Enter for 'Player 2'): ").strip() or "Player 2"
    
    game = Game(player1_name, player2_name)
    
    while game.status == GameStatus.RUNNING:
        print(f"\n{PlayerColor.BOLD.value}Current Status:{PlayerColor.RESET.value}")
        print(f"  {game.player1}")
        print(f"  {game.player2}")
        print(f"{PlayerColor.BOLD.value}Current Turn:{PlayerColor.RESET.value} {game.current_player}")
        
        command = input(f"\n{game.current_player.color.value}{game.current_player.name}{PlayerColor.RESET.value}, press Enter to roll: ").strip().lower()
        
        turn_data = game.play_turn()
        print(f"\n{PlayerColor.BOLD.value}TURN RESULT:{PlayerColor.RESET.value}")
        print(f"  Dice: {turn_data['dice_value']}")
        print(f"  {turn_data['message']}")
        
        if game.status == GameStatus.FINISHED:
            print(f"\n{PlayerColor.BOLD.value}{PlayerColor.GREEN.value}🎉 GAME OVER! 🎉{PlayerColor.RESET.value}")
            print(f"{game.current_player.color.value}{game.current_player.name}{PlayerColor.RESET.value} wins!")
        else:
            game.switch_player()

if __name__ == "__main__":
    try:
        play_game()
    except KeyboardInterrupt:
        print(f"\n{PlayerColor.BOLD.value}Thanks for playing! Goodbye!{PlayerColor.RESET.value}\n")
