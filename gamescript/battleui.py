import datetime

import pygame
import pygame.freetype
from gamescript import map, commonscript


class UIButton(pygame.sprite.Sprite):
    def __init__(self, x, y, image, event=None, layer=11):
        self._layer = layer
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = (x, y)
        self.image = image
        self.event = event
        self.rect = self.image.get_rect(center=self.pos)
        self.mouse_over = False


class SwitchButton(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = (x, y)
        self.images = image
        self.image = self.images[0]
        self.event = 0
        self.rect = self.image.get_rect(center=self.pos)
        self.mouse_over = False
        self.last_event = 0

    def update(self):
        if self.event != self.last_event:
            self.image = self.images[self.event]
            self.rect = self.image.get_rect(center=self.pos)
            self.last_event = self.event


class PopupIcon(pygame.sprite.Sprite):
    def __init__(self, x, y, image, event, game_ui, item_id=""):
        self._layer = 12
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.x, self.y = x, y
        self.image = image
        self.event = 0
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.mouse_over = False
        self.item_id = item_id


class GameUI(pygame.sprite.Sprite):
    def __init__(self, x, y, image, icon, ui_type, text="", text_size=16):
        from gamescript import start
        self.unit_state_text = start.unit_state_text
        self.morale_state_text = start.morale_state_text
        self.stamina_state_text = start.stamina_state_text
        self.subunit_state_text = start.subunit_state_text
        self.quality_text = start.quality_text
        self.leader_state_text = start.leader_state_text
        self.terrain_list = map.terrain_list

        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", text_size)
        self.x, self.y = x, y
        self.text = text
        self.image = image
        self.icon = icon
        self.ui_type = ui_type
        self.value = [-1, -1]
        self.last_value = 0
        self.option = 0
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.last_who = -1  # last showed parent unit, start with -1 which mean any new clicked will show up at start
        if self.ui_type == "topbar":  # setup variable for topbar ui
            position = 10
            for ic in self.icon:  # Blit icon into topbar ui
                self.icon_rect = ic.get_rect(
                    topleft=(self.image.get_rect()[0] + position, self.image.get_rect()[1]))
                self.image.blit(ic, self.icon_rect)
                position += 90

        elif self.ui_type == "commandbar":  # setup variable for command bar ui
            self.icon_rect = self.icon[6].get_rect(
                center=(self.image.get_rect()[0] + self.image.get_size()[0] / 1.1, self.image.get_rect()[1] + 40))
            self.image.blit(self.icon[6], self.icon_rect)
            self.white = [self.icon[0], self.icon[1], self.icon[2], self.icon[3], self.icon[4], self.icon[5]]  # team 1 white chess head
            self.black = [self.icon[7], self.icon[8], self.icon[9], self.icon[10], self.icon[11], self.icon[12]]  # team 2 black chess head
            self.last_auth = 0

        elif self.ui_type == "troopcard":  # setup variable for subunit card ui
            self.font_head = pygame.font.SysFont("curlz", text_size + 4)
            self.font_head.set_italic(True)
            self.font_long = pygame.font.SysFont("helvetica", text_size - 2)
            self.front_text = ["", "Troop: ", "Stamina: ", "Morale: ", "Discipline: ", "Melee Attack: ",
                               "Melee Defense: ", "Range Defense: ", "Armour: ", "Speed: ", "Accuracy: ",
                               "Range: ", "Ammunition: ", "Reload: ", "Charge Power: ", "Charge Defense: ", "Mental: "]  # stat name
        self.image_original = self.image.copy()

    def value_input(self, who, weapon_list="", armour_list="", button="", change_option=0, split=False):
        make_long_text = commonscript.make_long_text
        for this_button in button:
            this_button.draw(self.image)
        position = 65
        if self.ui_type == "topbar":
            self.value = ["{:,}".format(who.troop_number) + " (" + "{:,}".format(who.max_health) + ")", who.staminastate, who.moralestate, who.state]
            if self.value[3] in self.unit_state_text:  # Check subunit state and blit name
                self.value[3] = self.unit_state_text[self.value[3]]
            # if type(self.value[2]) != str:

            self.value[2] = round(self.value[2] / 10)  # morale state
            if self.value[2] in self.morale_state_text:  # Check if morale state in the list and blit the name
                self.value[2] = self.morale_state_text[self.value[2]]
            elif self.value[2] > 15:  # if morale somehow too high use the highest morale state one
                self.value[2] = self.morale_state_text[15]

            self.value[1] = round(self.value[1] / 10)  # stamina state
            if self.value[1] in self.stamina_state_text:  # Check if stamina state and blit the name
                self.value[1] = self.stamina_state_text[self.value[1]]

            if self.value != self.last_value or split:  # only blit new text when value change or subunit split
                self.image = self.image_original.copy()
                for value in self.value:  # blit value text
                    text_surface = self.font.render(str(value), True, (0, 0, 0))
                    text_rect = text_surface.get_rect(
                        center=(self.image.get_rect()[0] + position, self.image.get_rect()[1] + 25))
                    self.image.blit(text_surface, text_rect)
                    if position >= 200:
                        position += 50
                    else:
                        position += 95
                self.last_value = self.value
        # for line in range(len(label)):
        #     surface.blit(label(line), (position[0], position[1] + (line * font_size) + (15 * line)))

        elif self.ui_type == "commandbar":
            if who.game_id != self.last_who or split:  # only redraw leader circle when change subunit
                use_colour = self.white  # colour of the chess icon for leader, white for team 1
                if who.team == 2:  # black for team 2
                    use_colour = self.black
                self.image = self.image_original.copy()
                self.image.blit(who.coa, who.coa.get_rect(topleft=self.image.get_rect().topleft))  # blit coa

                if who.commander:  # commander parentunit use king and queen icon
                    # gamestart general
                    self.icon_rect = use_colour[0].get_rect(
                        center=(
                        self.image.get_rect()[0] + self.image.get_size()[0] / 2.1, self.image.get_rect()[1] + 45))
                    self.image.blit(use_colour[0], self.icon_rect)

                    # sub commander/strategist role
                    self.icon_rect = use_colour[1].get_rect(
                        center=(self.image.get_rect()[0] + self.image.get_size()[0] / 2.1, self.image.get_rect()[1] + 140))
                    self.image.blit(use_colour[1], self.icon_rect)

                else:  # the rest use rook and bishop
                    # general
                    self.icon_rect = use_colour[2].get_rect(
                        center=(self.image.get_rect()[0] + self.image.get_size()[0] / 2.1, self.image.get_rect()[1] + 45))
                    self.image.blit(use_colour[2], self.icon_rect)

                    # sub general/special advisor role
                    self.icon_rect = use_colour[5].get_rect(
                        center=(self.image.get_rect()[0] + self.image.get_size()[0] / 2.1, self.image.get_rect()[1] + 140))
                    self.image.blit(use_colour[5], self.icon_rect)

                self.icon_rect = use_colour[3].get_rect(center=(  # left sub general
                    self.image.get_rect()[0] - 10 + self.image.get_size()[0] / 3.1,
                    self.image.get_rect()[1] - 10 + self.image.get_size()[1] / 2.2))
                self.image.blit(use_colour[3], self.icon_rect)
                self.icon_rect = use_colour[0].get_rect(center=(  # right sub general
                    self.image.get_rect()[0] - 10 + self.image.get_size()[0] / 1.4,
                    self.image.get_rect()[1] - 10 + self.image.get_size()[1] / 2.2))
                self.image.blit(use_colour[4], self.icon_rect)

                self.image_original2 = self.image.copy()
            authority = str(who.authority).split(".")[0]
            if self.last_auth != authority or who.game_id != self.last_who or split:  # authority number change only when not same as last
                self.image = self.image_original2.copy()
                text_surface = self.font.render(authority, True, (0, 0, 0))
                text_rect = text_surface.get_rect(
                    center=(self.image.get_rect()[0] + self.image.get_size()[0] / 1.12, self.image.get_rect()[1] + 83))
                self.image.blit(text_surface, text_rect)
                self.last_auth = authority

        elif self.ui_type == "troopcard":
            position = 15  # starting row
            position_x = 45  # starting point of text
            self.value = [who.name, "{:,}".format(int(who.troop_number)) + " (" + "{:,}".format(int(who.maxtroop)) + ")",
                          str(who.stamina).split(".")[0] + ", " + str(self.subunit_state_text[who.state]), str(who.morale).split(".")[0],
                          str(who.discipline).split(".")[0], str(who.attack).split(".")[0], str(who.melee_def).split(".")[0],
                          str(who.range_def).split(".")[0], str(who.armour).split(".")[0], str(who.speed).split(".")[0],
                          str(who.accuracy).split(".")[0], str(who.shootrange).split(".")[0], str(who.magazine_left),
                          str(who.reload_time).split(".")[0] + "/" + str(who.reload).split(".")[0] + ": " + str(who.ammo_now),
                          str(who.charge).split(".")[0], str(who.charge_def).split(".")[0], str(who.mentaltext).split(".")[0],
                          str(who.temp_count).split(".")[0]]
            self.value2 = [who.trait, who.skill, who.skill_cooldown, who.skill_effect, who.status_effect]
            self.description = who.description
            if type(self.description) == list:
                self.description = self.description[0]
            if self.value != self.last_value or change_option == 1 or who.game_id != self.last_who:
                self.image = self.image_original.copy()
                row = 0
                self.name = self.value[0]
                leader_text = ""
                if who.leader is not None and who.leader.name != "None":
                    leader_text = "/" + str(who.leader.name)
                    if who.leader.state in self.leader_state_text:
                        leader_text += " " + "(" + self.leader_state_text[who.leader.state] + ")"
                text_surface = self.font_head.render(self.name + leader_text, True,
                                                     (0, 0, 0))  # subunit and leader name at the top
                text_rect = text_surface.get_rect(
                    midleft=(self.image.get_rect()[0] + position_x, self.image.get_rect()[1] + position))
                self.image.blit(text_surface, text_rect)
                row += 1
                position += 20
                if self.option == 1:  # stat card
                    # self.icon_rect = self.icon[0].get_rect(
                    #     center=(
                    #     self.image.get_rect()[0] + self.image.get_size()[0] -20, self.image.get_rect()[1] + 40))
                    # deletelist = [i for i,x in enumerate(self.value) if x == 0]
                    # if len(deletelist) != 0:
                    #     for i in sorted(deletelist, reverse = True):
                    #         self.value.pop(i)
                    #         text.pop(i)
                    new_value, text = self.value[0:-1], self.front_text[1:]
                    for n, value in enumerate(new_value[1:]):
                        value = value.replace("inf", "\u221e")
                        text_surface = self.font.render(text[n] + value, True, (0, 0, 0))
                        text_rect = text_surface.get_rect(
                            midleft=(self.image.get_rect()[0] + position_x, self.image.get_rect()[1] + position))
                        self.image.blit(text_surface, text_rect)
                        position += 20
                        row += 1
                        if row == 9:
                            position_x, position = 200, 35
                elif self.option == 0:  # description card
                    make_long_text(self.image, self.description, (42, 25), self.font_long)  # blit long description
                elif self.option == 3:  # equipment and terrain
                    # v Terrain text
                    terrain = self.terrain_list[who.terrain]
                    if who.feature is not None:
                        terrain += "/" + self.feature_list[who.feature]
                    # ^ End terrain text

                    # v Equipment text
                    text_value = [
                        self.quality_text[who.primary_main_weapon[1]] + " " + str(weapon_list.weapon_list[who.primary_main_weapon[0]][0]) + " / " +
                        self.quality_text[who.primary_sub_weapon[1]] + " " + str(weapon_list.weapon_list[who.primary_sub_weapon[0]][0]),
                        self.quality_text[who.secondary_main_weapon[1]] + " " + str(weapon_list.weapon_list[who.secondary_main_weapon[0]][0]) + " / " +
                        self.quality_text[who.secondary_sub_weapon[1]] + " " + str(weapon_list.weapon_list[who.secondary_sub_weapon[0]][0])]

                    text_value += ["Melee Damage: " + str(who.melee_dmg).split(".")[0] + ", Speed" + str(who.meleespeed).split(".")[0] +
                                  ", Penetrate: " + str(who.melee_penetrate).split(".")[0]]
                    text_value += ["Range Damage: " + str(who.range_dmg).split(".")[0] + ", Speed" + str(who.reload).split(".")[0] +
                                  ", Penetrate: " + str(who.range_penetrate).split(".")[0]]

                    text_value += [str(armour_list.armour_list[who.armourgear[0]][0]) + ": A: " + str(who.armour).split(".")[0] + ", W: " +
                                   str(armour_list.armour_list[who.armourgear[0]][2]), "Total Weight:" + str(who.weight), "Terrain:" + terrain,
                                  "Height:" + str(who.height), "Temperature:" + str(who.temp_count).split(".")[0]]

                    if "None" not in who.mount:  # if mount is not the None mount id 1
                        armour_text = "//" + who.mountarmour[0]
                        if "None" in who.mountarmour[0]:
                            armour_text = ""
                        text_value.insert(3, "Mount:" + who.mountgrade[0] + " " + who.mount[0] + armour_text)
                    # ^ End equipment text

                    for text in text_value:
                        text_surface = self.font.render(str(text), 1, (0, 0, 0))
                        text_rect = text_surface.get_rect(
                            midleft=(self.image.get_rect()[0] + position_x, self.image.get_rect()[1] + position))
                        self.image.blit(text_surface, text_rect)
                        position += 20
                self.last_value = self.value
        self.last_who = who.game_id


class SkillCardIcon(pygame.sprite.Sprite):
    cooldown = None
    active_skill = None

    def __init__(self, image, pos, icon_type, game_id=None):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.icon_type = icon_type  # type 0 is trait 1 is skill
        self.game_id = game_id  # ID of the skill
        self.pos = pos  # pos of the skill on ui
        self.font = pygame.font.SysFont("helvetica", 18)
        self.cooldown_check = 0  # cooldown number
        self.active_check = 0  # active timer number
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.image_original = self.image.copy()  # keep original image without number
        self.cooldown_rect = self.image.get_rect(topleft=(0, 0))

    def change_number(self, number):
        """Change number more than thousand to K digit e.g. 1k = 1000"""
        return str(round(number / 1000, 1)) + "K"

    def icon_change(self, cooldown, active_timer):
        """Show active effect timer first if none show cooldown"""
        if active_timer != self.active_check:
            self.active_check = active_timer  # renew number
            self.image = self.image_original.copy()
            if self.active_check > 0:
                rect = self.image.get_rect(topleft=(0, 0))
                self.image.blit(self.active_skill, rect)
                output_number = str(self.active_check)
                if self.active_check >= 1000:
                    output_number = self.change_number(output_number)
                text_surface = self.font.render(output_number, 1, (0, 0, 0))  # timer number
                text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
                self.image.blit(text_surface, text_rect)

        elif cooldown != self.cooldown_check and self.active_check == 0:  # Cooldown only get blit when skill is not active
            self.cooldown_check = cooldown
            self.image = self.image_original.copy()
            if self.cooldown_check > 0:
                self.image.blit(self.cooldown, self.cooldown_rect)
                output_number = str(self.cooldown_check)
                if self.cooldown_check >= 1000:  # change a thousand number into k (1k,2k)
                    output_number = self.change_number(output_number)
                text_surface = self.font.render(output_number, 1, (0, 0, 0))
                text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
                self.image.blit(text_surface, text_rect)


class EffectCardIcon(pygame.sprite.Sprite):

    def __init__(self, image, pos, icon_type, game_id=None):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.icon_type = icon_type
        self.game_id = game_id
        self.pos = pos
        self.cooldown_check = 0
        self.active_check = 0
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.image_original = self.image.copy()


class FPScount(pygame.sprite.Sprite):
    def __init__(self):
        self._layer = 12
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.image_original = self.image.copy()
        self.font = pygame.font.SysFont("Arial", 18)
        self.rect = self.image.get_rect(center=(30, 110))
        fps = "60"
        fps_text = self.font.render(fps, True, pygame.Color("blue"))
        self.text_rect = fps_text.get_rect(center=(25, 25))

    def fps_show(self, clock):
        """Update current fps"""
        self.image = self.image_original.copy()
        fps = str(int(clock.get_fps()))
        fps_text = self.font.render(fps, True, pygame.Color("blue"))
        text_rect = fps_text.get_rect(center=(25, 25))
        self.image.blit(fps_text, text_rect)


class SelectedSquad(pygame.sprite.Sprite):
    image = None

    def __init__(self, pos, layer=17):
        self._layer = layer
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)

    def pop(self, pos):
        """pop out at the selected subunit in inspect uo"""
        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)


