from game import MinesweeperMapGenerator

generator = MinesweeperMapGenerator(30, 16, 99, (15,8), no_guess=True)
generator.generate_needed_map()
generator.minesweeper.print()