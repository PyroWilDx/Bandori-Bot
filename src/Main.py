import cv2
import time
import numpy as np
import pyautogui
from keyboard import press_and_release, press, release
from colorama import init, Fore

import Setup
import Screen

init()

song_choice_var = 2
song_try_counter = 0
is_playing_easy = True
first_time = True
how_much_try = 5


def ask_options():
    global song_choice_var
    global is_playing_easy
    global how_much_try

    try:
        print("Enter 1 to always play the same song.")
        print("Enter 2 to play the next song each time.")
        print("Enter 3 to try to full-combo every song :\n"
              "   -If the bot doesn't get a full-combo then it plays the song again.\n"
              "      -If it doesn't full-combo after X times then it goes to the next song.\n"
              "   -If it gets the full combo then it plays the next song that isn't already full-comboed.")
        print("Enter 4 to try to full-perfect every song (same as full-combo but with for full-perfects).")
        song_choice_var = input()
        if song_choice_var != "v":
            song_choice_var = int(song_choice_var)
        if not (
                song_choice_var == 1 or song_choice_var == 2 or song_choice_var == 3 or song_choice_var == 4 or song_choice_var == "v"):
            raise ValueError
        if song_choice_var == 3 or song_choice_var == 4:
            print("Enter 0 if you are playing normal level songs.")
            print("Enter 1 if you are playing easy level songs.")
            try:
                is_playing_easy = int(input())
                if is_playing_easy != 0 and is_playing_easy != 1:
                    raise ValueError
                else:
                    is_playing_easy = bool(is_playing_easy)
                print("How much time do you want the bot to try again if it fails to full-combo/perfect the song ?")
                how_much_try = int(input())
                if how_much_try < 1:
                    print("The value will be set to the default value (3).\n")
                    how_much_try = 3
                elif how_much_try > 20:
                    print("The value will be set to (20).\n")
                    how_much_try = 20
            except ValueError:
                print("This value is not valid, please retry...\n")
                time.sleep(0.2)
                ask_options()
    except ValueError:
        print("This value is not valid, the bot will play the next song each time (2).\n")
        song_choice_var = 2

    Setup.bluestacks()
    home_to_game()