class Minimap(pygame.sprite.Sprite):
    def __init__(self, pos):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = pos

        self.team2_dot = pygame.Surface((8, 8))  # dot for team2 subunit
        self.team2_dot.fill((0, 0, 0))  # black corner
        self.team1_dot = pygame.Surface((8, 8))  # dot for team1 subunit
        self.team1_dot.fill((0, 0, 0))  # black corner
        team2 = pygame.Surface((6, 6))  # size 6x6
        team2.fill((255, 0, 0))  # red rect
        team1 = pygame.Surface((6, 6))
        team1.fill((0, 0, 255))  # blue rect
        rect = self.team2_dot.get_rect(topleft=(1, 1))
        self.team2_dot.blit(team2, rect)
        self.team1_dot.blit(team1, rect)
        self.team1_pos = []
        self.team2_pos = []

        self.last_scale = 10

    def draw_image(self, image, camera):
        self.image = image
        scale_width = self.image.get_width() / 5
        scale_height = self.image.get_height() / 5
        self.dim = pygame.Vector2(scale_width, scale_height)
        self.image = pygame.transform.scale(self.image, (int(self.dim[0]), int(self.dim[1])))
        self.image_original = self.image.copy()
        self.camera_border = [camera.image.get_width(), camera.image.get_height()]
        self.camera_pos = camera.pos
        self.rect = self.image.get_rect(bottomright=self.pos)

    def update(self, view_mode, camera_pos, team1_pos_list, team2_pos_list):
        """update parentunit dot on map"""
        if self.team1_pos != team1_pos_list.values() or self.team2_pos != team2_pos_list.values() or \
                self.camera_pos != camera_pos or self.last_scale != view_mode:
            self.team1_pos = team1_pos_list.values()
            self.team2_pos = team2_pos_list.values()
            self.camera_pos = camera_pos
            self.image = self.image_original.copy()
            for team1 in team1_pos_list.values():
                scaled_pos = team1 / 5
                rect = self.team1_dot.get_rect(center=scaled_pos)
                self.image.blit(self.team1_dot, rect)
            for team2 in team2_pos_list.values():
                scaled_pos = team2 / 5
                rect = self.team2_dot.get_rect(center=scaled_pos)
                self.image.blit(self.team2_dot, rect)
            pygame.draw.rect(self.image, (0, 0, 0), (camera_pos[1][0] / 5 / view_mode, camera_pos[1][1] / 5 / view_mode,
                                                     self.camera_border[0] * 10 / view_mode / 50, self.camera_border[1] * 10 / view_mode / 50), 2)


