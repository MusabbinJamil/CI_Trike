# Plan: Convert Trike Game to React Native Android App

## Context
The Trike board game is currently a Python/Tkinter desktop app with multiple trained AI opponents. The goal is to port it to a React Native Android app, preserving all game logic, AI opponents (except DQNAI which requires PyTorch), themes, scoring, and pie rule. All game logic and AI algorithms are pure logic with no Python-specific dependencies, making them directly translatable to JavaScript.

---

## Project Structure

```
TrikeApp/
├── App.tsx                          # Root component with navigation
├── app.json
├── package.json
├── assets/
│   └── strategic_ai_weights.json    # Bundled evolved weights from best_strategic_ai.json
├── src/
│   ├── game/                        # Core game logic (ported from src/)
│   │   ├── Board.ts                 # Board class (from board.py)
│   │   ├── Game.ts                  # Game class (from game.py)
│   │   ├── types.ts                 # Checker, Player, Pawn types
│   │   └── utils.ts                 # Score calculation (from utils.py)
│   ├── ai/                          # AI agents (ported from trike_ai/agents/)
│   │   ├── AIBase.ts                # Base interface
│   │   ├── RandomAI.ts              # Random move selection
│   │   ├── MinimaxAI.ts             # Minimax + alpha-beta pruning
│   │   ├── MCTSAI.ts                # Monte Carlo Tree Search
│   │   ├── HybridAI.ts              # Weighted ensemble
│   │   ├── EvolvedStrategicAI.ts    # Phase-aware strategic AI
│   │   ├── StrategicEvaluator.ts    # Complex position evaluator
│   │   └── index.ts                 # AI factory/registry
│   ├── screens/                     # App screens
│   │   ├── SetupScreen.tsx          # Game setup (board size, players, theme)
│   │   ├── GameScreen.tsx           # Main game board + controls
│   │   └── ScoreboardScreen.tsx     # Win history
│   ├── components/                  # Reusable components
│   │   ├── HexBoard.tsx             # SVG hexagonal board renderer
│   │   ├── HexCell.tsx              # Single hexagon cell
│   │   ├── PawnMarker.tsx           # Pawn visual (red circle + star markers)
│   │   ├── CheckerMarker.tsx        # Checker piece visual
│   │   ├── GameOverModal.tsx        # Game result popup
│   │   ├── PieRuleModal.tsx         # Pie rule offer dialog
│   │   └── InstructionsModal.tsx    # Game instructions
│   ├── hooks/
│   │   ├── useGame.ts               # Game state management hook
│   │   └── useScores.ts             # AsyncStorage score persistence
│   └── theme/
│       └── themes.ts                # 4 color themes (Classic, Green & Purple, etc.)
```

---

## Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Hex rendering | `react-native-svg` | Best for drawing hexagons with touch targets on mobile |
| State management | React `useReducer` in custom hook | Game state is localized, no need for Redux |
| Navigation | `@react-navigation/native` with stack navigator | 3 screens: Setup, Game, Scoreboard |
| Score persistence | `@react-native-async-storage/async-storage` | Simple key-value JSON storage like current file-based approach |
| AI execution | `setTimeout(..., 0)` with async/await | Keeps UI responsive during AI computation |
| Deep copy for AI | Structured clone or manual copy | Needed by Minimax/MCTS for state simulation |
| MCTS iterations | Reduce to 500 on mobile | 1000 may be slow on phones |
| DQN AI | **Excluded** | Requires PyTorch; not portable to JS without ONNX.js (out of scope) |

---

## Game Rules (Reference)

1. Player 1 places first checker + pawn on any empty hex
2. Player 2 can invoke "pie rule" (swap colors)
3. Each turn: pawn moves in straight line (6 hex directions) to empty hex, places checker of current player's color there
4. Game ends when pawn is trapped (all 6 neighbors occupied)
5. Winner = player with most checkers around pawn (adjacent + under). Max 7 points.

---

## Implementation Plan (Ordered)

### Phase 1: Project Setup
1. Initialize React Native project with TypeScript template
2. Install dependencies: `react-native-svg`, `@react-navigation/native`, `@react-native-async-storage/async-storage`
3. Set up navigation stack (Setup -> Game -> Scoreboard)

