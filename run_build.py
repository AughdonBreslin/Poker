import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
os.chdir('/mnt/c/Users/aughb/PersonalProjects/Poker')
sys.path.insert(0, '/mnt/c/Users/aughb/PersonalProjects/Poker/src')

from src.preflop_equity import build_lookup_table
build_lookup_table(num_players=2, checkpoint_path='preflop_equity_2p.pkl')