def play():
    global played
    print("Game Start")

    KEY_LIST_FLICK = ['r', 't', 'y']
    KEY_LIST_MAIN = ['f', 'g', 'h']
    KEY_LIST_SECOND = ['v', 'b', 'n']

    NOTE_LOW_RANGE = np.array([169, 74, 255])
    NOTE_UP_RANGE = np.array([169, 74, 255])
    SKILL_LOW_RANGE = np.array([91, 128, 255])
    SKILL_UP_RANGE = np.array([91, 128, 255])
    SLIDE_LOW_RANGE = np.array([44, 102, 255])
    SLIDE_UP_RANGE = np.array([44, 102, 255])
    SLIDE_LINE_LOW_RANGE = np.array([0, 250, 55])
    SLIDE_LINE_UP_RANGE = np.array([255, 255, 255])
    FLICK_LOW_RANGE = np.array([143, 82, 255])
    FLICK_UP_RANGE = np.array([146, 90, 255])

    NOTE_POSITION_LIST = ["Left", "Middle", "Right"]

    # FPS_list = []
    # last_time = time.time()

    start_play_time = time.time()

    for key in (KEY_LIST_MAIN + KEY_LIST_SECOND + KEY_LIST_FLICK):
        time.sleep(0.025)
        press_and_release(key)
    print("Playing !")

    last_note_pressed_time = time.time()

    while True:
        screen_main = Screen.grab_screen(region=(120, 480, 820, 490))
        screen_main = cv2.cvtColor(screen_main, cv2.COLOR_BGR2HSV)

        screens_list = [screen_main[:, 0:270],
                        screen_main[:, 320:380], screen_main[:, 430:700]]

        masks_list = [cv2.inRange(screens_list[i], NOTE_LOW_RANGE, NOTE_UP_RANGE) for i in range(0, 3)] + \
                     [cv2.inRange(screens_list[i], SKILL_LOW_RANGE, SKILL_UP_RANGE) for i in range(0, 3)] + \
                     [cv2.inRange(screens_list[i], SLIDE_LOW_RANGE, SLIDE_UP_RANGE) for i in range(0, 3)] + \
                     [cv2.inRange(screens_list[i], FLICK_LOW_RANGE, FLICK_UP_RANGE) for i in range(0, 3)]

        findNonZero_list = [cv2.findNonZero(
            masks_list[i]) for i in range(0, 12)]

        index_nonZero_list = [index for index, value in enumerate(findNonZero_list) if value is not None]

        if len(index_nonZero_list) > 0:
            if all(value <= 2 for value in index_nonZero_list):
                for i in index_nonZero_list:
                    press_and_release(KEY_LIST_MAIN[i])
                    if time.time() - last_note_pressed_time > 0.125:
                        for j in index_nonZero_list:
                            print(Fore.LIGHTCYAN_EX + "Note - " + NOTE_POSITION_LIST[j])
                        last_note_pressed_time = time.time()

            elif all(value >= 9 for value in index_nonZero_list):
                time.sleep(0.045)
                for i in index_nonZero_list:
                    press_and_release(KEY_LIST_FLICK[i - 9])
                    print(Fore.LIGHTMAGENTA_EX + "Flick")

            else:
                for k in KEY_LIST_MAIN:
                    press(k)
                print(Fore.LIGHTGREEN_EX + "Slide" + Fore.WHITE +
                      " / " + Fore.LIGHTYELLOW_EX + "Skill")

                get_mean = True
                middle_slide = False
                two_slide = False

                x = (120, 820)
                start_time = time.time()
                while True:
                    screen = Screen.grab_screen(region=(150, 370, 790, 400))
                    screen = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
                    mask_slide_line = cv2.inRange(
                        screen, SLIDE_LINE_LOW_RANGE, SLIDE_LINE_UP_RANGE)

                    slide_line_nonZero = cv2.findNonZero(mask_slide_line)
                    if slide_line_nonZero is None:
                        if time.time() - start_time > 0.25:
                            time.sleep(0.15)
                        else:
                            time.sleep(0.15)
                        for k in (KEY_LIST_MAIN + KEY_LIST_SECOND):
                            release(k)
                        break

                    if get_mean:
                        get_mean = False

                        mean_x = int((sum(slide_line_nonZero) /
                                      len(slide_line_nonZero))[0][0])
                        if mean_x <= 280:
                            x = (440, 820)
                        elif mean_x >= 360:
                            x = (120, 500)
                        else:
                            middle_slide = True

                    if not two_slide:
                        if not middle_slide:
                            screen = Screen.grab_screen(region=(x[0], 475, x[1], 490))
                        else:
                            img1 = Screen.grab_screen(region=(120, 475, 400, 490))
                            img2 = Screen.grab_screen(region=(540, 475, 820, 490))
                            screen = np.concatenate((img1, img2), axis=1)
                        screen = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
                        mask_note = cv2.inRange(
                            screen, NOTE_LOW_RANGE, NOTE_UP_RANGE)
                        mask_skill = cv2.inRange(
                            screen, SKILL_LOW_RANGE, SKILL_UP_RANGE)
                        mask_slide = cv2.inRange(
                            screen, SLIDE_LOW_RANGE, SLIDE_UP_RANGE)
                        mask_flick = cv2.inRange(
                            screen, FLICK_LOW_RANGE, FLICK_UP_RANGE)
                        if cv2.findNonZero(mask_note) is not None or cv2.findNonZero(mask_skill) is not None:
                            for k in KEY_LIST_SECOND:
                                press_and_release(k)
                            print(Fore.LIGHTCYAN_EX + "Normal" + Fore.WHITE +
                                  " / " + Fore.LIGHTYELLOW_EX + "Skill")
                        if cv2.findNonZero(mask_slide) is not None:
                            for k in KEY_LIST_SECOND:
                                press(k)
                            two_slide = True
                            print(Fore.LIGHTGREEN_EX + "Slide")
                            start_time = time.time()
                        if cv2.findNonZero(mask_flick) is not None:
                            time.sleep(0.045)
                            for k in KEY_LIST_FLICK:
                                press_and_release(k)
                            print(Fore.LIGHTMAGENTA_EX + "Flick")

                    # show_screen(True)

        if cv2.countNonZero(cv2.cvtColor(screen_main, cv2.COLOR_RGB2GRAY)) == 0 and time.time() - start_play_time > 30:
            played += 1
            gameEnd_to_home()
            break

        # show_screen(False)

        # FPS_list.append(round(1 / (time.time() - last_time)))
        # if len(FPS_list) == 250:
        #    print("FPS = {}".format(sum(FPS_list) / len(FPS_list)))
        #    FPS_list = []
        # last_time = time.time()


