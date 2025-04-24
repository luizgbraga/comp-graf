import sys

from direct.gui.DirectGui import DGG, DirectButton, DirectDialog, DirectLabel


class MenuManager:
    def __init__(self, game):
        self.game = game
        self.main_menu = None
        self.game_over_menu = None
        self.weapon_menu = None
        self.setupMainMenu()
        self.setupWeaponMenu()

    def setupMainMenu(self):
        """Create the main menu UI"""
        self.main_menu = DirectDialog(
            frameSize=(-0.7, 0.7, -0.7, 0.7),
            fadeScreen=0.4,
            relief=DGG.FLAT,
            frameColor=(0.1, 0.1, 0.1, 0.7),
        )

        self.titleText = DirectLabel(
            text="Monkey Dart Game",
            scale=0.1,
            pos=(0, 0, 0.5),
            parent=self.main_menu,
            relief=None,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
        )

        self.startButton = DirectButton(
            text="Start Game",
            scale=0.1,
            pos=(0, 0, 0.2),
            parent=self.main_menu,
            command=self.game.startGame,
            relief=DGG.FLAT,
            frameColor=(0.2, 0.2, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            pressEffect=1,
        )

        self.quitButton = DirectButton(
            text="Quit",
            scale=0.1,
            pos=(0, 0, 0),
            parent=self.main_menu,
            command=sys.exit,
            relief=DGG.FLAT,
            frameColor=(0.2, 0.2, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            pressEffect=1,
        )

        self.instructionsText = DirectLabel(
            text="Controls:\nW, A, S, D - Move\nMouse - Look/Aim\nLeft Mouse Button - Shoot\nC - Switch Camera",
            scale=0.05,
            pos=(0, 0, -0.3),
            parent=self.main_menu,
            relief=None,
            text_fg=(1, 1, 1, 1),
        )

    def setupWeaponMenu(self):
        """Create the weapon selection menu UI"""
        self.weapon_menu = DirectDialog(
            frameSize=(-0.5, 0.5, -0.5, 0.5),
            fadeScreen=0.4,
            relief=DGG.FLAT,
            frameColor=(0.1, 0.1, 0.1, 0.7),
        )

        self.weaponTitleText = DirectLabel(
            text="Weapon Selection",
            scale=0.08,
            pos=(0, 0, 0.3),
            parent=self.weapon_menu,
            relief=None,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
        )

        self.dartButton = DirectButton(
            text="Dart Gun",
            scale=0.07,
            pos=(0, 0, 0.1),
            parent=self.weapon_menu,
            command=self.selectDart,
            relief=DGG.FLAT,
            frameColor=(0.2, 0.2, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            pressEffect=1,
        )

        self.katanaButton = DirectButton(
            text="Katana (10 coins)",
            scale=0.07,
            pos=(0, 0, -0.1),
            parent=self.weapon_menu,
            command=self.selectKatana,
            relief=DGG.FLAT,
            frameColor=(0.2, 0.2, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            pressEffect=1,
        )

        self.closeButton = DirectButton(
            text="Close",
            scale=0.07,
            pos=(0, 0, -0.3),
            parent=self.weapon_menu,
            command=self.hideWeaponMenu,
            relief=DGG.FLAT,
            frameColor=(0.2, 0.2, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            pressEffect=1,
        )

        # Hide initially
        self.weapon_menu.hide()

    def selectDart(self):
        """Switch to dart gun"""
        self.game.weaponType = "dart"
        self.game.player.switchWeapon("dart")
        self.game.hud.updateWeapon("dart")
        self.hideWeaponMenu()

    def selectKatana(self):
        """Switch to katana if player has enough coins"""
        if self.game.coins >= 10:
            self.game.coins -= 10
            self.game.weaponType = "katana"
            self.game.player.switchWeapon("katana")
            self.game.hud.updateCoins(self.game.coins)
            self.game.hud.updateWeapon("katana")
            self.game.projectileManager.createUpgradeEffect(
                self.game.player.weapon_holder.getPos(self.game.render)
            )
            self.hideWeaponMenu()

    def showWeaponMenu(self):
        """Show the weapon selection menu"""
        if self.game.gameState == "playing":
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
