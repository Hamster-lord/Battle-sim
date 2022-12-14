def swap_weapon(self):
    """Change weapon, adjust stat, trait and skill"""
    self.weapon_cooldown[0] = 0  # reset weapon attack cooldown time
    self.weapon_cooldown[1] = 0

    # Reset base stat first
    self.base_melee_attack = self.original_melee_attack
    self.base_melee_def = self.original_melee_def
    self.base_range_def = self.original_range_def
    self.base_speed = self.original_speed
    self.base_accuracy = self.original_accuracy
    self.base_sight = self.original_sight
    self.base_hidden = self.original_hidden
    self.base_reload = self.original_reload
    self.base_charge = self.original_charge
    self.base_charge_def = self.original_charge_def

    self.base_mana = self.original_mana
    self.base_morale = self.original_morale
    self.base_discipline = self.original_discipline
    self.base_hp_regen = self.original_hp_regen
    self.base_stamina_regen = self.original_stamina_regen
    self.base_morale_regen = self.original_morale_regen
    self.base_heat_resistance = self.original_heat_resistance
    self.base_cold_resistance = self.original_cold_resistance
    self.base_element_resistance = self.original_element_resistance.copy()
    self.base_mental = self.original_mental
    self.skill = self.original_skill

    self.equipped_weapon_data = self.weapon_data[self.equipped_weapon]

    for weapon_index, weapon in enumerate(((self.primary_main_weapon, self.primary_sub_weapon),
                                            (self.secondary_main_weapon, self.secondary_sub_weapon))[self.equipped_weapon]):
        weapon_stat = self.equipped_weapon_data[weapon_index]
        self.base_melee_def += weapon_stat["Defence"] * self.troop_data.equipment_grade_list[weapon[1]]["Modifier"]
        self.base_range_def += weapon_stat["Defence"] * self.troop_data.equipment_grade_list[weapon[1]]["Modifier"]
        skill = self.weapon_skill[self.equipped_weapon][weapon_index]
        if skill != 0 and (self.troop_data.skill_list[skill]["Troop Type"] != 0 and
                           self.troop_data.skill_list[skill]["Troop Type"] != self.subunit_type + 1):
            self.weapon_skill[self.equipped_weapon][weapon_index] = 0  # remove unmatch class skill
        else:
            self.skill.append(skill)

    self.process_trait_skill()

    self.action_list = []
    for item in self.equipped_weapon_data:
        self.action_list.append({key: value for key, value in item.items() if key in ("Common", "Attack", "Properties")})
