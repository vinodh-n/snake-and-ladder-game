"""
Unit tests for Snake and Ladder Game

Run tests: python -m pytest test_snake_and_ladder.py -v
Or run: python test_snake_and_ladder.py
"""

import unittest
from snake_and_ladder import Player, Board, Game, GameStatus


class TestPlayer(unittest.TestCase):
    """Test cases for Player class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.player1 = Player(1, "Alice")
        self.player2 = Player(2, "Bob")
    
    def test_player_initialization(self):
        """Test player initialization"""
        self.assertEqual(self.player1.id, 1)
        self.assertEqual(self.player1.name, "Alice")
        self.assertEqual(self.player1.position, 1)
        self.assertEqual(self.player1.moves_count, 0)
    
    def test_player_move_forward(self):
        """Test player moves forward"""
        new_pos = self.player1.move(5)
        self.assertEqual(new_pos, 6)
        self.assertEqual(self.player1.position, 6)
        self.assertEqual(self.player1.moves_count, 1)
    
    def test_player_move_beyond_100(self):
        """Test player can't move beyond 100"""
        self.player1.position = 98
        new_pos = self.player1.move(5)
        self.assertEqual(new_pos, 100)  # Capped at 100
    
    def test_player_multiple_moves(self):
        """Test multiple consecutive moves"""
        self.player1.move(3)
        self.assertEqual(self.player1.position, 4)
        self.player1.move(5)
        self.assertEqual(self.player1.position, 9)
        self.assertEqual(self.player1.moves_count, 2)
    
    def test_player_reset(self):
        """Test player reset"""
        self.player1.move(10)
        self.player1.ladder_climbs = 5
        self.player1.reset_position()
        
        self.assertEqual(self.player1.position, 1)
        self.assertEqual(self.player1.moves_count, 0)
        self.assertEqual(self.player1.ladder_climbs, 0)


