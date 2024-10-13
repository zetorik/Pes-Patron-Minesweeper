import sys
from pathlib import Path
import json

from .tile import Tile

file_dir = Path(__file__).parent.parent

if getattr(sys, 'frozen', False):
    exe_dir = Path(sys.executable).parent
else:
    exe_dir = file_dir

config = (exe_dir / 'config.json').as_posix()
with open(config,'r') as file:
    dictionaries = json.load(file)

SETS:dict = dictionaries["difficulties"]
COLORS:dict = dictionaries["tile_colors"]
SECRETS:dict = dictionaries["custom_maps"]
TILE_MAP = list[list[Tile]]
TILE_SIZE = 40