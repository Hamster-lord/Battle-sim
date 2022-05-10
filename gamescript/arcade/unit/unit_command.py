def process_command(self, target_pos, run_command=False, revert_move=False, enemy=None, other_command=None):
    """Process input order into state and subunit base_target action
    other_command parameter 0 is default command, 1 is natural pause, 2 is order pause"""
    if other_command is None:  # move
        self.state = 1

        if run_command:
            self.state += 1  # run state

        self.range_combat_check = False
        self.command_target = self.base_target
        if revert_move:  # revert subunit without rotate, cannot run in this state
            self.set_target(target_pos)
        else:  # rotate unit only
            self.new_angle = self.set_rotate(target_pos)
            self.set_subunit_target()
    elif type(other_command) == str:
        if "Skill" in other_command:
            for subunit in self.subunits:
                subunit.command_action = (other_command, )
            if "Charge" in other_command:  # also move when charge
                self.state = 4
                self.set_target(target_pos)

    self.command_state = self.state
