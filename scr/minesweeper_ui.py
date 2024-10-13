from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QHBoxLayout, QVBoxLayout, QListWidget, QWidget, QSizePolicy, QLineEdit, QLabel, QCheckBox, QGridLayout,
                               QSpacerItem, QStackedWidget, QMessageBox, QDialog, QComboBox)
from PySide6.QtGui import QIcon, QFontDatabase, QPixmap
from PySide6.QtCore import Qt, QSize, QTranslator, Signal
from pygame import mixer
import qdarktheme
import webbrowser

from game import Minesweeper,MinesweeperMapGenerator
from utils.tile import Tile
from utils.resources import ukraine,flag,hint,icon,skull,zsu,mine,techies,techies_mine,start_icon,retur,cool_font,start_screen,pes_patron,music1,explosion,win_music,settings,ua_translation
from utils.constants import SETS,TILE_SIZE,SECRETS,config
from utils.ui_utils import int_to_3,get_auto_mines,get_color,read_config,write_to_config
from utils.widgets import TileButton,SettingLine,RBLabel,RBTimer,UtilButton
from utils.map_converter import bob_map_to_map

class SettingsWindow(QDialog):
    music_signal = Signal(bool)
    sound_effect_signal = Signal(bool)
    theme_signal = Signal(str)
    
    def __init__(self):
        super().__init__()
        
        self.resize(200, 300)
        self.setWindowIcon(QIcon(settings))
        self.setWindowTitle(self.tr('Settings'))
        
        settings_layout = QVBoxLayout(self)
        settings_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        music_checkbox = QCheckBox(text=self.tr('Music'))
        
        settings_layout.addWidget(music_checkbox)

        sound_effect_checkbox = QCheckBox(text=self.tr('Sound effects'))
        sound_effect_checkbox.setToolTip(self.tr('Sound effects like explosions'))
        settings_layout.addWidget(sound_effect_checkbox)

        language_label = QLabel(text=self.tr('Select language (requires app restart): '))
        settings_layout.addWidget(language_label)

        self.language_codes = ['en', 'ua']

        languange_combo = QComboBox()
        languange_combo.addItems(['English', 'Українська'])
        settings_layout.addWidget(languange_combo)

        theme_label = QLabel(text=self.tr('Select theme:'))
        settings_layout.addWidget(theme_label)

        self.themes = ['dark', 'light']

        theme_combo = QComboBox()
        theme_combo.addItems([self.tr('Dark'), self.tr('Light')])
        settings_layout.addWidget(theme_combo)

        custom_map_label = QLabel(text=self.tr('Custom map bobmap:'))
        settings_layout.addWidget(custom_map_label)

        self.custom_map_box = QLineEdit()
        self.custom_map_box.setToolTip(self.tr('Enter the bobmap of your map (can get from map creator, may cause errors)'))
        settings_layout.addWidget(self.custom_map_box)

        data = read_config()
        music_checkbox.setChecked(data['music'])
        sound_effect_checkbox.setChecked(data['sound_effects'])
        languange_combo.setCurrentIndex(self.language_codes.index(data['language']))
        theme_combo.setCurrentIndex(self.themes.index(data['theme']))

        music_checkbox.toggled.connect(self.music_toggled)
        sound_effect_checkbox.toggled.connect(self.sound_effects_toggled)
        languange_combo.currentIndexChanged.connect(self.language_changed)
        theme_combo.currentIndexChanged.connect(self.theme_changed)

    def music_toggled(self, enabled:bool):
        data = read_config()
        data['music'] = enabled

        write_to_config(data)
        self.music_signal.emit(enabled)

    def sound_effects_toggled(self, enabled:bool):
        data = read_config()
        data['sound_effects'] = enabled

        write_to_config(data)
        self.sound_effect_signal.emit(enabled)

    def language_changed(self, index):
        language_code = self.language_codes[index]

        data = read_config()
        data['language'] = language_code

        write_to_config(data)
    
    def theme_changed(self, index):
        data = read_config()
        theme = self.themes[index]

        data['theme'] = theme

        write_to_config(data)
        self.theme_signal.emit(theme)

class MinesweeperUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.qcool = QIcon(ukraine)
        self.qhint = QIcon(hint)
        self.qicon = QIcon(icon)
        self.qskull = QIcon(skull)
        self.qzsu = QIcon(zsu)
        self.qtechies = QIcon(techies)
        self.qstart_icon = QIcon(start_icon)
        self.qretur = QIcon(retur)
        self.skull_cursor = QPixmap(skull).scaled(32,32, mode=Qt.TransformationMode.SmoothTransformation)
        self.patron_cursor = QPixmap(pes_patron).scaled(32,32, mode=Qt.TransformationMode.SmoothTransformation)

        data = read_config()
        print('e')
        self.update_theme_setting(data['theme'])
        
        self.translator = QTranslator()
        
        language_code = data['language']
        if language_code != 'en':
            self.change_language(language_code)
        
        self.update_music_setting(data['music'])

        self.update_sound_effects_setting(data['sound_effects'])

        QFontDatabase.addApplicationFont(cool_font)
        
        mixer.init()
        
        self.settings_window = SettingsWindow()
        self.settings_window.music_signal.connect(self.update_music_setting)
        self.settings_window.sound_effect_signal.connect(self.update_sound_effects_setting)
        self.settings_window.theme_signal.connect(self.update_theme_setting)
        
        self.screen_w, self.screen_h = self.screen().size().toTuple()
        self.no_guess_value = False
        self.width_value = 0
        self.height_value = 0
        self.mines_value = 0
        self.reset_button = None
        self.timer = None
        self.game = None
        self.menu_size = QSize(365,400)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.menu_container = QWidget()
        self.stacked_widget.addWidget(self.menu_container)
        self.game_container = QWidget()
        self.stacked_widget.addWidget(self.game_container)
        self.start_container = QWidget()
        self.stacked_widget.addWidget(self.start_container)

        self.setWindowTitle('Pes Patron Minesweeper')
        self.setWindowIcon(self.qicon)
        
        self.start_UI()
    
    def update_music_setting(self, enabled:bool):
        self.music_enabled = enabled

        if not enabled:
            self.set_enabled_game_music(False)
    
    def update_sound_effects_setting(self, enabled:bool):
        self.sound_effects_enabled = enabled

    def update_theme_setting(self, theme:str):
        self.theme = theme
        QApplication.instance().setStyleSheet(qdarktheme.load_stylesheet(self.theme))

    def change_language(self, lang_code):
        if lang_code == 'en':
            QApplication.instance().removeTranslator(self.translator)
        elif lang_code == 'ua':
            self.translator.load(ua_translation)
            QApplication.instance().installTranslator(self.translator)

    def start_UI(self):
        self.setFixedWidth(710)
        self.start_container.setObjectName("start_container")
        self.start_container.setStyleSheet(f"#start_container {{ background-image: url('{start_screen}'); background-repeat: no-repeat }}")
        
        start_ui_layout = QVBoxLayout()
        play_layout = QHBoxLayout()
        
        start_text = QLabel(text=self.tr('Welcome to Pes Patron Minesweeper'))
        start_text.setStyleSheet('font-size: 20pt; color: #1e1e1e;  background-color: transparent; text-align: center;')
        start_text.setMinimumHeight(300)

        self.play_button = QPushButton(text=self.tr('Play'))
        self.play_button.setStyleSheet('font-family: VT323; color: green; font-size: 20pt;')
        self.play_button.clicked.connect(self.menu_UI)

        play_layout.addWidget(self.play_button)

        start_ui_layout.addWidget(start_text)
        start_ui_layout.setAlignment(start_text, Qt.AlignmentFlag.AlignHCenter)
        start_ui_layout.addLayout(play_layout)

        self.start_container.setLayout(start_ui_layout)

        self.switch_tab(self.start_container)

    def menu_UI(self):
        self.show_custom_mines = False
        
        self.setMinimumSize(self.menu_size)
        self.resize(self.menu_size)

        start_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        

        self.start_list = QListWidget()
        self.start_list.addItems([self.tr('Beginner'), self.tr('Intermediate'), self.tr('Expert'), self.tr('Custom')])
        self.start_list.currentTextChanged.connect(self.difficulty_changed)
        
        
        self.custom_width = QLineEdit()
        self.custom_width.textEdited.connect(self.set_width)

        self.custom_height = QLineEdit()
        self.custom_height.textEdited.connect(self.set_height)

        self.custom_mines = SettingLine()
        self.custom_mines.textEdited.connect(self.set_mines)

        trizub_image = QLabel()
        trizub_image.setPixmap(QPixmap(icon).scaled(100,100,mode=Qt.TransformationMode.SmoothTransformation))
        trizub_image.setFixedSize(100,100)
        
        start_button = QPushButton()
        start_button.setIcon(self.qstart_icon)
        start_button.setFixedSize(80,80)
        start_button.setIconSize(QSize(30,30))
        start_button.clicked.connect(lambda:self.start_game())

        guess_checkbox = QCheckBox(text=self.tr('No guess mode'))
        guess_checkbox.setToolTip(self.tr('Generate easy map without any guesses needed'))
        guess_checkbox.toggled.connect(self.guess_checkbox_toggled)

        show_custom_mines_checkbox = QCheckBox(text=self.tr('Show mines on custom maps'))
        show_custom_mines_checkbox.toggled.connect(self.show_custom_mines_checkbox_toggled)

        self.auto_mines_checkbox = QCheckBox(text=self.tr('Auto mines'))
        self.auto_mines_checkbox.setToolTip(self.tr('Auto set number of mines in custom difficulty'))
        self.auto_mines_checkbox.setEnabled(False)
        self.auto_mines_checkbox.clicked.connect(self.set_auto_mines)

        settings_button = QPushButton()
        settings_button.setFixedSize(40,40)
        settings_button.setIcon(QIcon(settings))
        settings_button.setIconSize(QSize(30,30))
        settings_button.setToolTip(self.tr('Settings'))
        settings_button.clicked.connect(self.settings_button_clicked)

        manual_button = QPushButton()
        manual_button.setFixedSize(40,40)
        manual_button.setText('?')
        manual_button.setStyleSheet('QPushButton{ color: green; font-size: 30px }')
        manual_button.setToolTip(self.tr('Manual'))
        manual_button.clicked.connect(lambda: webbrowser.open('https://docs.google.com/document/d/1XqTGdAj9KioytsVM6SQ839Kqbbn8F-tAbhrwuCz8jGs'))

        settings_manual_layout = QHBoxLayout()
        settings_manual_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        settings_manual_layout.addWidget(settings_button)
        settings_manual_layout.addWidget(manual_button)

        left_layout.setSpacing(5)
        left_layout.addWidget(self.start_list,2)

        left_layout.addWidget(QLabel(self.tr('Width')),0.5)
        left_layout.addWidget(self.custom_width,1)

        left_layout.addWidget(QLabel(self.tr('Height')),0.5)
        left_layout.addWidget(self.custom_height,1)

        left_layout.addWidget(QLabel(self.tr('Mines')),0.5)
        left_layout.addWidget(self.custom_mines,1)

        left_layout.addWidget(self.auto_mines_checkbox,1)
        left_layout.addWidget(guess_checkbox,1)
        left_layout.addWidget(show_custom_mines_checkbox,1)
        
        left_layout.addLayout(settings_manual_layout)

        image_layout = QVBoxLayout()
        image_layout.addWidget(trizub_image)
        image_layout.setAlignment(trizub_image, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        image_layout.addWidget(start_button)
        image_layout.setAlignment(start_button,Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        
        start_layout.addLayout(left_layout)
        start_layout.addLayout(image_layout)
        start_layout.setAlignment(start_button,Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)

        self.menu_container.setLayout(start_layout)
        self.switch_tab(self.menu_container)

        self.enable_custom_settings(False)

    def settings_button_clicked(self):
        self.settings_window.exec()

    def get_auto_mines(self) -> int:
        return get_auto_mines(self.width_value,self.height_value)

    def set_auto_mines(self,state:bool):
        
        if state == True:
            self.custom_mines.setEnabled(False)
            self.set_mines(self.get_auto_mines())
        else:
            self.custom_mines.setEnabled(True)

    def guess_checkbox_toggled(self,state:bool):
        self.no_guess_value = state

    def show_custom_mines_checkbox_toggled(self,state:bool):
        self.show_custom_mines = state

    def switch_tab(self,tab:QWidget) :
        self.stacked_widget.setCurrentWidget(tab)

        if tab == self.menu_container:
            self.new_game_context = 'menu'
            self.setCursor(self.patron_cursor)
            self.set_enabled_game_music(False)
            self.setMinimumSize(self.menu_size)
            self.resize(self.menu_size)


    def enable_custom_settings(self,state:bool):
        self.custom_width.setEnabled(state)
        self.custom_height.setEnabled(state)
        self.custom_mines.setEnabled(state)
        self.auto_mines_checkbox.setEnabled(state)
        if state == False:
            self.auto_mines_checkbox.setChecked(False)

    def difficulty_changed(self,*args): 
        difficulties = ["Beginner", "Intermediate", "Expert", "Custom"]
        index = self.start_list.currentIndex()
        self.difficulty = difficulties[index.row()]
        
        if self.difficulty == 'Custom':
            self.enable_custom_settings(True)
            
        else:
            self.enable_custom_settings(False)
            M_set = SETS.get(self.difficulty)
            self.set_width(M_set[0])
            self.set_height(M_set[1])
            self.set_mines(M_set[2])

    def set_setting_text(self,setting:str,value:int, setting_text:QLineEdit):
        if isinstance(value,str):
            if value.isdigit():
                value = int(value)
            else:
                return
        
        setattr(self,setting,value)
        if setting_text.text() != str(value):
            setting_text.setText(str(value))

        
    def set_width(self,value:int) :
        self.set_setting_text('width_value',value,self.custom_width)

        if self.auto_mines_checkbox.isChecked() == True:
            self.set_mines(self.get_auto_mines())

    def set_height(self,value:int) :
        self.set_setting_text('height_value',value,self.custom_height)

        if self.auto_mines_checkbox.isChecked() == True:
            self.set_mines(self.get_auto_mines())
    def set_mines(self,value:int) :
        self.set_setting_text('mines_value',value,self.custom_mines)
        self.reset_button

    def set_auto_game_size(self,tile_size:int=TILE_SIZE) :
        self.setMaximumSize(160000,160000)
        t = tile_size + 2
        w,h = self.game.width * t + 10*2 ,  self.game.height*t + 40 + 30 + 10*2 + 15 # 10 - offset, 40 - h of top menu, 30 - h of bot menu, 15 - offset
        self.k = tile_size

        while w > self.screen_w*0.8 or h > self.screen_h*0.8:
            w = round(w*0.9)
            h = round(h*0.9)
            self.k*=0.9
            print(w,h)
        
        while w < 199:
            w = round(w*1.25)
            h = round(h*1.25)
            self.k*=1.25
            print(w,h)

        self.setMinimumSize(1,1)
        self.resize(w,h)

    def set_enabled_game_music(self, enabled:bool):
        mixer.music.stop()

        if enabled and self.music_enabled:
            mixer.music.load(music1)
            mixer.music.set_volume(0.08)
            mixer.music.play(-1)

    def center_window(self):
        self.move(round(self.screen_w/2 - self.width()/2), round(self.screen_h/2 - self.height()/2))

    def start_game(self,resize=True):
        self.board_ready = False
        self.custom_map = False

        if self.width_value == 0:
            self.width_value = 1
        if self.height_value == 0:
            self.height_value = 1

        self.setCursor(self.patron_cursor)

        if self.new_game_context in ['menu', 'win', 'lose']:
            self.set_enabled_game_music(True)
        
        self.new_game_context = 'game'
        
        if self.mines_value > self.width_value * self.height_value:
            self.mines_value = self.width_value * self.height_value

        self.game = Minesweeper()
        
        custom_map_box_text = self.settings_window.custom_map_box.text()
        secret = None

        if custom_map_box_text.startswith('b') and custom_map_box_text.endswith('b'):
            secret = custom_map_box_text
        elif not self.custom_height.text().isdigit():
            secret = self.custom_height.text()
        elif SECRETS.get(self.custom_width.text(),None):
            secret = SECRETS.get(self.custom_width.text(),None)

        if secret:
            self.game.set_map_data(bob_map_to_map(secret))
            self.board_ready = True
            self.custom_map = True
        else:
            self.game.generator = MinesweeperMapGenerator(self.width_value,self.height_value,self.mines_value,no_guess=self.no_guess_value)
            self.generate_map()
        self.game.print()
        
        if resize == True:
            self.set_auto_game_size()
        
        self.game.start_game()
        
        game_layout = QVBoxLayout()
        
        menu_layout = QHBoxLayout()
        menu_layout.setSpacing(20)
        
        self.mines_left_label = RBLabel(text=int_to_3(self.game.mines_left))

        self.reset_button = QPushButton(icon=self.qzsu)
        self.reset_button.setFixedSize(40,40)
        self.reset_button.setIconSize(QSize(25,25))
        self.reset_button.clicked.connect(lambda:( self.disable_ingame(),self.start_game(resize=False)))

        self.timer = RBTimer(text='000')

        menu_layout.addWidget(self.mines_left_label,8)
        menu_layout.addWidget(self.reset_button,5)
        menu_layout.addWidget(self.timer,8)

        self.mine_layout = QGridLayout()
        self.mine_layout.setSpacing(1)

        for tile in self.game.get_tiles():
            tile_button = TileButton(self.k, self.theme) 
            tile_button.resize(200,200)
            tile_button.clicked.connect(self.tile_button_click)
            tile_button.customContextMenuRequested.connect(self.tile_button_right_click)
            self.mine_layout.addWidget(tile_button,*tile.get_pos())     
        
        utility_layout = QHBoxLayout()

        self.hint_button = UtilButton(icon=self.qhint,icon_size=QSize(25,25))
        self.hint_button.setToolTip(self.tr("Use mine detector"))
        self.hint_button.clicked.connect(self.hint )

        return_button = UtilButton(icon=self.qretur, icon_size=QSize(15,15))
        return_button.setToolTip(self.tr('Return to menu'))
        return_button.clicked.connect(lambda:( self.disable_ingame(), self.switch_tab(self.menu_container) ) ) 
        
        utility_layout.addSpacerItem(QSpacerItem(100,30,QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed))
        utility_layout.addWidget(self.hint_button)
        utility_layout.addWidget(return_button)
        
        game_layout.addLayout(menu_layout,1)
        game_layout.addLayout(self.mine_layout,8)
        game_layout.addLayout(utility_layout,1)
        
        self.stacked_widget.removeWidget(self.game_container)

        self.game_container = QWidget()
        self.game_container.setLayout(game_layout)

        self.stacked_widget.addWidget(self.game_container)
        self.switch_tab(self.game_container)
        self.center_window()
    
    def remove_hints(self):
        if self.game.map_data:
            for tile in self.game.remove_hints():
                self.update_button(self.tile_to_button(tile))
        
    def generate_map(self):
        self.remove_hints()
        self.game.generate_tile_map()

    def generate_needed_map(self) -> bool:
        self.remove_hints() 
        return self.game.generate_needed_map()

    def tile_button_click(self):
        if not self.game.game_running:
            return
        
        tile_button:TileButton = self.sender()
        tile = self.button_to_tile(tile_button)
        
        if not self.board_ready:
            self.game.generator.start_pos = tile.get_pos()

            if self.game.height * self.game.width <= self.game.max_mines:
                self.techies()
                return
            
            if self.generate_needed_map() == False:
                return
            self.board_ready = True
            tile = self.button_to_tile(tile_button)
            
        
        if self.timer.running == False:
            self.timer.start_timer()
        
        result,tiles_to_reveal = self.game.recursive_reveal(tile)
        
        for n_tile in tiles_to_reveal:
            button = self.tile_to_button(n_tile)
            self.update_button(button)
        
        if result == 'win':
            self.win()
        elif result == 'lose':
            self.lose()
    

    def update_button(self,button:TileButton):
        tile = self.button_to_tile(button)
        
        button.set_default_style()
        current_style = button.styleSheet()

        if button.theme == 'dark':
            revealed_color = '#2c2c2f'
        else:
            revealed_color = '#999999'

        if tile.revealed:
            button.setEnabled(False)
            
            if tile.value == -1:
                button.setStyleSheet(current_style.replace(button.base_color,'#c72828'))
            else:
                if tile.value == 0:
                    
                    button.setStyleSheet(current_style.replace(button.base_color, revealed_color))

                else:
                    button.label.setText(str(tile.value))
                    button.setStyleSheet(current_style.replace(button.base_color, revealed_color) + f'color: {get_color(tile.value)}; ')
        elif tile.flagged:
            button.label.setPixmap(QPixmap(flag).scaled(0.7*self.k,0.7*self.k, mode=Qt.TransformationMode.SmoothTransformation))
        elif tile.hinted:
            button.setStyleSheet(current_style.replace(button.base_color,'#3bb440'))
            if tile.value == -1:
                button.label.setPixmap(QPixmap(flag).scaled(0.7*self.k,0.7*self.k, mode=Qt.TransformationMode.SmoothTransformation))


    def tile_button_right_click(self):
        if not self.board_ready or not self.game.game_running:
            return
        
        tile_button:TileButton = self.sender()
        
        tile = self.button_to_tile(tile_button)
        if tile.flagged:
            self.unflag(tile)
        else:
            self.flag(tile)
        self.update_button(tile_button)
    
    def flag(self,tile:Tile):
        tile_button = self.tile_to_button(tile)
        self.game.flag_tile(tile)
        
        
        self.mines_left_label.setText(int_to_3(self.game.mines_left))
        self.update_button(tile_button)

    def unflag(self,tile:Tile):
        tile_button = self.tile_to_button(tile)
        self.game.unflag_tile(tile)
        
        self.mines_left_label.setText(int_to_3(self.game.mines_left))
        self.update_button(tile_button)

    def hint(self):
        if not self.game.game_running:
            return

        hint_tile:Tile = self.game.hint()
        if not hint_tile:
            return
        hint_button = self.tile_to_button(hint_tile)
        self.update_button(hint_button)

    def unhint(self,tile:Tile):
        hint_button = self.tile_to_button(tile)
        self.update_button(hint_button)

    def button_to_tile(self,button:TileButton) -> Tile:
        row,column,_,_ = self.mine_layout.getItemPosition(self.mine_layout.indexOf(button))
        return self.game.get_tile(row,column)
    
    def tile_to_button(self,tile:Tile) -> TileButton:
        return self.mine_layout.itemAtPosition(*tile.get_pos()).widget()


    def disable_ingame(self):
        self.game.stop_game()
        self.hint_button.setEnabled(False)
        self.timer.stop_timer()

        for n_tile in self.game.get_tiles():
            if n_tile.hinted == True:
                self.unhint(n_tile)

    def unflag_all(self):
        for n_tile in self.game.get_tiles():
            if n_tile.flagged == True:
                self.unflag(n_tile)

    def set_mines_icons(self,icon:QPixmap,size:QSize=QSize(15,15)):
        for n_tile in self.game.get_tiles_with_value(-1):
            n_tile_button = self.tile_to_button(n_tile)
            self.unflag_all()

            if n_tile.value == -1:
                n_tile_button.label.setPixmap(icon.scaled(size, mode=Qt.TransformationMode.SmoothTransformation))

    def lose(self):
        self.new_game_context = 'lose'
        self.reset_button.setIcon(self.qskull)
        self.set_enabled_game_music(False)
        
        if self.sound_effects_enabled:
            mixer.Sound(explosion).play()
        
        if self.custom_map == False or self.show_custom_mines == True:
            self.set_mines_icons(QPixmap(mine),QSize(0.7*self.k,0.7*self.k))
        
        self.setCursor(self.skull_cursor)
        
        self.disable_ingame()
            
    def win(self):
        self.reset_button.setIcon(self.qcool)

        self.new_game_context = 'win'

        mixer.music.stop()
        mixer.music.load(win_music)
        mixer.music.set_volume(0.17)
        mixer.music.play(-1)
        
        for n_tile in self.game.get_tiles_with_value(-1):
            if n_tile.flagged == False:
                self.flag(n_tile)
        
        self.disable_ingame()

        win_msg = QMessageBox()
        win_msg.setWindowTitle(self.tr('Win'))
        win_msg.setWindowIcon(self.qicon)
        win_msg.setText(self.tr("You demined all the russian mines!"))
        win_msg.exec()

    def techies(self):
        self.new_game_context = 'lose'
        self.reset_button.setIcon(self.qtechies)
        self.reset_button.setIconSize(QSize(50,50))

        self.set_mines_icons(QPixmap(techies_mine),QSize(0.7*self.k,0.7*self.k))

        self.disable_ingame()