import pyautogui as pgui
from ScreenCoords import ScreenCoords
from imagesearch_copy import imagesearch_all
from math import sqrt
import time
import cv2


class Bot:
    def __init__(self):
        """ positional variables """
        self.hangar_pos = ScreenCoords(170, 45)
        self.client_pos = ScreenCoords(418, 45)
        self.safe_point = ScreenCoords(1712, 842)
        self.my_ship_position = ScreenCoords(959, 565)
        self.panel_minimap_position = ScreenCoords(175, 75)

        points1 = [(1829, 817), (1794, 853), (1760, 816), (1726, 838), (1665, 814), (1598, 843), (1649, 878),
                   (1715, 851), (1841, 869)]
        self.pickup_path_points = [ScreenCoords(x, y - 10) for x, y in points1]

        """
        # loops through the path positions with the mouse
        
        for point in self.pickup_path_points:
            pgui.moveTo(*point)
            sleep(0.3)
        """

        """ other variables """
        self.bonus_box_cv2_image = cv2.imread("resources/box_retro_3.png", 0)
        self.mode = "moving_to_pick"

        self.path_counter = 0
        self.delay = 0

        self.print_counter = 0
        self.picking_time = time.time()

        self.map = "2-2"
        # self.map = "4-2"

    def start_picking(self):
        self.set_starting_point()

        while True:
            """
            if self.lost_connection():  # too slow? (or running too often?)
                self.click(ScreenCoords(872, 616))
                sleep(5)
                continue
            """
            if self.ship_destroyed():
                """ repairs in place for uridium """
                self.click(ScreenCoords(960, 543))  # click ok
                time.sleep(0.5)
                self.click(ScreenCoords(964, 758))  # choose uridium repair
                time.sleep(5)
                continue
            elif self.mode == "moving_to_safety":
                if not self.ship_is_moving():
                    self.mode = "idle"
                    continue
                elif not self.ship_in_radiation_zone():
                    self.stop_the_ship()
                    self.delay = 0
                    self.mode = "idle"
            elif self.mode == "moving_to_pick":
                # when clicked on npc instead of bonus box while moving through the map

                if time.time() - self.picking_time > 4:
                    self.stop_the_ship()
                    self.mode = "idle"

                self.delay = 0

                if self.ship_is_moving():
                    self.print_mode()
                    continue
                else:
                    self.mode = "idle"
            elif self.mode == "idle":
                picking = self.pick()

                if not picking and self.mode != "moving_to_safety":
                    self.move_path_map()
            elif self.mode == "moving_path":
                picking = self.pick()
                time.sleep(0.05)

                if not self.ship_is_moving():
                    self.mode = "idle"
                    continue

            if self.delay != 0:
                time.sleep(self.delay)

            self.print_mode()

    def pick(self):
        if self.ship_in_radiation_zone():
            self.mode = "moving_to_safety"
            self.delay = 2
            self.click(self.safe_point)
            return False

        self.delay = 0
        position = [-1, -1]
        positions = self.eliminate_similar(imagesearch_all(self.bonus_box_cv2_image, precision=0.9))
        positions = self.eliminate_boxes_under_the_ship(positions)

        if len(positions) != 0:
            position = self.get_closest_box(positions)

        if position[0] != -1:
            self.click(ScreenCoords(position[0] + 28, position[1] + 28))
            self.picking_time = time.time()
            self.mode = "moving_to_pick"

            return True
        else:
            return False

    def move_path_map(self):
        if not self.minimap_open():
            self.stop_the_ship()
            self.click(self.panel_minimap_position)
            time.sleep(0.3)
            return

        self.click(self.pickup_path_points[self.path_counter])
        self.mode = "moving_path"
        self.delay = 0  # 0.5

        if not self.ship_is_moving():  # indicates that we successfully moved to the current path point and stand idly
            self.increase_path_counter()
            self.move_path_map()
            return

    def increase_path_counter(self):
        self.path_counter += 1

        if self.path_counter == len(self.pickup_path_points):
            self.path_counter = 0

    @staticmethod
    def ship_is_moving() -> bool:
        return pgui.locateOnScreen("resources/moving_indicator.png", region=(1567, 748, 100, 100)) is not None

    def set_starting_point(self):
        if self.map == "2-2":
            self.path_counter = 0
        elif self.map == "4-2":
            self.path_counter = 4

    @staticmethod
    def lost_connection():
        return pgui.locateOnScreen("resources/red_cross_part.png", region=(865, 550, 45, 30)) is not None

    @staticmethod
    def ship_in_radiation_zone():
        """
        Checks a pixel on predetermined position.
        This pixel only changes color when the screen flashes (ship is in radiation zone)
        """

        control_pixel = pgui.screenshot(region=(266, 73, 5, 3)).getpixel((3, 1))
        return control_pixel != (22, 38, 47)

    @staticmethod
    def ship_destroyed():
        control_pixel = pgui.screenshot(region=(1121, 696, 5, 3)).getpixel((3, 1))

        return control_pixel == (28, 35, 41)

    def stop_the_ship(self):
        self.click(self.my_ship_position + ScreenCoords(120, 0))  # click next to my own ship
        time.sleep(0.25)

    @staticmethod
    def click(screencoords):
        pgui.moveTo(screencoords.x, screencoords.y, duration=0.1)
        pgui.mouseDown()
        time.sleep(0.01)
        pgui.mouseUp()

    @staticmethod
    def eliminate_boxes_under_the_ship(lst):
        """
        Eliminate found box positions that are under the ship (in proximity)
        so that the bot doesn't click on a just being picked box.
        """

        p0 = [903, 607]
        p1 = [1018, 727]
        done = []

        for point in lst:
            if p0[0] < point[0] < p1[0] and p0[1] < point[1] < p1[1]:
                continue

            done.append(point)

        return done

    def get_closest_box(self, lst):
        lst.sort(key=self.distance_to_box)
        return lst[0]

    def distance_to_box(self, point1):
        return sqrt((self.my_ship_position[0] - point1[0]) ** 2 + (self.my_ship_position[1] - point1[1]) ** 2)

    @staticmethod
    def minimap_open():
        return pgui.locateOnScreen("resources/minimap_open_icon.png", region=(154, 53, 60, 60)) is not None

    def print_mode(self):
        print(self.print_counter, self.mode)
        self.print_counter += 1

    @staticmethod
    def eliminate_similar(lst):
        """
        Eliminates multiple found positions that represent the same bonus box
        """

        def between(what, first, second):
            return first < what < second

        i = 0
        dif = 8

        done = []

        while i < len(lst):
            item = lst[i]
            tmp = [item]
            done.append(item)

            for x in lst[i + 1:]:
                if between(x[0], item[0] - dif, item[0] + dif) and between(x[1], item[1] - dif, item[1] + dif):
                    continue

                tmp.append(x)

            lst = tmp[:]
            i += 1

        return done
