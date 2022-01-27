import csv
import os
import pygame
from pathlib import Path

from gamescript import weather, battleui, lorebook, menu, uniteditor, readstat, popup, map
from gamescript.common import utility

load_image = utility.load_image
load_images = utility.load_images
csv_read = utility.csv_read
make_bar_list = utility.make_bar_list

def read_terrain_data(main_dir):
    """Read map data and create map texture and their default variables"""
    # read terrain feature list
    feature_list = []
    with open(os.path.join(main_dir, "data", "map", "unit_terrainbonus.csv"), encoding="utf-8", mode="r") as edit_file:
        rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
        for row in rd:
            feature_list.append(row[1])  # get terrain feature combination name for folder
    edit_file.close()
    feature_list = feature_list[1:]

    empty_image = load_image(main_dir, (1, 1), "empty.png", "map/texture")  # empty texture image
    map_texture = []
    texture_folder = [item for item in feature_list if item != ""]  # For now remove terrain with no planned name/folder yet
    for index, folder in enumerate(texture_folder):
        images = load_images(main_dir, (1, 1), ["map", "texture", folder], load_order=False)
        map_texture.append(list(images.values()))

    # read terrain feature mode
    feature_mod = {}
    with open(os.path.join(main_dir, "data", "map", "unit_terrainbonus.csv"), encoding="utf-8", mode="r") as edit_file:
        rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
        run = 0  # for skipping the first row
        for row in rd:
            for n, i in enumerate(row):
                if run != 0:
                    if n == 12:  # effect list is at column 12
                        if "," in i:
                            row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]
                        elif i.isdigit():
                            row[n] = [int(i)]

                    elif n in (2, 3, 4, 5, 6, 7):  # other modifer column
                        if i != "":
                            row[n] = float(i) / 100
                        else:  # empty row assign 1.0 default
                            row[n] = 1.0

                    elif i.isdigit() or "-" in i:  # modifer bonus (including negative) in other column
                        row[n] = int(i)

            run += 1
            feature_mod[row[0]] = row[1:]
    edit_file.close()

    # set up default
    map.FeatureMap.main_dir = main_dir
    map.FeatureMap.feature_mod = feature_mod
    map.BeautifulMap.main_dir = main_dir

    map.BeautifulMap.texture_images = map_texture
    map.BeautifulMap.load_texture_list = texture_folder
    map.BeautifulMap.empty_image = empty_image

    return feature_mod, feature_list


def read_weather_data(main_dir, screen_scale):
    """Create weather related class"""
    all_weather = csv_read(main_dir, "weather.csv", ["data", "map", "weather"])
    weather_list = [item[0] for item in all_weather.values()][2:]
    strength_list = ["Light ", "Normal ", "Strong "]
    new_weather_list = []
    for item in weather_list:  # list of weather with different strength
        for strength in strength_list:
            new_weather_list.append(strength + item)

    weather_matter_images = []
    for weather_sprite in weather_list:  # Load weather matter sprite image
        try:
            images = load_images(main_dir, screen_scale, ["map", "weather", "matter", weather_sprite], load_order=False)
            weather_matter_images.append(list(images.values()))
        except FileNotFoundError:
            weather_matter_images.append([])

    weather_effect_images = []
    for weather_effect in weather_list:  # Load weather effect sprite image
        try:
            images = load_images(main_dir, screen_scale, ["map", "weather", "effect", weather_effect], load_order=False)
            weather_effect_images.append(list(images.values()))
        except FileNotFoundError:
            weather_effect_images.append([])

    weather_icon_list = load_images(main_dir, screen_scale, ["map", "weather", "icon"], load_order=False)  # Load weather icon
    new_weather_icon = []
    for weather_icon in weather_list:
        for strength in range(0, 3):
            new_name = weather_icon + "_" + str(strength) + ".png"
            for item in weather_icon_list:
                if new_name == item:
                    new_weather_icon.append(weather_icon_list[item])
                    break

    weather.Weather.images = new_weather_icon
    return all_weather, new_weather_list, weather_matter_images, weather_effect_images


