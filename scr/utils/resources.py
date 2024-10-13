from .constants import file_dir,exe_dir

res = exe_dir/'res'
fonts = file_dir/'fonts'
sounds = file_dir/'sounds'
translations = file_dir/'translations'

ukraine = (res/'ukraine.png').as_posix()
flag = (res/'flag.png').as_posix()
hint = (res/'hint.png').as_posix()
icon= (res/'icon.png').as_posix()
mine= (res/'mine.png').as_posix()
retur = (res/'return.png').as_posix()
skull= (res/'skull.png').as_posix()
zsu= (res/'zsu.png').as_posix()
start_icon= (res/'start_icon.png').as_posix()
techies = (res/'techies.png').as_posix()
techies_mine = (res/'techies_mine.png').as_posix()
cursed_icon = (res/'cursed.png').as_posix()
start_screen = (res/'start_screen.png').as_posix()
trizub = (res/"trizub.png").as_posix()
pes_patron = (res/"pes_patron.png").as_posix()
settings = (res/"settings.png").as_posix()
tools = (res/'tools.png').as_posix()

cool_font = (fonts/'VT323-Regular.ttf').as_posix()

music1 = (sounds/"music1.mp3").as_posix()
explosion = (sounds/"explosion.mp3").as_posix()
win_music = (sounds/"win_music.mp3").as_posix()

ua_translation = (translations/'ua.qm').as_posix()