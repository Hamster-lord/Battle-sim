import random
import numpy as np

battle_side_cal = (1, 0.5, 0.1, 0.5)  # battle_side_cal is for melee combat side modifier
infinity = float("inf")

def change_leader(self, event):
    """Leader is subunit in arcode mode, so can't change to other subunit"""
    pass


def swap_equipment(self, new_weapon):
    """Swap weapon, reset base stat"""
    self.base_melee_def = self.original_melee_def
    self.base_range_def = self.original_range_def
    self.skill = self.original_skill
    self.trait = self.original_trait

    self.base_melee_def += self.weapon_list.weapon_list[new_weapon]["Defense"]
    self.base_range_def += self.weapon_list.weapon_list[new_weapon]["Defense"]

    self.skill += self.weapon_list.weapon_list[new_weapon]["Skill"]
    self.trait += self.weapon_list.weapon_list[new_weapon]["Trait"]

    self.trait = list(set([trait for trait in self.trait if trait != 0]))  # remove empty and duplicate traits
    if len(self.trait) > 0:
        self.trait = {x: self.stat_list.trait_list[x] for x in self.trait if
                      x in self.stat_list.trait_list}  # Any trait not available in ruleset will be ignored
        self.add_trait()

    self.skill = {x: self.stat_list.skill_list[x].copy() for x in self.skill if
                  x != 0 and x in self.stat_list.skill_list}  # grab skill stat into dict
    for skill in list(self.skill.keys()):  # remove skill if class mismatch
        skill_troop_cond = self.skill[skill]["Troop Type"]
        if skill_troop_cond == 0 or (self.subunit_type == 2 and skill_troop_cond == 2) or (self.subunit_type != 2 and skill_troop_cond != 2):
            pass
        else:
            self.skill.pop(skill)

def complex_dmg_cal(attacker, defender, hit, defence, dmg_type, def_side=None):
    """Calculate dmg, type 0 is melee melee_attack and will use attacker subunit stat,
    type that is not 0 will use the type object stat instead (mostly used for range melee_attack)"""
    who = attacker
    target = defender

    height_advantage = who.height - target.height
    if dmg_type != 0:
        height_advantage = int(height_advantage / 2)  # Range melee_attack use less height advantage
    hit += height_advantage

    if defence < 0 or who.ignore_def:  # Ignore def trait
        defence = 0

    hit_chance = hit - defence
    if hit_chance < 0:
        hit_chance = 0
    elif hit_chance > 80:  # Critical hit
        hit_chance *= who.crit_effect  # modify with crit effect further
        if hit_chance > 200:
            hit_chance = 200
    else:  # infinity number can cause nan value
        hit_chance = 200

    combat_score = round(hit_chance / 100, 1)
    if combat_score == 0 and random.randint(0, 10) > 9:  # Final chance to not miss
        combat_score = 0.1

    if combat_score > 0:
        if dmg_type == 0:  # Melee melee_dmg
            dmg = random.uniform(who.melee_dmg[0], who.melee_dmg[1])
            if who.charge_skill in who.skill_effect:  # Include charge in melee_dmg if attacking
                if who.ignore_charge_def is False:  # Ignore charge defence if have ignore trait
                    side_cal = battle_side_cal[def_side]
                    if target.full_def or target.temp_full_def:  # defence all side
                        side_cal = 1
                    dmg = dmg + ((who.charge - (target.charge_def * side_cal)) * 2)
                    if (target.charge_def * side_cal) >= who.charge / 2:
                        who.charge_momentum = 1  # charge get stopped by charge def
                    else:
                        who.charge_momentum -= (target.charge_def * side_cal) / who.charge
                else:
                    dmg = dmg + (who.charge * 2)
                    who.charge_momentum -= 1 / who.charge

            if target.charge_skill in target.skill_effect:  # Also include charge_def in melee_dmg if enemy charging
                if target.ignore_charge_def is False:
                    charge_def_cal = who.charge_def - target.charge
                    if charge_def_cal < 0:
                        charge_def_cal = 0
                    dmg = dmg + (charge_def_cal * 2)  # if charge def is higher than enemy charge then deal back additional melee_dmg
            elif who.charge_skill not in who.skill_effect:  # not charging or defend from charge, use melee_attack speed roll
                dmg += sum([random.uniform(who.melee_dmg[0], who.melee_dmg[1]) for x in range(who.weapon_speed)])

            penetrate = who.melee_penetrate / target.armour
            if penetrate > 1:
                penetrate = 1
            dmg = dmg * penetrate * combat_score

        else:  # Range Damage
            penetrate = dmg_type.penetrate / target.armour
            if penetrate > 1:
                penetrate = 1
            dmg = dmg_type.dmg * penetrate * combat_score

        unit_dmg = dmg * who.troop_number  # dmg on subunit is dmg multiply by troop number  # TODO change later
        if (who.anti_inf and target.subunit_type in (1, 2)) or (who.anti_cav and target.subunit_type in (4, 5, 6, 7)):  # Anti trait dmg bonus
            unit_dmg = unit_dmg * 1.25

        morale_dmg = dmg / 50

        # Damage cannot be negative (it would heal instead), same for morale dmg
        if unit_dmg < 0:
            unit_dmg = 0
        if morale_dmg < 0:
            morale_dmg = 0
    else:  # complete miss
        unit_dmg = 0
        morale_dmg = 0

    return unit_dmg, morale_dmg