### Phase 2: Core Game Logic (port from Python)
Files to create and their Python sources:

**`src/game/types.ts`** - Type definitions
- Port `Checker` (color: 'black' | 'white'), `Player` (color), `Pawn` (position: [q,r] | null)
- Define `GameState`, `HexPosition` types

**`src/game/Board.ts`** - Port from `src/board.py`
- `HEX_DIRECTIONS` constant: `[[1,0],[1,-1],[0,-1],[-1,0],[-1,1],[0,1]]`
- `createGrid(size)`: triangular grid `for q in 0..size, r in 0..size-q`
- Grid stored as `Map<string, Checker|null>` (key = `"q,r"`)
- `isValidMove(from, to)`: straight line check + no obstacles
- `isPawnTrapped(pos)`: all 6 neighbors occupied
- `getNeighbors(q,r)`: filter valid positions from 6 directions
- `placeChecker(q, r, player)`, `clone()` for deep copy

**`src/game/Game.ts`** - Port from `src/game.py`
- Properties: board, players[2], currentPlayerIndex, pawn, pieRuleAvailable, gameOver
- Methods: `reset()`, `makeMove(q, r)`, `calculateScores()`
- `clone()` for AI simulation (deep copy board + state)

**`src/game/utils.ts`** - Port from `src/utils.py`
- `calculateScore(board, color, pawnPos)`: count adjacent + under checkers

### Phase 3: AI Agents (port from Python)

**`src/ai/AIBase.ts`** - Interface
```typescript
interface AIAgent {
  name: string;
  chooseMove(game: Game): HexPosition;
  reset(): void;
}
```

**`src/ai/RandomAI.ts`** - Port from `random_ai.py`
- Pick random from valid moves list

**`src/ai/MinimaxAI.ts`** - Port from `minimax_ai.py`
- Alpha-beta pruning with configurable depth (2 for Easy, 3 for Hard)
- `_simulateMove()` uses `game.clone()`
- `_evaluatePosition()`: piece control + mobility heuristic
- First move: prefer center position

**`src/ai/MCTSAI.ts`** - Port from `mcts_ai.py`
- `MCTSNode` class with UCT selection (exploration weight 1.41)
- 500 iterations (reduced from 1000 for mobile performance)
- Selection -> Expansion -> Rollout -> Backpropagation
- First move: prefer center

**`src/ai/HybridAI.ts`** - Port from `hybrid_ai.py`
- Weighted random: Minimax 20%, MCTS 31%, Random 49%
- Delegates to selected sub-AI

**`src/ai/StrategicEvaluator.ts`** - Port from `strategic_evaluator.py`
- All methods: `determineGamePhase()`, `isCorner()`, `isSide()`, `calculateInfluence()`, `identifyPockets()`, `evaluateCorridorControl()`, trap detection methods
- Flood fill for connected regions
- `_simulateMove()` for lookahead analysis

**`src/ai/EvolvedStrategicAI.ts`** - Port from `evolved_strategic_ai.py`
- Load weights from bundled `strategic_ai_weights.json`
- 4-phase evaluation: early/middle/mid-late/late
- Trap strategy evaluation
- Uses `StrategicEvaluator` for all complex calculations

**`src/ai/index.ts`** - AI factory
- `createAI(type: string): AIAgent` matching current GUI dropdown options
- Types: 'RandomAI', 'MinimaxAI-Easy', 'MinimaxAI-Hard', 'MCTSAI', 'HybridAI', 'EvolvedStrategicAI'

### Phase 4: Theme System
**`src/theme/themes.ts`** - Port 4 themes from `guiv2.py`
- Classic, Green & Purple, Black & White, Red & Blue
- Each theme: bg, board, validMove, pawn, pawnOutline, player1, player2, panelBg

