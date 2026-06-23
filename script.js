// Game Configuration
const BOARD_SIZE = 100;
const GRID_SIZE = 10;

// Snakes and Ladders positions (start -> end)
const snakesAndLadders = {
    // Snakes (going down)
    17: 7,
    54: 34,
    62: 42,
    87: 36,
    93: 71,
    95: 80,
    98: 79,
    
    // Ladders (going up)
    1: 38,
    4: 14,
    9: 31,
    21: 42,
    28: 84,
    51: 67,
    72: 91,
    80: 99
};

// Game State
let gameState = {
    players: [
        { id: 1, position: 1, element: 'p1-position' },
        { id: 2, position: 1, element: 'p2-position' }
    ],
    currentPlayer: 0,
    diceValue: 0,
    gameOver: false,
    moveHistory: [],
    diceRolled: false
};

// DOM Elements
const boardElement = document.getElementById('board');
const rollBtn = document.getElementById('rollBtn');
const resetBtn = document.getElementById('resetBtn');
const rulesBtn = document.getElementById('rulesBtn');
const playAgainBtn = document.getElementById('playAgainBtn');
const diceElement = document.getElementById('dice');
const diceValueElement = document.getElementById('dice-value');
const currentPlayerElement = document.getElementById('current-player');
const gameMessageElement = document.getElementById('game-message');
const movesListElement = document.getElementById('movesList');
const rulesModal = document.getElementById('rulesModal');
const winnerModal = document.getElementById('winnerModal');
const winnerText = document.getElementById('winnerText');
const closeButton = document.querySelector('.close');

// Initialize Game
function initializeGame() {
    createBoard();
    updateUI();
    addEventListeners();
}

// Create Board
function createBoard() {
    boardElement.innerHTML = '';
    
    // Create squares in reverse order for the snake and ladder board pattern
    const squareNumbers = [];
    for (let row = GRID_SIZE - 1; row >= 0; row--) {
        if (row % 2 === GRID_SIZE - 1) {
            // Left to right
            for (let col = 0; col < GRID_SIZE; col++) {
                squareNumbers.push(row * GRID_SIZE + col + 1);
            }
        } else {
            // Right to left
            for (let col = GRID_SIZE - 1; col >= 0; col--) {
                squareNumbers.push(row * GRID_SIZE + col + 1);
            }
        }
    }
    
    squareNumbers.forEach(num => {
        const square = document.createElement('div');
        square.className = 'square empty';
        square.id = `square-${num}`;
        square.textContent = num;
        
        // Add ladder or snake icon
        if (snakesAndLadders[num]) {
            const destination = snakesAndLadders[num];
            if (destination > num) {
                square.classList.add('ladder');
                square.title = `Ladder to ${destination}`;
            } else {
                square.classList.add('snake');
                square.title = `Snake to ${destination}`;
            }
        }
        
        boardElement.appendChild(square);
    });
}

// Add Event Listeners
function addEventListeners() {
    rollBtn.addEventListener('click', rollDice);
    resetBtn.addEventListener('click', resetGame);
    rulesBtn.addEventListener('click', openRulesModal);
    closeButton.addEventListener('click', closeModal);
    playAgainBtn.addEventListener('click', () => {
        closeWinnerModal();
        resetGame();
    });
    
    window.addEventListener('click', (e) => {
        if (e.target === rulesModal) {
            closeModal();
        }
        if (e.target === winnerModal) {
            closeWinnerModal();
        }
    });
}

// Roll Dice
function rollDice() {
    if (gameState.gameOver || gameState.diceRolled) return;
    
    gameState.diceRolled = true;
    rollBtn.disabled = true;
    
    // Animate dice
    diceElement.classList.add('rolling');
    
    // Generate random number
    setTimeout(() => {
        gameState.diceValue = Math.floor(Math.random() * 6) + 1;
        diceElement.classList.remove('rolling');
        diceValueElement.textContent = `You rolled a ${gameState.diceValue}!`;
        
        movePlayer();
    }, 600);
}