class EventLog(pygame.sprite.Sprite):
    max_row_show = 9  # maximum 9 text rows can appear at once
    log_scroll = None  # Link from gamebattle after creation of both object

    def __init__(self, image, pos):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", 16)
        self.pos = pos
        self.image = image
        self.image_original = self.image.copy()
        self.rect = self.image.get_rect(bottomleft=self.pos)
        self.len_check = 0
        self.current_start_row = 0
        self.mode = 0
        self.battle_log = []  # 0 troop
        self.unit_log = []  # 1 army
        self.leader_log = []  # 2 leader
        self.subunit_log = []  # 3 subunit
        self.current_start_row = 0

    def make_new_log(self):
        self.mode = 0  # 0=troop,1=army(subunit),2=leader,3=subunit(sub-subunit)
        self.battle_log = []  # 0 troop
        self.unit_log = []  # 1 army
        self.leader_log = []  # 2 leader
        self.subunit_log = []  # 3 subunit
        self.current_start_row = 0
        self.len_check = 0  # total number of row in the current mode

    def add_event_log(self, map_event):
        self.map_event = map_event
        if self.map_event != {}:  # Edit map based event
            self.map_event.pop("id")
            for event in self.map_event:
                if type(self.map_event[event][2]) == int:
                    self.map_event[event][2] = [self.map_event[event][2]]
                elif "," in self.map_event[event][2]:  # Change mode list to list here since csvread don't have that function
                    self.map_event[event][2] = [int(item) if item.isdigit() else item for item in self.map_event[event][2].split(",")]
                if self.map_event[event][3] != "":  # change time string to time delta same reason as above
                    new_time = datetime.datetime.strptime(self.map_event[event][3], "%H:%M:%S").time()
                    new_time = datetime.timedelta(hours=new_time.hour, minutes=new_time.minute, seconds=new_time.second)
                    self.map_event[event][3] = new_time
                else:
                    self.map_event[event][3] = None

    def change_mode(self, mode):
        """Change tab"""
        self.mode = mode
        self.len_check = len((self.battle_log, self.unit_log, self.leader_log, self.subunit_log)[self.mode])
        self.current_start_row = 0
        if self.len_check > self.max_row_show:  # go to last row if there are more log than limit
            self.current_start_row = self.len_check - self.max_row_show
        self.log_scroll.current_row = self.current_start_row
        self.log_scroll.change_image(log_size=self.len_check)
        self.recreate_image()

    def clear_tab(self, all_tab=False):
        """Clear event from log for that mode"""
        self.len_check = 0
        self.current_start_row = 0
        log = (self.battle_log, self.unit_log, self.leader_log, self.subunit_log)[self.mode]  # log to edit
        log.clear()
        if all_tab:  # Clear event from every mode
            for log in (self.battle_log, self.unit_log, self.leader_log, self.subunit_log):
                log.clear()
        self.log_scroll.current_row = self.current_start_row
        self.log_scroll.change_image(log_size=self.len_check)
        self.recreate_image()

    def recreate_image(self):
        log = (self.battle_log, self.unit_log, self.leader_log, self.subunit_log)[self.mode]  # log to edit
        self.image = self.image_original.copy()
        row = 10
        for index, text in enumerate(log[self.current_start_row:]):
            if index == self.max_row_show:
                break
            text_surface = self.font.render(text[1], True, (0, 0, 0))
            text_rect = text_surface.get_rect(topleft=(40, row))
            self.image.blit(text_surface, text_rect)
            row += 20  # Whitespace between text row

    def log_text_process(self, who, mode_list, text_output):
        """Cut up whole log into separate sentence based on space"""
        image_change = False
        for mode in mode_list:
            log = (self.battle_log, self.unit_log, self.leader_log, self.subunit_log)[mode]  # log to edit
            if len(text_output) <= 45:  # EventLog each row cannot have more than 45 characters including space
                log.append([who, text_output])
            else:  # Cut the text log into multiple row if more than 45 char
                cut_space = [index for index, letter in enumerate(text_output) if letter == " "]
                loop_number = len(text_output) / 45  # number of row
                if loop_number.is_integer() is False:  # always round up if there is decimal number
                    loop_number = int(loop_number) + 1
                starting_index = 0

                for run in range(1, int(loop_number) + 1):
                    text_cut_number = [number for number in cut_space if number <= run * 45]
                    cut_number = text_cut_number[-1]
                    final_text_output = text_output[starting_index:cut_number]
                    if run == loop_number:
                        final_text_output = text_output[starting_index:]
                    if run == 1:
                        log.append([who, final_text_output])
                    else:
                        log.append([-1, final_text_output])
                    starting_index = cut_number + 1

            if len(log) > 1000:  # log cannot be more than 1000 length
                log_delete = len(log) - 1000
                del log[0:log_delete]  # remove the first few so only 1000 left
            if mode == self.mode:
                image_change = True
        return image_change

    def add_log(self, log, mode_list, event_id=None):
        """Add log to appropriate event log, the log must be in list format following this rule [attacker (game_id), logtext]"""
        at_last_row = False
        image_change = False
        image_change2 = False
        if self.current_start_row + self.max_row_show >= self.len_check:
            at_last_row = True
        if log is not None:  # when event map log commentary come in, log will be none
            text_output = ": " + log[1]
            image_change = self.log_text_process(log[0], mode_list, text_output)
        if event_id is not None and event_id in self.map_event:  # Process whether there is historical commentary to add to event log
            text_output = self.map_event[event_id]
            image_change2 = self.log_text_process(text_output[0], text_output[2],
                                                  str(text_output[3]) + ": " + text_output[1])
        if image_change or image_change2:
            self.len_check = len((self.battle_log, self.unit_log, self.leader_log, self.subunit_log)[self.mode])
            if at_last_row and self.len_check > 9:
                self.current_start_row = self.len_check - self.max_row_show
                self.log_scroll.current_row = self.current_start_row
            self.log_scroll.change_image(log_size=self.len_check)
            self.recreate_image()