Theme colors:
```
Classic:        bg=#ffffff, board=#808080, validMove=#800080, pawn=#ff0000, player1=#000000, player2=#ffffff, panelBg=#ffffe0
Green & Purple: bg=#e8f5e9, board=#81c784, validMove=#7b1fa2, pawn=#f57f17, player1=#388e3c, player2=#9c27b0, panelBg=#c8e6c9
Black & White:  bg=#f5f5f5, board=#9e9e9e, validMove=#616161, pawn=#ff5722, player1=#212121, player2=#f5f5f5, panelBg=#e0e0e0
Red & Blue:     bg=#e3f2fd, board=#90caf9, validMove=#880e4f, pawn=#ffd600, player1=#d32f2f, player2=#1565c0, panelBg=#bbdefb
```

### Phase 5: UI Components

**`src/components/HexBoard.tsx`** - Main board (replaces Canvas drawing)
- SVG container with `<Svg>` from react-native-svg
- `hexToPixel(q, r)`: `x = HEX_SIZE * 1.5 * q + 50`, `y = HEX_SIZE * sqrt(3) * (r + q/2) + 50`
- Render each hex cell, pass touch handler
- Pinch-to-zoom + pan for larger boards using `react-native-gesture-handler`

**`src/components/HexCell.tsx`** - Single hex
- SVG `<Polygon>` with 6 vertices computed as: `for i in 0..5: x + HEX_SIZE * cos(pi/3 * i), y + HEX_SIZE * sin(pi/3 * i)`
- Fill color based on: empty (board color), valid move (highlighted), has checker (player color)
- Touch target via `onPress`
- Crosshatch pattern for valid moves (two diagonal lines)

**`src/components/PawnMarker.tsx`** - Pawn visual
- Red circle (r=14) with black outline (width=3)
- Inner dot showing checker color (r=6)
- Star markers at 4 corners (45/135/225/315 degrees, distance 18)

**`src/components/CheckerMarker.tsx`** - Checker piece
- Colored circle (r=10) with contrasting outline (width=2)

**`src/components/GameOverModal.tsx`** - Results popup
- Shows both player scores, winner announcement
- "Play Again" and "Close" buttons

**`src/components/PieRuleModal.tsx`** - Pie rule dialog
- "Do you want to swap colors?" Yes/No
- AI auto-decides (50% chance, same as Python)

**`src/components/InstructionsModal.tsx`** - Game rules text

### Phase 6: Screens

**`src/screens/SetupScreen.tsx`** - Port setup panel
- Welcome header: "WELCOME TO TRIKE" with hex decorations (⬡ ⬢ ⬣)
- Subtitle: "The hexagonal strategy game!"
- Board size picker (7-19)
- 2x2 grid: Player 1/2 name inputs + AI type pickers
- AI types: Human, RandomAI, MinimaxAI-Easy, MinimaxAI-Hard, MCTSAI, HybridAI, EvolvedStrategicAI
- Theme selector dropdown
- "Start Game" button -> navigates to GameScreen
- "Instructions" button -> shows modal

**`src/screens/GameScreen.tsx`** - Main game screen
- Status bar: "Current Turn: {playerName} ({color})"
- HexBoard component (scrollable/zoomable)
- Bottom bar: New Game, Reset, Options (Instructions/Scoreboard/Theme submenu)
- Game flow: human tap -> `handleMove()`, AI turns via `setTimeout`
- AI thinking indicator: "{playerName} (AI) is thinking..."
- 0.5s delay before AI move for visual feedback

**`src/screens/ScoreboardScreen.tsx`** - Win history
- Header: "Trike Scoreboard"
- Table: Player | Wins, sorted by wins descending
- "No games played yet!" if empty
- Close button

### Phase 7: Game State Hook

**`src/hooks/useGame.ts`**
- `useReducer` with actions: MAKE_MOVE, RESET, NEW_GAME, USE_PIE_RULE
- Manages: game instance, gameOver, validMoves, aiPlayers, playerNames, currentTheme
- AI turn logic: after human move, if next player is AI, schedule AI move via setTimeout
- `makeAIMove()`: runs AI.chooseMove() then dispatches MAKE_MOVE

**`src/hooks/useScores.ts`**
- `loadScores()`, `saveScore(winnerName)` via AsyncStorage
- Same JSON format as current `trike_scores.json`