def show_screen(showLine):
    NOTE_LOW_RANGE = np.array([169, 74, 255])
    NOTE_UP_RANGE = np.array([169, 74, 255])
    SKILL_LOW_RANGE = np.array([91, 128, 255])
    SKILL_UP_RANGE = np.array([91, 128, 255])
    SLIDE_LOW_RANGE = np.array([44, 102, 255])
    SLIDE_UP_RANGE = np.array([44, 102, 255])
    SLIDE_LINE_LOW_RANGE = np.array([0, 250, 55])
    SLIDE_LINE_UP_RANGE = np.array([255, 255, 255])
    FLICK_LOW_RANGE = np.array([143, 82, 255])
    FLICK_UP_RANGE = np.array([146, 90, 255])

    screen_show = Screen.grab_screen(region=(120, 250, 820, 500))
    screen_show = cv2.cvtColor(screen_show, cv2.COLOR_BGR2HSV)

    if not showLine:
        screen_show = cv2.inRange(screen_show, NOTE_LOW_RANGE, NOTE_UP_RANGE) + \
                      cv2.inRange(screen_show, SKILL_LOW_RANGE, SKILL_UP_RANGE) + \
                      cv2.inRange(screen_show, SLIDE_LOW_RANGE, SLIDE_UP_RANGE) + \
                      cv2.inRange(screen_show, SLIDE_LOW_RANGE, SLIDE_UP_RANGE) + \
                      cv2.inRange(screen_show, FLICK_LOW_RANGE, FLICK_UP_RANGE)
    else:
        screen_show = cv2.inRange(screen_show, NOTE_LOW_RANGE, NOTE_UP_RANGE) + \
                      cv2.inRange(screen_show, SKILL_LOW_RANGE, SKILL_UP_RANGE) + \
                      cv2.inRange(screen_show, SLIDE_LOW_RANGE, SLIDE_UP_RANGE) + \
                      cv2.inRange(screen_show, SLIDE_LOW_RANGE, SLIDE_UP_RANGE) + \
                      cv2.inRange(screen_show, FLICK_LOW_RANGE, FLICK_UP_RANGE) + \
                      cv2.inRange(screen_show, SLIDE_LINE_LOW_RANGE, SLIDE_LINE_UP_RANGE)

    cv2.imshow("Bot global game view", np.array(screen_show))
    cv2.waitKey(1)


played = 0


