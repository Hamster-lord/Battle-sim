import datetime
import glob
import random
import sys

import main
import numpy as np
import pygame
import pygame.freetype
from gamescript import gamesubunit, gameunit, gameui, gameleader, gamecamera, gamelongscript, gameweather, gameprepare, gameunitedit, gamemap
from pygame.locals import *
from scipy.spatial import KDTree

config = main.config
SoundVolume = main.Soundvolume
SCREENRECT = main.SCREENRECT
main_dir = main.main_dir

load_image = gamelongscript.load_image
load_images = gamelongscript.load_images
csv_read = gamelongscript.csv_read
load_sound = gamelongscript.load_sound


class Battle:
    splitunit = gamelongscript.splitunit
    traitskillblit = gamelongscript.traitskillblit
    effecticonblit = gamelongscript.effecticonblit
    countdownskillicon = gamelongscript.countdownskillicon
    teamcolour = main.teamcolour

    def __init__(self, main, winstyle):
        # v Get game object/variable from main
        self.mode = None  # battle map mode can be "uniteditor" for unit editor or "battle" for game battle
        self.main = main
        self.widthadjust = main.widthadjust
        self.heightadjust = main.heightadjust
        self.eventlog = main.eventlog
        self.battlecamera = main.battlecamera
        self.battleui = main.battleui

        self.unit_updater = main.unit_updater
        self.subunit_updater = main.subunit_updater
        self.leader_updater = main.leader_updater
        self.uiupdater = main.ui_updater
        self.weather_updater = main.weather_updater
        self.effect_updater = main.effect_updater

        self.battlemap_base = main.battlemap_base
        self.battlemap_feature = main.battlemap_feature
        self.battlemap_height = main.battlemap_height
        self.showmap = main.showmap

        self.team0army = main.team0army
        self.team1army = main.team1army
        self.team2army = main.team2army
        self.team0subunit = main.team0subunit
        self.team1subunit = main.team1subunit
        self.team2subunit = main.team2subunit
        self.subunit = main.subunit
        self.armyleader = main.armyleader

        self.arrows = main.arrows
        self.directionarrows = main.directionarrows
        self.troopnumbersprite = main.troopnumbersprite

        self.gameui = main.gameui
        self.inspectuipos = main.inspectuipos
        self.inspectsubunit = main.inspectsubunit
        self.popgameui = main.gameui  # saving list of gameui that will pop out when parentunit is selected

        self.battlemap_base = main.battlemap_base
        self.battlemap_feature = main.battlemap_feature
        self.battlemap_height = main.battlemap_height
        self.showmap = main.showmap

        self.minimap = main.minimap
        self.eventlog = main.eventlog
        self.logscroll = main.logscroll
        self.buttonui = main.buttonui
        self.subunitselectedborder = main.inspectselectedborder
        self.switch_button = main.switch_button

        self.fpscount = main.fpscount

        self.terraincheck = main.terraincheck
        self.button_name_popup = main.button_name_popup
        self.leaderpopup = main.leaderpopup
        self.effectpopup = main.effectpopup
        self.textdrama = main.textdrama

        self.skill_icon = main.skill_icon
        self.effect_icon = main.effect_icon

        self.battle_menu = main.battle_menu
        self.battle_menu_button = main.battle_menu_button
        self.escoptionmenubutton = main.escoption_menu_button

        self.army_delete_button = self.main.army_delete_button
        self.army_save_button = self.main.army_save_button
        self.troop_listbox = main.troop_listbox
        self.troopnamegroup = main.troopnamegroup
        self.filterbox = main.filterbox
        self.teamchange_button = main.teamchange_button
        self.slotdisplay_button = main.slotdisplay_button
        self.deploy_button = main.deploy_button
        self.popup_listbox = main.popup_listbox
        self.popupnamegroup = main.popupnamegroup
        self.terrain_change_button = main.terrain_change_button
        self.feature_change_button = main.feature_change_button
        self.weather_change_button = main.weather_change_button
        self.armybuildslot = main.armybuildslot
        self.uniteditborder = main.uniteditborder
        self.previewleader = main.previewleader
        self.armypresetnamegroup = main.armypresetnamegroup
        self.customarmypresetlist = main.customarmypresetlist
        self.army_listbox = main.army_listbox
        self.troo_scroll = main.troop_scroll
        self.faction_list = main.faction_list
        self.weather_list = main.weather_list
        self.popup_listscroll = main.popup_listscroll
        self.troop_scroll = main.troop_scroll
        self.teamcoa = main.teamcoa
        self.army_presetname_scroll = main.army_presetname_scroll

        self.armyselector = main.armyselector
        self.armyicon = main.armyicon
        self.selectscroll = main.selectscroll

        self.timeui = main.timeui
        self.timenumber = main.timenumber

        self.scaleui = main.scaleui

        self.speednumber = main.speednumber

        self.weathermatter = main.weathermatter
        self.weathereffect = main.weathereffect

        self.lorebook = main.lorebook
        self.lorenamelist = main.lorenamelist
        self.lorebuttonui = main.lorebuttonui
        self.lorescroll = main.lorescroll
        self.subsection_name = main.subsection_name
        self.pagebutton = main.pagebutton

        self.allweather = main.allweather
        self.weathermatterimgs = main.weathermatterimgs
        self.weathereffectimgs = main.weathereffectimgs

        self.featuremod = main.featuremod

        self.allfaction = main.allfaction
        self.coa = main.coa

        self.allweapon = main.allweapon
        self.allarmour = main.allarmour

        self.statusimgs = main.statusimgs
        self.roleimgs = main.roleimgs
        self.traitimgs = main.traitimgs
        self.skillimgs = main.skillimgs

        self.gameunitstat = main.gameunitstat
        self.leader_stat = main.leader_stat

        self.statetext = main.statetext

        self.squadwidth = main.squadwidth
        self.squadheight = main.squadheight
        self.collidedistance = self.squadheight / 10  # distance to check collision
        self.frontdistance = self.squadheight / 20

        self.combatpathqueue = []  # queue of sub-unit to run melee combat pathfiding

        self.escslidermenu = main.escslidermenu
        self.escvaluebox = main.escvaluebox

        self.screenbuttonlist = main.screenbuttonlist
        self.unitcardbutton = main.unitcardbutton
        self.inspectbutton = main.inspectbutton
        self.col_split_button = main.col_split_button
        self.rowsplitbutton = main.rowsplitbutton

        self.leaderposname = main.leaderposname
        # ^ End load from main

        self.bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)  # Set the display mode
        self.screen = pygame.display.set_mode(SCREENRECT.size, winstyle | pygame.RESIZABLE, self.bestdepth)  # set up game screen

        # v Assign default variable to some class
        gameunit.Unitarmy.gamebattle = self
        gameunit.Unitarmy.imgsize = (self.squadwidth, self.squadheight)
        gamesubunit.Subunit.gamebattle = self
        gameleader.Leader.gamebattle = self
        # ^ End assign default

        self.background = pygame.Surface(SCREENRECT.size)  # Create background image
        self.background.fill((255, 255, 255))  # fill background image with black colour

    def editor_map_change(self, basecolour, featurecolour):
        imgs = (pygame.Surface((1000, 1000)), pygame.Surface((1000, 1000)), pygame.Surface((1000, 1000), pygame.SRCALPHA), None)
        imgs[0].fill(basecolour)  # start with temperate terrain
        imgs[1].fill(featurecolour)  # start with plain feature
        imgs[2].fill((255, 100, 100, 125))  # start with height 100 plain

        self.battlemap_base.drawimage(imgs[0])
        self.battlemap_feature.drawimage(imgs[1])
        self.battlemap_height.drawimage(imgs[2])
        self.showmap.drawimage(self.battlemap_base, self.battlemap_feature, self.battlemap_height, None, self, True)

    def preparenewgame(self, ruleset, rulesetfolder, teamselected, enactment, mapselected, source, unitscale, mode):

        self.ruleset = ruleset  # current ruleset used
        self.rulesetfolder = rulesetfolder  # the folder of rulseset used
        self.mapselected = mapselected  # map folder name
        self.source = str(source)
        self.unitscale = unitscale
        self.playerteam = teamselected  # player selected team

        # v load the sound effects
        # boom_sound = load_sound("boom.wav")
        # shoot_sound = load_sound("car_door.wav")
        # ^ End load sound effect

        # v Random music played from list
        if pygame.mixer and not pygame.mixer.get_init():
            pygame.mixer = None
        if pygame.mixer:
            self.SONG_END = pygame.USEREVENT + 1
            # musiclist = os.path.join(main_dir, "data/sound/")
            self.musiclist = glob.glob(main_dir + "/data/sound/music/*.mp3")
            self.pickmusic = random.randint(1, 1)
            pygame.mixer.music.set_endevent(self.SONG_END)
            pygame.mixer.music.load(self.musiclist[self.pickmusic])
            pygame.mixer.music.play(0)
        # ^ End music play

        # v Load weather schedule
        try:
            self.weatherevent = csv_read("weather.csv", ["data", "ruleset", self.rulesetfolder.strip("/"), "map", self.mapselected], 1)
            self.weatherevent = self.weatherevent[1:]
            gamelongscript.convert_weather_time(self.weatherevent)
        except Exception:  # If no weather found use default light sunny weather start at 9.00
            newtime = datetime.datetime.strptime("09:00:00", "%H:%M:%S").time()
            newtime = datetime.timedelta(hours=newtime.hour, minutes=newtime.minute, seconds=newtime.second)
            self.weatherevent = [[4, newtime, 0]]  # default weather light sunny all day
        self.weatherschedule = self.weatherevent[0][1]
        # ^ End weather schedule

        try:  # get new map event for event log
            mapevent = csv_read("eventlog.csv", ["data", "ruleset", self.rulesetfolder.strip("/"), "map", self.mapselected], 0)
            gameui.Eventlog.mapevent = mapevent
        except Exception:  # can't find any event file
            mapevent = {}  # create empty list

        self.eventlog.makenew()  # reset old event log

        self.eventlog.addeventlog(mapevent)

        self.eventschedule = None
        self.eventlist = []
        for index, event in enumerate(self.eventlog.mapevent):
            if self.eventlog.mapevent[event][3] is not None:
                if index == 0:
                    self.eventmapid = event
                    self.eventschedule = self.eventlog.mapevent[event][3]
                self.eventlist.append(event)

        self.timenumber.startsetup(self.weatherschedule)

        # v Create the battle map
        self.camerapos = pygame.Vector2(500, 500)  # Camera pos at the current zoom, start at center of map
        self.basecamerapos = pygame.Vector2(500, 500)  # Camera pos at furthest zoom for recalculate sprite pos after zoom
        self.camerascale = 1  # Camera zoom
        gamecamera.Camera.SCREENRECT = SCREENRECT
        self.camera = gamecamera.Camera(self.camerapos, self.camerascale)

        if mapselected is not None:
            imgs = load_images(["ruleset", self.rulesetfolder.strip("/"), "map", self.mapselected], loadorder=False)
            self.battlemap_base.drawimage(imgs[0])
            self.battlemap_feature.drawimage(imgs[1])
            self.battlemap_height.drawimage(imgs[2])

            try:  # placename map layer is optional, if not existed in folder then assign None
                placenamemap = imgs[3]
            except Exception:
                placenamemap = None
            self.showmap.drawimage(self.battlemap_base, self.battlemap_feature, self.battlemap_height, placenamemap, self, False)
        else:  # for unit editor mode, create empty temperate glass map
            self.editor_map_change((166, 255, 107), (181, 230, 29))
        # ^ End create battle map

        self.minimap.drawimage(self.showmap.trueimage, self.camera)

        self.clock = pygame.time.Clock()  # Game clock to keep track of realtime pass

        self.enactment = enactment  # enactment mod, control both team
        self.mapshown = self.showmap

        self.team0poslist = {}  # team 0 parentunit position
        self.team1poslist = {}  # team 1 parentunit position
        self.team2poslist = {}  # same for team 2

        # v initialise starting subunit sprites
        self.mode = mode
        if self.mode == "battle":
            gamelongscript.unitsetup(self)

        self.allunitlist = []
        self.allsubunitlist = []
        for group in (self.team0army, self.team1army, self.team2army):
            for army in group:
                self.allunitlist.append(army)  # list of every parentunit in game alive

        self.allunitindex = [army.gameid for army in self.allunitlist]  # list of every parentunit index alive

        for unit in self.allunitlist:  # create troop number text sprite
            self.troopnumbersprite.add(gameunit.Troopnumber(unit))

        for subunit in self.subunit:  # list of all subunit alive in game
            self.allsubunitlist.append(subunit)
        # ^ End start subunit sprite

    def previewauthority(self, leaderlist, armyid):
        # vcalculate authority
        authority = int(
            leaderlist[0].authority + (leaderlist[0].authority / 2) +
            (leaderlist[1].authority / 4) + (leaderlist[2].authority / 4) +
            (leaderlist[3].authority / 10))
        bigarmysize = len([slot for slot in self.armybuildslot if slot.armyid == armyid and slot.name != "None"])
        if bigarmysize > 20:  # army size larger than 20 will reduce main leader authority
            authority = int(leaderlist[0].authority +
                            (leaderlist[0].authority / 2 * (100 - bigarmysize) / 100) +
                            leaderlist[1].authority / 2 + leaderlist[2].authority / 2 +
                            leaderlist[3].authority / 4)

        for slot in self.armybuildslot:
            if slot.armyid == armyid:
                slot.authority = authority

        if self.showincard is not None:
            self.gameui[1].valueinput(who=self.showincard)
        # ^ End cal authority

    def setup_armyicon(self):
        """Setup army selection list in army selector ui top left of screen"""
        row = 30
        startcolumn = 25
        column = startcolumn
        armylist = self.team1army
        if self.enactment:  # include another team army icon as well in enactment mode
            armylist = self.allunitlist
        currentindex = int(self.armyselector.current_row * self.armyselector.max_column_show)  # the first index of current row
        self.armyselector.logsize = len(armylist) / self.armyselector.max_column_show

        if self.armyselector.logsize.is_integer() is False:
            self.armyselector.logsize = int(self.armyselector.logsize) + 1

        if self.armyselector.current_row > self.armyselector.logsize - 1:
            self.armyselector.current_row = self.armyselector.logsize - 1
            currentindex = int(self.armyselector.current_row * self.armyselector.max_column_show)
            self.selectscroll.changeimage(newrow=self.armyselector.current_row)

        if len(self.armyicon) > 0:  # Remove all old icon first before making new list
            for icon in self.armyicon:
                icon.kill()
                del icon

        for index, army in enumerate(armylist):  # add army icon for drawing according to appopriate current row
            if index >= currentindex:
                self.armyicon.add(gameui.Armyicon((column, row), army))
                column += 40
                if column > 250:
                    row += 50
                    column = startcolumn
                if row > 100:
                    break  # do not draw for the third row
        self.selectscroll.changeimage(logsize=self.armyselector.logsize)

    def checksplit(self, whoinput):
        """Check if army can be splitted, if not remove splitting button"""
        # v split by middle collumn
        if np.array_split(whoinput.armysubunit, 2, axis=1)[0].size >= 10 and np.array_split(whoinput.armysubunit, 2, axis=1)[1].size >= 10 and \
                whoinput.leader[1].name != "None":  # can only split if both parentunit size will be larger than 10 and second leader exist
            self.battleui.add(self.col_split_button)
        elif self.col_split_button in self.battleui:
            self.col_split_button.kill()
        # ^ End col

        # v split by middle row
        if np.array_split(whoinput.armysubunit, 2)[0].size >= 10 and np.array_split(whoinput.armysubunit, 2)[1].size >= 10 and \
                whoinput.leader[1].name != "None":
            self.battleui.add(self.rowsplitbutton)
        elif self.rowsplitbutton in self.battleui:
            self.rowsplitbutton.kill()

    def popout_lorebook(self, section, gameid):
        """open and draw enclycopedia at the specified subsection, used for when user right click at icon that has encyclopedia section"""
        self.gamestate = 0
        self.battle_menu.mode = 2
        self.battleui.add(self.lorebook, self.lorenamelist, self.lorescroll, *self.lorebuttonui)

        self.lorebook.change_section(section, self.lorenamelist, self.subsection_name, self.lorescroll, self.pagebutton, self.battleui)
        self.lorebook.change_subsection(gameid, self.pagebutton, self.battleui)
        self.lorescroll.changeimage(newrow=self.lorebook.current_subsection_row)

    def popuplist_newopen(self, newrect, newlist, uitype):
        """Move popup_listbox and scroll sprite to new location and create new name list baesd on type"""
        self.currentpopuprow = 0

        if uitype == "leader":
            self.popup_listbox.rect = self.popup_listbox.image.get_rect(topleft=newrect)
        else:
            self.popup_listbox.rect = self.popup_listbox.image.get_rect(midbottom=newrect)

        self.main.setuplist(gameprepare.Namelist, 0, newlist, self.popupnamegroup,
                            self.popup_listbox, self.battleui, layer=17)

        self.popup_listscroll.pos = self.popup_listbox.rect.topright  # change position variable
        self.popup_listscroll.rect = self.popup_listscroll.image.get_rect(topleft=self.popup_listbox.rect.topright)  #
        self.popup_listscroll.changeimage(newrow=0, logsize=len(newlist))

        self.battleui.add(self.popup_listbox, *self.popupnamegroup, self.popup_listscroll)  # add the option list to screen

        self.popup_listbox.type = uitype

    def ui_mouseover(self):
        """mouse over ui that is not subunit card and armybox (topbar and commandbar)"""
        for ui in self.gameui:
            if ui in self.battleui and ui.rect.collidepoint(self.mousepos):
                self.clickany = True
                self.uiclick = True
                break
        return self.clickany

    def armyicon_mouseover(self, mouseup, mouseright):
        """process user mouse input on army icon, left click = select, right click = go to parentunit position on map"""
        self.clickany = True
        self.uiclick = True
        for icon in self.armyicon:
            if icon.rect.collidepoint(self.mousepos):
                if mouseup:
                    self.last_selected = icon.army
                    self.last_selected.justselected = True
                    self.last_selected.selected = True

                elif mouseright:
                    self.basecamerapos = pygame.Vector2(icon.army.base_pos[0], icon.army.base_pos[1])
                    self.camerapos = self.basecamerapos * self.camerascale
                break
        return self.clickany

    def button_mouseover(self, mouseright):
        """process user mouse input on various ui buttons"""
        for button in self.buttonui:
            if button in self.battleui and button.rect.collidepoint(self.mousepos):
                self.clickany = True
                self.uiclick = True  # for avoiding selecting subunit under ui
                break
        return self.clickany

    def leader_mouseover(self, mouseright):  # TODO make it so button and leader popup not show at same time
        """process user mouse input on leader portrait in command ui"""
        leadermouseover = False
        for leader in self.leadernow:
            if leader.rect.collidepoint(self.mousepos):
                if leader.parentunit.commander:
                    armyposition = self.leaderposname[leader.armyposition]
                else:
                    armyposition = self.leaderposname[leader.armyposition + 4]

                self.leaderpopup.pop(self.mousepos, armyposition + ": " + leader.name)  # popup leader name when mouse over
                self.battleui.add(self.leaderpopup)
                leadermouseover = True

                if mouseright:
                    self.popout_lorebook(8, leader.gameid)
                break
        return leadermouseover

    def effecticon_mouseover(self, iconlist, mouseright):
        effectmouseover = False
        for icon in iconlist:
            if icon.rect.collidepoint(self.mousepos):
                checkvalue = self.gameui[2].value2[icon.icontype]
                self.effectpopup.pop(self.mousepos, checkvalue[icon.gameid])
                self.battleui.add(self.effectpopup)
                effectmouseover = True
                if mouseright:
                    if icon.icontype == 0:  # Trait
                        section = 7
                    elif icon.icontype == 1:  # Skill
                        section = 6
                    else:
                        section = 5  # Status effect
                    self.popout_lorebook(section, icon.gameid)
                break
        return effectmouseover

    def camerafix(self):
        if self.basecamerapos[0] > 999:  # camera cannot go further than 999 x
            self.basecamerapos[0] = 999
        elif self.basecamerapos[0] < 0:  # camera cannot go less than 0 x
            self.basecamerapos[0] = 0

        if self.basecamerapos[1] > 999:  # same for y
            self.basecamerapos[1] = 999
        elif self.basecamerapos[1] < 0:
            self.basecamerapos[1] = 0

    def addbehaviourui(self, whoinput, elsecheck=False):
        if whoinput.control:
            self.battleui.add(self.buttonui[7])  # add decimation button
            self.battleui.add(*self.switch_button[0:7])  # add parentunit behaviour change button
            self.switch_button[0].event = whoinput.skill_cond
            self.switch_button[1].event = whoinput.fireatwill
            self.switch_button[2].event = whoinput.hold
            self.switch_button[3].event = whoinput.use_min_range
            self.switch_button[4].event = whoinput.shoothow
            self.switch_button[5].event = whoinput.runtoggle
            self.switch_button[6].event = whoinput.attackmode
            self.checksplit(whoinput)  # check if selected parentunit can split, if yes draw button
        elif elsecheck:
            if self.rowsplitbutton in self.battleui:
                self.rowsplitbutton.kill()
            if self.col_split_button in self.battleui:
                self.col_split_button.kill()
            self.battleui.remove(self.buttonui[7])  # add decimation button
            self.battleui.remove(*self.switch_button[0:6])  # add parentunit behaviour change button

        self.leadernow = whoinput.leader
        self.battleui.add(*self.leadernow)  # add leader portrait to draw
        self.gameui[0].valueinput(who=whoinput, splithappen=self.splithappen)
        self.gameui[1].valueinput(who=whoinput, splithappen=self.splithappen)

    def unitcardbutton_click(self, who):
        for button in self.unitcardbutton:  # Change subunit card option based on button clicking
            if button.rect.collidepoint(self.mousepos):
                self.clickany = True
                self.uiclick = True
                if self.gameui[2].option != button.event:
                    self.gameui[2].option = button.event
                    self.gameui[2].valueinput(who=who, weaponlist=self.allweapon,
                                              armourlist=self.allarmour,
                                              changeoption=1, splithappen=self.splithappen)

                    if self.gameui[2].option == 2:
                        self.traitskillblit()
                        self.effecticonblit()
                        self.countdownskillicon()
                    else:
                        for icon in self.skill_icon.sprites():
                            icon.kill()
                        for icon in self.effect_icon.sprites():
                            icon.kill()
                break

    def rungame(self):
        # v Create Starting Values
        self.mixervolume = SoundVolume
        self.gamestate = 1
        self.current_army_row = 0
        self.current_troop_row = 0
        if self.mode == "uniteditor":
            self.gamestate = 2

            self.full_troop_list = [item[0] for item in self.gameunitstat.unit_list.values()][1:]

            self.troop_list = self.full_troop_list  # generate troop name list
            self.troop_index_list = list(range(0, len(self.troop_list) + 1))

            self.leader_list = [item[0] for item in self.leader_stat.leader_list.values()][1:]  # generate leader name list

            self.main.setuplist(gameprepare.Namelist, self.current_army_row, list(self.customarmypresetlist.keys()),
                                self.armypresetnamegroup, self.army_listbox, self.battleui)  # setup preset army list
            self.main.setuplist(gameprepare.Namelist, self.current_troop_row, self.troop_list,
                                self.troopnamegroup, self.troop_listbox, self.battleui)  # setup troop name list

            self.current_list_show = "troop"
            self.preparestate = True
            self.baseterrain = 0
            self.featureterrain = 0
            self.weathertype = 4
            self.weatherstrength = 0
            self.currentweather = gameweather.Weather(self.timeui, self.weathertype, self.weatherstrength, self.allweather)
            self.showincard = None  # current sub-subunit showing in subunit card
            self.leadernow = []  # list of showing leader in command ui

            self.main.maketeamcoa([0], uiclass=self.battleui, oneteam=True,
                                  team1setpos=(self.troop_listbox.rect.midleft[0] - int((200 * self.widthadjust) / 2),
                                               self.troop_listbox.rect.midleft[1]))  # default faction select as all faction

            self.troop_scroll.changeimage(newrow=self.current_troop_row, logsize=len(self.troop_list))  # change troop scroll image

            for index, slot in enumerate(self.armybuildslot):  # start with the first player subunit slot selected when enter
                if index == 0:
                    slot.selected = True
                    for border in self.uniteditborder:
                        border.kill()
                        del border
                    self.uniteditborder.add(gameui.Selectedsquad(slot.inspposition))
                    self.battleui.add(*self.uniteditborder)
                else:  # reset all other slot
                    slot.selected = False

            self.gameui[2].rect = self.gameui[2].image.get_rect(bottomright=(SCREENRECT.width,
                                                                             SCREENRECT.height))  # troop info card ui
            self.buttonui[0].rect = self.buttonui[0].image.get_rect(topleft=(self.gameui[2].rect.topleft[0],  # description button
                                                                             self.gameui[2].rect.topleft[1] + 120))
            self.buttonui[1].rect = self.buttonui[1].image.get_rect(topleft=(self.gameui[2].rect.topleft[0],  # stat button
                                                                             self.gameui[2].rect.topleft[1]))
            self.buttonui[2].rect = self.buttonui[2].image.get_rect(topleft=(self.gameui[2].rect.topleft[0],  # skill button
                                                                             self.gameui[2].rect.topleft[1] + 40))
            self.buttonui[3].rect = self.buttonui[3].image.get_rect(topleft=(self.gameui[2].rect.topleft[0],  # equipment button
                                                                             self.gameui[2].rect.topleft[1] + 80))

            self.battleui.add(self.army_delete_button, self.army_save_button, self.troop_listbox, self.troop_scroll, self.army_listbox,
                              self.army_presetname_scroll, self.filterbox, self.teamchange_button, self.slotdisplay_button, self.deploy_button,
                              *self.unitcardbutton, self.terrain_change_button, self.feature_change_button, self.weather_change_button,
                              *self.armybuildslot, self.teamcoa, self.gameui[1], self.gameui[2])
            self.battleui.remove(self.eventlog, self.logscroll, self.buttonui[8:14])

        else:  # add various ui that was disable in army editor
            self.gameui[1].rect = self.gameui[1].image.get_rect(
                center=(self.gameui[1].x, self.gameui[1].y))  # change leader ui position back
            self.gameui[2].rect = self.gameui[2].image.get_rect(
                center=(self.gameui[2].x, self.gameui[2].y))  # change subunit card position back
            self.buttonui[0].rect = self.buttonui[0].image.get_rect(center=(self.gameui[2].x - 152, self.gameui[2].y + 10))
            self.buttonui[1].rect = self.buttonui[1].image.get_rect(center=(self.gameui[2].x - 152, self.gameui[2].y - 70))
            self.buttonui[2].rect = self.buttonui[2].image.get_rect(center=(self.gameui[2].x - 152, self.gameui[2].y - 30))
            self.buttonui[3].rect = self.buttonui[3].image.get_rect(center=(self.gameui[2].x - 152, self.gameui[2].y + 50))

            self.battleui.add(self.eventlog, self.logscroll, self.buttonui[8:14],
                              self.gameui[1], self.gameui[2])

        self.previous_gamestate = self.gamestate
        self.mapscaledelay = 0  # delay for map zoom input
        self.mousetimer = 0  # This is timer for checking double mouse click, use realtime
        self.ui_timer = 0  # This is timer for ui update function, use realtime
        self.drama_timer = 0  # This is timer for combat related function, use game time (realtime * gamespeed)
        self.dt = 0  # Realtime used for in game calculation
        self.uidt = 0  # Realtime used for ui timer
        self.combattimer = 0  # This is timer for combat related function, use game time (realtime * gamespeed)
        self.last_mouseover = None  # Which subunit last mouse over
        self.gamespeed = 1  # Current game speed
        self.speednumber.speedupdate(self.gamespeed)
        self.gamespeedset = (0, 0.5, 1, 2, 4, 6)  # availabe game speed
        self.leadernow = []  # list of showing leader in command ui
        self.uiclick = False  # for checking if mouse click is on ui
        self.clickany = False  # For checking if mouse click on anything, if not close ui related to parentunit
        self.newarmyclick = False  # For checking if another subunit is clicked when inspect ui open
        self.inspectui = False  # For checking if inspect ui is currently open or not
        self.last_selected = None  # Which army is selected last update loop
        self.mapviewmode = 0  # default, another one show height map
        self.subunit_selected = None  # which subunit in inspect ui is selected in last update loop
        self.before_selected = None  # Which army is selected before
        self.splithappen = False  # Check if parentunit get split in that loop
        self.currentweather = None
        self.showtroopnumber = True  # for toggle troop number on/off
        self.weatherscreenadjust = SCREENRECT.width / SCREENRECT.height  # for weather sprite spawn position
        self.rightcorner = SCREENRECT.width - 5
        self.bottomcorner = SCREENRECT.height - 5
        self.centerscreen = [SCREENRECT.width / 2, SCREENRECT.height / 2]  # center position of the screen
        self.battle_mouse_pos = [[0, 0],
                                 [0, 0]]  # mouse position list in game not screen, the first without zoom and the second with camera zoom adjust
        self.teamtroopnumber = [1, 1, 1]  # list of troop number in each team, minimum at one because percentage can't divide by 0
        self.lastteamtroopnumber = [1, 1, 1]
        self.armyselector.current_row = 0
        # ^ End start value

        self.setup_armyicon()
        self.selectscroll.changeimage(newrow=self.armyselector.current_row)

        # v Run starting function
        for army in self.allunitlist:
            army.startset(self.subunit)
        for subunit in self.subunit:
            subunit.gamestart(self.camerascale)
        for leader in self.leader_updater:
            leader.gamestart()
        # ^ End starting

        self.effect_updater.update(self.allunitlist, self.dt, self.camerascale)

        # self.mapdefarray = []
        # self.mapunitarray = [[x[random.randint(0, 1)] if i != j else 0 for i in range(1000)] for j in range(1000)]

        while True:  # game running
            self.fpscount.fpsshow(self.clock)
            keypress = None
            self.mousepos = pygame.mouse.get_pos()  # current mouse pos based on screen
            mouse_up = False  # left click
            mouse_down = False  # hold left click
            mouse_right = False  # right click
            double_mouse_right = False  # double right click
            mouse_scrolldown = False
            mouse_scrollup = False
            keystate = pygame.key.get_pressed()

            for event in pygame.event.get():  # get event that happen
                if event.type == QUIT:  # quit game
                    self.battleui.clear(self.screen, self.background)
                    self.battlecamera.clear(self.screen, self.background)
                    pygame.quit()
                    sys.exit()

                elif event.type == self.SONG_END:  # change music track
                    # pygame.mixer.music.unload()
                    self.pickmusic = random.randint(1, 1)
                    pygame.mixer.music.load(self.musiclist[self.pickmusic])
                    pygame.mixer.music.play(0)

                elif event.type == pygame.KEYDOWN and event.key == K_ESCAPE:  # open/close menu
                    if self.gamestate in (1, 2):  # in battle
                        self.gamestate = 0  # open munu
                        self.battleui.add(self.battle_menu)  # add menu to drawer
                        self.battleui.add(*self.battle_menu_button)  # add menu button to

                    else:  # in menu
                        if self.battle_menu.mode in (0, 1):  # in menu or option
                            if self.battle_menu.mode == 1:  # option menu
                                self.mixervolume = self.oldsetting
                                pygame.mixer.music.set_volume(self.mixervolume)
                                self.escslidermenu[0].update(self.mixervolume, self.escvaluebox[0], forcedvalue=True)
                                self.battle_menu.changemode(0)

                            self.battleui.remove(self.battle_menu)
                            self.battleui.remove(*self.battle_menu_button)
                            self.battleui.remove(*self.escoptionmenubutton)
                            self.battleui.remove(*self.escslidermenu)
                            self.battleui.remove(*self.escvaluebox)
                            self.gamestate = self.previous_gamestate

                        elif self.battle_menu.mode == 2:  # encyclopedia
                            self.battleui.remove(self.lorebook, *self.lorebuttonui, self.lorescroll, self.lorenamelist)

                            for name in self.subsection_name:
                                name.kill()
                                del name
                            self.battle_menu.changemode(0)

                            if self.battle_menu not in self.battleui:
                                self.gamestate = self.previous_gamestate

                if pygame.mouse.get_pressed()[0]:  # Hold left click
                    mouse_down = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # left click
                        mouse_up = True

                    elif event.button == 4:  # Mouse scroll up
                        if self.gamestate == 0 and self.battle_menu.mode == 2:  # Scrolling at lore book subsection list
                            if self.lorenamelist.rect.collidepoint(self.mousepos):
                                self.lorebook.current_subsection_row -= 1
                                if self.lorebook.current_subsection_row < 0:
                                    self.lorebook.current_subsection_row = 0
                                else:
                                    self.lorebook.setup_subsection_list(self.lorenamelist, self.subsection_name)
                                    self.lorescroll.changeimage(newrow=self.lorebook.current_subsection_row)

                    elif event.button == 5:  # Mouse scroll down
                        if self.gamestate == 0 and self.battle_menu.mode == 2:  # Scrolling at lore book subsection list
                            if self.lorenamelist.rect.collidepoint(self.mousepos):
                                self.lorebook.current_subsection_row += 1
                                if self.lorebook.current_subsection_row + self.lorebook.max_subsection_show - 1 < self.lorebook.logsize:
                                    self.lorebook.setup_subsection_list(self.lorenamelist, self.subsection_name)
                                    self.lorescroll.changeimage(newrow=self.lorebook.current_subsection_row)
                                else:
                                    self.lorebook.current_subsection_row -= 1

                # v register user input during gameplay
                if self.gamestate != 0:  # game in battle state
                    # v Mouse input
                    if event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 3:  # Right Click
                            mouse_right = True
                            if self.mousetimer == 0:
                                self.mousetimer = 0.001  # Start timer after first mouse click
                            elif self.mousetimer < 0.3:  # if click again within 0.3 second for it to be considered double click
                                double_mouse_right = True  # double right click
                                self.mousetimer = 0

                        elif event.button == 4 or event.button == 5:  # Mouse scroll up
                            if event.button == 4:
                                mouse_scrollup = True
                                rowchange = -1

                            elif event.button == 5:  # Mouse scroll down
                                mouse_scrolldown = True
                                rowchange = 1

                            if self.eventlog.rect.collidepoint(self.mousepos):  # Scrolling when mouse at event log
                                self.eventlog.current_start_row += rowchange
                                if mouse_scrollup:
                                    if self.eventlog.current_start_row < 0:  # can go no further than the first log
                                        self.eventlog.current_start_row = 0
                                    else:
                                        self.eventlog.recreateimage()  # recreate eventlog image
                                        self.logscroll.changeimage(newrow=self.eventlog.current_start_row)
                                elif mouse_scrolldown:
                                    if self.eventlog.current_start_row + self.eventlog.max_row_show - 1 < self.eventlog.lencheck and \
                                            self.eventlog.lencheck > 9:
                                        self.eventlog.recreateimage()
                                        self.logscroll.changeimage(newrow=self.eventlog.current_start_row)
                                    else:
                                        self.eventlog.current_start_row -= 1

                            elif self.armyselector.rect.collidepoint(self.mousepos):  # Scrolling when mouse at army selector ui
                                self.armyselector.current_row += rowchange
                                if mouse_scrollup:
                                    if self.armyselector.current_row < 0:
                                        self.armyselector.current_row = 0
                                    else:
                                        self.setup_armyicon()
                                        self.selectscroll.changeimage(newrow=self.armyselector.current_row)
                                elif mouse_scrolldown:
                                    if self.armyselector.current_row < self.armyselector.logsize:
                                        self.setup_armyicon()
                                        self.selectscroll.changeimage(newrow=self.armyselector.current_row)
                                    else:
                                        self.armyselector.current_row -= 1
                                        if self.armyselector.current_row < 0:
                                            self.armyselector.current_row = 0

                            elif self.popup_listbox in self.battleui:  # mouse scroll on popup list
                                if self.popup_listbox.type == "terrain":
                                    self.currentpopuprow = self.main.listscroll(mouse_scrollup, mouse_scrolldown, self.popup_listscroll,
                                                                                self.popup_listbox,
                                                                                self.currentpopuprow, self.battlemap_base.terrainlist,
                                                                                self.popupnamegroup, self.battleui)
                                elif self.popup_listbox.type == "feature":
                                    self.currentpopuprow = self.main.listscroll(mouse_scrollup, mouse_scrolldown, self.popup_listscroll,
                                                                                self.popup_listbox,
                                                                                self.currentpopuprow, self.battlemap_feature.featurelist,
                                                                                self.popupnamegroup, self.battleui)
                                elif self.popup_listbox.type == "weather":
                                    self.currentpopuprow = self.main.listscroll(mouse_scrollup, mouse_scrolldown, self.popup_listscroll,
                                                                                self.popup_listbox, self.currentpopuprow, self.weather_list,
                                                                                self.popupnamegroup, self.battleui)
                                elif self.popup_listbox.type == "leader":
                                    self.currentpopuprow = self.main.listscroll(mouse_scrollup, mouse_scrolldown, self.popup_listscroll,
                                                                                self.popup_listbox, self.currentpopuprow, self.leader_list,
                                                                                self.popupnamegroup, self.battleui)

                            elif self.army_listbox.rect.collidepoint(self.mousepos):  # mouse scroll on army preset list
                                self.current_army_row = self.main.listscroll(mouse_scrollup, mouse_scrolldown, self.army_presetname_scroll,
                                                                             self.army_listbox,
                                                                             self.current_army_row, list(self.customarmypresetlist.keys()),
                                                                             self.armypresetnamegroup, self.battleui)
                            elif self.troop_listbox.rect.collidepoint(self.mousepos):
                                if self.current_list_show == "troop":  # mouse scroll on troop list
                                    self.current_troop_row = self.main.listscroll(mouse_scrollup, mouse_scrolldown, self.troop_scroll, self.troop_listbox,
                                                                                  self.current_troop_row, self.troop_list,
                                                                                  self.troopnamegroup, self.battleui)
                                elif self.current_list_show == "faction":  # mouse scroll on faction list
                                    self.current_troop_row = self.main.listscroll(mouse_scrollup, mouse_scrolldown, self.troop_scroll, self.troop_listbox,
                                                                                  self.current_troop_row, self.faction_list,
                                                                                  self.troopnamegroup, self.battleui)

                            elif self.mapscaledelay == 0:  # Scrolling in game map to zoom
                                if mouse_scrollup:
                                    self.camerascale += 1
                                    if self.camerascale > 10:
                                        self.camerascale = 10
                                    else:
                                        self.camerapos[0] = self.basecamerapos[0] * self.camerascale
                                        self.camerapos[1] = self.basecamerapos[1] * self.camerascale
                                        self.mapshown.changescale(self.camerascale)
                                        if self.gamestate == 1:  # only have delay in battle mode
                                            self.mapscaledelay = 0.001

                                elif mouse_scrolldown:
                                    self.camerascale -= 1
                                    if self.camerascale < 1:
                                        self.camerascale = 1
                                    else:
                                        self.camerapos[0] = self.basecamerapos[0] * self.camerascale
                                        self.camerapos[1] = self.basecamerapos[1] * self.camerascale
                                        self.mapshown.changescale(self.camerascale)
                                        if self.gamestate == 1:  # only have delay in battle mode
                                            self.mapscaledelay = 0.001
                    # ^ End mouse input

                    # v keyboard input
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_TAB:
                            if self.mapviewmode == 0:  # Currently in normal map mode
                                self.mapviewmode = 1
                                self.showmap.changemode(self.mapviewmode)
                            else:  # Currently in height mode
                                self.mapviewmode = 0
                                self.showmap.changemode(self.mapviewmode)
                            self.mapshown.changescale(self.camerascale)

                        elif event.key == pygame.K_o:  # Speed Pause/unpause Button
                            if self.showtroopnumber:
                                self.showtroopnumber = False
                                self.effect_updater.remove(*self.troopnumbersprite)
                                self.battlecamera.remove(*self.troopnumbersprite)
                            else:  # speed currently pause
                                self.showtroopnumber = True
                                self.effect_updater.add(*self.troopnumbersprite)
                                self.battlecamera.add(*self.troopnumbersprite)

                        elif event.key == pygame.K_p:  # Speed Pause/unpause Button
                            if self.gamespeed >= 0.5:  #
                                self.gamespeed = 0  # pause game speed
                            else:  # speed currently pause
                                self.gamespeed = 1  # unpause game and set to speed 1
                            self.speednumber.speedupdate(self.gamespeed)

                        elif event.key == pygame.K_KP_MINUS:  # reduce game speed
                            newindex = self.gamespeedset.index(self.gamespeed) - 1
                            if newindex >= 0:  # cannot reduce game speed than what is available
                                self.gamespeed = self.gamespeedset[newindex]
                            self.speednumber.speedupdate(self.gamespeed)

                        elif event.key == pygame.K_KP_PLUS:  # increase game speed
                            newindex = self.gamespeedset.index(self.gamespeed) + 1
                            if newindex < len(self.gamespeedset):  # cannot increase game speed than what is available
                                self.gamespeed = self.gamespeedset[newindex]
                            self.speednumber.speedupdate(self.gamespeed)

                        elif event.key == pygame.K_PAGEUP:  # Go to top of event log
                            self.eventlog.current_start_row = 0
                            self.eventlog.recreateimage()
                            self.logscroll.changeimage(newrow=self.eventlog.current_start_row)

                        elif event.key == pygame.K_PAGEDOWN:  # Go to bottom of event log
                            if self.eventlog.lencheck > self.eventlog.max_row_show:
                                self.eventlog.current_start_row = self.eventlog.lencheck - self.eventlog.max_row_show
                                self.eventlog.recreateimage()
                                self.logscroll.changeimage(newrow=self.eventlog.current_start_row)

                        elif event.key == pygame.K_SPACE and self.last_selected is not None:
                            whoinput.command(self.battle_mouse_pos[0], mouse_right, double_mouse_right,
                                             self.last_mouseover, keystate, othercommand=2)

                        # v FOR DEVELOPMENT DELETE LATER
                        elif event.key == pygame.K_1:
                            self.textdrama.queue.append("Hello and Welcome to update video")
                        elif event.key == pygame.K_2:
                            self.textdrama.queue.append("Showcase: New melee combat test")
                        elif event.key == pygame.K_3:
                            self.textdrama.queue.append("Also add pathfind algorithm for melee combat")
                        elif event.key == pygame.K_4:
                            self.textdrama.queue.append("The combat mechanic will be much more dynamic")
                        elif event.key == pygame.K_5:
                            self.textdrama.queue.append("Will take a while for everything to work again")
                        elif event.key == pygame.K_6:
                            self.textdrama.queue.append("Current special effect still need rework")
                        elif event.key == pygame.K_n and self.last_selected is not None:
                            if whoinput.team == 1:
                                self.allunitindex = whoinput.switchfaction(self.team1army, self.team2army, self.team1poslist, self.allunitindex,
                                                                           self.enactment)
                            else:
                                self.allunitindex = whoinput.switchfaction(self.team2army, self.team1army, self.team2poslist, self.allunitindex,
                                                                           self.enactment)
                        elif event.key == pygame.K_l and self.last_selected is not None:
                            for subunit in whoinput.subunit_sprite:
                                subunit.base_morale = 0
                        elif event.key == pygame.K_k and self.last_selected is not None:
                            # for index, subunit in enumerate(self.last_selected.subunit_sprite):
                            #     subunit.unit_health -= subunit.unit_health
                            self.subunit_selected.who.unit_health -= self.subunit_selected.who.unit_health
                        elif event.key == pygame.K_m and self.last_selected is not None:
                            self.last_selected.leader[0].health -= 1000
                            # self.subunit_selected.who.base_morale -= 1000
                            # self.subunit_selected.who.brokenlimit = 80
                            # self.subunit_selected.who.state = 99
                        elif event.key == pygame.K_COMMA and self.last_selected is not None:
                            for index, subunit in enumerate(self.last_selected.subunit_sprite):
                                subunit.stamina -= subunit.stamina
                        # ^ End For development test

                        else:  # pressing other keys (Not hold)
                            keypress = event.key
                    # ^ End keyboard input
                # ^ End register input

            self.battleui.clear(self.screen, self.background)  # Clear sprite before update new one
            if self.gamestate != 0:  # game in battle state or unit editor
                # v Camera movement
                if keystate[K_s] or self.mousepos[1] >= self.bottomcorner:  # Camera move down
                    self.basecamerapos[1] += 5 * (
                            11 - self.camerascale)  # need "11 -" for converting cameral scale so the further zoom camera move faster
                    self.camerapos[1] = self.basecamerapos[1] * self.camerascale  # resize camera pos
                    self.camerafix()

                elif keystate[K_w] or self.mousepos[1] <= 5:  # Camera move up
                    self.basecamerapos[1] -= 5 * (11 - self.camerascale)
                    self.camerapos[1] = self.basecamerapos[1] * self.camerascale
                    self.camerafix()

                if keystate[K_a] or self.mousepos[0] <= 5:  # Camera move left
                    self.basecamerapos[0] -= 5 * (11 - self.camerascale)
                    self.camerapos[0] = self.basecamerapos[0] * self.camerascale
                    self.camerafix()

                elif keystate[K_d] or self.mousepos[0] >= self.rightcorner:  # Camera move right
                    self.basecamerapos[0] += 5 * (11 - self.camerascale)
                    self.camerapos[0] = self.basecamerapos[0] * self.camerascale
                    self.camerafix()

                self.cameraupcorner = (self.camerapos[0] - self.centerscreen[0],
                                       self.camerapos[1] - self.centerscreen[1])  # calculate top left corner of camera position
                # ^ End camera movement

                if self.mousetimer != 0:  # player click mouse once before
                    self.mousetimer += self.uidt  # increase timer for mouse click using real time
                    if self.mousetimer >= 0.3:  # time pass 0.3 second no longer count as double click
                        self.mousetimer = 0

                if self.mapscaledelay > 0:  # player change map scale once before
                    self.mapscaledelay += self.uidt
                    if self.mapscaledelay >= 0.1:  # delay for 1 second until user can change scale again
                        self.mapscaledelay = 0

                self.uiupdater.update()  # update ui
                self.camera.update(self.camerapos, self.battlecamera, self.camerascale)

            if self.gamestate == 1:  # only for battle

                self.battle_mouse_pos[0] = pygame.Vector2((self.mousepos[0] - self.centerscreen[0]) + self.camerapos[0],
                                                          self.mousepos[1] - self.centerscreen[1] + self.camerapos[
                                                              1])  # mouse pos on the map based on camera position
                self.battle_mouse_pos[1] = self.battle_mouse_pos[0] / self.camerascale  # mouse pos on the map at current camera zoom scale

                if self.dt > 0:
                    self.teamtroopnumber = [1, 1, 1]  # reset troop count

                if self.terraincheck in self.battleui and (
                        self.terraincheck.pos != self.mousepos or keystate[K_s] or keystate[K_w] or keystate[K_a] or keystate[K_d]):
                    self.battleui.remove(self.terraincheck)  # remove terrain popup when move mouse or camera

                if mouse_up or mouse_right or mouse_down:
                    self.uiclick = False  # reset mouse check on ui, if stay false it mean mouse click is not on any ui
                    if mouse_up:
                        self.clickany = False
                        self.newarmyclick = False
                    if self.minimap.rect.collidepoint(self.mousepos):  # mouse position on mini map
                        if mouse_up:  # move game camera to position clicked on mini map
                            posmask = pygame.Vector2(int(self.mousepos[0] - self.minimap.rect.x), int(self.mousepos[1] - self.minimap.rect.y))
                            self.basecamerapos = posmask * 5
                            self.camerapos = self.basecamerapos * self.camerascale
                            self.clickany = True
                            self.uiclick = True
                        elif mouse_right:  # nothing happen with mouse right
                            if self.last_selected is not None:
                                self.uiclick = True

                    elif self.logscroll.rect.collidepoint(self.mousepos):  # Must check mouse collide for scroller before event log ui
                        self.clickany = True
                        self.uiclick = True
                        if mouse_down or mouse_up:
                            newrow = self.logscroll.update(self.mousepos)
                            if self.eventlog.current_start_row != newrow:
                                self.eventlog.current_start_row = newrow
                                self.eventlog.recreateimage()

                    elif self.selectscroll.rect.collidepoint(self.mousepos):  # Must check mouse collide for scroller before army select ui
                        self.clickany = True
                        self.uiclick = True
                        if mouse_down or mouse_up:
                            newrow = self.selectscroll.update(self.mousepos)
                            if self.armyselector.current_row != newrow:
                                self.armyselector.current_row = newrow
                                self.setup_armyicon()

                    elif self.eventlog.rect.collidepoint(self.mousepos):  # check mouse collide for event log ui
                        self.clickany = True
                        self.uiclick = True

                    elif self.timeui.rect.collidepoint(self.mousepos):  # check mouse collide for time bar ui
                        self.clickany = True
                        self.uiclick = True

                    elif self.armyselector.rect.collidepoint(self.mousepos):  # check mouse collide for army selector ui
                        self.armyicon_mouseover(mouse_up, mouse_right)

                    elif self.ui_mouseover():  # check mouse collide for other ui
                        pass

                    elif self.button_mouseover(mouse_right):  # check mouse collide for button
                        pass

                    elif mouse_right and self.last_selected is None and self.uiclick is False:  # draw terrain popup ui when right click at map with no selected parentunit
                        if 0 <= self.battle_mouse_pos[1][0] <= 999 and 0 <= self.battle_mouse_pos[1][1] <= 999:  # not draw if pos is off the map
                            terrainpop, featurepop = self.battlemap_feature.getfeature(self.battle_mouse_pos[1], self.battlemap_base)
                            featurepop = self.battlemap_feature.featuremod[featurepop]
                            heightpop = self.battlemap_height.getheight(self.battle_mouse_pos[1])
                            self.terraincheck.pop(self.mousepos, featurepop, heightpop)
                            self.battleui.add(self.terraincheck)

                    for index, button in enumerate(self.screenbuttonlist):  # Event log button and timer button click
                        if button.rect.collidepoint(self.mousepos):
                            if index in (0, 1, 2, 3, 4, 5):  # eventlog button
                                self.uiclick = True
                                if mouse_up:
                                    if button.event in (0, 1, 2, 3):  # change tab mode
                                        self.eventlog.changemode(button.event)
                                    elif button.event == 4:  # delete tab log button
                                        self.eventlog.cleartab()
                                    elif button.event == 5:  # delete all tab log button
                                        self.eventlog.cleartab(alltab=True)

                            elif index in (6, 7, 8):  # timer button
                                self.uiclick = True
                                if mouse_up:
                                    if button.event == 0:  # pause button
                                        self.gamespeed = 0
                                    elif button.event == 1:  # reduce speed button
                                        newindex = self.gamespeedset.index(self.gamespeed) - 1
                                        if newindex >= 0:
                                            self.gamespeed = self.gamespeedset[newindex]
                                    elif button.event == 2:  # increase speed button
                                        newindex = self.gamespeedset.index(self.gamespeed) + 1
                                        if newindex < len(self.gamespeedset):
                                            self.gamespeed = self.gamespeedset[newindex]
                                    self.speednumber.speedupdate(self.gamespeed)
                            break

                # v Event log timer
                if self.eventschedule is not None and self.eventlist != [] and self.timenumber.timenum >= self.eventschedule:
                    self.eventlog.addlog(None, None, eventmapid=self.eventmapid)
                    for event in self.eventlog.mapevent:
                        if self.eventlog.mapevent[event][3] is not None and self.eventlog.mapevent[event][3] > self.timenumber.timenum:
                            self.eventmapid = event
                            self.eventschedule = self.eventlog.mapevent[event][3]
                            break
                    self.eventlist = self.eventlist[1:]
                # ^ End event log timer

                # v Weather system
                if self.weatherschedule is not None and self.timenumber.timenum >= self.weatherschedule:
                    del self.currentweather
                    weather = self.weatherevent[0]

                    if weather[0] != 0:
                        self.currentweather = gameweather.Weather(self.timeui, weather[0], weather[2], self.allweather)
                    else:  # Random weather
                        self.currentweather = gameweather.Weather(self.timeui, random.randint(0, 11), random.randint(0, 2), self.allweather)
                    self.weatherevent.pop(0)
                    self.showmap.addeffect(self.battlemap_height, self.weathereffectimgs[self.currentweather.weathertype][self.currentweather.level])

                    try:  # Get end time of next event which is now index 0
                        self.weatherschedule = self.weatherevent[0][1]
                    except Exception:
                        self.weatherschedule = None

                if self.currentweather.spawnrate > 0 and len(self.weathermatter) < self.currentweather.speed:
                    spawnnum = range(0,
                                     int(self.currentweather.spawnrate * self.dt * random.randint(0, 10)))  # number of sprite to spawn at this time
                    for spawn in spawnnum:  # spawn each weather sprite
                        truepos = (random.randint(10, SCREENRECT.width), 0)  # starting pos
                        target = (truepos[0], SCREENRECT.height)  # final base_target pos

                        if self.currentweather.spawnangle == 225:  # top right to bottom left movement
                            startpos = random.randint(10, SCREENRECT.width * 2)  # starting x pos that can be higher than screen width
                            truepos = (startpos, 0)
                            if startpos >= SCREENRECT.width:  # x higher than screen width will spawn on the right corner of screen but not at top
                                startpos = SCREENRECT.width  # revert x back to screen width
                                truepos = (startpos, random.randint(0, SCREENRECT.height))

                            if truepos[1] > 0:  # start position simulate from beyond top right of screen
                                target = (truepos[1] * self.weatherscreenadjust, SCREENRECT.height)
                            elif truepos[0] < SCREENRECT.width:  # start position inside screen width
                                target = (0, truepos[0] / self.weatherscreenadjust)

                        elif self.currentweather.spawnangle == 270:  # right to left movement
                            truepos = (SCREENRECT.width, random.randint(0, SCREENRECT.height))
                            target = (0, truepos[1])

                        randompic = random.randint(0, len(self.weathermatterimgs[self.currentweather.weathertype]) - 1)
                        self.weathermatter.add(gameweather.Mattersprite(truepos, target,
                                                                        self.currentweather.speed,
                                                                        self.weathermatterimgs[self.currentweather.weathertype][randompic]))

                # v code that only run when any unit is selected
                if self.last_selected is not None and self.last_selected.state != 100:
                    whoinput = self.last_selected
                    if self.before_selected is None:  # add back the pop up ui to group so it get shown when click subunit with none selected before
                        self.gameui = self.popgameui
                        self.battleui.add(*self.gameui[0:2])  # add leader and top ui
                        self.battleui.add(self.inspectbutton)  # add inspection ui open/close button

                        self.addbehaviourui(whoinput)

                    elif self.before_selected != self.last_selected or self.splithappen:  # change subunit information on ui when select other parentunit
                        if self.inspectui:  # change inspect ui
                            self.newarmyclick = True
                            self.battleui.remove(*self.inspectsubunit)

                            self.subunit_selected = None
                            for index, subunit in enumerate(whoinput.subunit_sprite_array.flat):
                                if subunit is not None:
                                    self.inspectsubunit[index].addsubunit(subunit)
                                    self.battleui.add(self.inspectsubunit[index])
                                    if self.subunit_selected is None:
                                        self.subunit_selected = self.inspectsubunit[index]

                            self.subunitselectedborder.pop(self.subunit_selected.pos)
                            self.battleui.add(self.subunitselectedborder)
                            self.gameui[2].valueinput(who=self.subunit_selected.who, weaponlist=self.allweapon, armourlist=self.allarmour,
                                                      splithappen=self.splithappen)
                        self.battleui.remove(*self.leadernow)

                        self.addbehaviourui(whoinput, elsecheck=True)

                        if self.splithappen:  # end split check
                            self.splithappen = False

                    else:  # Update topbar and command ui value every 1.1 seconds
                        if self.ui_timer >= 1.1:
                            self.gameui[0].valueinput(who=whoinput, splithappen=self.splithappen)
                            self.gameui[1].valueinput(who=whoinput, splithappen=self.splithappen)
                    if self.inspectbutton.rect.collidepoint(self.mousepos) or (
                            mouse_up and self.inspectui and self.newarmyclick):  # mouse on inspect ui open/close button
                        if self.inspectbutton.rect.collidepoint(self.mousepos):
                            self.button_name_popup.pop(self.mousepos, "Inspect Subunit")
                            self.battleui.add(self.button_name_popup)
                            if mouse_right:
                                self.uiclick = True  # for some reason the loop mouse check above does not work for inspect button, so it here instead
                        if mouse_up:
                            if self.inspectui is False:  # Add army inspect ui when left click at ui button or when change subunit with inspect open
                                self.inspectui = True
                                self.battleui.add(*self.gameui[2:4])
                                self.battleui.add(*self.unitcardbutton)
                                self.subunit_selected = None

                                for index, subunit in enumerate(whoinput.subunit_sprite_array.flat):
                                    if subunit is not None:
                                        self.inspectsubunit[index].addsubunit(subunit)
                                        self.battleui.add(self.inspectsubunit[index])
                                        if self.subunit_selected is None:
                                            self.subunit_selected = self.inspectsubunit[index]

                                self.subunitselectedborder.pop(self.subunit_selected.pos)
                                self.battleui.add(self.subunitselectedborder)
                                self.gameui[2].valueinput(who=self.subunit_selected.who, weaponlist=self.allweapon, armourlist=self.allarmour,
                                                          splithappen=self.splithappen)

                                if self.gameui[2].option == 2:  # blit skill icon is previous mode is skill
                                    self.traitskillblit()
                                    self.effecticonblit()
                                    self.countdownskillicon()

                            elif self.inspectui:  # Remove when click again and the ui already open
                                self.battleui.remove(*self.inspectsubunit)
                                self.battleui.remove(self.subunitselectedborder)
                                for ui in self.gameui[2:4]:
                                    ui.kill()
                                for button in self.unitcardbutton:
                                    button.kill()
                                self.inspectui = False
                                self.newarmyclick = False

                    elif self.gameui[1] in self.battleui and (
                            self.gameui[1].rect.collidepoint(self.mousepos) or keypress is not None):  # mouse position on command ui
                        if whoinput.control:
                            if self.switch_button[0].rect.collidepoint(self.mousepos) or keypress == pygame.K_g:
                                if mouse_up or keypress == pygame.K_g:  # rotate skill condition when clicked
                                    whoinput.skill_cond += 1
                                    if whoinput.skill_cond > 3:
                                        whoinput.skill_cond = 0
                                    self.switch_button[0].event = whoinput.skill_cond
                                if self.switch_button[0].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                    poptext = ("Free Skill Use", "Conserve 50% Stamina", "Conserve 25% stamina", "Forbid Skill")
                                    self.button_name_popup.pop(self.mousepos, poptext[self.switch_button[0].event])
                                    self.battleui.add(self.button_name_popup)

                            elif self.switch_button[1].rect.collidepoint(self.mousepos) or keypress == pygame.K_f:
                                if mouse_up or keypress == pygame.K_f:  # rotate fire at will condition when clicked
                                    whoinput.fireatwill += 1
                                    if whoinput.fireatwill > 1:
                                        whoinput.fireatwill = 0
                                    self.switch_button[1].event = whoinput.fireatwill
                                if self.switch_button[1].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                    poptext = ("Fire at will", "Hold fire until order")
                                    self.button_name_popup.pop(self.mousepos, poptext[self.switch_button[1].event])
                                    self.battleui.add(self.button_name_popup)

                            elif self.switch_button[2].rect.collidepoint(self.mousepos) or keypress == pygame.K_h:
                                if mouse_up or keypress == pygame.K_h:  # rotate hold condition when clicked
                                    whoinput.hold += 1
                                    if whoinput.hold > 2:
                                        whoinput.hold = 0
                                    self.switch_button[2].event = whoinput.hold
                                if self.switch_button[2].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                    poptext = ("Aggressive", "Skirmish/Scout", "Hold Ground")
                                    self.button_name_popup.pop(self.mousepos, poptext[self.switch_button[2].event])
                                    self.battleui.add(self.button_name_popup)

                            elif self.switch_button[3].rect.collidepoint(self.mousepos) or keypress == pygame.K_j:
                                if mouse_up or keypress == pygame.K_j:  # rotate min range condition when clicked
                                    whoinput.use_min_range += 1
                                    if whoinput.use_min_range > 1:
                                        whoinput.use_min_range = 0
                                    self.switch_button[3].event = whoinput.use_min_range
                                if self.switch_button[3].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                    poptext = ("Minimum Shoot Range", "Maximum Shoot range")
                                    self.button_name_popup.pop(self.mousepos, poptext[self.switch_button[3].event])
                                    self.battleui.add(self.button_name_popup)

                            elif self.switch_button[4].rect.collidepoint(self.mousepos) or keypress == pygame.K_j:
                                if mouse_up or keypress == pygame.K_j:  # rotate min range condition when clicked
                                    whoinput.shoothow += 1
                                    if whoinput.shoothow > 2:
                                        whoinput.shoothow = 0
                                    self.switch_button[4].event = whoinput.shoothow
                                if self.switch_button[4].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                    poptext = ("Both Arc and Direct Shot", "Only Arc Shot", "Only Direct Shot")
                                    self.button_name_popup.pop(self.mousepos, poptext[self.switch_button[4].event])
                                    self.battleui.add(self.button_name_popup)

                            elif self.switch_button[5].rect.collidepoint(self.mousepos) or keypress == pygame.K_j:
                                if mouse_up or keypress == pygame.K_j:  # rotate min range condition when clicked
                                    whoinput.runtoggle += 1
                                    if whoinput.runtoggle > 1:
                                        whoinput.runtoggle = 0
                                    self.switch_button[5].event = whoinput.runtoggle
                                if self.switch_button[5].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                    poptext = ("Toggle Walk", "Toggle Run")
                                    self.button_name_popup.pop(self.mousepos, poptext[self.switch_button[5].event])
                                    self.battleui.add(self.button_name_popup)

                            elif self.switch_button[6].rect.collidepoint(self.mousepos):  # or keypress == pygame.K_j
                                if mouse_up:  # or keypress == pygame.K_j  # rotate min range condition when clicked
                                    whoinput.attackmode += 1
                                    if whoinput.attackmode > 2:
                                        whoinput.attackmode = 0
                                    self.switch_button[6].event = whoinput.attackmode
                                if self.switch_button[6].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                    poptext = ("Frontline Attack Only", "Keep Formation", "All Out Attack")
                                    self.button_name_popup.pop(self.mousepos, poptext[self.switch_button[6].event])
                                    self.battleui.add(self.button_name_popup)

                            elif self.col_split_button in self.battleui and self.col_split_button.rect.collidepoint(self.mousepos):
                                self.button_name_popup.pop(self.mousepos, "Split By Middle Column")
                                self.battleui.add(self.button_name_popup)
                                if mouse_up and whoinput.state != 10:
                                    self.splitunit(whoinput, 1)
                                    self.splithappen = True
                                    self.checksplit(whoinput)
                                    self.battleui.remove(*self.leadernow)
                                    self.leadernow = whoinput.leader
                                    self.battleui.add(*self.leadernow)
                                    self.setup_armyicon()

                            elif self.rowsplitbutton in self.battleui and self.rowsplitbutton.rect.collidepoint(self.mousepos):
                                self.button_name_popup.pop(self.mousepos, "Split by Middle Row")
                                self.battleui.add(self.button_name_popup)
                                if mouse_up and whoinput.state != 10:
                                    self.splitunit(whoinput, 0)
                                    self.splithappen = True
                                    self.checksplit(whoinput)
                                    self.battleui.remove(*self.leadernow)
                                    self.leadernow = whoinput.leader
                                    self.battleui.add(*self.leadernow)
                                    self.setup_armyicon()

                            elif self.buttonui[7].rect.collidepoint(self.mousepos):  # decimation effect
                                self.button_name_popup.pop(self.mousepos, "Decimation")
                                self.battleui.add(self.button_name_popup)
                                if mouse_up and whoinput.state == 0:
                                    for subunit in whoinput.subunit_sprite:
                                        subunit.status_effect[98] = self.gameunitstat.status_list[98].copy()
                                        subunit.unit_health -= round(subunit.unit_health * 0.1)
                        if self.leader_mouseover(mouse_right):
                            self.battleui.remove(self.button_name_popup)
                            pass
                    else:
                        self.battleui.remove(self.leaderpopup)  # remove leader name popup if no mouseover on any button
                        self.battleui.remove(self.button_name_popup)  # remove popup if no mouseover on any button

                    if self.inspectui:  # if inspect ui is openned
                        # self.battleui.add(*self.inspectsubunit)
                        if mouse_up or mouse_right:
                            if self.gameui[3].rect.collidepoint(self.mousepos):  # if mouse pos inside armybox ui when click
                                self.clickany = True  # for avoding right click or  subunit
                                self.uiclick = True  # for avoiding clicking subunit under ui
                                for subunit in self.inspectsubunit:
                                    if subunit.rect.collidepoint(
                                            self.mousepos) and subunit in self.battleui:  # Change showing stat to the clicked subunit one
                                        if mouse_up:
                                            self.subunit_selected = subunit
                                            self.subunitselectedborder.pop(self.subunit_selected.pos)
                                            self.eventlog.addlog(
                                                [0, str(self.subunit_selected.who.board_pos) + " " + str(self.subunit_selected.who.name) + " in " +
                                                 self.subunit_selected.who.parentunit.leader[0].name + "'s parentunit is selected"], [3])
                                            self.battleui.add(self.subunitselectedborder)
                                            self.gameui[2].valueinput(who=self.subunit_selected.who, weaponlist=self.allweapon,
                                                                      armourlist=self.allarmour, splithappen=self.splithappen)

                                            if self.gameui[2].option == 2:
                                                self.traitskillblit()
                                                self.effecticonblit()
                                                self.countdownskillicon()
                                            else:
                                                for icon in self.skill_icon.sprites():
                                                    icon.kill()
                                                for icon in self.effect_icon.sprites():
                                                    icon.kill()

                                        elif mouse_right:
                                            self.popout_lorebook(3, subunit.who.unitid)
                                        break

                            elif self.gameui[2].rect.collidepoint(self.mousepos):  # mouse position in subunit card
                                self.clickany = True
                                self.uiclick = True  # for avoiding clicking subunit under ui
                                self.unitcardbutton_click(self.subunit_selected.who)

                        if (self.ui_timer >= 1.1 and self.gameui[2].option != 0) or \
                                self.before_selected != self.last_selected:  # Update value of the clicked subunit every 1.1 second
                            self.gameui[2].valueinput(who=self.subunit_selected.who, weaponlist=self.allweapon, armourlist=self.allarmour,
                                                      splithappen=self.splithappen)
                            if self.gameui[2].option == 2:  # skill and status effect card
                                self.countdownskillicon()
                                self.effecticonblit()
                                if self.before_selected != self.last_selected:  # change subunit, reset trait icon as well
                                    self.traitskillblit()
                                    self.countdownskillicon()
                            else:
                                for icon in self.skill_icon.sprites():
                                    icon.kill()
                                for icon in self.effect_icon.sprites():
                                    icon.kill()

                        if self.gameui[2].option == 2:
                            if self.effecticon_mouseover(self.skill_icon, mouse_right):
                                pass
                            elif self.effecticon_mouseover(self.effect_icon, mouse_right):
                                pass
                            else:
                                self.battleui.remove(self.effectpopup)

                    else:
                        for icon in self.skill_icon.sprites():
                            icon.kill()
                        for icon in self.effect_icon.sprites():
                            icon.kill()

                    if mouse_right and self.uiclick is False:  # Unit command
                        whoinput.command(self.battle_mouse_pos[1], mouse_right, double_mouse_right,
                                         self.last_mouseover, keystate)

                    self.before_selected = self.last_selected

                    if self.ui_timer >= 1.1:  # reset ui timer every 1.1 seconds
                        self.ui_timer -= 1.1
                # ^ End subunit selected code

                # fight_sound.play()

                # v Drama text function
                if self.drama_timer == 0 and len(self.textdrama.queue) != 0:  # Start timer and add to allui If there is event queue
                    self.battleui.add(self.textdrama)
                    self.textdrama.processqueue()
                    self.drama_timer = 0.1
                elif self.drama_timer > 0:
                    self.textdrama.playanimation()
                    self.drama_timer += self.uidt
                    if self.drama_timer > 3:
                        self.drama_timer = 0
                        self.battleui.remove(self.textdrama)
                # ^ End drama

                # v Updater
                for unit in self.allunitlist:
                    unit.collide = False  # reset collide

                if len(self.allsubunitlist) > 1:
                    tree = KDTree([sprite.base_pos for sprite in self.allsubunitlist])  # collision loop check, much faster than pygame collide check
                    collisions = tree.query_pairs(self.collidedistance)
                    for one, two in collisions:
                        spriteone = self.allsubunitlist[one]
                        spritetwo = self.allsubunitlist[two]
                        if spriteone.parentunit != spritetwo.parentunit:  # collide with subunit in other unit
                            if spriteone.front_pos.distance_to(spritetwo.base_pos) < self.frontdistance:  # first subunit collision
                                spriteone.enemy_front.append(spritetwo)
                                spriteone.parentunit.collide = True
                            else:
                                spriteone.enemy_side.append(spritetwo)
                            if spritetwo.front_pos.distance_to(spriteone.base_pos) < self.frontdistance:  # second subunit
                                spritetwo.enemy_front.append(spriteone)
                                spritetwo.parentunit.collide = True
                            else:
                                spritetwo.enemy_side.append(spriteone)
                        else:  # collide with subunit in same unit
                            if spriteone.front_pos.distance_to(spritetwo.base_pos) < self.frontdistance:  # first subunit collision
                                if spritetwo.state != 99:
                                    spriteone.friend_front.append(spritetwo)
                            if spritetwo.front_pos.distance_to(spriteone.base_pos) < self.frontdistance:  # second subunit
                                # if spriteone.frontline:
                                if spriteone.state != 99:
                                    spritetwo.friend_front.append(spriteone)

                self.subunitposarray = self.mapmovearray.copy()
                for subunit in self.allsubunitlist:
                    for y in subunit.posrange[0]:
                        for x in subunit.posrange[1]:
                            self.subunitposarray[x][y] = 0

                self.unit_updater.update(self.currentweather, self.subunit, self.dt, self.camerascale,
                                         self.battle_mouse_pos[0], mouse_up)
                self.last_mouseover = None  # reset last parentunit mouse over

                self.leader_updater.update()
                self.subunit_updater.update(self.currentweather, self.dt, self.camerascale, self.combattimer,
                                            self.battle_mouse_pos[0], mouse_up)

                # v Run pathfinding for melee combat no more than limit number of sub-unit per update to prevent stutter
                if len(self.combatpathqueue) > 0:
                    run = 0
                    while len(self.combatpathqueue) > 0 and run < 5:
                        self.combatpathqueue[0].combat_pathfind()
                        self.combatpathqueue = self.combatpathqueue[1:]
                        run += 1
                # ^ End melee pathfinding

                if self.ui_timer > 1:
                    self.scaleui.changefightscale(self.teamtroopnumber)  # change fight colour scale on timeui bar
                    self.lastteamtroopnumber = self.teamtroopnumber

                if self.combattimer >= 0.5:  # reset combat timer every 0.5 seconds
                    self.combattimer -= 0.5  # not reset to 0 because higher speed can cause inconsistency in update timing

                self.effect_updater.update(self.subunit, self.dt, self.camerascale)
                self.weather_updater.update(self.dt, self.timenumber.timenum)
                self.minimap.update(self.camerascale, [self.camerapos, self.cameraupcorner], self.team1poslist, self.team2poslist)
                # ^ End battle updater

                # v Remove the subunit ui when click at no group
                if self.clickany is False:  # not click at any parentunit
                    if self.last_selected is not None:  # any parentunit is selected
                        self.last_selected = None  # reset last_selected

                    self.gameui[2].option = 1  # reset subunit card option
                    for ui in self.gameui:
                        ui.kill()  # remove ui
                    for button in self.buttonui[0:8]:
                        button.kill()  # remove button
                    for icon in self.skill_icon.sprites():
                        icon.kill()  # remove skill and trait icon
                    for icon in self.effect_icon.sprites():
                        icon.kill()  # remove effect icon
                    self.battleui.remove(*self.switch_button)  # remove change parentunit behaviour button
                    self.battleui.remove(*self.inspectsubunit)  # remove subunit sprite in army inspect ui
                    self.inspectui = False  # inspect ui close
                    self.before_selected = None  # reset before selected parentunit after remove last selected
                    self.battleui.remove(*self.leadernow)  # remove leader image from command ui
                    self.subunit_selected = None  # reset subunit selected
                    self.battleui.remove(self.subunitselectedborder)  # remove subunit selected border sprite
                    self.leadernow = []  # clear leader list in command ui
                # ^ End remove

                # v Update game time
                self.dt = self.clock.get_time() / 1000  # dt before gamespeed
                self.ui_timer += self.dt  # ui update by real time instead of game time to reduce workload
                self.uidt = self.dt  # get ui timer before apply game

                self.dt = self.dt * self.gamespeed  # apply dt with gamespeed for ingame calculation
                if self.dt > 0.1:
                    self.dt = 0.1  # make it so stutter does not cause sprite to clip other sprite especially when zoom change

                self.combattimer += self.dt  # update combat timer
                self.timenumber.timerupdate(self.dt * 10)  # update ingame time with 5x speed
                # ^ End update game time

            elif self.gamestate == 2:  # uniteditor state
                if self.popup_listbox in self.battleui and self.popup_listbox.type == "leader" \
                        and self.popup_listbox.rect.collidepoint(self.mousepos):  # this need to be at the top here to prioritise popup click
                    self.battleui.remove(self.leaderpopup)
                    for index, name in enumerate(self.popupnamegroup):  # change leader with the new selected one
                        if name.rect.collidepoint(self.mousepos):
                            if mouse_up and self.showincard.name != "None":
                                if self.leadernow[self.selectleader].name != "None":  # remove leader from previous slot first
                                    self.leadernow[self.selectleader].leader = None
                                    self.leadernow[self.selectleader].subunit.leader = None

                                trueindex = [index for index, value in
                                             enumerate(list(self.leader_stat.leader_list.values())) if value[0] == name.name][0]
                                trueindex = list(self.leader_stat.leader_list.keys())[trueindex]
                                self.leadernow[self.selectleader].change_leader(trueindex, self.leader_stat)
                                self.leadernow[self.selectleader].subunit = self.showincard
                                self.showincard.leader = self.leadernow[self.selectleader]
                                self.previewauthority(self.leadernow, self.leadernow[self.selectleader].subunit.armyid)
                                self.gameui[2].valueinput(who=self.showincard, weaponlist=self.allweapon, armourlist=self.allarmour,
                                                          changeoption=1)
                            elif mouse_right:
                                self.popout_lorebook(8, self.currentpopuprow + index + 1)

                elif self.army_listbox.rect.collidepoint(self.mousepos):
                    for index, name in enumerate(self.armypresetnamegroup):
                        if name.rect.collidepoint(self.mousepos) and mouse_up:
                            if list(self.customarmypresetlist.keys())[index] != "New Preset":
                                armylist = []
                                arraylist = list(self.customarmypresetlist[list(self.customarmypresetlist.keys())[index]])
                                for listnum in (0, 1, 2, 3, 4, 5, 6, 7):
                                    armylist += [int(item) if item.isdigit() else item
                                                 for item in arraylist[listnum].split(",")]
                                leaderwholist = [int(item) if item.isdigit() else item
                                                 for item in arraylist[8].split(",")]
                                leaderposlist = [int(item) if item.isdigit() else item
                                                 for item in arraylist[9].split(",")]

                                for armyindex, item in enumerate(armylist):  # change all slot to whatever save in the selected preset
                                    for slot in self.armybuildslot:
                                        if slot.gameid == armyindex:
                                            slot.changetroop(item, self.baseterrain,
                                                             self.baseterrain * len(self.battlemap_feature.featurelist)
                                                             + self.featureterrain, self.currentweather)
                                            break

                                for leaderindex, item in enumerate(leaderwholist):
                                    self.previewleader[leaderindex].leader = None
                                    if self.previewleader[leaderindex].subunit is not None:
                                        self.previewleader[leaderindex].subunit.leader = None

                                    self.previewleader[leaderindex].change_leader(item, self.leader_stat)

                                    posindex = 0
                                    for slot in self.armybuildslot:  # can't use gameid here as none subunit not count in position check
                                        if posindex == leaderposlist[leaderindex]:
                                            self.previewleader[leaderindex].subunit = slot
                                            slot.leader = self.previewleader[leaderindex]
                                            break
                                        else:
                                            if slot.name != "None":
                                                posindex += 1

                                # self.previewauthority(self.previewleader, 0)  # calculate authority

                            else:  # new preset
                                for slot in self.armybuildslot:  # reset all sub-subunit slot
                                    slot.changetroop(0, self.baseterrain,
                                                     self.baseterrain * len(self.battlemap_feature.featurelist) + self.featureterrain,
                                                     self.currentweather)
                                    slot.leader = None  # remove leader link in

                                for leader in self.previewleader:
                                    leader.subunit = None  # remove subunit link in leader
                                    leader.change_leader(1, self.leader_stat)

                                # self.gameui[2].valueinput(attacker=self.showincard, weapon_list=self.allweapon, armour_list=self.allarmour,
                                #                       changeoption=1)

                elif self.gameui[1].rect.collidepoint(self.mousepos):
                    for leaderindex, leader in enumerate(self.leadernow):  # loop mouse pos on leader portrait
                        if leader.rect.collidepoint(self.mousepos):
                            armyposition = self.leaderposname[leader.armyposition + 4]

                            self.leaderpopup.pop(self.mousepos, armyposition + ": " + leader.name)  # popup leader name when mouse over
                            self.battleui.add(self.leaderpopup)

                            if mouse_up:  # open list of leader to change leader in that slot
                                self.selectleader = leaderindex
                                self.popuplist_newopen(leader.rect.midright, self.leader_list, "leader")

                            elif mouse_right:
                                self.popout_lorebook(8, leader.gameid)
                            break
                        else:
                            self.battleui.remove(self.leaderpopup)

                elif self.gameui[2].rect.collidepoint(self.mousepos):
                    if self.showincard is not None and mouse_up:
                        self.unitcardbutton_click(self.showincard)

                    if self.gameui[2].option == 2:
                        for iconlist in (self.effect_icon, self.skill_icon):
                            if self.effecticon_mouseover(self.skill_icon, mouse_right):
                                pass
                            elif self.effecticon_mouseover(self.effect_icon, mouse_right):
                                pass
                            else:
                                self.battleui.remove(self.effectpopup)

                elif mouse_up or mouse_down or mouse_right:  # accept both click and hold left mouse button
                    if mouse_up or mouse_down:
                        if self.popup_listbox in self.battleui:
                            if self.popup_listbox.rect.collidepoint(self.mousepos):
                                for index, name in enumerate(self.popupnamegroup):
                                    if name.rect.collidepoint(self.mousepos) and mouse_up:
                                        if self.popup_listbox.type == "terrain":
                                            self.terrain_change_button.changetext(self.battlemap_base.terrainlist[index])
                                            self.baseterrain = index
                                            self.editor_map_change(gamemap.terraincolour[self.baseterrain],
                                                                   gamemap.featurecolour[self.featureterrain])

                                        elif self.popup_listbox.type == "feature":
                                            self.feature_change_button.changetext(self.battlemap_feature.featurelist[index])
                                            self.featureterrain = index
                                            self.editor_map_change(gamemap.terraincolour[self.baseterrain],
                                                                   gamemap.featurecolour[self.featureterrain])

                                        elif self.popup_listbox.type == "weather":
                                            self.weathertype = int(index / 3)
                                            self.weatherstrength = index - (self.weathertype * 3)
                                            self.weather_change_button.changetext(self.weather_list[index])
                                            del self.currentweather
                                            self.currentweather = gameweather.Weather(self.timeui, self.weathertype + 1, self.weatherstrength,
                                                                                      self.allweather)

                                        for slot in self.armybuildslot:  # reset all troop stat
                                            slot.changetroop(slot.troopindex, self.baseterrain,
                                                             self.baseterrain * len(
                                                                 self.battlemap_feature.featurelist) + self.featureterrain,
                                                             self.currentweather)
                                            if slot.selected and slot.name != "None":  # reset subunit card as well
                                                self.gameui[1].valueinput(who=self.showincard)
                                                self.gameui[2].valueinput(who=self.showincard, weaponlist=self.allweapon,
                                                                          armourlist=self.allarmour,
                                                                          changeoption=1)
                                                if self.gameui[2].option == 2:
                                                    self.traitskillblit()
                                                    self.effecticonblit()
                                                    self.countdownskillicon()

                                        for name in self.popupnamegroup:  # remove troop name list
                                            name.kill()
                                            del name

                                        self.battleui.remove(self.popup_listbox, self.popup_listscroll)
                                        break

                            elif self.popup_listscroll.rect.collidepoint(self.mousepos):
                                self.currentpopuprow = self.popup_listscroll.update(
                                    self.mousepos)  # update the scroller and get new current subsection
                                if self.popup_listbox.type == "terrain":
                                    self.main.setuplist(gameprepare.Namelist, self.currentpopuprow, self.battlemap_base.terrainlist,
                                                        self.popupnamegroup, self.popup_listbox, self.battleui, layer=17)
                                elif self.popup_listbox.type == "feature":
                                    self.main.setuplist(gameprepare.Namelist, self.currentpopuprow, self.battlemap_feature.featurelist,
                                                        self.popupnamegroup, self.popup_listbox, self.battleui, layer=17)
                                elif self.popup_listbox.type == "weather":
                                    self.main.setuplist(gameprepare.Namelist, self.currentpopuprow, self.weather_list, self.popupnamegroup,
                                                        self.popup_listbox, self.battleui, layer=17)
                                elif self.popup_listbox.type == "leader":
                                    self.main.setuplist(gameprepare.Namelist, self.currentpopuprow, self.leader_list, self.popupnamegroup,
                                                        self.popup_listbox, self.battleui, layer=17)

                            else:
                                self.battleui.remove(self.popup_listbox, self.popup_listscroll, *self.popupnamegroup)

                        elif self.troop_scroll.rect.collidepoint(self.mousepos):  # click on subsection list scroller
                            self.current_troop_row = self.troop_scroll.update(
                                self.mousepos)  # update the scroller and get new current subsection
                            if self.current_list_show == "troop":
                                self.main.setuplist(gameprepare.Namelist, self.current_troop_row, self.troop_list, self.troopnamegroup,
                                                    self.troop_listbox, self.battleui)
                            elif self.current_list_show == "faction":
                                self.main.setuplist(gameprepare.Namelist, self.current_troop_row, self.faction_list, self.troopnamegroup,
                                                    self.troop_listbox, self.battleui)

                        elif self.army_presetname_scroll.rect.collidepoint(self.mousepos):
                            self.current_army_row = self.army_presetname_scroll.update(
                                self.mousepos)  # update the scroller and get new current subsection
                            self.main.setuplist(gameprepare.Namelist, self.current_army_row, list(self.customarmypresetlist.keys()),
                                                self.armypresetnamegroup, self.army_listbox, self.battleui)  # setup preset army list

                        else:
                            slotclick = None
                            for slot in self.armybuildslot:  # left click on any sub-subunit slot
                                if slot.rect.collidepoint(self.mousepos):
                                    slotclick = slot
                                    break

                            if slotclick is not None:
                                if keystate[pygame.K_LSHIFT]:  # add all sub-subunit from the first selected
                                    firstone = None
                                    for newslot in self.armybuildslot:
                                        if newslot.armyid == slotclick.armyid and newslot.gameid <= slotclick.gameid:
                                            if firstone is None and newslot.selected:  # found the previous selected sub-subunit
                                                firstone = newslot.gameid
                                                if slotclick.gameid <= firstone:  # cannot go backward, stop loop
                                                    break
                                                else:  # forward select, acceptable
                                                    slotclickselected = True
                                                    self.uniteditborder.add(gameui.Selectedsquad(slotclick.inspposition, 5))
                                                    self.battleui.add(*self.uniteditborder)
                                            elif firstone is not None and newslot.gameid > firstone and newslot.selected is False:  # select from first select to clicked
                                                newslot.selected = True
                                                self.uniteditborder.add(gameui.Selectedsquad(newslot.inspposition, 5))
                                                self.battleui.add(*self.uniteditborder)

                                elif keystate[pygame.K_LCTRL]:  # add another selected sub-subunit with left ctrl + left mouse button
                                    slotclick.selected = True
                                    self.uniteditborder.add(gameui.Selectedsquad(slotclick.inspposition, 5))
                                    self.battleui.add(*self.uniteditborder)

                                else:  # select one sub-subunit by normal left click
                                    for border in self.uniteditborder:  # remove all other border
                                        border.kill()
                                        del border
                                    for newslot in self.armybuildslot:
                                        newslot.selected = False
                                    slotclick.selected = True
                                    self.uniteditborder.add(gameui.Selectedsquad(slotclick.inspposition, 5))
                                    self.battleui.add(*self.uniteditborder)

                                    if slotclick.name != "None":
                                        self.battleui.remove(*self.leadernow)
                                        self.leadernow = [leader for leader in self.previewleader]
                                        self.battleui.add(*self.leadernow)  # add leader portrait to draw
                                        self.showincard = slot
                                        self.gameui[1].valueinput(who=self.showincard)
                                        self.gameui[2].valueinput(who=self.showincard, weaponlist=self.allweapon,
                                                                  armourlist=self.allarmour)  # update subunit card on selected subunit
                                        if self.gameui[2].option == 2:
                                            self.traitskillblit()
                                            self.effecticonblit()
                                            self.countdownskillicon()

                    if mouse_up or mouse_right:
                        if self.troop_listbox.rect.collidepoint(self.mousepos):
                            for index, name in enumerate(self.troopnamegroup):
                                if name.rect.collidepoint(self.mousepos):
                                    if self.current_list_show == "faction":
                                        self.current_troop_row = 0

                                        if mouse_up:
                                            if index != 0:  # pick faction
                                                self.troop_list = [item[1][0] for item in self.gameunitstat.unit_list.items()
                                                                   if item[1][0] == "None" or
                                                                   item[0] in self.allfaction.faction_list[index][1]]
                                                self.troop_index_list = [0] + self.allfaction.faction_list[index][1]

                                                self.leader_list = [item[1][0] for thisindex, item in
                                                                    enumerate(self.leader_stat.leader_list.items())
                                                                    if thisindex > 0 and (item[1][0] == "None" or
                                                                                          (item[0] >= 10000 and item[1][8] in (0, index)) or
                                                                                          item[0] in self.allfaction.faction_list[index][2])]

                                            else:  # pick all faction
                                                self.troop_list = [item[0] for item in self.gameunitstat.unit_list.values()][1:]
                                                self.troop_index_list = list(range(0, len(self.troop_list) + 1))

                                                self.leader_list = self.leader_list = [item[0] for item in
                                                                                       self.leader_stat.leader_list.values()][1:]

                                            self.main.setuplist(gameprepare.Namelist, self.current_troop_row, self.troop_list, self.troopnamegroup,
                                                                self.troop_listbox, self.battleui)  # setup troop name list
                                            self.troop_scroll.changeimage(newrow=self.current_troop_row,
                                                                          logsize=len(self.troop_list))  # change troop scroll image

                                            self.main.maketeamcoa([index], uiclass=self.battleui, oneteam=True,
                                                                  team1setpos=(self.troop_listbox.rect.midleft[0] - int((200 * self.widthadjust) / 2),
                                                                               self.troop_listbox.rect.midleft[1]))  # change team coa

                                            self.current_list_show = "troop"

                                        elif mouse_right:
                                            self.popout_lorebook(2, index)

                                    elif self.current_list_show == "troop":
                                        if mouse_up:
                                            for slot in self.armybuildslot:
                                                if slot.selected:
                                                    if keystate[pygame.K_LSHIFT]:  # change all sub-subunit in army
                                                        for newslot in self.armybuildslot:
                                                            if newslot.armyid == slot.armyid:
                                                                newslot.changetroop(self.troop_index_list[index + self.current_troop_row],
                                                                                    self.baseterrain,
                                                                                    self.baseterrain * len(self.battlemap_feature.featurelist)
                                                                                    + self.featureterrain, self.currentweather)

                                                    else:
                                                        slot.changetroop(self.troop_index_list[index + self.current_troop_row],
                                                                         self.baseterrain,
                                                                         self.baseterrain * len(
                                                                             self.battlemap_feature.featurelist) + self.featureterrain,
                                                                         self.currentweather)

                                                    if slot.name != "None":  # update information of subunit that just got changed
                                                        self.battleui.remove(*self.leadernow)
                                                        self.leadernow = [leader for leader in self.previewleader]
                                                        self.battleui.add(*self.leadernow)  # add leader portrait to draw
                                                        self.showincard = slot
                                                        self.previewauthority(self.leadernow, slot.armyid)
                                                        self.gameui[2].valueinput(who=self.showincard, weaponlist=self.allweapon,
                                                                                  armourlist=self.allarmour)  # update subunit card on selected subunit
                                                        if self.gameui[2].option == 2:
                                                            self.traitskillblit()
                                                            self.effecticonblit()
                                                            self.countdownskillicon()
                                                    elif slot.name == "None" and slot.leader is not None:  # remove leader from none subunit if any
                                                        slot.leader.change_leader(1, self.leader_stat)
                                                        slot.leader.subunit = None  # remove subunit link in leader
                                                        slot.leader = None  # remove leader link in subunit
                                                        self.previewauthority(self.leadernow, slot.armyid)

                                        elif mouse_right:  # upen encyclopedia
                                            self.popout_lorebook(3, self.troop_index_list[index + self.current_troop_row])
                                    break

                        elif mouse_up:
                            if self.filterbox.rect.collidepoint(self.mousepos):
                                if self.teamchange_button.rect.collidepoint(self.mousepos):
                                    if self.teamchange_button.event == 0:
                                        self.teamchange_button.event = 1

                                    elif self.teamchange_button.event == 1:
                                        self.teamchange_button.event = 0

                                    for slot in self.armybuildslot:
                                        slot.team = self.teamchange_button.event + 1
                                        slot.changeteam()

                                elif self.slotdisplay_button.rect.collidepoint(self.mousepos):
                                    if self.slotdisplay_button.event == 0:
                                        self.slotdisplay_button.event = 1
                                        self.battleui.remove(*self.armybuildslot, *self.uniteditborder)

                                    elif self.slotdisplay_button.event == 1:
                                        self.slotdisplay_button.event = 0
                                        self.battleui.add(*self.armybuildslot, *self.uniteditborder)

                                elif self.deploy_button.rect.collidepoint(self.mousepos):
                                    pass

                            elif self.terrain_change_button.rect.collidepoint(self.mousepos):  # change map terrain button
                                self.popuplist_newopen(self.terrain_change_button.rect.midtop, self.battlemap_base.terrainlist, "terrain")

                            elif self.feature_change_button.rect.collidepoint(self.mousepos):  # change map feature button
                                self.popuplist_newopen(self.feature_change_button.rect.midtop, self.battlemap_feature.featurelist, "feature")

                            elif self.weather_change_button.rect.collidepoint(self.mousepos):  # change map weather button
                                self.popuplist_newopen(self.weather_change_button.rect.midtop, self.weather_list, "weather")

                            for team in self.teamcoa:
                                if team.rect.collidepoint(self.mousepos):
                                    if self.current_list_show == "troop":
                                        self.current_troop_row = 0
                                        self.main.setuplist(gameprepare.Namelist, self.current_troop_row, self.faction_list, self.troopnamegroup,
                                                            self.troop_listbox, self.battleui)
                                        self.troop_scroll.changeimage(newrow=self.current_troop_row,
                                                                      logsize=len(self.faction_list))  # change troop scroll image
                                        self.current_list_show = "faction"

            else:  # Complete game pause when open either esc menu or enclycopedia
                if self.battle_menu.mode == 0:  # main esc menu
                    for button in self.battle_menu_button:
                        if button.rect.collidepoint(self.mousepos):
                            button.image = button.images[1]  # change button image to mouse over one
                            if mouse_up:  # click on button
                                button.image = button.images[2]  # change button image to clicked one
                                if button.text == "Resume":  # resume game
                                    self.gamestate = self.previous_gamestate  # resume battle gameplay state
                                    self.battleui.remove(self.battle_menu, *self.battle_menu_button, *self.escslidermenu,
                                                         *self.escvaluebox)  # remove menu sprite

                                elif button.text == "Encyclopedia":  # open encyclopedia
                                    self.battle_menu.mode = 2  # change to enclycopedia mode
                                    self.battleui.add(self.lorebook, self.lorenamelist, self.lorescroll,
                                                      *self.lorebuttonui)  # add sprite related to encyclopedia
                                    self.lorebook.change_section(0, self.lorenamelist, self.subsection_name, self.lorescroll, self.pagebutton,
                                                                 self.battleui)
                                    # self.lorebook.setupsubsectionlist(self.lorenamelist, listgroup)

                                elif button.text == "Option":  # open option menu
                                    self.battle_menu.changemode(1)  # change to option menu mode
                                    self.battleui.remove(*self.battle_menu_button)  # remove main esc menu button
                                    self.battleui.add(*self.escoptionmenubutton, *self.escslidermenu, *self.escvaluebox)
                                    self.oldsetting = self.escslidermenu[0].value  # Save previous setting for in case of cancel

                                elif button.text == "Main Menu":  # back to main menu
                                    self.battleui.clear(self.screen, self.background)  # remove all sprite
                                    self.battlecamera.clear(self.screen, self.background)  # remove all sprite

                                    self.battleui.remove(self.battle_menu, *self.battle_menu_button, *self.escslidermenu,
                                                         *self.escvaluebox)  # remove menu

                                    for group in (self.subunit, self.armyleader, self.team0army, self.team1army, self.team2army,
                                                  self.armyicon, self.troopnumbersprite,
                                                  self.inspectsubunit):  # remove all reference from battle object
                                        for stuff in group:
                                            stuff.delete()
                                            stuff.kill()
                                            del stuff

                                    for arrow in self.arrows:  # remove all range attack
                                        arrow.kill()
                                        del arrow

                                    self.subunit_selected = None
                                    self.allunitlist = []
                                    self.combatpathqueue = []
                                    self.team0poslist, self.team1poslist, self.team2poslist = {}, {}, {}
                                    self.before_selected = None

                                    self.drama_timer = 0  # reset drama text popup
                                    self.battleui.remove(self.textdrama)

                                    if self.mode == "uniteditor":
                                        self.showincard = None

                                        self.battleui.remove(self.troop_listbox, self.teamchange_button, self.troop_scroll, self.teamcoa,
                                                             self.army_listbox, self.army_presetname_scroll, self.filterbox, self.teamchange_button,
                                                             self.slotdisplay_button, self.deploy_button, *self.unitcardbutton,
                                                             self.terrain_change_button, self.feature_change_button, self.weather_change_button,
                                                             self.timenumber, self.speednumber, *self.armybuildslot, *self.leadernow)

                                        for group in self.troopnamegroup, self.uniteditborder, self.armypresetnamegroup:
                                            for item in group:  # remove name list
                                                item.kill()
                                                del item

                                        for slot in self.armybuildslot:  # reset all sub-subunit slot
                                            slot.changetroop(0, self.baseterrain,
                                                             self.baseterrain * len(self.battlemap_feature.featurelist) + self.featureterrain,
                                                             self.currentweather)
                                            slot.leader = None  # remove leader link in

                                        for leader in self.previewleader:
                                            leader.subunit = None  # remove subunit link in leader
                                            leader.change_leader(1, self.leader_stat)

                                        del self.currentweather

                                        self.troop_list = [item[0] for item in self.gameunitstat.unit_list.values()][
                                                          1:]  # reset troop filter back to all faction
                                        self.troop_index_list = list(range(0, len(self.troop_list) + 1))

                                        self.leader_list = [item[0] for item in self.leader_stat.leader_list.values()][
                                                           1:]  # generate leader name list)

                                        self.leadernow = []

                                    return  # end battle game loop

                                elif button.text == "Desktop":  # quit game
                                    self.battleui.clear(self.screen, self.background)  # remove all sprite
                                    self.battlecamera.clear(self.screen, self.background)  # remove all sprite
                                    sys.exit()  # quit
                                break  # found clicked button, break loop
                        else:
                            button.image = button.images[0]

                elif self.battle_menu.mode == 1:  # option menu
                    for button in self.escoptionmenubutton:  # check if any button get collided with mouse or clicked
                        if button.rect.collidepoint(self.mousepos):
                            button.image = button.images[1]  # change button image to mouse over one
                            if mouse_up:  # click on button
                                button.image = button.images[2]  # change button image to clicked one
                                if button.text == "Confirm":  # confirm button, save the setting and close option menu
                                    self.oldsetting = self.mixervolume  # save mixer volume
                                    pygame.mixer.music.set_volume(self.mixervolume)  # set new music player volume
                                    main.editconfig("DEFAULT", "SoundVolume", str(slider.value), "configuration.ini", config)  # save to config file
                                    self.battle_menu.changemode(0)  # go back to main esc menu
                                    self.battleui.remove(*self.escoptionmenubutton, *self.escslidermenu,
                                                         *self.escvaluebox)  # remove option menu sprite
                                    self.battleui.add(*self.battle_menu_button)  # add main esc menu buttons back

                                elif button.text == "Apply":  # apply button, save the setting
                                    self.oldsetting = self.mixervolume  # save mixer volume
                                    pygame.mixer.music.set_volume(self.mixervolume)  # set new music player volume
                                    main.editconfig("DEFAULT", "SoundVolume", str(slider.value), "configuration.ini", config)  # save to config file

                                elif button.text == "Cancel":  # cancel button, revert the setting to the last saved one
                                    self.mixervolume = self.oldsetting  # revert to old setting
                                    pygame.mixer.music.set_volume(self.mixervolume)  # set new music player volume
                                    self.escslidermenu[0].update(self.mixervolume, self.escvaluebox[0], forcedvalue=True)  # update slider bar
                                    self.battle_menu.changemode(0)  # go back to main esc menu
                                    self.battleui.remove(*self.escoptionmenubutton, *self.escslidermenu,
                                                         *self.escvaluebox)  # remove option menu sprite
                                    self.battleui.add(*self.battle_menu_button)  # add main esc menu buttons back

                        else:  # no button currently collided with mouse
                            button.image = button.images[0]  # revert button image back to the idle one

                    for slider in self.escslidermenu:
                        if slider.rect.collidepoint(self.mousepos) and (mouse_down or mouse_up):  # mouse click on slider bar
                            slider.update(self.mousepos, self.escvaluebox[0])  # update slider button based on mouse value
                            self.mixervolume = float(slider.value / 100)  # for now only music volume slider exist

                elif self.battle_menu.mode == 2:  # Encyclopedia mode
                    if mouse_up or mouse_down:  # mouse down (hold click) only for subsection listscroller
                        if mouse_up:
                            for button in self.lorebuttonui:
                                if button in self.battleui and button.rect.collidepoint(self.mousepos):  # click button
                                    if button.event in range(0, 11):  # section button
                                        self.lorebook.change_section(button.event, self.lorenamelist, self.subsection_name, self.lorescroll,
                                                                     self.pagebutton, self.battleui)  # change to section of that button
                                    elif button.event == 19:  # Close button
                                        self.battleui.remove(self.lorebook, *self.lorebuttonui, self.lorescroll,
                                                             self.lorenamelist)  # remove enclycopedia related sprites
                                        for name in self.subsection_name:  # remove subsection name
                                            name.kill()
                                            del name
                                        self.battle_menu.changemode(0)  # change menu back to default 0
                                        if self.battle_menu not in self.battleui:  # in case open encyclopedia via right click on icon or other way
                                            self.gamestate = self.previous_gamestate  # resume gameplay
                                    elif button.event == 20:  # Previous page button
                                        self.lorebook.change_page(self.lorebook.page - 1, self.pagebutton, self.battleui)  # go back 1 page
                                    elif button.event == 21:  # Next page button
                                        self.lorebook.change_page(self.lorebook.page + 1, self.pagebutton, self.battleui)  # go forward 1 page
                                    break  # found clicked button, break loop

                            for name in self.subsection_name:  # too lazy to include break for button found to avoid subsection loop since not much optimisation is needed here
                                if name.rect.collidepoint(self.mousepos):  # click on subsection name
                                    self.lorebook.change_subsection(name.subsection, self.pagebutton, self.battleui)  # change subsection
                                    break  # found clicked subsection, break loop

                        if self.lorescroll.rect.collidepoint(self.mousepos):  # click on subsection list scroller
                            self.lorebook.current_subsection_row = self.lorescroll.update(
                                self.mousepos)  # update the scroller and get new current subsection
                            self.lorebook.setup_subsection_list(self.lorenamelist, self.subsection_name)  # update subsection name list

            self.screen.blit(self.camera.image, (0, 0))  # Draw the game camera and everything that appear in it
            self.battleui.draw(self.screen)  # Draw the UI
            pygame.display.update()  # update game display, draw everything
            self.clock.tick(60)  # clock update even if game pause

        if pygame.mixer:  # close music player
            pygame.mixer.music.fadeout(1000)

        pygame.time.wait(1000)  # wait a bit before closing
        pygame.quit()