---

## Python Source Files to Reference During Porting

| React Native File | Python Source | Key Logic |
|-------------------|-------------|-----------|
| `src/game/Board.ts` | `src/board.py` | Hex grid, valid moves, pawn trapped |
| `src/game/Game.ts` | `src/game.py` | Game state, turns, pie rule, scoring |
| `src/game/types.ts` | `src/checker.py`, `src/player.py`, `src/pawn.py` | Data types |
| `src/game/utils.ts` | `src/utils.py` | Score calculation |
| `src/ai/RandomAI.ts` | `trike_ai/agents/random_ai.py` | Random valid move |
| `src/ai/MinimaxAI.ts` | `trike_ai/agents/minimax_ai.py` | Alpha-beta minimax |
| `src/ai/MCTSAI.ts` | `trike_ai/agents/mcts_ai.py` | Monte Carlo Tree Search |
| `src/ai/HybridAI.ts` | `trike_ai/agents/hybrid_ai.py` | Weighted ensemble |
| `src/ai/EvolvedStrategicAI.ts` | `trike_ai/agents/evolved_strategic_ai.py` | 21-weight phase AI |
| `src/ai/StrategicEvaluator.ts` | `trike_ai/training/strategic_evaluator.py` | Position analysis |
| `src/theme/themes.ts` | `src/guiv2.py` lines 29-69 | 4 color themes |
| `src/components/HexBoard.tsx` | `src/guiv2.py` draw_board/draw_hex | Hex rendering |
| `src/screens/SetupScreen.tsx` | `src/guiv2.py` show_setup_panel | Setup UI |
| `src/screens/GameScreen.tsx` | `src/guiv2.py` game panel + AI flow | Game UI |
| `assets/strategic_ai_weights.json` | `evolved_strategic_players/best_strategic_ai.json` | Trained weights |

## Files from Python to Bundle As-Is
- `evolved_strategic_players/best_strategic_ai.json` -> `assets/strategic_ai_weights.json` (the 21 evolved strategy weights)

## Excluded from Port
- **DQNAI** and all `.pt` model files (requires PyTorch, not feasible in JS)
- **Training scripts** (`trike_ai/training/`) - not needed in the app
- **CLI argument parsing** from `guiv2.py __main__`
- **auto_play / close_when_done** - desktop automation features

---

## Evolved Strategic AI Weights (to bundle)

```json
{
  "center_control": 27,
  "corner_avoidance": 84,
  "side_preference": 56,
  "corner_capture": 50,
  "influence_maximization": 45,
  "opponent_influence_reduction": 19,
  "trap_avoidance": 87,
  "region_separation_awareness": 78,
  "pocket_identification": 0,
  "enemy_pocket_filling": 60,
  "own_pocket_avoidance": 62,
  "stone_burial_strategy": 4,
  "corridor_control": 98,
  "closing_avoidance": 39,
  "endpoint_manipulation": 85,
  "set_trap": 0,
  "extend_trap": 84,
  "multiple_traps": 88,
  "sacrifice_trap": 27,
  "defuse_inside": 37,
  "defuse_downstream": 16,
  "lock_away_traps": 9
}
```

## HybridAI Default Weights
- MinimaxAI: 20%
- MCTSAI: 31%
- RandomAI: 49%

---

## Verification / Testing Plan
1. **Game logic unit tests**: Create a board, verify `isValidMove()`, `isPawnTrapped()`, score calculation match Python behavior
2. **AI smoke tests**: Run each AI against RandomAI for 10 games, verify they produce valid moves and games complete
3. **Manual testing on Android emulator**:
   - Start game with each board size (7, 10, 19)
   - Play Human vs Human - verify touch, move highlighting, pie rule, scoring
   - Play Human vs each AI type - verify AI makes valid moves, UI stays responsive
   - Test all 4 themes
   - Verify scoreboard persists across app restarts
   - Test Game Over modal, Play Again flow
4. **Performance**: MCTS should complete move within 2-3 seconds on mid-range Android device
5. **Build APK**: `npx react-native run-android` and test on physical device
