import numpy as np

letter_board = ("a", "b", "c", "d", "e", "f", "g", "h")  # letter according to subunit position in inspect ui similar to chess board
number_board = ("8", "7", "6", "5", "4", "3", "2", "1")  # same as above
board_pos = []
for dd in number_board:
    for ll in letter_board:
        board_pos.append(ll + dd)

battle_side_cal = (1, 0.5, 0.1, 0.5)  # battle_side_cal is for melee combat side modifier


def add_unit(game_id, pos, subunit_list, colour, leader_list, leader_stat, control, coa, command, start_angle, start_hp, start_stamina,
             team):
    """Create unit object into the battle and leader of the unit"""
    from gamescript import unit, leader
    old_subunit_list = subunit_list[~np.all(subunit_list == 0, axis=1)]  # remove whole empty column in subunit list
    subunit_list = old_subunit_list[:, ~np.all(old_subunit_list == 0, axis=0)]  # remove whole empty row in subunit list
    unit = unit.Unit(game_id, pos, subunit_list, colour, control, coa, command, abs(360 - start_angle), start_hp, start_stamina, team)

    # add leader
    unit.leader = [leader.Leader(leader_list[0], leader_list[4], 0, unit, leader_stat),
                   leader.Leader(leader_list[1], leader_list[5], 1, unit, leader_stat),
                   leader.Leader(leader_list[2], leader_list[6], 2, unit, leader_stat),
                   leader.Leader(leader_list[3], leader_list[7], 3, unit, leader_stat)]
    return unit


def generate_unit(self, which_army, setup_data, control, command, colour, coa, subunit_game_id, *args):
    """generate unit"""
    from gamescript import battleui, subunit
    this_unit = add_unit(setup_data["ID"], setup_data["POS"],
                         np.array([setup_data["Row 1"], setup_data["Row 2"], setup_data["Row 3"], setup_data["Row 4"],
                                   setup_data["Row 5"], setup_data["Row 6"], setup_data["Row 7"], setup_data["Row 8"]]),
                         colour, setup_data["Leader"] + setup_data["Leader Position"], self.leader_data, control,
                         coa, command, setup_data["Angle"], setup_data["Start Health"], setup_data["Start Stamina"],
                         setup_data["Team"])
    which_army.add(this_unit)
    army_subunit_index = 0  # army_subunit_index is list index for subunit list in a specific army

    # v Setup subunit in unit to subunit group
    row, column = 0, 0
    max_column = len(this_unit.subunit_list[0])
    for subunit_number in np.nditer(this_unit.subunit_list, op_flags=["readwrite"], order="C"):
        if subunit_number != 0:
            add_subunit = subunit.Subunit(subunit_number, subunit_game_id, this_unit, this_unit.subunit_position_list[army_subunit_index],
                                          this_unit.start_hp, this_unit.start_stamina, self.unit_scale, self.genre)
            self.subunit.add(add_subunit)
            add_subunit.board_pos = board_pos[army_subunit_index]
            subunit_number[...] = subunit_game_id
            this_unit.subunits_array[row][column] = add_subunit
            this_unit.subunits.append(add_subunit)
            subunit_game_id += 1
        else:
            this_unit.subunits_array[row][column] = None  # replace numpy None with python None

        column += 1
        if column == max_column:
            column = 0
            row += 1
        army_subunit_index += 1
    self.troop_number_sprite.add(battleui.TroopNumber(self.screen_scale, this_unit))  # create troop number text sprite
    return subunit_game_id


def split_new_unit(self, who, add_unit_list=True):
    from gamescript import battleui
    # generate subunit sprite array for inspect ui
    who.subunits_array = np.empty((8, 8), dtype=object)  # array of subunit object(not index)
    found_count = 0  # for subunit_sprite index
    found_count2 = 0  # for positioning
    for row in range(0, len(who.subunit_list)):
        for column in range(0, len(who.subunit_list[0])):
            if who.subunit_list[row][column] != 0:
                who.subunits_array[row][column] = who.subunits[found_count]
                who.subunits[found_count].unit_position = (who.subunit_position_list[found_count2][0] / 10,
                                                           who.subunit_position_list[found_count2][1] / 10)  # position in unit sprite
                found_count += 1
            else:
                who.subunits_array[row][column] = None
            found_count2 += 1
    # ^ End generate subunit array

    for index, this_subunit in enumerate(who.subunits):  # reset leader subunit_pos
        if this_subunit.leader is not None:
            this_subunit.leader.subunit_pos = index

    who.zoom = 11 - self.camera_zoom
    who.new_angle = who.angle

    who.start_set(self.subunit)
    who.set_target(who.front_pos)

    number_pos = (who.base_pos[0] - who.base_width_box,
                  (who.base_pos[1] + who.base_height_box))
    who.number_pos = who.rotation_xy(who.base_pos, number_pos, who.radians_angle)
    who.change_pos_scale()  # find new position for troop number text

    for this_subunit in who.subunits:
        this_subunit.start_set(this_subunit.zoom)

    if add_unit_list:
        self.alive_unit_list.append(who)
        self.alive_unit_index.append(who.game_id)

    number_spite = battleui.TroopNumber(self.screen_scale, who)
    self.troop_number_sprite.add(number_spite)