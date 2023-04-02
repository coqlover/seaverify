# tic_tac_toe
# Built with Seahorse v0.2.4

import sys
sys.path.append(".")
from seaverify.prelude import *

declare_id('G5s63XbRZMDnypYYBcnZZxg73FftZ2byYe1KbpcNXUwf')

@instruction
def first_win(moves:List[u64]) -> u64:
    if((moves[0]==1 and moves[1]==1 and moves[2]==1) or (moves[0]==1 and moves[3]==1 and moves[6]==1) or 
    (moves[6]==1  and moves[7]==1 and moves[8]==1) or (moves[2]==1 and moves[5]==1 and moves[8]==1) or
    (moves[0]==1 and moves[4]==1 and moves[8]==1 ) or (moves[2]==1 and moves[4]==1 and moves[6]==1) or
    (moves[1]==1 and moves[4]==1 and moves[7]==1) or (moves[3]==1 and moves[4]==1 and moves[5]==1)):
        return 1
    else:
        return 0

@instruction
def second_win(moves:List[u64]) -> u64:
    if((moves[0]==2 and moves[1]==2 and moves[2]==2) or (moves[0]==2 and moves[3]==2 and moves[6]==2) or 
    (moves[6]==2  and moves[7]==2 and moves[8]==2) or (moves[2]==2 and moves[5]==2 and moves[8]==2) or
    (moves[0]==2 and moves[4]==2 and moves[8]==2 ) or (moves[2]==2 and moves[4]==2 and moves[6]==2) or
    (moves[1]==2 and moves[4]==2 and moves[7]==2) or (moves[3]==2 and moves[4]==2 and moves[5]==2)):
        return 1
    else:
        return 0
    
@instruction
@enforce(lambda before, after: seaverify_implies(((not (first_win(moves=before.moves)==1)) and (not (second_win(moves=before.moves)==1))), not ((first_win(moves=after.moves)==1) and (second_win(moves=after.moves)==1))))
def play_single_turn(moves:List[u64], player:u64, position:u64, player2: u64, position2: u64) -> List[u64]:
    assert player == 1 or player == 2
    assert position >= 0 and position < 9
    assert moves[position] == 0
    moves[position] = player
    if False: # Set it to true and see the enforce property fail
        assert player2 == 1 or player2 == 2
        assert position2 >= 0 and position2 < 9
        assert moves[position2] == 0
        moves[position2] = player2
    return moves

if __name__ == '__main__':
    verify_contract()