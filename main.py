"""
THIS CODE WAS GENERATED WITH GEMINI

"""

import sys
import os
import chess

# --- 1. SETUP PATHS ---
# Ensure we can import from src/
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# --- 2. LOGGING FUNCTION ---
LOG_FILE = os.path.join(current_dir, "communications.log")

def log(message, direction="INFO"):
    """Writes a message to communications.log with a prefix."""
    prefix = ">> GUI" if direction == "IN" else "<< ENG" if direction == "OUT" else "-- LOG"
    with open(LOG_FILE, "a") as f:
        f.write(f"{prefix}: {message}\n")

# Project imports (Must happen after sys.path.append)
try:
    from src.evaluation.pipeline import EvaluationPipeline
    from src.evaluation.material import MaterialEvaluator
    from src.move_ordering.pipeline import MoveSortingPipeline
    from src.move_ordering.mvv_lva import MvvLva
    from src.search.alpha_beta import AlphaBeta
    log("Imports successful", "INFO")
except Exception as e:
    log(f"Import Error: {e}", "INFO")
    sys.exit(1)

def main():
    log("Engine Process Started", "INFO")

    # Initialize Engine
    try:
        eval_pipeline = EvaluationPipeline(MaterialEvaluator())
        move_sorting_pipeline = MoveSortingPipeline(MvvLva())
        search_engine = AlphaBeta(eval_pipeline, move_sorting_pipeline)
        board = chess.Board()
        log("Engine initialized successfully", "INFO")
    except Exception as e:
        log(f"Initialization Error: {e}", "INFO")
        return

    # --- 3. THE COMMAND LOOP ---
    while True:
        try:
            # We use sys.stdin.readline() instead of input() to handle EOF better
            command = sys.stdin.readline()
            
            # If command is empty, the GUI has closed the pipe (Quit)
            if not command:
                log("GUI closed connection (EOF)", "INFO")
                break
                
            command = command.strip()
            
            # LOG INPUT
            log(command, "IN")

        except Exception as e:
            log(f"Input Error: {e}", "INFO")
            break

        # --- PROCESS COMMANDS ---
        if command == "uci":
            response = [
                "id name BiasFish",
                "id author RealPhonki",
                "uciok"
            ]
            for r in response:
                print(r)
                log(r, "OUT")
            # Force flush to ensure GUI sees it immediately
            sys.stdout.flush()
        
        elif command == "isready":
            print("readyok")
            log("readyok", "OUT")
            sys.stdout.flush()
        
        elif command == "quit":
            log("Quitting...", "INFO")
            break
            
        elif command.startswith("position"):
            try:
                parts = command.split()
                if "startpos" in parts:
                    board.reset()
                    moves_idx = parts.index("moves") + 1 if "moves" in parts else len(parts)
                elif "fen" in parts:
                    fen_part = []
                    moves_idx = len(parts)
                    for i in range(2, len(parts)):
                        if parts[i] == "moves":
                            moves_idx = i + 1
                            break
                        fen_part.append(parts[i])
                    board.set_fen(" ".join(fen_part))
                else:
                    moves_idx = len(parts)

                if moves_idx < len(parts):
                    for move_uci in parts[moves_idx:]:
                        board.push(chess.Move.from_uci(move_uci))
                
                log(f"Position set. Turn: {board.turn}", "INFO")
            except Exception as e:
                log(f"Position Error: {e}", "INFO")

        elif command.startswith("go"):
            try:
                # Run search
                best_move = search_engine.get_best_move(board, depth=5)
                
                # Send result
                res = f"bestmove {best_move.uci() if best_move else '0000'}"
                print(res)
                log(res, "OUT")
                sys.stdout.flush()
            except Exception as e:
                log(f"Search Error: {e}", "INFO")

if __name__ == "__main__":
    main()