// Move Player
function movePlayer() {
    const currentPlayer = gameState.players[gameState.currentPlayer];
    let newPosition = currentPlayer.position + gameState.diceValue;
    
    // Check if moved beyond 100
    if (newPosition > BOARD_SIZE) {
        gameMessageElement.textContent = `Player ${gameState.currentPlayer + 1} rolled too high! Stay at ${currentPlayer.position}`;
        gameState.diceRolled = false;
        setTimeout(switchPlayer, 2000);
        return;
    }
    
    // Update position
    const oldPosition = currentPlayer.position;
    currentPlayer.position = newPosition;
    
    // Check for snake or ladder
    let message = `Player ${gameState.currentPlayer + 1} moved from ${oldPosition} to ${newPosition}`;
    
    if (snakesAndLadders[newPosition]) {
        const destination = snakesAndLadders[newPosition];
        currentPlayer.position = destination;
        
        if (destination > newPosition) {
            message += ` - Ladder! Climbed to ${destination} 🪜`;
        } else {
            message += ` - Snake! Slid to ${destination} 🐍`;
        }
    }
    
    // Add to history
    addMoveToHistory(message);
    
    // Update board
    updateBoard();
    gameMessageElement.textContent = message;
    
    // Check for winner
    if (currentPlayer.position === BOARD_SIZE) {
        gameState.gameOver = true;
        showWinner(gameState.currentPlayer + 1);
        return;
    }
    
    // Switch player
    gameState.diceRolled = false;
    setTimeout(switchPlayer, 1500);
}

// Switch Player
function switchPlayer() {
    gameState.currentPlayer = (gameState.currentPlayer + 1) % gameState.players.length;
    diceValueElement.textContent = 'Roll the dice!';
    rollBtn.disabled = false;
    updateUI();
}

// Update Board Display
function updateBoard() {
    // Clear all player markers
    document.querySelectorAll('.square').forEach(sq => {
        sq.classList.remove('player1', 'player2');
    });
    
    // Place player markers
    gameState.players.forEach((player) => {
        const square = document.getElementById(`square-${player.position}`);
        if (square) {
            square.classList.add(`player${player.id}`);
            square.classList.remove('empty');
        }
    });
    
    // Update position displays
    gameState.players.forEach((player) => {
        document.getElementById(player.element).textContent = player.position;
    });
}

// Update UI
function updateUI() {
    currentPlayerElement.textContent = `Player ${gameState.currentPlayer + 1}`;
    updateBoard();
    
    // Highlight current player status
    document.getElementById('player1-status').classList.remove('active');
    document.getElementById('player2-status').classList.remove('active');
    
    if (gameState.currentPlayer === 0) {
        document.getElementById('player1-status').classList.add('active');
        gameMessageElement.textContent = `Player 1's turn - Click "Roll Dice"`;
    } else {
        document.getElementById('player2-status').classList.add('active');
        gameMessageElement.textContent = `Player 2's turn - Click "Roll Dice"`;
    }
}

// Add Move to History
function addMoveToHistory(message) {
    gameState.moveHistory.unshift(message);
    
    // Keep only last 10 moves
    if (gameState.moveHistory.length > 10) {
        gameState.moveHistory.pop();
    }
    
    // Update display
    movesListElement.innerHTML = '';
    gameState.moveHistory.forEach(move => {
        const li = document.createElement('li');
        li.textContent = move;
        movesListElement.appendChild(li);
    });
}

// Show Winner
function showWinner(playerNumber) {
    winnerText.textContent = `🎉 Player ${playerNumber} Wins! 🎉`;
    gameMessageElement.textContent = `🎉 Player ${playerNumber} reached 100 and won the game!`;
    rollBtn.disabled = true;
    winnerModal.style.display = 'block';
}

// Close Winner Modal
function closeWinnerModal() {
    winnerModal.style.display = 'none';
}

// Reset Game
function resetGame() {
    gameState = {
        players: [
            { id: 1, position: 1, element: 'p1-position' },
            { id: 2, position: 1, element: 'p2-position' }
        ],
        currentPlayer: 0,
        diceValue: 0,
        gameOver: false,
        moveHistory: [],
        diceRolled: false
    };
    
    diceValueElement.textContent = 'Roll the dice!';
    rollBtn.disabled = false;
    movesListElement.innerHTML = '';
    closeWinnerModal();
    updateUI();
    gameMessageElement.textContent = `Player 1's turn - Click "Roll Dice"`;
}

// Modal Functions
function openRulesModal() {
    rulesModal.style.display = 'block';
}

function closeModal() {
    rulesModal.style.display = 'none';
}

// Initialize game on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeGame();
});
