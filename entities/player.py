import math

from panda3d.core import NodePath, Point3, WindowProperties


class Player:
    def __init__(self, game):
        self.game = game

        # Create a model for the player (monkey) using simple shapes
        self._createModel()

        # Set up camera system
        self._setupCameras()

        # Set initial position
        self.root.setPos(0, 0, 0)

        # Initial heading and pitch
        self.heading = 0
        self.pitch = 0

        # Current camera mode
        self.camera_mode = "first-person"
        self.camera = game.camera

        # Note: We don't call switchToFirstPerson() here anymore
        # It will be called after all components are created

    def initializeCamera(self):
        """Initialize camera after all components are created"""
        self.switchToFirstPerson()

    def _createModel(self):
        """Create the player model parts"""
        self.root = NodePath("player_root")
        self.root.reparentTo(self.game.render)

        # Body
        self.player_body = self.game.createBox(0.5, 0.3, 0.8, (0.6, 0.45, 0.3, 1))
        self.player_body.reparentTo(self.root)
        self.player_body.setPos(0, 0, 0.8)

        # Head
        self.player_head = self.game.createBox(0.4, 0.4, 0.4, (0.8, 0.65, 0.5, 1))
        self.player_head.reparentTo(self.root)
        self.player_head.setPos(0, 0, 1.6)

        # Arms
        self.player_arm_r = self.game.createBox(0.15, 0.15, 0.4, (0.6, 0.45, 0.3, 1))
        self.player_arm_r.reparentTo(self.root)
        self.player_arm_r.setPos(0.35, 0, 1.1)

        self.player_arm_l = self.game.createBox(0.15, 0.15, 0.4, (0.6, 0.45, 0.3, 1))
        self.player_arm_l.reparentTo(self.root)
        self.player_arm_l.setPos(-0.35, 0, 1.1)

        # Legs
        self.player_leg_r = self.game.createBox(0.18, 0.18, 0.5, (0.6, 0.45, 0.3, 1))
        self.player_leg_r.reparentTo(self.root)
        self.player_leg_r.setPos(0.2, 0, 0.25)

        self.player_leg_l = self.game.createBox(0.18, 0.18, 0.5, (0.6, 0.45, 0.3, 1))
        self.player_leg_l.reparentTo(self.root)
        self.player_leg_l.setPos(-0.2, 0, 0.25)

        # Weapon holder
        self.weapon_holder = NodePath("weapon_holder")
        self.weapon_holder.reparentTo(self.root)
        self.weapon_holder.setPos(0.4, 0.3, 1.2)

        # Current dart gun
        self.dart_gun = self.game.createBox(0.1, 0.4, 0.1, (0.3, 0.3, 0.3, 1))
        self.dart_gun.reparentTo(self.weapon_holder)

        # Katana (hidden initially)
        # Create katana blade
        self.katana_blade = self.game.createBox(
            0.02, 0.8, 0.1, (0.8, 0.8, 0.8, 1)
        )  # Silver color
        self.katana_blade.reparentTo(self.weapon_holder)
        self.katana_blade.setPos(0, 0.4, 0)  # Position the blade forward

        # Create katana handle
        self.katana_handle = self.game.createBox(
            0.03, 0.2, 0.03, (0.2, 0.1, 0.1, 1)
        )  # Dark red color
        self.katana_handle.reparentTo(self.weapon_holder)
        self.katana_handle.setPos(0, -0.1, 0)  # Position the handle at the back

        # Create katana guard
        self.katana_guard = self.game.createBox(
            0.05, 0.02, 0.05, (0.3, 0.3, 0.3, 1)
        )  # Dark gray color
        self.katana_guard.reparentTo(self.weapon_holder)
        self.katana_guard.setPos(
            0, 0.1, 0
        )  # Position the guard between blade and handle

        # Group all katana parts
        self.katana = NodePath("katana")
        self.katana_blade.reparentTo(self.katana)
        self.katana_handle.reparentTo(self.katana)
        self.katana_guard.reparentTo(self.katana)
        self.katana.reparentTo(self.weapon_holder)
        self.katana.hide()

    def _setupCameras(self):
        """Create camera nodes for different views"""
        # First-person camera (at eye level)
        self.firstPersonCamNode = self.root.attachNewNode("first_person_cam")
        self.firstPersonCamNode.setPos(0, 0, 1.7)

        # Third-person camera (behind player)
        self.thirdPersonCamNode = self.root.attachNewNode("third_person_cam")
        self.thirdPersonCamNode.setPos(0, -5, 3)

        # Top-down camera (above player)
        self.topDownCamNode = self.root.attachNewNode("top_down_cam")
        self.topDownCamNode.setPos(0, 0, 15)

    def update(self, dt, keys):
        """Update player movement and state"""
        # Move the player based on the key presses
        speed = 8

        # Get the player's heading in radians
        heading_rad = math.radians(self.root.getH())

        # Calculate forward and right vectors based on the player's heading
        forward_vec = Point3(math.sin(-heading_rad), math.cos(-heading_rad), 0)
        right_vec = Point3(
            math.sin(-heading_rad + math.pi / 2),
            math.cos(-heading_rad + math.pi / 2),
            0,
        )

        # Move based on keys
        if keys["forward"]:
            self.root.setPos(self.root.getPos() + forward_vec * dt * speed)
            # Add bobbing animation to simulate walking
            self.root.setZ(
                math.sin(self.game.taskMgr.globalClock.getFrameTime() * 10) * 0.05 + 0
            )

        if keys["backward"]:
            self.root.setPos(self.root.getPos() - forward_vec * dt * speed)
            # Add bobbing animation for walking backward
            self.root.setZ(
                math.sin(self.game.taskMgr.globalClock.getFrameTime() * 10) * 0.05 + 0
            )

        if keys["left"]:
            self.root.setPos(self.root.getPos() - right_vec * dt * speed)

        if keys["right"]:
            self.root.setPos(self.root.getPos() + right_vec * dt * speed)

        # Constrain player movement to the play area
        playerPos = self.root.getPos()
        playerPos.x = max(-35, min(35, playerPos.x))
        playerPos.y = max(-35, min(35, playerPos.y))

        # Make sure player is at correct z height
        playerPos.z = 0  # Base height
        self.root.setPos(playerPos)

    def switchCamera(self):
        """Cycle through camera modes"""
        if self.camera_mode == "first-person":
            self.switchToThirdPerson()
        elif self.camera_mode == "third-person":
            self.switchToTopDown()
        else:
            self.switchToFirstPerson()

    def switchToFirstPerson(self):
        """Switch to first-person view"""
        self.camera_mode = "first-person"
        self.camera.reparentTo(self.firstPersonCamNode)
        self.camera.setPos(0, 0, 0)
        self.camera.setHpr(0, 0, 0)

        # Update camera text in HUD
        if hasattr(self.game, "hud"):
            self.game.hud.updateCameraText("First-Person")

        # Show crosshair
        if hasattr(self.game, "inputController"):
            self.game.inputController.setCrosshairVisible(True)

        # Hide mouse cursor for first-person view
        props = WindowProperties()
        props.setCursorHidden(True)
        self.game.win.requestProperties(props)

    def switchToThirdPerson(self):
        """Switch to third-person view"""
        self.camera_mode = "third-person"
        self.camera.reparentTo(self.thirdPersonCamNode)
        self.camera.setPos(0, 0, 0)
        self.camera.lookAt(self.player_head)

        # Update camera text in HUD
        if hasattr(self.game, "hud"):
            self.game.hud.updateCameraText("Third-Person")

        # Hide crosshair
        if hasattr(self.game, "inputController"):
            self.game.inputController.setCrosshairVisible(False)

        # Show mouse cursor in third-person
        props = WindowProperties()
        props.setCursorHidden(False)
        self.game.win.requestProperties(props)

    def switchToTopDown(self):
        """Switch to top-down view"""
        self.camera_mode = "top-down"
        self.camera.reparentTo(self.topDownCamNode)
        self.camera.setPos(0, 0, 0)
        self.camera.setHpr(0, -90, 0)  # Look straight down

        # Update camera text in HUD
        if hasattr(self.game, "hud"):
            self.game.hud.updateCameraText("Top-Down")

        # Hide crosshair
        if hasattr(self.game, "inputController"):
            self.game.inputController.setCrosshairVisible(False)

        # Show mouse cursor in top-down
        props = WindowProperties()
        props.setCursorHidden(False)
        self.game.win.requestProperties(props)

    def switchWeapon(self, weaponType):
        """Switch between dart gun and katana"""
        if weaponType == "dart":
            self.dart_gun.show()
            self.katana.hide()
        else:  # katana
            self.dart_gun.hide()
            self.katana.show()

    def reset(self):
        """Reset player for new game"""
        self.root.setPos(0, 0, 0)
        self.heading = 0
        self.pitch = 0
        self.root.setH(self.heading)
        self.firstPersonCamNode.setP(0)
        self.switchToFirstPerson()
        self.switchWeapon("dart")
