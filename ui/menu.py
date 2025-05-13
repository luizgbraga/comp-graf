import sys

from direct.gui.DirectGui import (
    DGG,
    DirectButton,
    DirectDialog,
    DirectLabel,
)
from panda3d.core import TextNode

MENU_BG_COLOR = (0.1, 0.1, 0.1, 0.9)
BUTTON_COLOR = (0.2, 0.2, 0.2, 0.8)
BUTTON_HOVER_COLOR = (0.3, 0.3, 0.3, 0.8)
TEXT_COLOR = (1, 1, 1, 1)
TITLE_COLOR = (1, 1, 1, 1)
COIN_COLOR = (1, 0.8, 0, 1)


class MenuManager:
    def __init__(self, game):
        self.game = game
        self.main_menu = None
        self.game_over_menu = None
        self.weapon_menu = None
        self.store_menu = None
        self.rules_menu = None
        self.setupMainMenu()
        self.setupWeaponMenu()
        self.setupStoreMenu()
        self.setupRulesMenu()

    def createButton(self, text, pos, command=None, parent=None, scale=0.07):
        return DirectButton(
            text=text,
            scale=scale,
            pos=pos,
            parent=parent,
            command=command,
            relief=DGG.FLAT,
            frameColor=BUTTON_COLOR,
            text_fg=TEXT_COLOR,
            pressEffect=1,
            rolloverSound=None,
            clickSound=None,
        )

    def createLabel(self, text, pos, parent=None, scale=0.07, align=TextNode.ACenter):
        return DirectLabel(
            text=text,
            scale=scale,
            pos=pos,
            parent=parent,
            relief=None,
            text_fg=TEXT_COLOR,
            text_align=align,
        )

    def setupMainMenu(self):
        self.main_menu = DirectDialog(
            frameSize=(-0.7, 0.7, -0.7, 0.7),
            fadeScreen=0.4,
            relief=DGG.FLAT,
            frameColor=MENU_BG_COLOR,
        )

        self.createLabel(
            "Monkey Dart Game",
            (0, 0, 0.5),
            parent=self.main_menu,
            scale=0.12,
        )

        # Main menu buttons
        button_spacing = 0.15
        start_y = 0.2
        self.createButton(
            "Start Game",
            (0, 0, start_y),
            command=self.game.startGame,
            parent=self.main_menu,
            scale=0.08,
        )
        self.createButton(
            "Store",
            (0, 0, start_y - button_spacing),
            command=self.showStore,
            parent=self.main_menu,
            scale=0.08,
        )
        self.createButton(
            "Rules",
            (0, 0, start_y - button_spacing * 2),
            command=self.showRules,
            parent=self.main_menu,
            scale=0.08,
        )
        self.createButton(
            "Quit",
            (0, 0, start_y - button_spacing * 3),
            command=sys.exit,
            parent=self.main_menu,
            scale=0.08,
        )

        # Controls section
        controls_text = (
            "Controls:\n"
            "• W, A, S, D - Move\n"
            "• Mouse - Look/Aim\n"
            "• Left Mouse Button - Shoot\n"
            "• C - Switch Camera\n"
            "• TAB - Switch Weapons"
        )
        self.createLabel(
            controls_text,
            (0, 0, -0.3),
            parent=self.main_menu,
            scale=0.05,
        )

    def setupWeaponMenu(self):
        self.weapon_menu = DirectDialog(
            frameSize=(-0.5, 0.5, -0.5, 0.5),
            fadeScreen=0.4,
            relief=DGG.FLAT,
            frameColor=MENU_BG_COLOR,
        )

        self.createLabel(
            "Weapon Selection",
            (0, 0, 0.3),
            parent=self.weapon_menu,
            scale=0.1,
        )

        self.weaponButtons = {}
        self.updateWeaponButtons()

        self.createButton(
            "Close",
            (0, 0, -0.3),
            command=self.hideWeaponMenu,
            parent=self.weapon_menu,
            scale=0.07,
        )

        # Hide initially
        self.weapon_menu.hide()

    def updateWeaponButtons(self):
        # Remove old buttons
        for button in self.weaponButtons.values():
            button.destroy()
        self.weaponButtons.clear()

        # Create new buttons for owned weapons
        y_pos = 0.1
        for weapon in self.game.owned_weapons:
            button = DirectButton(
                text=weapon.capitalize(),
                scale=0.07,
                pos=(0, 0, y_pos),
                parent=self.weapon_menu,
                command=lambda w=weapon: self.selectWeapon(w),
                relief=DGG.FLAT,
                frameColor=(0.2, 0.2, 0.2, 0.8),
                text_fg=(1, 1, 1, 1),
                pressEffect=1,
            )
            self.weaponButtons[weapon] = button
            y_pos -= 0.2

    def selectWeapon(self, weapon):
        self.game.weaponType = weapon
        self.game.player.switchWeapon(weapon)
        self.game.hud.updateWeapon(weapon)
        self.hideWeaponMenu()

    def showWeaponMenu(self):
        if self.game.gameState == "playing":
            self.updateWeaponButtons()
            self.weapon_menu.show()
            self.game.inputController.hideMouseCursor(False)  # Show cursor

    def hideWeaponMenu(self):
        self.weapon_menu.hide()
        if self.game.gameState == "playing":
            self.game.inputController.hideMouseCursor(
                self.game.player.camera_mode == "first-person"
            )  # Hide cursor in first-person

    def hidePauseMenu(self):
        if self.pause_menu:
            self.pause_menu.destroy()
            self.pause_menu = None

    def showPauseMenu(self):
        self.pause_menu = DirectDialog(
            frameSize=(-0.7, 0.7, -0.7, 0.7),
            fadeScreen=0.4,
            relief=DGG.FLAT,
            frameColor=MENU_BG_COLOR,
        )

        self.createLabel(
            "Game Paused",
            (0, 0, 0.5),
            parent=self.pause_menu,
            scale=0.1,
        )

        self.createButton(
            "Resume",
            (0, 0, 0.2),
            command=self.game.pauseGame,
            parent=self.pause_menu,
            scale=0.07,
        )
        self.createButton(
            "Main Menu",
            (0, 0, 0),
            command=self.game.returnToMenu,
            parent=self.pause_menu,
            scale=0.07,
        )
        self.createButton(
            "Quit",
            (0, 0, -0.2),
            command=sys.exit,
            parent=self.pause_menu,
            scale=0.07,
        )

    def showGameOver(self, score):
        self.game_over_menu = DirectDialog(
            frameSize=(-0.7, 0.7, -0.7, 0.7),
            fadeScreen=0.4,
            relief=DGG.FLAT,
            frameColor=(0.1, 0.1, 0.1, 0.7),
        )

        self.gameOverText = DirectLabel(
            text="Game Over",
            scale=0.1,
            pos=(0, 0, 0.5),
            parent=self.game_over_menu,
            relief=None,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
        )

        self.scoreText = DirectLabel(
            text=f"Score: {score}",
            scale=0.07,
            pos=(0, 0, 0.3),
            parent=self.game_over_menu,
            relief=None,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
        )

        self.restartButton = DirectButton(
            text="Play Again",
            scale=0.1,
            pos=(0, 0, 0.1),
            parent=self.game_over_menu,
            command=self.game.restartGame,
            relief=DGG.FLAT,
            frameColor=(0.2, 0.2, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            pressEffect=1,
        )

        self.menuButton = DirectButton(
            text="Main Menu",
            scale=0.1,
            pos=(0, 0, -0.1),
            parent=self.game_over_menu,
            command=self.game.returnToMenu,
            relief=DGG.FLAT,
            frameColor=(0.2, 0.2, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            pressEffect=1,
        )

        self.quitButton = DirectButton(
            text="Quit",
            scale=0.1,
            pos=(0, 0, -0.3),
            parent=self.game_over_menu,
            command=sys.exit,
            relief=DGG.FLAT,
            frameColor=(0.2, 0.2, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            pressEffect=1,
        )

    def showStore(self):
        self.main_menu.hide()
        self.store_menu.show()
        self.updateStoreCoins()

    def hideStore(self):
        self.store_menu.hide()
        self.main_menu.show()

    def updateStoreCoins(self):
        self.store_coin_label.setText(f"Coins: {self.game.coins}")

    def buyKatana(self):
        if self.game.coins >= 50 and "katana" not in self.game.owned_weapons:
            self.game.coins -= 50
            self.game.owned_weapons.append("katana")
            self.updateStoreCoins()
            self.katanaButton.setText("Katana (Owned)")
            self.katanaButton["state"] = DGG.DISABLED
            self.game.projectileManager.createUpgradeEffect(
                self.game.player.weapon_holder.getPos(self.game.render)
            )

    def hideMainMenu(self):
        if self.main_menu:
            self.main_menu.hide()

    def showMainMenu(self):
        if self.main_menu:
            self.main_menu.show()

    def hideGameOver(self):
        if self.game_over_menu:
            self.game_over_menu.destroy()
            self.game_over_menu = None

    def setupStoreMenu(self):
        self.store_menu = DirectDialog(
            frameSize=(-0.7, 0.7, -0.7, 0.7),
            fadeScreen=0.4,
            relief=DGG.FLAT,
            frameColor=MENU_BG_COLOR,
        )

        # Title and coins
        self.createLabel(
            "Store",
            (0, 0, 0.5),
            parent=self.store_menu,
            scale=0.12,
        )
        self.store_coin_label = self.createLabel(
            f"Coins: {self.game.coins}",
            (0, 0, 0.35),
            parent=self.store_menu,
            scale=0.08,
        )
        self.store_coin_label["text_fg"] = COIN_COLOR

        # Weapon display section
        weapon_spacing = 0.4
        dart_props = self.game.projectileManager.weaponProperties["dart"]
        katana_props = self.game.projectileManager.weaponProperties["katana"]

        # Dart Gun Info
        self.createLabel(
            "Dart Gun",
            (-weapon_spacing, 0, 0.2),
            parent=self.store_menu,
            scale=0.08,
        )
        self.createLabel(
            f"Damage: {dart_props['damage']}\nSpeed: {dart_props['speed']}\nCooldown: {dart_props['cooldown']}s\n{dart_props['description']}",
            (-weapon_spacing, 0, 0),
            parent=self.store_menu,
            scale=0.05,
        )

        # Katana Info
        self.createLabel(
            "Katana",
            (weapon_spacing, 0, 0.2),
            parent=self.store_menu,
            scale=0.08,
        )
        self.createLabel(
            f"Damage: {katana_props['damage']}\nSpeed: {katana_props['speed']}\nCooldown: {katana_props['cooldown']}s\n{katana_props['description']}",
            (weapon_spacing, 0, 0),
            parent=self.store_menu,
            scale=0.05,
        )

        # Buy button
        self.buy_katana_button = self.createButton(
            "Buy Katana (50 coins)",
            (0, 0, -0.2),
            command=self.game.upgradeWeapon,
            parent=self.store_menu,
            scale=0.07,
        )

        # Back button
        self.createButton(
            "Back",
            (0, 0, -0.4),
            command=self.hideStore,
            parent=self.store_menu,
            scale=0.07,
        )

        self.store_menu.hide()

    def setupRulesMenu(self):
        """Create the rules and mechanics menu UI"""
        self.rules_menu = DirectDialog(
            frameSize=(-0.7, 0.7, -0.7, 0.7),
            fadeScreen=0.4,
            relief=DGG.FLAT,
            frameColor=MENU_BG_COLOR,
        )

        self.createLabel(
            "Game Rules & Mechanics",
            (0, 0, 0.5),
            parent=self.rules_menu,
            scale=0.12,
        )

        rules_text = (
            "Game Rules:\n\n"
            "1. Survive as long as possible\n"
            "2. Collect coins to buy upgrades\n"
            "3. Defeat enemies to earn points\n"
            "4. Use different weapons strategically\n\n"
            "Tips:\n"
            "• Dart Gun is good for long range\n"
            "• Katana is powerful at close range\n"
            "• Watch out for enemy projectiles\n"
            "• Use the environment to your advantage"
        )

        self.createLabel(
            rules_text,
            (0, 0, 0.1),
            parent=self.rules_menu,
            scale=0.05,
        )

        self.createButton(
            "Back",
            (0, 0, -0.4),
            command=self.hideRules,
            parent=self.rules_menu,
            scale=0.07,
        )

        self.rules_menu.hide()

    def showRules(self):
        self.main_menu.hide()
        self.rules_menu.show()

    def hideRules(self):
        self.rules_menu.hide()
        self.main_menu.show()
