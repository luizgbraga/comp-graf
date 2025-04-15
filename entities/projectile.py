import math
import random

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorInterval,
    Parallel,
    Sequence,
    Wait,
)
from panda3d.core import Point3


class ProjectileManager:
    def __init__(self, game):
        self.game = game
        self.projectiles = []
        self.canShoot = True
        self.lastShootTime = 0

        # Weapon properties
        self.weaponProperties = {
            "dart": {"damage": 1, "speed": 30, "cooldown": 0.5},
            "katana": {"damage": 3, "speed": 45, "cooldown": 0.3},
        }

    def shootProjectile(self):
        """Fire a projectile based on the current weapon"""
        if not self.canShoot or self.game.gameState != "playing":
            return

        # Get weapon type
        weaponType = self.game.weaponType

        # Create a dart/katana model
        if weaponType == "dart":
            dart_model = self.game.createBox(
                0.1, 0.5, 0.1, (0.8, 0.8, 0, 1)
            )  # Yellow dart
        else:  # Katana
            dart_model = self.game.createBox(
                0.2, 1.0, 0.2, (0.7, 0.7, 0.7, 1)
            )  # Silver katana

        dart_model.reparentTo(self.game.render)

        # Set position based on camera mode
        if self.game.player.camera_mode == "first-person":
            # In first-person, shoot from the camera view
            start_pos = self.game.camera.getPos(self.game.render)
            direction = self.game.camera.getQuat(self.game.render).getForward()
        else:
            # In other modes, shoot from the weapon position toward the center of the screen
            start_pos = self.game.player.weapon_holder.getPos(self.game.render)

            # Get a point in the middle of the screen
            if self.game.mouseWatcherNode.hasMouse():
                mpos = self.game.mouseWatcherNode.getMouse()
                near_point = Point3()
                far_point = Point3()

                self.game.camLens.extrude(mpos, near_point, far_point)
                direction = far_point - near_point
                direction.normalize()
            else:
                # Default to forward if mouse not available
                direction = self.game.camera.getQuat(self.game.render).getForward()

        # Set the dart position and orientation
        dart_model.setPos(start_pos)

        # Make the dart look in the direction it's traveling
        look_at = start_pos + direction * 10
        dart_model.lookAt(look_at)

        # Create a visual effect for shooting
        self.createShootEffect(start_pos, direction)

        # Add dart to the list
        self.projectiles.append(
            {"model": dart_model, "direction": direction, "type": weaponType}
        )

        # Set cooldown
        self.canShoot = False
        self.lastShootTime = self.game.taskMgr.globalClock.getFrameTime()

    def createShootEffect(self, position, direction):
        """Create visual effect when shooting"""
        # Create a quick muzzle flash effect
        flash = self.game.createBox(0.2, 0.2, 0.2, (1, 0.8, 0, 0.8))  # Yellow-orange
        flash.reparentTo(self.game.render)
        flash.setPos(position + direction * 0.5)  # Slightly in front of gun

        # Create a fade-out effect
        fade_out = LerpColorInterval(flash, 0.2, (1, 0.8, 0, 0), (1, 0.8, 0, 0.8))
        fade_out.start()

        # Remove the flash after the fade
        Sequence(Wait(0.2), Func(flash.removeNode)).start()

    def createUpgradeEffect(self, position):
        """Create a sparkle effect around the weapon when upgrading"""
        # Create a sparkle effect around the weapon
        for i in range(20):
            particle = self.game.createBox(
                0.1, 0.1, 0.1, (1, 1, 1, 0.8)
            )  # White sparkle
            particle.reparentTo(self.game.render)
            particle.setPos(position)

            # Random direction for the sparkle
            angle = random.uniform(0, 2 * math.pi)
            height = random.uniform(0.2, 1.0)
            end_pos = Point3(
                position.x + math.cos(angle) * 1,
                position.y + math.sin(angle) * 1,
                position.z + height,
            )

            # Create animation sequence with color change
            particle_seq = Sequence(
                Parallel(
                    particle.posInterval(0.5, end_pos, blendType="easeOut"),
                    LerpColorInterval(particle, 0.5, (1, 0.5, 0, 0), (1, 1, 1, 0.8)),
                ),
                Func(particle.removeNode),
            )
            particle_seq.start()

    def createBalloonPopEffect(self, position, color):
        """Create effect for balloon popping"""
        # Create a simple balloon pop effect using custom particles
        for _ in range(12):
            # Create small fragments of the balloon
            fragment = self.game.createBox(0.2, 0.2, 0.2, color)
            fragment.reparentTo(self.game.render)
            fragment.setPos(position)

            # Random direction for the fragment
            angle = random.uniform(0, 2 * math.pi)
            height = random.uniform(0.5, 2.0)
            end_pos = Point3(
                position.x + math.cos(angle) * 2,
                position.y + math.sin(angle) * 2,
                position.z + height,
            )

            # Create animation sequence
            fragment_seq = Sequence(
                fragment.posInterval(0.6, end_pos, blendType="easeOut"),
                fragment.scaleInterval(0.3, 0.01),  # Shrink to nothing
                Func(fragment.removeNode),
            )
            fragment_seq.start()

    def update(self, dt):
        """Update all projectiles and handle shooting cooldown"""
        # Update shooting cooldown
        current_time = self.game.taskMgr.globalClock.getFrameTime()
        weaponType = self.game.weaponType

        if not self.canShoot:
            if (
                current_time - self.lastShootTime
                >= self.weaponProperties[weaponType]["cooldown"]
            ):
                self.canShoot = True

        # Update projectiles
        for projectile in self.projectiles[:]:
            # Move the projectile forward
            speed = self.weaponProperties[projectile["type"]]["speed"]
            projectile["model"].setY(projectile["model"], dt * speed)

            # Check for collision with balloons
            for balloon in self.game.balloonManager.balloons[:]:
                projectile_pos = projectile["model"].getPos()
                balloon_pos = balloon["model"].getPos()

                if (projectile_pos - balloon_pos).length() < 1.5:
                    # Create a particle effect for balloon pop
                    self.createBalloonPopEffect(balloon_pos, balloon["color"])

                    # Sometimes spawn a coin where the balloon popped
                    if random.random() < 0.3:  # 30% chance
                        self.game.coinManager.spawnFlyingCoin(balloon_pos)

                    # Remove the balloon
                    self.game.balloonManager.removeBalloon(balloon)

                    # Remove the projectile
                    projectile["model"].removeNode()
                    if projectile in self.projectiles:
                        self.projectiles.remove(projectile)

                    # Increase score and coins
                    self.game.score += 1
                    self.game.coins += 1

                    # Update HUD
                    self.game.hud.updateScore(self.game.score)
                    self.game.hud.updateCoins(self.game.coins)

                    break

            # Remove if too far away or already hit something
            if projectile in self.projectiles:
                projectile_pos = projectile["model"].getPos()
                player_pos = self.game.player.root.getPos()

                if (projectile_pos - player_pos).length() > 50:
                    projectile["model"].removeNode()
                    self.projectiles.remove(projectile)

    def reset(self):
        """Clear all projectiles"""
        for projectile in self.projectiles:
            projectile["model"].removeNode()
        self.projectiles = []
        self.canShoot = True
        self.lastShootTime = 0