def loss_cal(attacker, receiver, dmg, morale_dmg, dmg_effect, timer_mod):
    final_dmg = round(dmg * dmg_effect * timer_mod)
    final_morale_dmg = round(morale_dmg * dmg_effect * timer_mod)
    if final_dmg > receiver.unit_health:  # dmg cannot be higher than remaining health
        final_dmg = receiver.unit_health

    receiver.unit_health -= final_dmg
    health_check = 0.1
    if receiver.max_health != infinity:
        health_check = 1 - (receiver.unit_health / receiver.max_health)
    receiver.base_morale -= (final_morale_dmg + attacker.bonus_morale_dmg) * receiver.mental * health_check
    receiver.stamina -= attacker.bonus_stamina_dmg

    # v Add red corner to indicate combat
    if receiver.red_border is False:
        receiver.block.blit(receiver.unit_ui_images["ui_squad_combat.png"], receiver.corner_image_rect)
        receiver.red_border = True
    # ^ End red corner

    if attacker.elem_melee not in (0, 5):  # apply element effect if atk has element, except 0 physical, 5 magic
        receiver.elem_count[attacker.elem_melee - 1] += round(final_dmg * (100 - receiver.elem_res[attacker.elem_melee - 1] / 100))

    attacker.base_morale += round((final_morale_dmg / 5))  # recover some morale when deal morale dmg to enemy


def dmg_cal(attacker, target, attacker_side, target_side, status_list, combat_timer):
    """base_target position 0 = Front, 1 = Side, 3 = Rear, attacker_side and target_side is the side attacking and defending respectively"""
    who_luck = random.randint(-50, 50)  # attacker luck
    target_luck = random.randint(-50, 50)  # defender luck
    who_mod = battle_side_cal[attacker_side]  # attacker melee_attack side modifier

    """34 battlemaster full_def or 91 allrounddef status = no flanked penalty"""
    if attacker.full_def or 91 in attacker.status_effect:
        who_mod = 1
    target_percent = battle_side_cal[target_side]  # defender defend side

    if target.full_def or 91 in target.status_effect:
        target_percent = 1

    dmg_effect = attacker.front_dmg_effect
    target_dmg_effect = target.front_dmg_effect

    if attacker_side != 0 and who_mod != 1:  # if melee_attack or defend from side will use discipline to help reduce penalty a bit
        who_mod = battle_side_cal[attacker_side] + (attacker.discipline / 300)
        dmg_effect = attacker.side_dmg_effect  # use side dmg effect as some skill boost only front dmg
        if who_mod > 1:
            who_mod = 1

    if target_side != 0 and target_percent != 1:  # same for the base_target defender
        target_percent = battle_side_cal[target_side] + (target.discipline / 300)
        target_dmg_effect = target.side_dmg_effect
        if target_percent > 1:
            target_percent = 1

    who_hit = float(attacker.melee_attack * who_mod) + who_luck
    target_defence = float(target.melee_def * target_percent) + target_luck

    """backstabber ignore def when melee_attack rear side, Oblivious To Unexpected can't defend from rear at all"""
    if (attacker.backstab and target_side == 2) or (target.oblivious and target_side == 2) or (
            target.flanker and attacker_side in (1, 3)):  # Apply only for attacker
        target_defence = 0

    who_dmg, who_morale_dmg = complex_dmg_cal(attacker, target, who_hit, target_defence, 0, target_side)  # get dmg by attacker

    timer_mod = combat_timer / 0.5  # Since the update happen anytime more than 0.5 second, high speed that pass by longer than x1 speed will become inconsistent
    loss_cal(attacker, target, who_dmg, who_morale_dmg, dmg_effect, timer_mod)  # Inflict dmg to defender

    if target.reflect:
        target_dmg = who_dmg / 10
        target_morale_dmg = who_dmg / 50
        if target.full_reflect:
            target_dmg = who_dmg
            target_morale_dmg = who_dmg / 10
        loss_cal(target, attacker, target_dmg, target_morale_dmg, target_dmg_effect, timer_mod)  # Inflict dmg to attacker

    # v Attack corner (side) of self with aoe melee_attack
    if attacker.corner_atk:
        loop_list = [target.nearby_subunit_list[2], target.nearby_subunit_list[5]]  # Side melee_attack get (2) front and (5) rear nearby subunit
        if target_side in (0, 2):
            loop_list = target.nearby_subunit_list[0:2]  # Front/rear melee_attack get (0) left and (1) right nearby subunit
        for this_subunit in loop_list:
            if this_subunit != 0 and this_subunit.state != 100:
                target_hit, target_defence = float(attacker.melee_attack * target_percent) + target_luck, float(
                    this_subunit.melee_def * target_percent) + target_luck
                who_dmg, who_morale_dmg = complex_dmg_cal(attacker, this_subunit, who_hit, target_defence, 0)
                loss_cal(attacker, this_subunit, who_dmg, who_morale_dmg, dmg_effect, timer_mod)
    # ^ End melee_attack corner

    # Inflict status based on aoe 1 = front only 2 = all 4 side, 3 corner enemy subunit, 4 entire unit
    if attacker.inflict_status != {}:
        apply_status_to_enemy(status_list, attacker.inflict_status, target, attacker_side, target_side)


