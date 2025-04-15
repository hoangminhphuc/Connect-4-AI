from fastapi import FastAPI, HTTPException
import random
import uvicorn
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from connect4 import Connect4
from mcts import ucb2_agent

app = FastAPI()
agent = ucb2_agent(7)
game = Connect4()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GameState(BaseModel):
    board: List[List[int]]
    current_player: int
    valid_moves: List[int]

class AIResponse(BaseModel):
    move: int

def create_position_from_game_state(game_state: GameState):
    # Khởi tạo một position trắng
    pos = game.get_initial_position()
    pos.board = game_state.board
    pos.turn = game_state.current_player
    pos.valid_moves = game_state.valid_moves
    return pos


@app.post("/api/connect4-move")
async def make_move(game_state: GameState) -> AIResponse:
    try:
        if not game_state.valid_moves:
            raise ValueError("Không có nước đi hợp lệ")
            
        pos = create_position_from_game_state(game_state)
        selected_move = agent(pos) 
                
        return AIResponse(move=selected_move)
    except Exception as e:
        if game_state.valid_moves:
            return AIResponse(move=game_state.valid_moves[0])
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)