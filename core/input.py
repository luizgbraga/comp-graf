from panda3d.core import CardMaker, NodePath, WindowProperties


class InputController:
    def __init__(self, game, player):
        self.game = game
        self.player = player

        # Set up key map
        self.keyMap = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "shoot": False,
            "switchCamera": False,
            "weaponMenu": False,
            "zoom": False,
        }

        # Set up key bindings
        self.setupKeyBindings()

        # Set up crosshair
        self.setupCrosshair()

        # Set up mouse look variables
        self.heading = 0
        self.pitch = 0
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.mouseSensitivity = 0.2

        # Add mouse task
        self.game.taskMgr.add(self.mouseTask, "MouseTask")

        # Add player update task
        self.game.taskMgr.add(self.updatePlayerTask, "UpdatePlayerTask")

    def setupKeyBindings(self):
        """Set up keyboard controls"""
        self.game.accept("w", self.updateKeyMap, ["forward", True])
        self.game.accept("w-up", self.updateKeyMap, ["forward", False])
        self.game.accept("s", self.updateKeyMap, ["backward", True])
        self.game.accept("s-up", self.updateKeyMap, ["backward", False])
        self.game.accept("a", self.updateKeyMap, ["left", True])
        self.game.accept("a-up", self.updateKeyMap, ["left", False])
        self.game.accept("d", self.updateKeyMap, ["right", True])
        self.game.accept("d-up", self.updateKeyMap, ["right", False])
        self.game.accept("mouse1", self.updateKeyMap, ["shoot", True])
        self.game.accept("mouse1-up", self.updateKeyMap, ["shoot", False])
        self.game.accept("c", self.updateKeyMap, ["switchCamera", True])
        self.game.accept("c-up", self.updateKeyMap, ["switchCamera", False])
        self.game.accept("tab", self.updateKeyMap, ["weaponMenu", True])
        self.game.accept("tab-up", self.updateKeyMap, ["weaponMenu", False])
        self.game.accept("space", self.updateKeyMap, ["jump", True])
        self.game.accept("space-up", self.updateKeyMap, ["jump", False])
        self.game.accept("mouse3", self.updateKeyMap, ["zoom", True])
        self.game.accept("mouse3-up", self.updateKeyMap, ["zoom", False])
        self.game.accept("escape", self.game.pauseGame, [])

    def setupCrosshair(self):
        """Create a crosshair for aiming"""
        self.crosshair_node = NodePath("crosshair")
        self.crosshair_node.reparentTo(self.game.aspect2d)

        # Create horizontal line
        cm = CardMaker("horizontal")
        cm.setFrame(-0.02, 0.02, -0.002, 0.002)
        horizontal = self.crosshair_node.attachNewNode(cm.generate())
        horizontal.setColor(1, 0, 0, 1)  # Red

        # Create vertical line
        cm = CardMaker("vertical")
        cm.setFrame(-0.002, 0.002, -0.02, 0.02)
        vertical = self.crosshair_node.attachNewNode(cm.generate())
        vertical.setColor(1, 0, 0, 1)  # Red

        # Create dot in the middle
        cm = CardMaker("dot")
        cm.setFrame(-0.004, 0.004, -0.004, 0.004)
        dot = self.crosshair_node.attachNewNode(cm.generate())
        dot.setColor(1, 1, 1, 1)  # White

        # Hide initially
        self.crosshair_node.hide()

    def updateKeyMap(self, key, value):
        """Update key state in the key map"""
        self.keyMap[key] = value
        # Handle one-shot actions
        if key == "shoot" and value and self.game.gameState == "playing":
            if self.player.currentWeapon == "dart":
                self.game.projectileManager.shootProjectile()
            elif self.player.currentWeapon == "katana":
                self.player.swingKatana()
        if key == "switchCamera" and value and self.game.gameState == "playing":
            self.player.switchCamera()

        if key == "weaponMenu" and value and self.game.gameState == "playing":
            self.game.menuManager.showWeaponMenu()

    def mouseTask(self, task):
        """Handle mouse movement for camera control"""
        if self.game.gameState != "playing":
            return task.cont

        # Get the mouse position
        if self.game.mouseWatcherNode.hasMouse():
            x = self.game.mouseWatcherNode.getMouseX()
            y = self.game.mouseWatcherNode.getMouseY()

            # Calculate the change in mouse position
            dx = x - self.last_mouse_x
            dy = y - self.last_mouse_y

            # Update based on camera mode
            if self.player.camera_mode == "first-person":
                # Update the heading and pitch
                self.heading -= dx * self.mouseSensitivity * 100
                self.pitch += dy * self.mouseSensitivity * 100

                # Clamp the pitch to prevent the camera from flipping over
                self.pitch = max(-80, min(80, self.pitch))

                # Set the player's orientation
                self.player.root.setH(self.heading)
                self.player.firstPersonCamNode.setP(self.pitch)

                # Center the crosshair
                self.crosshair_node.setPos(0, 0, 0)

            elif self.player.camera_mode == "third-person":
                # In third-person, rotate the player with the mouse
                self.heading -= dx * self.mouseSensitivity * 100
                self.player.root.setH(self.heading)

                # Update pitch for aiming
                self.pitch += dy * self.mouseSensitivity * 100
                self.pitch = max(-80, min(80, self.pitch))

                # Adjust camera height based on vertical mouse movement
                currentPos = self.player.thirdPersonCamNode.getPos()
                newZ = currentPos.getZ() - dy * self.mouseSensitivity * 10
                newZ = max(2, min(6, newZ))  # Clamp between 2 and 6
                self.player.thirdPersonCamNode.setZ(newZ)

                # Make the camera look at the player's head
                self.game.camera.lookAt(self.player.player_head)

                # Position crosshair at mouse position
                self.crosshair_node.setPos(x, 0, y)

            elif self.player.camera_mode == "top-down":
                # In top-down, adjust zoom with vertical mouse movement
                zoom = -dy * self.mouseSensitivity * 10
                currentPos = self.player.topDownCamNode.getPos()
                newZ = currentPos.getZ() + zoom
                newZ = max(5, min(20, newZ))  # Clamp between 5 and 20
                self.player.topDownCamNode.setZ(newZ)

                # Look directly at the player
                self.game.camera.lookAt(self.player.root)

                # Position crosshair at mouse position
                self.crosshair_node.setPos(x, 0, y)

            # Store the mouse position for the next frame
            self.last_mouse_x = x
            self.last_mouse_y = y

            # Update minimap player marker
            self.game.minimap.updatePlayerMarker(
                self.player.root.getPos(), self.heading
            )

            # Recenter the mouse if it's too close to the edge in any camera mode
            if abs(x) > 0.9 or abs(y) > 0.9:
                x_size = self.game.win.getXSize()
                y_size = self.game.win.getYSize()
                self.game.win.movePointer(0, x_size // 2, y_size // 2)
                self.last_mouse_x = 0
                self.last_mouse_y = 0

        return task.cont

    def updatePlayerTask(self, task):
        """Update player based on input"""
        if self.game.gameState != "playing":
            return task.cont

        # Get time since last frame
        dt = task.time - task.lastTime if hasattr(task, "lastTime") else 0
        task.lastTime = task.time

        # Update player movement
        self.player.update(dt, self.keyMap)

        return task.cont

    def setCrosshairVisible(self, visible):
        """Show or hide the crosshair"""
        if visible:
            self.crosshair_node.show()
        else:
            self.crosshair_node.hide()

    def hideMouseCursor(self, hidden):
        """Show or hide the mouse cursor"""
        props = WindowProperties()
        props.setCursorHidden(hidden)
        self.game.win.requestProperties(props)

    def reset(self):
        """Reset controller state"""
        self.heading = 0
        self.pitch = 0
        self.last_mouse_x = 0
        self.last_mouse_y = 0

        # Reset key map
        for key in self.keyMap:
            self.keyMap[key] = False
