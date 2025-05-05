from direct.gui.DirectGui import DirectFrame, DirectLabel


class HUD:
    def __init__(self, game):
        self.game = game

        # Create HUD frame
        self.frame = DirectFrame(
            frameColor=(0, 0, 0, 0),
            frameSize=(-1, 1, -1, 1),
            parent=game.a2dTopLeft,
        )

        # Background frame for HUD elements
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
        """Update the score display"""
        self.scoreText["text"] = f"Score: {score}"

    def updateCoins(self, coins):
        """Update the coins display"""
        self.coinsText["text"] = f"Coins: {coins}"

    def updateWeapon(self, weapon_type):
        """Update the weapon display"""
        self.weaponText["text"] = f"Weapon: {weapon_type.capitalize()}"

    def updateCameraText(self, camera_mode):
        """Update the camera mode display"""
        self.cameraText["text"] = f"Camera: {camera_mode}"

    def show(self):
        """Show the HUD"""
        self.frame.show()

    def hide(self):
        """Hide the HUD"""
        self.frame.hide()