class UIScroller(pygame.sprite.Sprite):
    def __init__(self, pos, height_ui, max_row_show, layer=11):
        self._layer = layer
        pygame.sprite.Sprite.__init__(self)
        self.height_ui = height_ui
        self.pos = pos
        self.image = pygame.Surface((10, self.height_ui))
        self.image.fill((255, 255, 255))
        self.image_original = self.image.copy()
        self.button_colour = (100, 100, 100)
        pygame.draw.rect(self.image, self.button_colour, (0, 0, self.image.get_width(), self.height_ui))
        self.rect = self.image.get_rect(topright=self.pos)
        self.current_row = 0
        self.max_row_show = max_row_show
        self.log_size = 0

    def create_new_image(self):
        percent_row = 0
        max_row = 100
        self.image = self.image_original.copy()
        if self.log_size > 0:
            percent_row = self.current_row * 100 / self.log_size
        # if self.current_row + self.max_row_show < self.log_size:
        if self.log_size > 0:
            max_row = (self.current_row + self.max_row_show) * 100 / self.log_size
        max_row = max_row - percent_row
        pygame.draw.rect(self.image, self.button_colour,
                         (0, int(self.height_ui * percent_row / 100), self.image.get_width(), int(self.height_ui * max_row / 100)))

    def change_image(self, new_row=None, log_size=None):
        """New row is input of scrolling by user to new row, log_size is changing based on adding more log or clear"""
        if log_size is not None and self.log_size != log_size:
            self.log_size = log_size
            self.create_new_image()
        if new_row is not None and self.current_row != new_row:  # accept from both wheeling scroll and drag scroll bar
            self.current_row = new_row
            self.create_new_image()

    def update(self, mouse_pos, *args):
        """User input update"""
        if (args is False or (args and args[0] and self.rect.collidepoint(mouse_pos))) and mouse_pos is not None:
            mouse_value = (mouse_pos[1] - self.pos[
                1]) * 100 / self.height_ui  # find what percentage of mouse_pos at the scroll bar (0 = top, 100 = bottom)
            if mouse_value > 100:
                mouse_value = 100
            if mouse_value < 0:
                mouse_value = 0
            new_row = int(self.log_size * mouse_value / 100)
            if self.log_size > self.max_row_show and new_row > self.log_size - self.max_row_show:
                new_row = self.log_size - self.max_row_show
            if self.log_size > self.max_row_show:  # only change scroll position in list longer than max length
                self.change_image(new_row)
            return self.current_row


