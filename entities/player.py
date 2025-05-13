import math

from panda3d.core import NodePath, Point3, WindowProperties


class Player:
    def __init__(self, game):
        self.game = game
        self.health = 3
        self.gravity = 22
        self.jump_speed = 7
        self.max_jump_hold = 0.4
        self.gravity_scale = 0.3
        self.jump_buffer_time = 0.1
        self.playerHeight = 0.5
        self.hasKatana = False

        self.is_zoomed = False
        self.normal_fov = 60
        self.zoom_fov = 30
        self.zoom_speed = 5

        self.z_velocity = 0.0
        self.jump_timer = self.max_jump_hold
        self.buffer_timer = 0.0
        self.max_jump_buffer_time = 0.2
        self.is_jumping = False

        self._createModel()

        self._setupCameras()

        self.root.setPos(0, 0, 0)

        self.heading = 0
        self.pitch = 0
        self.currentWeapon = "dart"
        self.camera_mode = "first-person"
        self.camera = game.camera

    def initializeCamera(self):
        self.switchToFirstPerson()

    def _createModel(self):
        self.root = NodePath("player_root")
        self.root.reparentTo(self.game.render)

        self.player_body = self.game.createBox(0.5, 0.3, 0.8, (0.6, 0.45, 0.3, 1))
        self.player_body.reparentTo(self.root)
        self.player_body.setPos(0, 0, 0.8)

        self.player_head = self.game.createBox(0.4, 0.4, 0.4, (0.8, 0.65, 0.5, 1))
        self.player_head.reparentTo(self.root)
        self.player_head.setPos(0, 0, 1.6)

        self.player_arm_r = self.game.createBox(0.15, 0.15, 0.4, (0.6, 0.45, 0.3, 1))
        self.player_arm_r.reparentTo(self.root)
        self.player_arm_r.setPos(0.35, 0, 1.1)

        self.player_arm_l = self.game.createBox(0.15, 0.15, 0.4, (0.6, 0.45, 0.3, 1))
        self.player_arm_l.reparentTo(self.root)
        self.player_arm_l.setPos(-0.35, 0, 1.1)

        self.player_leg_r = self.game.createBox(0.18, 0.18, 0.5, (0.6, 0.45, 0.3, 1))
        self.player_leg_r.reparentTo(self.root)
        self.player_leg_r.setPos(0.2, 0, 0)

        self.player_leg_l = self.game.createBox(0.18, 0.18, 0.5, (0.6, 0.45, 0.3, 1))
        self.player_leg_l.reparentTo(self.root)
        self.player_leg_l.setPos(-0.2, 0, 0)

        self.weapon_holder = NodePath("weapon_holder")
        self.weapon_holder.reparentTo(self.root)
        self.weapon_holder.setPos(0.4, 0.3, 1.2)

        self.dart_gun = self.game.createBox(0.1, 0.4, 0.1, (0.3, 0.3, 0.3, 1))
        self.dart_gun.reparentTo(self.weapon_holder)

        self.katana_blade = self.game.createBox(0.02, 0.8, 0.1, (0.8, 0.8, 0.8, 1))
        self.katana_blade.reparentTo(self.weapon_holder)
        self.katana_blade.setPos(0, 0.4, 0)

        self.katana_handle = self.game.createBox(0.03, 0.2, 0.03, (0.2, 0.1, 0.1, 1))
        self.katana_handle.reparentTo(self.weapon_holder)
        self.katana_handle.setPos(0, -0.1, 0)

        self.katana_guard = self.game.createBox(0.05, 0.02, 0.05, (0.3, 0.3, 0.3, 1))
        self.katana_guard.reparentTo(self.weapon_holder)
        self.katana_guard.setPos(0, 0.1, 0)

        self.katana = NodePath("katana")
        self.katana_blade.reparentTo(self.katana)
        self.katana_handle.reparentTo(self.katana)
        self.katana_guard.reparentTo(self.katana)
        self.katana.reparentTo(self.weapon_holder)
        self.katana.hide()

    def _setupCameras(self):
        self.firstPersonCamNode = self.root.attachNewNode("first_person_cam")
        self.firstPersonCamNode.setPos(0, 0, 1.7)

        self.thirdPersonCamNode = self.root.attachNewNode("third_person_cam")
        self.thirdPersonCamNode.setPos(0, -5, 3)

        self.topDownCamNode = self.root.attachNewNode("top_down_cam")
        self.topDownCamNode.setPos(0, 0, 15)

    def takeHealthBox(self, health):
        self.health = max(self.health + health, 3)

    def takesDamage(self, damage):
        self.root.setZ(self.root.getZ() + 0.5)
        self.root.setH(self.root.getH() + 1)
        self.game.camera.setH(self.game.camera.getH() + 1)
        self.game.taskMgr.doMethodLater(
            0.1,
            lambda task: self.game.camera.setH(self.game.camera.getH() - 1),
            "reset_camera_tilt",
        )
        self.game.taskMgr.doMethodLater(
            0.2,
            lambda task: self.root.setZ(self.root.getZ() - 0.5),
            "reset_bounce",
        )
        if self.game.playerInvulnerable:
            return
        self.health -= damage
        self.game.hud.removeHeart()
        if self.health <= 0:
            self.game.gameOver()
            return
        self.game.playerInvulnerable = True
        self.game.taskMgr.doMethodLater(
            1,
            lambda task: setattr(self.game, "playerInvulnerable", False),
            "reset_invulnerability",
        )

    def swingKatanaAnimation(self):
        self.game.taskMgr.doMethodLater(
            0.05,
            lambda task: self.katana.setH(self.katana.getH() - 30),
            "swing_katana",
        )
        self.game.taskMgr.doMethodLater(
            0.1,
            lambda task: self.katana.setH(self.katana.getH() + 60),
            "reset_katana",
        )
        self.game.taskMgr.doMethodLater(
            0.2,
            lambda task: self.katana.setH(self.katana.getH() - 30),
            "reset_katana",
        )
        self.game.taskMgr.doMethodLater(
            0.1,
            lambda task: self.katana.setR(self.katana.getR() + 30),
            "swing_katana",
        )
        self.game.taskMgr.doMethodLater(
            0.2,
            lambda task: self.katana.setR(self.katana.getR() - 30),
            "reset_katana",
        )
        self.game.taskMgr.doMethodLater(
            0.15,
            lambda task: self.katana.setP(self.katana.getP() + 30),
            "swing_katana",
        )
        self.game.taskMgr.doMethodLater(
            0.2,
            lambda task: self.katana.setP(self.katana.getP() - 30),
            "reset_katana",
        )

    def swingKatana(self):
        self.swingKatanaAnimation()
        for balloon in self.game.balloonManager.balloons:
            # check distance and direction into a cone range
            balloonPos = balloon["model"].getPos()
            # balloonPos.setZ(0)
            playerPos = self.root.getPos()
            # playerPos.setZ(0)
            to_balloon = balloonPos - playerPos
            forward = self.camera.getQuat(self.game.render).getForward()
            # forward.setZ(0)
            distance = to_balloon.length()
            forward.normalize()
            to_balloon.normalize()
            angle = forward.angleDeg(to_balloon)
            # print('distance', distance)
            # print('angle', angle)
            # print('ballon', balloonPos)
            # print('player', playerPos)
            # print('to balloon', to_balloon)
            # print('forward', forward)
            # print()
            # if angle < 22.5:
            # print("Balloon is within the 45° cone in front of the player")
            if distance < 10 and angle < 30:
                self.game.balloonManager.takeDamage(balloon, 2)

    def checkObstacleCollision(self, playerPos, oldPos):
        """
        Check for codllision between player poswwwwwwition and any obstacles.
        :param playerPos: LPoint3f or a tuple (x, y, z)
        :return: True if a collision is detected, otherwise False
        """
        px, py, pz = playerPos
        old_x, old_y, old_z = oldPos
        groundHeight = 0
        for node, radius, height in self.game.obstacles:
            ox, oy, oz = node.getPos()

            dx = px - ox
            dy = py - oy
            dx_old = old_x - ox
            dy_old = old_y - oy
            distance_sq = dx * dx + dy * dy
            old_distance_sq = dx_old * dx_old + dy_old * dy_old

            if distance_sq < radius * radius:
                if pz + 0.01 > height:
                    if old_distance_sq < radius * radius:
                        return False, groundHeight + height
                    return False, groundHeight
                return True, groundHeight
        return False, groundHeight

    def update(self, dt, keys):
        if keys["zoom"] and not self.is_zoomed:
            self.is_zoomed = True
            self.game.camLens.setFov(self.zoom_fov)
        elif not keys["zoom"] and self.is_zoomed:
            self.is_zoomed = False
            self.game.camLens.setFov(self.normal_fov)

        speed = 8

        heading_rad = math.radians(self.root.getH())

        forward_vec = Point3(math.sin(-heading_rad), math.cos(-heading_rad), 0)
        right_vec = Point3(
            math.sin(-heading_rad + math.pi / 2),
            math.cos(-heading_rad + math.pi / 2),
            0,
        )
        old_pos = self.root.getPos()
        if keys["forward"]:
            self.root.setPos(self.root.getPos() + forward_vec * dt * speed)

        if keys["backward"]:
            self.root.setPos(self.root.getPos() - forward_vec * dt * speed)

        if keys["left"]:
            self.root.setPos(self.root.getPos() - right_vec * dt * speed)

        if keys["right"]:
            self.root.setPos(self.root.getPos() + right_vec * dt * speed)
        blocked, groundHeight = self.checkObstacleCollision(self.root.getPos(), old_pos)
        if blocked:
            self.root.setPos(old_pos)
        on_ground = self.root.getZ() <= groundHeight + 0.01
        if on_ground:
            self.root.setZ(
                math.sin(self.game.taskMgr.globalClock.getFrameTime() * 10) * 0.05
                + self.root.getZ()
            )
        jumping = keys.get("jump", False) or (
            self.buffer_timer > 0 and self.buffer_timer < self.max_jump_buffer_time
        )
        if self.is_jumping:
            self.buffer_timer += dt
        else:
            self.buffer_timer = 0.0

        if self.is_jumping and jumping and self.jump_timer < self.max_jump_hold:
            self.jump_timer += dt
            gravity_scale = self.gravity_scale
        else:
            gravity_scale = 1.0

        if on_ground and not self.is_jumping and jumping:
            self.is_jumping = True
            self.z_velocity = self.jump_speed
            self.jump_timer = 0.0
            self.buffer_timer = 0.0

        if self.is_jumping and not jumping:
            self.jump_timer = 0.0
            self.is_jumping = False
            self.buffer_timer = 0.0

        self.z_velocity -= self.gravity * gravity_scale * dt

        new_z = self.root.getZ() + self.z_velocity * dt
        if new_z <= groundHeight + 0.01 and not jumping:
            new_z = groundHeight
            self.z_velocity = 0.0
            self.is_jumping = False

        playerPos = self.root.getPos()
        playerPos.x = max(-80, min(80, playerPos.x))
        playerPos.y = max(-80, min(80, playerPos.y))
        playerPos.z = new_z
        self.root.setPos(playerPos)
        self.root.setZ(new_z)

    def switchCamera(self):
        if self.camera_mode == "first-person":
            self.switchToThirdPerson()
        elif self.camera_mode == "third-person":
            self.switchToTopDown()
        else:
            self.switchToFirstPerson()

    def switchToFirstPerson(self):
        self.camera_mode = "first-person"
        self.camera.reparentTo(self.firstPersonCamNode)
        self.camera.setPos(0, 0, 0)
        self.camera.setHpr(0, 0, 0)

        if hasattr(self.game, "hud"):
            self.game.hud.updateCameraText("First-Person")

        if hasattr(self.game, "inputController"):
            self.game.inputController.setCrosshairVisible(True)

        props = WindowProperties()
        props.setCursorHidden(True)
        self.game.win.requestProperties(props)

    def switchToThirdPerson(self):
        self.camera_mode = "third-person"
        self.camera.reparentTo(self.thirdPersonCamNode)
        self.camera.setPos(0, 0, 0)
        self.camera.lookAt(self.player_head)

        if hasattr(self.game, "hud"):
            self.game.hud.updateCameraText("Third-Person")

        if hasattr(self.game, "inputController"):
            self.game.inputController.setCrosshairVisible(True)

        props = WindowProperties()
        props.setCursorHidden(True)
        self.game.win.requestProperties(props)

    def switchToTopDown(self):
        self.camera_mode = "top-down"
        self.camera.reparentTo(self.topDownCamNode)
        self.camera.setPos(0, 0, 0)
        self.camera.setHpr(0, -90, 0)

        if hasattr(self.game, "hud"):
            self.game.hud.updateCameraText("Top-Down")

        if hasattr(self.game, "inputController"):
            self.game.inputController.setCrosshairVisible(True)

        props = WindowProperties()
        props.setCursorHidden(True)
        self.game.win.requestProperties(props)

    def switchWeapon(self, weaponType):
        if weaponType == "dart":
            self.dart_gun.show()
            self.katana.hide()
        elif self.hasKatana:
            self.dart_gun.hide()
            self.katana.show()
        self.currentWeapon = weaponType

    def reset(self):
        self.root.setPos(0, 0, 0)
        self.heading = 0
        self.pitch = 0
        self.health = 3
        self.root.setH(self.heading)
        self.firstPersonCamNode.setP(0)
        self.switchToFirstPerson()
        self.switchWeapon("dart")
        self.is_zoomed = False
        self.game.camLens.setFov(self.normal_fov)
