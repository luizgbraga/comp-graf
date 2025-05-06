import sys

from direct.gui.DirectGui import (
    DGG,
    DirectButton,
    DirectDialog,
    DirectLabel,
    DirectFrame,
)
from panda3d.core import TextNode

# Color constants for consistent theming
MENU_BG_COLOR = (0.08, 0.08, 0.12, 0.95)  # Darker, more professional background
BUTTON_COLOR = (0.15, 0.15, 0.2, 0.9)  # Slightly lighter than background
BUTTON_HOVER_COLOR = (0.25, 0.25, 0.35, 0.9)  # More vibrant hover state
TEXT_COLOR = (0.9, 0.9, 0.95, 1)  # Slightly off-white for better readability
TITLE_COLOR = (1, 0.8, 0.2, 1)  # Gold color for titles
COIN_COLOR = (1, 0.8, 0, 1)  # Gold color for coins
ACCENT_COLOR = (0.2, 0.6, 1, 1)  # Blue accent color for highlights


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
        """Helper method to create consistent buttons"""
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
            frameSize=(-0.5, 0.5, -0.15, 0.15),  # Wider buttons
            text_align=TextNode.ACenter,
            text_pos=(0, -0.02),  # Slight vertical adjustment
            text_scale=0.8,  # Slightly smaller text
            extraArgs=[],
            frameTexture=None,
            text_font=None,
            text_shadow=(0, 0, 0, 0.5),  # Add text shadow
            text_shadowOffset=(0.002, -0.002),  # Subtle shadow offset
        )

    def createLabel(self, text, pos, parent=None, scale=0.07, align=TextNode.ACenter):
        """Helper method to create consistent labels"""
        return DirectLabel(
            text=text,
            scale=scale,
            pos=pos,
            parent=parent,
            relief=None,
            text_fg=TEXT_COLOR,
            text_align=align,
            text_shadow=(0, 0, 0, 0.5),  # Add text shadow
            text_shadowOffset=(0.002, -0.002),  # Subtle shadow offset
        )

    def setupMainMenu(self):
        """Create the main menu UI"""
        self.main_menu = DirectDialog(
            frameSize=(-0.8, 0.8, -0.8, 0.8),  # Slightly larger menu
            fadeScreen=0.5,  # Darker fade
            relief=DGG.FLAT,
            frameColor=MENU_BG_COLOR,
        )

        # Add a decorative border
        border = DirectFrame(
            frameColor=ACCENT_COLOR,
            frameSize=(-0.82, 0.82, -0.82, 0.82),
            parent=self.main_menu,
        )

        self.createLabel(
            "Monkey Dart Game",
            (0, 0, 0.5),
            parent=self.main_menu,
            scale=0.15,  # Larger title
        )["text_fg"] = TITLE_COLOR  # Gold color for title

        # Main menu buttons
        button_spacing = 0.18  # Increased spacing
        start_y = 0.2
        self.createButton(
            "Start Game",
            (0, 0, start_y),
            command=self.game.startGame,
            parent=self.main_menu,
            scale=0.09,  # Larger buttons
        )
        self.createButton(
            "Store",
            (0, 0, start_y - button_spacing),
            command=self.showStore,
            parent=self.main_menu,
            scale=0.09,
        )
        self.createButton(
            "Rules",
            (0, 0, start_y - button_spacing * 2),
            command=self.showRules,
            parent=self.main_menu,
            scale=0.09,
        )
        self.createButton(
            "Quit",
            (0, 0, start_y - button_spacing * 3),
            command=sys.exit,
            parent=self.main_menu,
            scale=0.09,
        )

        # Controls section with better formatting
        controls_text = (
            "Controls:\n\n"
            "• W, A, S, D - Move\n"
            "• Mouse - Look/Aim\n"
            "• Left Mouse Button - Shoot\n"
            "• C - Switch Camera\n"
            "• TAB - Switch Weapons"
        )
        controls_label = self.createLabel(
            controls_text,
            (0, 0, -0.3),
            parent=self.main_menu,
            scale=0.06,
        )
        controls_label["text_fg"] = (
            0.8,
            0.8,
            0.9,
            1,
        )  # Slightly dimmed text for controls

    def setupWeaponMenu(self):
        """Create the weapon selection menu UI"""
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
        """Update the weapon buttons based on owned weapons"""
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
        """Switch to selected weapon"""
        self.game.weaponType = weapon
        self.game.player.switchWeapon(weapon)
        self.game.hud.updateWeapon(weapon)
        self.hideWeaponMenu()

    def showWeaponMenu(self):
        """Show the weapon selection menu"""
        if self.game.gameState == "playing":
            self.updateWeaponButtons()
            self.weapon_menu.show()
            self.game.inputController.hideMouseCursor(False)  # Show cursor

    def hideWeaponMenu(self):
        """Hide the weapon selection menu"""
        self.weapon_menu.hide()
        if self.game.gameState == "playing":
            self.game.inputController.hideMouseCursor(
                self.game.player.camera_mode == "first-person"
            )  # Hide cursor in first-person

    def showGameOver(self, score):
        """Create and show game over screen"""
        self.game_over_menu = DirectDialog(
            frameSize=(-0.8, 0.8, -0.8, 0.8),
            fadeScreen=0.6,  # Darker fade for game over
            relief=DGG.FLAT,
            frameColor=(0.08, 0.08, 0.12, 0.95),
        )

        # Add a decorative border
        border = DirectFrame(
            frameColor=ACCENT_COLOR,
            frameSize=(-0.82, 0.82, -0.82, 0.82),
            parent=self.game_over_menu,
        )

        self.gameOverText = DirectLabel(
            text="Game Over",
            scale=0.15,
            pos=(0, 0, 0.5),
            parent=self.game_over_menu,
            relief=None,
            text_fg=TITLE_COLOR,
            text_shadow=(0, 0, 0, 0.5),
            text_shadowOffset=(0.002, -0.002),
        )

        self.scoreText = DirectLabel(
            text=f"Score: {score}",
            scale=0.1,
            pos=(0, 0, 0.3),
            parent=self.game_over_menu,
            relief=None,
            text_fg=TEXT_COLOR,
            text_shadow=(0, 0, 0, 0.5),
            text_shadowOffset=(0.002, -0.002),
        )

        self.restartButton = self.createButton(
            "Play Again",
            (0, 0, 0.1),
            command=self.game.restartGame,
            parent=self.game_over_menu,
            scale=0.09,
        )

        self.menuButton = self.createButton(
            "Main Menu",
            (0, 0, -0.1),
            command=self.game.returnToMenu,
            parent=self.game_over_menu,
            scale=0.09,
        )

        self.quitButton = self.createButton(
            "Quit",
            (0, 0, -0.3),
            command=sys.exit,
            parent=self.game_over_menu,
            scale=0.09,
        )

    def showStore(self):
        """Show the store menu"""
        self.main_menu.hide()
        self.store_menu.show()
        self.updateStoreCoins()

    def hideStore(self):
        """Hide the store menu"""
        self.store_menu.hide()
        self.main_menu.show()

    def updateStoreCoins(self):
        """Update the coins display in the store"""
        self.store_coin_label.setText(f"Coins: {self.game.coins}")

    def buyKatana(self):
        """Buy the katana if player has enough coins"""
        if self.game.coins >= 50 and "katana" not in self.game.owned_weapons:
            self.game.coins -= 50
            self.game.owned_weapons.append("katana")
            self.updateStoreCoins()
            self.katanaButton.setText("Katana (Owned)")
            self.katanaButton["state"] = DGG.DISABLED
            self.game.projectileManager.createUpgradeEffect(
                self.game.player.weapon_holder.getPos(self.game.render)
            )

    def hideMenu(self):
        """Hide the main menu"""
        if self.main_menu:
            self.main_menu.hide()

    def showMenu(self):
        """Show the main menu"""
        if self.main_menu:
            self.main_menu.show()

    def hideGameOver(self):
        """Hide the game over screen"""
        if self.game_over_menu:
            self.game_over_menu.destroy()
            self.game_over_menu = None

    def setupStoreMenu(self):
        """Create the store menu UI"""
        self.store_menu = DirectDialog(
            frameSize=(-0.8, 0.8, -0.8, 0.8),
            fadeScreen=0.5,
            relief=DGG.FLAT,
            frameColor=MENU_BG_COLOR,
        )

        # Add a decorative border
        border = DirectFrame(
            frameColor=ACCENT_COLOR,
            frameSize=(-0.82, 0.82, -0.82, 0.82),
            parent=self.store_menu,
        )

        # Title and coins
        self.createLabel(
            "Store",
            (0, 0, 0.5),
            parent=self.store_menu,
            scale=0.15,
        )["text_fg"] = TITLE_COLOR

        self.store_coin_label = self.createLabel(
            f"Coins: {self.game.coins}",
            (0, 0, 0.35),
            parent=self.store_menu,
            scale=0.09,
        )
        self.store_coin_label["text_fg"] = COIN_COLOR

        # Weapon display section with better layout
        weapon_spacing = 0.45  # Increased spacing
        dart_props = self.game.projectileManager.weaponProperties["dart"]
        katana_props = self.game.projectileManager.weaponProperties["katana"]

        # Dart Gun Info with better formatting
        self.createLabel(
            "Dart Gun",
            (-weapon_spacing, 0, 0.2),
            parent=self.store_menu,
            scale=0.09,
        )["text_fg"] = ACCENT_COLOR

        dart_info = (
            f"Damage: {dart_props['damage']}\n"
            f"Speed: {dart_props['speed']}\n"
            f"Cooldown: {dart_props['cooldown']}s\n\n"
            f"{dart_props['description']}"
        )
        self.createLabel(
            dart_info,
            (-weapon_spacing, 0, 0),
            parent=self.store_menu,
            scale=0.06,
        )

        # Katana Info with better formatting
        self.createLabel(
            "Katana",
            (weapon_spacing, 0, 0.2),
            parent=self.store_menu,
            scale=0.09,
        )["text_fg"] = ACCENT_COLOR

        katana_info = (
            f"Damage: {katana_props['damage']}\n"
            f"Speed: {katana_props['speed']}\n"
            f"Cooldown: {katana_props['cooldown']}s\n\n"
            f"{katana_props['description']}"
        )
        self.createLabel(
            katana_info,
            (weapon_spacing, 0, 0),
            parent=self.store_menu,
            scale=0.06,
        )

        # Buy button with better styling
        self.buy_katana_button = self.createButton(
            "Buy Katana (50 coins)",
            (0, 0, -0.2),
            command=self.game.upgradeWeapon,
            parent=self.store_menu,
            scale=0.08,
        )

        # Back button
        self.createButton(
            "Back",
            (0, 0, -0.4),
            command=self.hideStore,
            parent=self.store_menu,
            scale=0.08,
        )

        # Hide initially
        self.store_menu.hide()

    def setupRulesMenu(self):
        """Create the rules and mechanics menu UI"""
        self.rules_menu = DirectDialog(
            frameSize=(-0.8, 0.8, -0.8, 0.8),
            fadeScreen=0.5,
            relief=DGG.FLAT,
            frameColor=MENU_BG_COLOR,
        )

        # Add a decorative border
        border = DirectFrame(
            frameColor=ACCENT_COLOR,
            frameSize=(-0.82, 0.82, -0.82, 0.82),
            parent=self.rules_menu,
        )

        self.createLabel(
            "Game Rules & Mechanics",
            (0, 0, 0.5),
            parent=self.rules_menu,
            scale=0.15,
        )["text_fg"] = TITLE_COLOR

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

        rules_label = self.createLabel(
            rules_text,
            (0, 0, 0.1),
            parent=self.rules_menu,
            scale=0.06,
        )
        rules_label["text_fg"] = (
            0.9,
            0.9,
            0.95,
            1,
        )  # Brighter text for better readability

        self.createButton(
            "Back",
            (0, 0, -0.4),
            command=self.hideRules,
            parent=self.rules_menu,
            scale=0.08,
        )

        # Hide initially
        self.rules_menu.hide()

    def showRules(self):
        """Show the rules menu"""
        self.main_menu.hide()
        self.rules_menu.show()

    def hideRules(self):
        """Hide the rules menu"""
        self.rules_menu.hide()
        self.main_menu.show()
