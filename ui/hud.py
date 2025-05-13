from direct.gui.DirectGui import DirectFrame, DirectLabel
from direct.gui.OnscreenImage import OnscreenImage
import math
from panda3d.core import TransparencyAttrib

class HUD:
    def __init__(self, game):
        self.game = game
        self.heart_icons = []
        self.max_hearts = 3
        self.heart_image_path = "assets/health.png"
        self.heart_icons = []
        self.refreshHearts()

        # Create HUD frame
        self.frame = DirectFrame(
            frameColor=(0, 0, 0, 0),
            frameSize=(-1, 1, -1, 1),
            parent=game.a2dTopLeft,
        )

        # Background
        self.hud_bg = DirectFrame(
            frameColor=(0, 0, 0, 0.5),
            frameSize=(0, 0.4, -0.45, 0.05),  # Adjusted to cover full height
            pos=(0.05, 0, -0.05),
            parent=self.frame,
        )

        # Score display
        self.scoreText = DirectLabel(
            text="Score: 0",
            scale=0.04,
            pos=(0.07, 0, -0.05),
            parent=self.frame,
            relief=None,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_align=0,  # Left align
        )

        # Coins display
        self.coinsText = DirectLabel(
            text="Coins: 0",
            scale=0.04,
            pos=(0.07, 0, -0.11),
            parent=self.frame,
            relief=None,
            text_fg=(1, 0.84, 0, 1),  # Gold color for coins
            text_shadow=(0, 0, 0, 1),
            text_align=0,  # Left align
        )

        # Weapon type display
        self.weaponText = DirectLabel(
            text="Weapon: Dart",
            scale=0.04,
            pos=(0.07, 0, -0.17),
            parent=self.frame,
            relief=None,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_align=0,  # Left align
        )

        # Camera mode indicator
        self.cameraText = DirectLabel(
            text="Camera: First-Person",
            scale=0.035,
            pos=(0.07, 0, -0.23),
            parent=self.frame,
            relief=None,
            text_fg=(0.8, 0.8, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_align=0,  # Left align
        )

        # Hide HUD initially
        self.hide()

    def updateScore(self, score):
        self.scoreText["text"] = f"Score: {score}"

    def updateCoins(self, coins):
        self.coinsText["text"] = f"Coins: {coins}"

    def updateWeapon(self, weapon_type):
        self.weaponText["text"] = f"Weapon: {weapon_type.capitalize()}"

    def updateCameraText(self, camera_mode):
        self.cameraText["text"] = f"Camera: {camera_mode}"

    def show(self):
        self.frame.show()

    def hide(self):
        self.frame.hide()

    def disableUpgradeButton(self):
        if hasattr(self.game, "menuManager") and hasattr(
            self.game.menuManager, "store"
        ):
            self.game.menuManager.store.disableUpgradeButton()
    def refreshHearts(self):
        # Remove any existing hearts
        for heart in self.heart_icons:
            heart.removeNode()
        self.heart_icons.clear()

        spacing = 0.12  # adjust as needed
        scale = 0.07   # adjust size of heart icon
        base_x = 1 - scale * 1.2  # starting from right edge
        y_pos = 0.9

        for i in range(self.game.player.health):
            x = base_x - i * spacing
            heart = OnscreenImage(
                image=self.heart_image_path,
                pos=(x, 0, y_pos),
                scale=(scale, 1, scale),
                parent=self.game.aspect2d
            )
            heart.setTransparency(TransparencyAttrib.M_alpha)
            self.heart_icons.append(heart)
    def addHeart(self):
        self.refreshHearts()

    def removeHeart(self):
        self.refreshHearts()
