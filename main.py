import pyautogui as pgui
from time import sleep
from bot import Bot

pgui.FAILSAFE = True


wait = 1
mouse_pos = 0
sleep(wait)

if mouse_pos == 1:
    print(pgui.position())
else:
    bot = Bot()
    bot.start_picking()