def apply_status_to_enemy(status_list, inflict_status, receiver, attacker_side, receiver_side):
    """apply aoe status effect to enemy subunits"""
    for status in inflict_status.items():
        if status[1] == 1 and attacker_side == 0:  # only front enemy
            receiver.status_effect[status[0]] = status_list[status[0]].copy()
        elif status[1] == 2:  # aoe effect to side enemy
            receiver.status_effect[status[0]] = status_list[status[0]].copy()
            if status[1] == 3:  # apply to corner enemy subunit (left and right of self front enemy subunit)
                corner_enemy_apply = receiver.nearby_subunit_list[0:2]
                if receiver_side in (1, 2):  # melee_attack on left/right side means corner enemy would be from front and rear side of the enemy
                    corner_enemy_apply = [receiver.nearby_subunit_list[2], receiver.nearby_subunit_list[5]]
                for this_subunit in corner_enemy_apply:
                    if this_subunit != 0:
                        this_subunit.status_effect[status[0]] = status_list[status[0]].copy()
        elif status[1] == 3:  # whole unit aoe
            for this_subunit in receiver.unit.subunit_sprite:
                if this_subunit.state != 100:
                    this_subunit.status_effect[status[0]] = status_list[status[0]].copy()


def die(self):
    self.image_original3.blit(self.health_image_list[5], self.health_image_rect)  # blit white hp bar
    self.block_original.blit(self.health_image_rect[5], self.health_block_rect)
    self.zoom_scale()
    self.last_health_state = 0
    self.skill_cooldown = {}  # remove all cooldown
    self.skill_effect = {}  # remove all skill effects

    self.block.blit(self.block_original, self.corner_image_rect)
    self.red_border = True  # to prevent red border appear when dead

    self.unit.dead_change = True

    if self in self.battle.battle_camera:
        self.battle.battle_camera.change_layer(sprite=self, new_layer=1)
    self.battle.all_subunit_list.remove(self)
    self.unit.subunit_sprite.remove(self)

    for subunit in self.unit.subunit_list.flat:  # remove from index array
        if subunit == self.game_id:
            self.unit.subunit_list = np.where(self.unit.subunit_list == self.game_id, 0, self.unit.subunit_list)
            break

    self.change_leader("destroyed")

    self.battle.event_log.add_log([0, str(self.board_pos) + " " + str(self.name)
                                   + " in " + self.unit.leader[0].name
                                   + "'s unit is destroyed"], [3])  # add log to say this subunit is destroyed in subunit tab