class ArmySelect(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = image
        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)
        self.current_row = 0
        self.max_row_show = 2
        self.max_column_show = 6
        self.log_size = 0


class ArmyIcon(pygame.sprite.Sprite):
    def __init__(self, pos, army):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.army = army  # link army object so when click can correctly select or go to position
        army.icon = self  # link this icon to army object, mostly for when it gets killed so can easily remove from list
        self.pos = pos  # position on army selector ui
        self.leader_image = self.army.leader[0].image.copy()  # get leader image
        self.leader_image = pygame.transform.scale(self.leader_image, (int(self.leader_image.get_width() / 1.5),
                                                                       int(self.leader_image.get_height() / 1.5)))  # scale leader image to fit the icon
        self.image = pygame.Surface((self.leader_image.get_width() + 4, self.leader_image.get_height() + 4))  # create image black corner block
        self.image.fill((0, 0, 0))  # fill black corner
        center_image = pygame.Surface((self.leader_image.get_width() + 2, self.leader_image.get_height() + 2))  # create image block
        center_image.fill((144, 167, 255))  # fill colour according to team, blue for team 1
        if self.army.team == 2:
            center_image.fill((255, 114, 114))  # red colour for team 2
        image_rect = center_image.get_rect(topleft=(1, 1))
        self.image.blit(center_image, image_rect)  # blit colour block into border image
        self.leader_image_rect = self.leader_image.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(self.leader_image, self.leader_image_rect)  # blit leader image
        self.rect = self.image.get_rect(center=self.pos)

    def change_pos(self, pos):
        """change position of icon to new one"""
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)

    def change_image(self, new_image=None, change_side=False):
        """For changing side"""
        if change_side:
            self.image.fill((144, 167, 255))
            if self.army.team == 2:
                self.image.fill((255, 114, 114))
            self.image.blit(self.leader_image, self.leader_image_rect)
        if new_image is not None:
            self.leader_image = new_image
            self.image.blit(self.leader_image, self.leader_image_rect)

    def delete(self, local=False):
        """delete reference when del is called"""
        if local:
            print(locals())
        else:
            del self.army


