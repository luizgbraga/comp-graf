from direct.gui.DirectGui import DGG, DirectButton, DirectFrame, DirectLabel


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
            frameSize=(0, 0.5, -0.5, 0),
            pos=(0, 0, 0),
            parent=self.frame,
        )

        # Score display
        self.scoreText = DirectLabel(
            text="Score: 0",
            scale=0.05,
            pos=(0.1, 0, -0.05),
            parent=self.frame,
            relief=None,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
        )

        # Coins display
        self.coinsText = DirectLabel(
            text="Coins: 0",
            scale=0.05,
            pos=(0.1, 0, -0.12),
            parent=self.frame,
            relief=None,
            text_fg=(1, 0.84, 0, 1),  # Gold color for coins
            text_shadow=(0, 0, 0, 1),
        )

        # Weapon type display
        self.weaponText = DirectLabel(
            text="Weapon: Dart",
            scale=0.05,
            pos=(0.1, 0, -0.19),
            parent=self.frame,
            relief=None,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
        )

        # Upgrade button
        self.upgradeButton = DirectButton(
            text="Upgrade to Katana (50 coins)",
            scale=0.05,
            pos=(0.25, 0, -0.28),
            parent=self.frame,
            command=game.upgradeWeapon,
            relief=DGG.FLAT,
            frameColor=(0.2, 0.2, 0.2, 0.8),
            text_fg=(1, 1, 1, 1),
            pressEffect=1,
        )

        # Camera mode indicator
        self.cameraText = DirectLabel(
            text="Camera: First-Person",
            scale=0.04,
            pos=(0.1, 0, -0.36),
            parent=self.frame,
            relief=None,
            text_fg=(0.8, 0.8, 1, 1),
            text_shadow=(0, 0, 0, 1),
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

    def disableUpgradeButton(self):
        """Disable the upgrade button after purchasing katana"""
        self.upgradeButton["text"] = "Weapon Fully Upgraded"
        self.upgradeButton["state"] = DGG.DISABLED

    def enableUpgradeButton(self):
        """Enable the upgrade button for a new game"""
        self.upgradeButton["text"] = "Upgrade to Katana (50 coins)"
        self.upgradeButton["state"] = DGG.NORMAL

    def show(self):
        """Show the HUD"""
        self.frame.show()

    def hide(self):
        """Hide the HUD"""
        self.frame.hide()