def read_map_data(main_dir, ruleset_folder):

    # Load map list
    read_folder = Path(os.path.join(main_dir, "data", "ruleset", ruleset_folder, "map"))
    subdirectories = [x for x in read_folder.iterdir() if x.is_dir()]

    for index, file_map in enumerate(subdirectories):
        if "custom" in str(file_map):  # remove custom from this folder list to load
            subdirectories.pop(index)
            break

    preset_map_list = []  # map name list for map selection list
    preset_map_folder = []  # folder for reading later

    for file_map in subdirectories:
        preset_map_folder.append(str(file_map).split("\\")[-1])
        with open(os.path.join(str(file_map), "info.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            for row in rd:
                if row[0] != "name":
                    preset_map_list.append(row[0])
        edit_file.close()

    # Load custom map list
    read_folder = Path(os.path.join(main_dir, "data", "ruleset", ruleset_folder, "map", "custom"))
    subdirectories = [x for x in read_folder.iterdir() if x.is_dir()]

    custom_map_list = []
    custom_map_folder = []

    for file_map in subdirectories:
        custom_map_folder.append(str(file_map).split("\\")[-1])
        with open(os.path.join(str(file_map), "info.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            for row in rd:
                if row[0] != "name":
                    custom_map_list.append(row[0])
        edit_file.close()

    return preset_map_list, preset_map_folder, custom_map_list, custom_map_folder


def read_faction_data(main_dir, screen_scale, ruleset_folder):
    readstat.FactionStat.main_dir = main_dir
    all_faction = readstat.FactionStat(option=ruleset_folder)
    images_old = load_images(main_dir, screen_scale, ["ruleset", ruleset_folder, "faction", "coa"],
                           load_order=False)  # coa_list images list
    coa_list = []
    for image in images_old:
        coa_list.append(images_old[image])
    faction_list = [item["Name"] for item in all_faction.faction_list.values()][1:]
    return all_faction, coa_list, faction_list


def make_encyclopedia_ui(main_dir, ruleset_folder, screen_scale, screen_rect):
    """Create Encyclopedia related objects"""
    lorebook.Lorebook.concept_stat = csv_read(main_dir, "concept_stat.csv", ["data", "ruleset", ruleset_folder, "lore"])
    lorebook.Lorebook.concept_lore = csv_read(main_dir, "concept_lore.csv", ["data", "ruleset", ruleset_folder, "lore"])
    lorebook.Lorebook.history_stat = csv_read(main_dir, "history_stat.csv", ["data", "ruleset", ruleset_folder, "lore"])
    lorebook.Lorebook.history_lore = csv_read(main_dir, "history_lore.csv", ["data", "ruleset", ruleset_folder, "lore"])

    encyclopedia_images = load_images(main_dir, screen_scale, ["ui", "lorebook_ui"], load_order=False)
    encyclopedia = lorebook.Lorebook(main_dir, screen_scale, screen_rect, encyclopedia_images["encyclopedia.png"])  # encyclopedia sprite
    lore_name_list = lorebook.SubsectionList(screen_scale, encyclopedia.rect.topleft, encyclopedia_images["section_list.png"])

    lore_button_images = load_images(main_dir, screen_scale, ["ui", "lorebook_ui", "button"], load_order=False)
    for image in lore_button_images:  # scale button image
        lore_button_images[image] = pygame.transform.scale(lore_button_images[image], (int(lore_button_images[image].get_width() * screen_scale[0]),
                                                   int(lore_button_images[image].get_height() * screen_scale[1])))
    lore_button_ui = [battleui.UIButton(lore_button_images["concept.png"], 0, 13),  # concept section button
                      battleui.UIButton(lore_button_images["history.png"], 1, 13),  # history section button
                      battleui.UIButton(lore_button_images["faction.png"], 2, 13),  # faction section button
                      battleui.UIButton(lore_button_images["troop.png"], 3, 13),  # troop section button
                      battleui.UIButton(lore_button_images["equipment.png"], 4, 13),  # troop equipment section button
                      battleui.UIButton(lore_button_images["status.png"], 5, 13),  # troop status section button
                      battleui.UIButton(lore_button_images["skill.png"], 6, 13),  # troop skill section button
                      battleui.UIButton(lore_button_images["property.png"], 7, 13),  # troop property section button
                      battleui.UIButton(lore_button_images["leader.png"], 8, 13),  # leader section button
                      battleui.UIButton(lore_button_images["terrain.png"], 9, 13),  # terrain section button
                      battleui.UIButton(lore_button_images["weather.png"], 10, 13),  # weather section button
                      battleui.UIButton(lore_button_images["close.png"], "close", 13),  # close button
                      battleui.UIButton(lore_button_images["previous.png"], "previous", 24),  # previous page button
                      battleui.UIButton(lore_button_images["next.png"], "next", 24)]  # next page button

    lore_button_ui[0].change_pos((encyclopedia.rect.topleft[0] + (lore_button_images["concept.png"].get_width() / 2),
                                  encyclopedia.rect.topleft[1] - (lore_button_images["concept.png"].get_height() / 2)))
    lore_button_ui[1].change_pos((encyclopedia.rect.topleft[0] + (lore_button_images["concept.png"].get_width() * 1.1) * 1.5,
                                  encyclopedia.rect.topleft[1] - (lore_button_images["concept.png"].get_height() / 2)))
    lore_button_ui[2].change_pos((encyclopedia.rect.topleft[0] + (lore_button_images["concept.png"].get_width() * 1.1) * 2.5,
                                  encyclopedia.rect.topleft[1] - (lore_button_images["concept.png"].get_height() / 2)))
    lore_button_ui[3].change_pos((encyclopedia.rect.topleft[0] + (lore_button_images["concept.png"].get_width() * 1.1) * 3.5,
                                  encyclopedia.rect.topleft[1] - (lore_button_images["concept.png"].get_height() / 2)))
    lore_button_ui[4].change_pos((encyclopedia.rect.topleft[0] + (lore_button_images["concept.png"].get_width() * 1.1) * 4.5,
                                  encyclopedia.rect.topleft[1] - (lore_button_images["concept.png"].get_height() / 2)))
    lore_button_ui[5].change_pos((encyclopedia.rect.topleft[0] + (lore_button_images["concept.png"].get_width() * 1.1) * 5.5,
                                  encyclopedia.rect.topleft[1] - (lore_button_images["concept.png"].get_height() / 2)))
    lore_button_ui[6].change_pos((encyclopedia.rect.topleft[0] + (lore_button_images["concept.png"].get_width() * 1.1) * 6.5,
                                  encyclopedia.rect.topleft[1] - (lore_button_images["concept.png"].get_height() / 2)))
    lore_button_ui[7].change_pos((encyclopedia.rect.topleft[0] + (lore_button_images["concept.png"].get_width() * 1.1) * 7.5,
                                  encyclopedia.rect.topleft[1] - (lore_button_images["concept.png"].get_height() / 2)))
    lore_button_ui[8].change_pos((encyclopedia.rect.topleft[0] + (lore_button_images["concept.png"].get_width() * 1.1) * 8.5,
                                  encyclopedia.rect.topleft[1] - (lore_button_images["concept.png"].get_height() / 2)))
    lore_button_ui[9].change_pos((encyclopedia.rect.topleft[0] + (lore_button_images["concept.png"].get_width() * 1.1) * 9.5,
                                  encyclopedia.rect.topleft[1] - (lore_button_images["concept.png"].get_height() / 2)))
    lore_button_ui[10].change_pos((encyclopedia.rect.topleft[0] + (lore_button_images["concept.png"].get_width() * 1.1) * 10.5,
                                   encyclopedia.rect.topleft[1] - (lore_button_images["concept.png"].get_height() / 2)))
    lore_button_ui[11].change_pos((encyclopedia.rect.topleft[0] + (lore_button_images["concept.png"].get_width() * 1.1) * 11.5,
                                   encyclopedia.rect.topleft[1] - (lore_button_images["concept.png"].get_height() / 2)))
    lore_button_ui[12].change_pos((encyclopedia.rect.bottomleft[0] + (lore_button_images["previous.png"].get_width()),
                                   encyclopedia.rect.bottomleft[1] - lore_button_images["previous.png"].get_height()))
    lore_button_ui[13].change_pos((encyclopedia.rect.bottomright[0] - (lore_button_images["next.png"].get_width()),
                                   encyclopedia.rect.bottomright[1] - lore_button_images["next.png"].get_height()))
    page_button = (lore_button_ui[12], lore_button_ui[13])
    lore_scroll = battleui.UIScroller(lore_name_list.rect.topright, lore_name_list.image.get_height(),
                                          encyclopedia.max_subsection_show, layer=25)  # add subsection list scroller

    return encyclopedia, lore_name_list, lore_button_ui, page_button, lore_scroll


def make_time_ui(battle_ui_image):
    time_ui = battleui.TimeUI(battle_ui_image["timebar.png"])
    time_number = battleui.Timer(time_ui.rect.topleft)  # time number on time ui
    speed_number = battleui.SpeedNumber(1)  # self speed number on the time ui

    image = pygame.Surface((battle_ui_image["timebar.png"].get_width(), 15))
    scale_ui = battleui.ScaleUI(image)

    time_button = [battleui.UIButton(battle_ui_image["pause.png"], "pause"),  # time pause button
                        battleui.UIButton(battle_ui_image["timedec.png"], "decrease"),  # time decrease button
                        battleui.UIButton(battle_ui_image["timeinc.png"], "increase")]  # time increase button
    return {"time_ui": time_ui, "time_number": time_number, "speed_number": speed_number, "scale_ui": scale_ui, "time_button": time_button}


def make_editor_ui(main_dir, screen_scale, screen_rect, listbox_image, image_list, scale_ui, colour):
    """Create army editor ui and button"""

    bottom_height = screen_rect.height - image_list[0].get_height()
    box_image = load_image(main_dir, screen_scale, "unit_presetbox.png", "ui\\mainmenu_ui")
    unit_listbox = menu.ListBox(screen_scale, (0, screen_rect.height / 2.2),
                                box_image)  # box for showing unit preset list
    unit_preset_name_scroll = battleui.UIScroller(unit_listbox.rect.topright, unit_listbox.image.get_height(),
                                                 unit_listbox.max_show, layer=14)  # preset name scroll
    preset_select_border = uniteditor.SelectedPresetBorder(unit_listbox.image.get_width() - int(15 * screen_scale[0]),
                                                           int(25 * screen_scale[1]))

    troop_listbox = menu.ListBox(screen_scale, (screen_rect.width / 1.19, 0), listbox_image)

    troop_scroll = battleui.UIScroller(troop_listbox.rect.topright, troop_listbox.image.get_height(),
                                       troop_listbox.max_show, layer=14)

    unit_delete_button = menu.MenuButton(screen_scale, image_list,
                                              pos=(image_list[0].get_width() / 2, bottom_height),
                                              text="Delete")
    unit_save_button = menu.MenuButton(screen_scale, image_list,
                                            pos=((screen_rect.width - (screen_rect.width - (image_list[0].get_width() * 1.7))),
                                                 bottom_height),
                                            text="Save")

    popup_listbox = menu.ListBox(screen_scale, (0, 0), box_image, 15)  # popup box need to be in higher layer
    popup_list_scroll = battleui.UIScroller(popup_listbox.rect.topright,
                                           popup_listbox.image.get_height(),
                                           popup_listbox.max_show,
                                           layer=14)

    box_image = load_image(main_dir, screen_scale, "map_change.png", "ui\\mainmenu_ui")
    terrain_change_button = menu.TextBox(screen_scale, box_image, (screen_rect.width / 3, screen_rect.height),
                                                                "Temperate")  # start with temperate terrain
    feature_change_button = menu.TextBox(screen_scale, box_image, (screen_rect.width / 2, screen_rect.height),
                                                                "Plain")  # start with plain feature
    weather_change_button = menu.TextBox(screen_scale, box_image, (screen_rect.width / 1.5, screen_rect.height),
                                                                "Light Sunny")  # start with light sunny
    box_image = load_image(main_dir, screen_scale, "filter_box.png", "ui\\mainmenu_ui")  # filter box ui in editor
    filter_box = uniteditor.FilterBox(screen_scale, (screen_rect.width / 2.5, 0), box_image)
    image1 = load_image(main_dir, screen_scale, "team1_button.png", "ui\\mainmenu_ui")  # change unit slot to team 1 in editor
    image2 = load_image(main_dir, screen_scale, "team2_button.png", "ui\\mainmenu_ui")  # change unit slot to team 2 in editor
    team_change_button = battleui.SwitchButton([image1, image2])
    team_change_button.change_pos((filter_box.rect.topleft[0] + 220, filter_box.rect.topleft[1] + 30))
    image1 = load_image(main_dir, screen_scale, "show_button.png", "ui\\mainmenu_ui")  # show unit slot ui in editor
    image2 = load_image(main_dir, screen_scale, "hide_button.png", "ui\\mainmenu_ui")  # hide unit slot ui in editor
    slot_display_button = battleui.SwitchButton([image1, image2])
    slot_display_button.change_pos((filter_box.rect.topleft[0] + 80, filter_box.rect.topleft[1] + 30))
    image1 = load_image(main_dir, screen_scale, "deploy_button.png",
                      "ui\\mainmenu_ui")  # deploy unit in unit slot to test map in editor
    deploy_button = battleui.UIButton(image1, 0)
    deploy_button.change_pos((filter_box.rect.topleft[0] + 150, filter_box.rect.topleft[1] + 90))
    image1 = load_image(main_dir, screen_scale, "test_button.png", "ui\\mainmenu_ui")  # start test button in editor
    image2 = load_image(main_dir, screen_scale, "end_button.png", "ui\\mainmenu_ui")  # stop test button
    test_button = battleui.SwitchButton([image1, image2])
    test_button.change_pos((scale_ui.rect.bottomleft[0] + 55, scale_ui.rect.bottomleft[1] + 25))  # TODO change later
    image1 = load_image(main_dir, screen_scale, "tick_box_no.png", "ui\\mainmenu_ui")  # start test button in editor
    image2 = load_image(main_dir, screen_scale, "tick_box_yes.png", "ui\\mainmenu_ui")  # stop test button
    filter_tick_box = [menu.TickBox(screen_scale, (filter_box.rect.bottomright[0] / 1.26,
                                                   filter_box.rect.bottomright[1] / 8), image1, image2, "meleeinf"),
                       menu.TickBox(screen_scale, (filter_box.rect.bottomright[0] / 1.26,
                                                   filter_box.rect.bottomright[1] / 1.7), image1, image2, "rangeinf"),
                       menu.TickBox(screen_scale, (filter_box.rect.bottomright[0] / 1.11,
                                                   filter_box.rect.bottomright[1] / 8), image1, image2, "meleecav"),
                       menu.TickBox(screen_scale, (filter_box.rect.bottomright[0] / 1.11,
                                                   filter_box.rect.bottomright[1] / 1.7), image1, image2, "rangecav")]
    warning_msg = uniteditor.WarningMsg(screen_scale, (test_button.rect.bottomleft[0], test_button.rect.bottomleft[1]))

    unit_build_slot = uniteditor.UnitBuildSlot(1, colour[0])

    return {"unit_listbox": unit_listbox, "unit_preset_name_scroll": unit_preset_name_scroll, "preset_select_border": preset_select_border,
            "troop_listbox": troop_listbox, "troop_scroll": troop_scroll, "unit_delete_button": unit_delete_button,
            "unit_save_button": unit_save_button, "popup_listbox": popup_listbox, "popup_list_scroll": popup_list_scroll,
            "terrain_change_button": terrain_change_button, "feature_change_button": feature_change_button,
            "weather_change_button": weather_change_button, "filter_box": filter_box, "team_change_button": team_change_button,
            "slot_display_button": slot_display_button, "deploy_button": deploy_button, "test_button": test_button,
            "filter_tick_box": filter_tick_box, "warning_msg": warning_msg, "unit_build_slot": unit_build_slot}


def make_input_box(main_dir, screen_scale, screen_rect, image_list):
    """Input box popup"""
    input_ui_image = load_image(main_dir, screen_scale, "input_ui.png", "ui\\mainmenu_ui")
    input_ui = menu.InputUI(screen_scale, input_ui_image,
                                 (screen_rect.width / 2, screen_rect.height / 2))  # user text input ui box popup
    input_ok_button = menu.MenuButton(screen_scale, image_list,
                                           pos=(input_ui.rect.midleft[0] + (image_list[0].get_width() / 1.2),
                                                input_ui.rect.midleft[1] + (image_list[0].get_height() / 1.3)),
                                           text="Confirm", layer=31)
    input_cancel_button = menu.MenuButton(screen_scale, image_list,
                                               pos=(input_ui.rect.midright[0] - (image_list[0].get_width() / 1.2),
                                                    input_ui.rect.midright[1] + (image_list[0].get_height() / 1.3)),
                                               text="Cancel", layer=31)

    input_box = menu.InputBox(screen_scale, input_ui.rect.center, input_ui.image.get_width())  # user text input box

    confirm_ui = menu.InputUI(screen_scale, input_ui_image,
                                   (screen_rect.width / 2, screen_rect.height / 2))  # user confirm input ui box popup

    return input_ui, input_ok_button, input_cancel_button, input_box, confirm_ui


def load_icon_data(main_dir, screen_scale):
    status_images = load_images(main_dir, screen_scale, ["ui", "status_icon"], load_order=False)
    role_images = load_images(main_dir, screen_scale, ["ui", "role_icon"], load_order=False)
    trait_images = load_images(main_dir, screen_scale, ["ui", "trait_icon"], load_order=False)
    skill_images = load_images(main_dir, screen_scale, ["ui", "skill_icon"], load_order=False)

    cooldown = pygame.Surface((skill_images["0.png"].get_width(), skill_images["0.png"].get_height()), pygame.SRCALPHA)
    cooldown.fill((230, 70, 80, 200))  # red colour filter for skill cooldown timer
    battleui.SkillCardIcon.cooldown = cooldown

    active_skill = pygame.Surface((skill_images["0.png"].get_width(), skill_images["0.png"].get_height()), pygame.SRCALPHA)
    active_skill.fill((170, 220, 77, 200))  # green colour filter for skill active timer
    battleui.SkillCardIcon.active_skill = active_skill

    return status_images, role_images, trait_images, skill_images

def load_battle_data(main_dir, screen_scale, ruleset, ruleset_folder):

    # v create subunit related class
    images = load_images(main_dir, screen_scale, ["ui", "unit_ui", "weapon"])
    for image in images:
        x, y = images[image].get_width(), images[image].get_height()
        images[image] = pygame.transform.scale(images[image],
                                     (int(x / 1.7), int(y / 1.7)))  # scale 1.7 seem to be most fitting as a placeholder
    all_weapon = readstat.WeaponStat(main_dir, images, ruleset)  # Create weapon class

    images = load_images(main_dir, screen_scale, ["ui", "unit_ui", "armour"])
    all_armour = readstat.ArmourStat(main_dir, images, ruleset)  # Create armour class
    troop_data = readstat.UnitStat(main_dir, ruleset, ruleset_folder)

    # v create leader list
    images, order = load_images(main_dir, screen_scale, ["ruleset", ruleset_folder, "leader", "portrait"], load_order=False,
                              return_order=True)
    leader_stat = readstat.LeaderStat(main_dir, images, order, option=ruleset_folder)
    # ^ End leader
    return all_weapon, all_armour, troop_data, leader_stat

def make_event_log(battle_ui_image, screen_rect):
    event_log = battleui.EventLog(battle_ui_image["event_log.png"], (0, screen_rect.height))
    troop_log_button = battleui.UIButton(battle_ui_image["event_log_button1.png"], 0)  # war tab log

    event_log_button = [
        battleui.UIButton(battle_ui_image["event_log_button2.png"], 1), # army tab log button
        battleui.UIButton(battle_ui_image["event_log_button3.png"], 2),  # leader tab log button
        battleui.UIButton(battle_ui_image["event_log_button4.png"], 3), # subunit tab log button
        battleui.UIButton(battle_ui_image["event_log_button5.png"], 4), # delete current tab log button
        battleui.UIButton(battle_ui_image["event_log_button6.png"], 5)] # delete all log button

    event_log_button = [troop_log_button] + event_log_button
    log_scroll = battleui.UIScroller(event_log.rect.topright, battle_ui_image["event_log.png"].get_height(),
                                          event_log.max_row_show)  # event log scroller
    event_log.log_scroll = log_scroll  # Link scroller to ui since it is easier to do here with the current order

    return event_log, troop_log_button, event_log_button, log_scroll

def make_esc_menu(main_dir, screen_rect, screen_scale, mixer_volume):
    """create Esc menu related objects"""
    menu.EscBox.images = load_images(main_dir, screen_scale, ["ui", "battlemenu_ui"], load_order=False)  # Create ESC Menu box
    menu.EscBox.screen_rect = screen_rect
    battle_menu = menu.EscBox()

    button_image = load_images(main_dir, screen_scale, ["ui", "battlemenu_ui", "button"], load_order=False)
    menu_rect_center0 = battle_menu.rect.center[0]
    menu_rect_center1 = battle_menu.rect.center[1]

    battle_menu_button = [
        menu.EscButton(button_image, (menu_rect_center0, menu_rect_center1 - 100), text="Resume", size=14),
        menu.EscButton(button_image, (menu_rect_center0, menu_rect_center1 - 50), text="Encyclopedia", size=14),
        menu.EscButton(button_image, (menu_rect_center0, menu_rect_center1), text="Option", size=14),
        menu.EscButton(button_image, (menu_rect_center0, menu_rect_center1 + 50), text="End Battle", size=14),
        menu.EscButton(button_image, (menu_rect_center0, menu_rect_center1 + 100), text="Desktop", size=14)]

    esc_option_menu_button = [
        menu.EscButton(button_image, (menu_rect_center0 - button_image["0.png"].get_width() * 1.5, menu_rect_center1 * 1.3), text="Confirm", size=14),
        menu.EscButton(button_image, (menu_rect_center0, menu_rect_center1 * 1.3), text="Apply", size=13),
        menu.EscButton(button_image, (menu_rect_center0 + button_image["0.png"].get_width() * 1.5, menu_rect_center1 * 1.3), text="Cancel", size=14)]

    esc_menu_images = load_images(main_dir, screen_scale, ["ui", "battlemenu_ui", "slider"], load_order=False)
    esc_slider_menu = [menu.SliderMenu([esc_menu_images["scroller_box.png"], esc_menu_images["scroller.png"]],
                                       [esc_menu_images["scoll_button_normal.png"], esc_menu_images["scoll_button_click.png"]],
                                       (menu_rect_center0, menu_rect_center1), mixer_volume, 0)]
    esc_value_box = [menu.ValueBox(esc_menu_images["value.png"], (battle_menu.rect.topright[0] * 1.08, menu_rect_center1), mixer_volume)]

    return {"battle_menu": battle_menu, "battle_menu_button": battle_menu_button, "esc_option_menu_button": esc_option_menu_button,
            "esc_slider_menu": esc_slider_menu, "esc_value_box": esc_value_box}


def make_popup_ui(main_dir, screen_rect, screen_scale, battle_ui_image):
    """Create Popup Ui"""
    popup.TerrainPopup.images = list(load_images(main_dir, screen_scale, ["ui", "popup_ui", "terrain_check"], load_order=False).values())
    popup.TerrainPopup.screen_rect = screen_rect

    troop_card_ui = battleui.TroopCard(image=battle_ui_image["troop_card.png"], icon="")

    # Button related to subunit card and command
    troop_card_button = [battleui.UIButton(battle_ui_image["troopcard_button1.png"], 0),  # subunit card description button
                         battleui.UIButton(battle_ui_image["troopcard_button2.png"], 1),  # subunit card stat button
                         battleui.UIButton(battle_ui_image["troopcard_button3.png"], 2),  # subunit card skill button
                         battleui.UIButton(battle_ui_image["troopcard_button4.png"], 3)]  # subunit card equipment button

    terrain_check = popup.TerrainPopup()  # popup box that show terrain information when right click on map
    button_name_popup = popup.OneLinePopup()  # popup box that show name when mouse over
    leader_popup = popup.OneLinePopup()  # popup box that show leader name when mouse over
    effect_popup = popup.EffectIconPopup()  # popup box that show skill/trait/status name when mouse over

    return troop_card_ui, troop_card_button, terrain_check, button_name_popup, terrain_check, button_name_popup, leader_popup, effect_popup


def load_option_menu(main_dir, screen_scale, screen_rect, screen_width, screen_height, image_list, mixer_volume):
    # v Create option menu button and icon
    back_button = menu.MenuButton(screen_scale, image_list, (screen_rect.width / 2, screen_rect.height / 1.2), text="BACK")

    # Resolution changing bar that fold out the list when clicked
    image = load_image(main_dir, screen_scale, "drop_normal.jpg", "ui\\mainmenu_ui")
    image2 = image
    image3 = load_image(main_dir, screen_scale, "drop_click.jpg", "ui\\mainmenu_ui")
    image_list = [image, image2, image3]
    resolution_drop = menu.MenuButton(screen_scale, image_list, (screen_rect.width / 2, screen_rect.height / 2.3),
                                             text=str(screen_width) + " x " + str(screen_height), size=30)
    resolution_list = ["1920 x 1080", "1600 x 900", "1366 x 768", "1280 x 720", "1024 x 768"]
    resolution_bar = make_bar_list(main_dir, screen_scale, list_to_do=resolution_list,
                                        menu_image=resolution_drop)
    image = load_image(main_dir, screen_scale, "resolution_icon.png", "ui\\mainmenu_ui")
    resolution_icon = menu.MenuIcon(image, (resolution_drop.pos[0] - (resolution_drop.pos[0] / 4.5), resolution_drop.pos[1]))
    # End resolution

    # Volume change scroll bar
    esc_menu_images = load_images(main_dir, screen_scale, ["ui", "battlemenu_ui", "slider"], load_order=False)
    volume_slider = menu.SliderMenu([esc_menu_images["scroller_box.png"], esc_menu_images["scroller.png"]],
                                    [esc_menu_images["scoll_button_normal.png"], esc_menu_images["scoll_button_click.png"]],
                                    (screen_rect.width / 2, screen_rect.height / 3), mixer_volume)
    value_box = [menu.ValueBox(esc_menu_images["value.png"], (volume_slider.rect.topright[0] * 1.1, volume_slider.rect.topright[1]),
                      mixer_volume)]

    image = load_image(main_dir, screen_scale, "volume_icon.png", "ui\\mainmenu_ui")
    volume_icon = menu.MenuIcon(image, (volume_slider.pos[0] - (volume_slider.pos[0] / 4.5), volume_slider.pos[1]))
    # End volume change
    return back_button, resolution_drop, resolution_bar, resolution_icon, volume_slider, value_box, volume_icon