class Timer(pygame.sprite.Sprite):
    def __init__(self, pos, text_size=20):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", text_size)
        self.pos = pos
        self.image = pygame.Surface((100, 30), pygame.SRCALPHA)
        self.image_original = self.image.copy()
        self.rect = self.image.get_rect(topleft=pos)
        self.timer = 0

    def start_setup(self, time_start):
        self.timer = time_start.total_seconds()
        self.old_timer = self.timer
        self.image = self.image_original.copy()
        self.time_number = time_start  # datetime.timedelta(seconds=self.timer)
        self.timer_surface = self.font.render(str(self.timer), True, (0, 0, 0))
        self.timer_rect = self.timer_surface.get_rect(topleft=(5, 5))
        self.image.blit(self.timer_surface, self.timer_rect)

    def timerupdate(self, dt):
        """Update in-self timer number"""
        if dt > 0:
            self.timer += dt
            if self.timer - self.old_timer > 1:
                self.old_timer = self.timer
                if self.timer >= 86400:  # Time pass midnight
                    self.timer -= 86400  # Restart clock to 0
                    self.old_timer = self.timer
                self.image = self.image_original.copy()
                self.time_number = datetime.timedelta(seconds=self.timer)
                time_num = str(self.time_number).split(".")[0]
                self.timer_surface = self.font.render(time_num, True, (0, 0, 0))
                self.image.blit(self.timer_surface, self.timer_rect)


