import math
import random

from direct.gui.DirectGui import DirectFrame
from panda3d.core import NodePath


class BalloonManager:
    def __init__(self, game):
        self.game = game
        self.balloons = []
        self.balloon_spawn_timer = 0

        # Load the balloon model
        self.balloon_model = self.game.loader.loadModel("assets/models/balloon.bam")

        # Balloon colors
        self.balloon_colors = [
            (1, 0, 0, 1),  # Red
            (0, 1, 0, 1),  # Green
            (0, 0, 1, 1),  # Blue
            (1, 1, 0, 1),  # Yellow
            (1, 0, 1, 1),  # Magenta
            (0, 1, 1, 1),  # Cyan
        ]

    def spawnBalloon(self):
        """Create a new balloon enemy"""
        # Create balloon model instance
        balloon_model = self.balloon_model.copyTo(self.game.render)

        # Choose random color
        color = random.choice(self.balloon_colors)
        balloon_model.setColor(*color)

        # Set the balloon position randomly around the player
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(30, 40)
        player_pos = self.game.player.root.getPos()
        x = player_pos.x + distance * math.cos(angle)
        y = player_pos.y + distance * math.sin(angle)
        z = 2 + random.uniform(0, 3)  # Random height

        # Constrain the balloon position to the play area
        x = max(-35, min(35, x))
        y = max(-35, min(35, y))

        balloon_model.setPos(x, y, z)

        # Add a minimap marker for this balloon
        marker = DirectFrame(
            frameColor=(color[0], color[1], color[2], 0.8),
            frameSize=(-0.005, 0.005, -0.005, 0.005),
            parent=self.game.minimap.frame,
        )

        # Calculate minimap position
        map_scale = 0.14 / 35  # Same scale as player marker
        marker.setPos(0.15 + x * map_scale, 0, -0.15 - y * map_scale)

        # Store balloon and its marker
        self.balloons.append(
            {"model": balloon_model, "minimap_marker": marker, "color": color}
        )

    def update(self, dt):
        """Update all balloons"""
        # Update spawn timer
        self.balloon_spawn_timer += dt

        # Spawn new balloons
        if self.balloon_spawn_timer > 1.0:  # Every 1 second
            self.balloon_spawn_timer = 0
            if len(self.balloons) < 10 + self.game.score // 10:  # More balloons as score increases
                self.spawnBalloon()

        # Update balloon positions
        for balloon in self.balloons[:]:
            # Move the balloon towards the player
            player_pos = self.game.player.root.getPos()
            balloon_pos = balloon["model"].getPos()
            direction = player_pos - balloon_pos
            direction.normalize()

            # Speed increases with score
            balloon_speed = 2 + (self.game.score / 100)  # Starts at 2, gradually increases
            balloon["model"].setPos(balloon_pos + direction * dt * balloon_speed)

            # Bob up and down
            current_z = balloon["model"].getZ()
            balloon["model"].setZ(
                current_z + math.sin(self.game.taskMgr.globalClock.getFrameTime() * 2) * 0.02
            )

            # Update minimap balloon markers
            balloon_pos = balloon["model"].getPos()
            map_scale = 0.14 / 35  # Same scale as player marker
            balloon["minimap_marker"].setPos(
                0.15 + balloon_pos.x * map_scale, 0, -0.15 - balloon_pos.y * map_scale
            )

            # Check if the balloon reached the player
            if (balloon_pos - player_pos).length() < 1.5:
                self.game.gameOver()
                return

    def reset(self):
        """Clear all balloons"""
        for balloon in self.balloons:
            balloon["model"].removeNode()
            balloon["minimap_marker"].destroy()
        self.balloons = []
        self.balloon_spawn_timer = 0

    def removeBalloon(self, balloon):
        """Remove a balloon and its marker"""
        balloon["model"].removeNode()
        balloon["minimap_marker"].destroy()
        if balloon in self.balloons:
            self.balloons.remove(balloon) 