class TestBoard(unittest.TestCase):
    """Test cases for Board class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.board = Board()
    
    def test_board_size(self):
        """Test board has correct size"""
        self.assertEqual(len(self.board.board_data), 100)
    
    def test_snakes_count(self):
        """Test correct number of snakes"""
        self.assertEqual(len(self.board.SNAKES), 7)
    
    def test_ladders_count(self):
        """Test correct number of ladders"""
        self.assertEqual(len(self.board.LADDERS), 8)
    
    def test_get_destination_empty_square(self):
        """Test destination for empty square"""
        destination, encounter_type = self.board.get_destination(5)
        self.assertEqual(destination, 5)
        self.assertIsNone(encounter_type)
    
    def test_get_destination_ladder(self):
        """Test destination for ladder"""
        destination, encounter_type = self.board.get_destination(1)
        self.assertEqual(destination, 38)
        self.assertEqual(encounter_type, 'ladder')
    
    def test_get_destination_snake(self):
        """Test destination for snake"""
        destination, encounter_type = self.board.get_destination(17)
        self.assertEqual(destination, 7)
        self.assertEqual(encounter_type, 'snake')
    
    def test_is_valid_position(self):
        """Test position validation"""
        self.assertTrue(self.board.is_valid_position(1))
        self.assertTrue(self.board.is_valid_position(50))
        self.assertTrue(self.board.is_valid_position(100))
        self.assertFalse(self.board.is_valid_position(0))
        self.assertFalse(self.board.is_valid_position(101))
    
    def test_is_winning_position(self):
        """Test winning position"""
        self.assertTrue(self.board.is_winning_position(100))
        self.assertFalse(self.board.is_winning_position(99))
        self.assertFalse(self.board.is_winning_position(1))


class TestGame(unittest.TestCase):
    """Test cases for Game class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.game = Game("Alice", "Bob")
    
    def test_game_initialization(self):
        """Test game initialization"""
        self.assertEqual(self.game.player1.name, "Alice")
        self.assertEqual(self.game.player2.name, "Bob")
        self.assertEqual(self.game.current_player_id, 1)
        self.assertEqual(self.game.status, GameStatus.RUNNING)
    
    def test_current_player_property(self):
        """Test current player property"""
        self.assertEqual(self.game.current_player.id, 1)
        self.game.current_player_id = 2
        self.assertEqual(self.game.current_player.id, 2)
    
    def test_other_player_property(self):
        """Test other player property"""
        self.assertEqual(self.game.other_player.id, 2)
        self.game.current_player_id = 2
        self.assertEqual(self.game.other_player.id, 1)
    
    def test_roll_dice_range(self):
        """Test dice roll is in range 1-6"""
        for _ in range(100):
            dice_value = self.game.roll_dice()
            self.assertGreaterEqual(dice_value, 1)
            self.assertLessEqual(dice_value, 6)
    
    def test_dice_rolls_recorded(self):
        """Test dice rolls are recorded"""
        initial_count = len(self.game.dice_rolls)
        self.game.roll_dice()
        self.assertEqual(len(self.game.dice_rolls), initial_count + 1)
    
    def test_play_turn_basic_move(self):
        """Test basic turn play"""
        # Mock the dice roll for testing
        self.game.roll_dice = lambda: 5
        turn_data = self.game.play_turn()
        
        self.assertEqual(turn_data['player_id'], 1)
        self.assertEqual(turn_data['old_position'], 1)
        self.assertEqual(turn_data['dice_value'], 5)
        self.assertEqual(turn_data['final_position'], 6)
    
    def test_play_turn_with_ladder(self):
        """Test turn with ladder encounter"""
        self.game.player1.position = 1
        self.game.roll_dice = lambda: 0  # Will be called in play_turn
        
        # Manually set up ladder landing
        self.game.roll_dice = lambda: 0  # Avoid recursive call
        original_roll = self.game.roll_dice
        self.game.roll_dice = lambda: 3  # Land on position 4 (has ladder to 14)
        
        turn_data = self.game.play_turn()
        
        # Reset roll_dice
        self.game.roll_dice = original_roll
        
        self.assertEqual(turn_data['new_position'], 4)
        self.assertEqual(turn_data['encounter'], 'ladder')
    
    def test_switch_player(self):
        """Test player switching"""
        self.assertEqual(self.game.current_player_id, 1)
        self.game.switch_player()
        self.assertEqual(self.game.current_player_id, 2)
        self.game.switch_player()
        self.assertEqual(self.game.current_player_id, 1)
    
    def test_game_reset(self):
        """Test game reset"""
        # Make some moves
        self.game.player1.position = 50
        self.game.player2.position = 30
        self.game.moves_history.append({'test': 'data'})
        self.game.current_player_id = 2
        
        # Reset
        self.game.reset()
        
        self.assertEqual(self.game.player1.position, 1)
        self.assertEqual(self.game.player2.position, 1)
        self.assertEqual(self.game.current_player_id, 1)
        self.assertEqual(len(self.game.moves_history), 0)
    
    def test_get_game_stats(self):
        """Test game statistics"""
        self.game.player1.position = 50
        self.game.player1.moves_count = 10
        self.game.player1.ladder_climbs = 2
        self.game.player1.snake_slides = 1
        
        stats = self.game.get_game_stats()
        
        self.assertEqual(stats['player1']['position'], 50)
        self.assertEqual(stats['player1']['moves'], 10)
        self.assertEqual(stats['player1']['ladder_climbs'], 2)
        self.assertEqual(stats['player1']['snake_slides'], 1)
    
    def test_cant_exceed_100(self):
        """Test player can't exceed position 100"""
        self.game.player1.position = 98
        self.game.roll_dice = lambda: 5  # Would be 103
        turn_data = self.game.play_turn()
        
        # Should stay at 98 (rolled too high)
        self.assertEqual(self.game.player1.position, 98)


class TestGameWinCondition(unittest.TestCase):
    """Test cases for game winning conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.game = Game("Alice", "Bob")
    
    def test_win_at_100(self):
        """Test player wins when reaching 100"""
        self.game.player1.position = 95
        self.game.roll_dice = lambda: 5
        
        turn_data = self.game.play_turn()
        
        self.assertEqual(self.game.player1.position, 100)
        self.assertEqual(self.game.status, GameStatus.FINISHED)
    
    def test_cant_win_past_100(self):
        """Test player can't win by rolling past 100"""
        self.game.player1.position = 96
        self.game.roll_dice = lambda: 5  # Would be 101
        
        turn_data = self.game.play_turn()
        
        self.assertEqual(self.game.player1.position, 96)
        self.assertEqual(self.game.status, GameStatus.RUNNING)


class TestGameIntegration(unittest.TestCase):
    """Integration tests for complete game scenarios"""
    
    def test_complete_game_scenario(self):
        """Test a complete game scenario"""
        game = Game("Alice", "Bob")
        
        # Play several turns
        for _ in range(20):
            if game.status == GameStatus.FINISHED:
                break
            
            turn_data = game.play_turn()
            self.assertIsNotNone(turn_data)
            self.assertEqual(turn_data['player_id'] in [1, 2], True)
            
            if game.status == GameStatus.RUNNING:
                game.switch_player()
        
        # Game should have history
        self.assertGreater(len(game.moves_history), 0)


def run_tests():
    """Run all tests"""
    unittest.main(verbosity=2)


if __name__ == '__main__':
    run_tests()