class TimeUI(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = pos
        self.image = image.copy()
        self.image_original = self.image.copy()
        self.rect = self.image.get_rect(topleft=pos)


class ScaleUI(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.percent_scale = -100
        self.team1_colour = (144, 167, 255)
        self.team2_colour = (255, 114, 114)
        self.font = pygame.font.SysFont("helvetica", 12)
        self.pos = pos
        self.image = image
        self.image_width = self.image.get_width()
        self.image_height = self.image.get_height()
        self.rect = self.image.get_rect(topleft=pos)

    def change_fight_scale(self, troop_number_list):
        new_percent = round(troop_number_list[1] / (troop_number_list[1] + troop_number_list[2]), 4)
        if self.percent_scale != new_percent:
            self.percent_scale = new_percent
            self.image.fill(self.team1_colour, (0, 0, self.image_width, self.image_height))
            self.image.fill(self.team2_colour, (self.image_width * self.percent_scale, 0, self.image_width, self.image_height))

            team1_text = self.font.render("{:,}".format(troop_number_list[1] - 1), True, (0, 0, 0))  # add troop number text
            team1_text_rect = team1_text.get_rect(topleft=(0, 0))
            self.image.blit(team1_text, team1_text_rect)
            team2_text = self.font.render("{:,}".format(troop_number_list[2] - 1), True, (0, 0, 0))
            team2_text_rect = team2_text.get_rect(topright=(self.image_width, 0))
            self.image.blit(team2_text, team2_text_rect)


class SpeedNumber(pygame.sprite.Sprite):
    def __init__(self, pos, speed, text_size=20):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", text_size)
        self.pos = pos
        self.image = pygame.Surface((50, 30), pygame.SRCALPHA)
        self.image_original = self.image.copy()
        self.speed = speed
        self.timer_surface = self.font.render(str(self.speed), True, (0, 0, 0))
        self.timer_rect = self.timer_surface.get_rect(topleft=(3, 3))
        self.image.blit(self.timer_surface, self.timer_rect)
        self.rect = self.image.get_rect(center=pos)

    def speed_update(self, new_speed):
        """change speed number text"""
        self.image = self.image_original.copy()
        self.speed = new_speed
        self.timer_surface = self.font.render(str(self.speed), True, (0, 0, 0))
        self.image.blit(self.timer_surface, self.timer_rect)


class InspectSubunit(pygame.sprite.Sprite):
    def __init__(self, pos):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.who = None
        self.image = pygame.Surface((1, 1))
        self.rect = self.image.get_rect(topleft=self.pos)

    def add_subunit(self, who):
        self.who = who
        self.image = self.who.imageblock
        self.rect = self.image.get_rect(topleft=self.pos)

    def delete(self):
        self.who = None


class BattleDone(pygame.sprite.Sprite):
    def __init__(self, screen_scale, pos, box_image, result_image):
        self._layer = 18
        pygame.sprite.Sprite.__init__(self)
        self.screen_scale = screen_scale
        self.box_image = box_image
        self.result_image = result_image
        self.font = pygame.font.SysFont("oldenglishtext", int(self.screen_scale[1] * 36))
        self.text_font = pygame.font.SysFont("timesnewroman", int(self.screen_scale[1] * 24))
        self.pos = pos
        self.image = self.box_image.copy()
        self.rect = self.image.get_rect(center=self.pos)
        self.winner = None

    def pop(self, winner):
        self.winner = winner
        self.image = self.box_image.copy()
        text_surface = self.font.render(self.winner, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, int(self.screen_scale[1] * 36) + 3))
        self.image.blit(text_surface, text_rect)
        if self.winner != "Draw":
            text_surface = self.font.render("Victory", True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, int(self.screen_scale[1] * 36) * 2))
            self.image.blit(text_surface, text_rect)
        self.rect = self.image.get_rect(center=self.pos)

    def show_result(self, team1_coa, team2_coa, stat):
        self.image = self.result_image.copy()
        text_surface = self.font.render(self.winner, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, int(self.height_adjust * 36) + 3))
        self.image.blit(text_surface, text_rect)
        if self.winner != "Draw":
            text_surface = self.font.render("Victory", True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(self.image.get_width() / 2, int(self.height_adjust * 36) * 2))
            self.image.blit(text_surface, text_rect)
        coa1_rect = team1_coa.get_rect(center=(self.image.get_width() / 3, int(self.height_adjust * 36) * 5))
        coa2_rect = team2_coa.get_rect(center=(self.image.get_width() / 1.5, int(self.height_adjust * 36) * 5))
        self.image.blit(team1_coa, coa1_rect)
        self.image.blit(team2_coa, coa2_rect)
        self.rect = self.image.get_rect(center=self.pos)
        team_coa_rect = (coa1_rect, coa2_rect)
        text_header = ("Total Troop: ", "Remaining: ", "Injured: ", "Death: ", "Flee: ", "Captured: ")
        for index, team in enumerate([1, 2]):
            row_number = 1
            for stat_index, this_stat in enumerate(stat):
                if stat_index == 1:
                    text_surface = self.font.render(text_header[stat_index] + str(this_stat[team] - 1), True, (0, 0, 0))
                else:
                    text_surface = self.font.render(text_header[stat_index] + str(this_stat[team]), True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=(team_coa_rect[index].midbottom[0],
                                                        team_coa_rect[index].midbottom[1] + (int(self.height_adjust * 25) * row_number)))
                self.image.blit(text_surface, text_rect)
                row_number += 1
