from PySide6.QtWidgets import QApplication
import sys

from minesweeper_ui import MinesweeperUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = MinesweeperUI()
    window.show()
    
    app.exec()