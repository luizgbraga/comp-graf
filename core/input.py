from panda3d.core import CardMaker, NodePath, WindowProperties


class InputController:
    def __init__(self, game, player):
        self.game = game
        self.player = player

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

        self.setupKeyBindings()

        self.setupCrosshair()

        self.heading = 0
        self.pitch = 0
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.mouseSensitivity = 0.2

        self.game.taskMgr.add(self.mouseTask, "MouseTask")

        self.game.taskMgr.add(self.updatePlayerTask, "UpdatePlayerTask")

    def setupKeyBindings(self):
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
        self.crosshair_node = NodePath("crosshair")
        self.crosshair_node.reparentTo(self.game.aspect2d)

        cm = CardMaker("horizontal")
        cm.setFrame(-0.02, 0.02, -0.002, 0.002)
        horizontal = self.crosshair_node.attachNewNode(cm.generate())
        horizontal.setColor(1, 0, 0, 1)

        cm = CardMaker("vertical")
        cm.setFrame(-0.002, 0.002, -0.02, 0.02)
        vertical = self.crosshair_node.attachNewNode(cm.generate())
        vertical.setColor(1, 0, 0, 1)

        cm = CardMaker("dot")
        cm.setFrame(-0.004, 0.004, -0.004, 0.004)
        dot = self.crosshair_node.attachNewNode(cm.generate())
        dot.setColor(1, 1, 1, 1)

        self.crosshair_node.hide()

    def updateKeyMap(self, key, value):
        self.keyMap[key] = value
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
        if self.game.gameState != "playing":
            return task.cont

        if self.game.mouseWatcherNode.hasMouse():
            x = self.game.mouseWatcherNode.getMouseX()
            y = self.game.mouseWatcherNode.getMouseY()

            dx = x - self.last_mouse_x
            dy = y - self.last_mouse_y

            if self.player.camera_mode == "first-person":
                self.heading -= dx * self.mouseSensitivity * 100
                self.pitch += dy * self.mouseSensitivity * 100

                self.pitch = max(-80, min(80, self.pitch))

                self.player.root.setH(self.heading)
                self.player.firstPersonCamNode.setP(self.pitch)

                self.crosshair_node.setPos(0, 0, 0)

            elif self.player.camera_mode == "third-person":
                self.heading -= dx * self.mouseSensitivity * 100
                self.player.root.setH(self.heading)

                self.pitch += dy * self.mouseSensitivity * 100
                self.pitch = max(-80, min(80, self.pitch))

                currentPos = self.player.thirdPersonCamNode.getPos()
                newZ = currentPos.getZ() - dy * self.mouseSensitivity * 10
                newZ = max(2, min(6, newZ))
                self.player.thirdPersonCamNode.setZ(newZ)

                self.game.camera.lookAt(self.player.player_head)

                self.crosshair_node.setPos(x, 0, y)

            elif self.player.camera_mode == "top-down":
                zoom = -dy * self.mouseSensitivity * 10
                currentPos = self.player.topDownCamNode.getPos()
                newZ = currentPos.getZ() + zoom
                newZ = max(5, min(20, newZ))
                self.player.topDownCamNode.setZ(newZ)

                self.game.camera.lookAt(self.player.root)

                self.crosshair_node.setPos(x, 0, y)

            self.last_mouse_x = x
            self.last_mouse_y = y

            self.game.minimap.updatePlayerMarker(
                self.player.root.getPos(), self.heading
            )

            if abs(x) > 0.9 or abs(y) > 0.9:
                x_size = self.game.win.getXSize()
                y_size = self.game.win.getYSize()
                self.game.win.movePointer(0, x_size // 2, y_size // 2)
                self.last_mouse_x = 0
                self.last_mouse_y = 0

        return task.cont

    def updatePlayerTask(self, task):
        if self.game.gameState != "playing":
            return task.cont

        dt = task.time - task.lastTime if hasattr(task, "lastTime") else 0
        task.lastTime = task.time

        self.player.update(dt, self.keyMap)

        return task.cont

    def setCrosshairVisible(self, visible):
        if visible:
            self.crosshair_node.show()
        else:
            self.crosshair_node.hide()

    def hideMouseCursor(self, hidden):
        props = WindowProperties()
        props.setCursorHidden(hidden)
        self.game.win.requestProperties(props)

    def reset(self):
        self.heading = 0
        self.pitch = 0
        self.last_mouse_x = 0
        self.last_mouse_y = 0

        for key in self.keyMap:
            self.keyMap[key] = False
