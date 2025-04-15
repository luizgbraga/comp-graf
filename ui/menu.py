import sys

from direct.gui.DirectGui import DGG, DirectButton, DirectDialog, DirectLabel


class MenuManager:
    def __init__(self, game):
        self.game = game
        self.main_menu = None
        self.game_over_menu = None
        self.setupMainMenu()

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