def home_to_game():
    global played
    global first_time
    global song_try_counter

    while pyautogui.locateOnScreen("LiveButton.png", region=(825, 520, 905, 550), confidence=0.75) is None:
        print(
            "Can\'t find live button, please go to the home screen of the game (where we see the characters talking).")
        time.sleep(1)
    print("Don\'t move your mouse.")
    time.sleep(1)
    pyautogui.click(860, 500)
    time.sleep(2)
    pyautogui.click(535, 220)
    time.sleep(1)
    pyautogui.click(470, 370)
    while pyautogui.locateOnScreen("ConfirmButton.png", region=(680, 500, 800, 530), confidence=0.75) is None:
        time.sleep(0.5)
    time.sleep(1)

    if song_choice_var == 1:
        time.sleep(1)
        print("Choosing same song...")

    elif song_choice_var == 2:
        if not first_time:
            print("Choosing next song...")
            pyautogui.moveTo(250, 320)
            pyautogui.dragTo(250, 240, duration=1)
        else:
            print("Selecting song...")
            first_time = False
            time.sleep(1)

    elif song_choice_var == 3:
        time.sleep(1)

        if is_playing_easy:
            x1 = 327
            width = 0
        else:
            x1 = 351
            width = 1

        while pyautogui.locateOnScreen("FullComboStar.png", region=(x1, 267, 27 + width, 28),
                                       confidence=0.75) is not None \
                or pyautogui.locateOnScreen("FullPerfectStar.png", region=(x1, 267, 27 + width, 28),
                                            confidence=0.75) is not None:
            print("This song is already full-comboed, selecting next song...")
            pyautogui.moveTo(250, 320)
            pyautogui.dragTo(250, 240, duration=1)
            song_try_counter = 0
            time.sleep(1)

        if song_try_counter == how_much_try:
            print("The bot did not succeed to full-combo this song after", how_much_try,
                  "times, selecting next song...")
            pyautogui.moveTo(250, 320)
            pyautogui.dragTo(250, 240, duration=1)
            song_try_counter = 0

        song_try_counter += 1

        if song_try_counter > 1:
            print("Replaying same song.")

    elif song_choice_var == 4:
        time.sleep(1)

        if is_playing_easy:
            x1 = 327
            width = 0
        else:
            x1 = 351
            width = 1

        while pyautogui.locateOnScreen("FullPerfectStar.png", region=(x1, 267, 27 + width, 28),
                                       confidence=0.75) is not None:
            print("This song is already full-perfected, selecting next song...")
            pyautogui.moveTo(250, 320)
            pyautogui.dragTo(250, 240, duration=1)
            song_try_counter = 0
            time.sleep(1)

        if song_try_counter == how_much_try:
            print("The bot did not succeed to full-perfect this song after", how_much_try,
                  "times, selecting next song...")
            pyautogui.moveTo(250, 320)
            pyautogui.dragTo(250, 240, duration=1)
            song_try_counter = 0

        song_try_counter += 1

        if song_try_counter > 1:
            print("Replaying same song.")

    elif song_choice_var == "v":
        if played != 0:
            if pyautogui.locateOnScreen("FullComboStar.png", region=(351, 267, 28, 28), confidence=0.75) is not None \
                    or pyautogui.locateOnScreen("FullPerfectStar.png", region=(351, 267, 28, 28),
                                                confidence=0.75) is not None:
                print("This song is already full-comboed, selecting next song...")
                pyautogui.moveTo(250, 320)
                pyautogui.dragTo(250, 240, duration=1)
                played = 0
                time.sleep(1)
            elif played > 2:
                print("Couldn't full-combo this song within 2 tries selecting next one.")

    pyautogui.click(730, 510)
    time.sleep(1)
    pyautogui.click(740, 510)
    time.sleep(1)
    pyautogui.click(560, 410)
    time.sleep(0.1)
    pyautogui.moveTo(470, 540)
    time.sleep(5)
    while cv2.countNonZero(cv2.cvtColor(Screen.grab_screen(region=(904, 64, 906, 66)), cv2.COLOR_RGB2GRAY)) == 0:
        time.sleep(1)
    time.sleep(2)
    while cv2.countNonZero(cv2.cvtColor(Screen.grab_screen(region=(120, 465, 820, 500)), cv2.COLOR_RGB2GRAY)) == 0:
        time.sleep(0.5)
    time.sleep(1)
    play()


def gameEnd_to_home():
    print(Fore.WHITE + "Game finished.")
    time.sleep(5)
    KEY_LIST = ['e', 'd', 'c']
    no_live_button = True
    while no_live_button:
        for k in KEY_LIST:
            time.sleep(0.5)
            screen = Screen.grab_screen(region=(820, 70, 850, 95))
            screen = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(screen, np.array(
                [0, 0, 76]), np.array([0, 0, 79]))
            if cv2.findNonZero(mask) is not None:
                no_live_button = False
                break
            else:
                press_and_release(k)
    pyautogui.moveTo(680, 90)
    for n in range(0, 4):
        time.sleep(0.25)
        pyautogui.click()
    time.sleep(1)
    time.sleep(1)
    home_to_game()


if __name__ == '__main__':
    ask_options()
