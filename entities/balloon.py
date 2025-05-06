import math
import random

from direct.gui.DirectGui import DirectFrame


class BalloonManager:
    def __init__(self, game):
        self.game = game
        self.balloons = []
        self.balloon_spawn_timer = 0

        # Load the balloon model
        self.balloon_model = self.game.loader.loadModel("assets/models/balloon.bam")

        # Balloon colors with their properties (health, spawn chance, and speed multiplier)
        self.balloon_colors = [
            {
                "color": (1, 0, 0, 1),
                "health": 2,
                "chance": 0.20,
                "speed_multiplier": 1.0,
            },  # Red - Common, 2 hits
            {
                "color": (0, 1, 0, 1),
                "health": 2,
                "chance": 0.20,
                "speed_multiplier": 1.2,
            },  # Green - Common, 2 hits, faster
            {
                "color": (0, 0, 1, 1),
                "health": 3,
                "chance": 0.20,
                "speed_multiplier": 0.9,
            },  # Blue - Uncommon, 3 hits, slower
            {
                "color": (1, 1, 0, 1),
                "health": 3,
                "chance": 0.20,
                "speed_multiplier": 1.1,
            },  # Yellow - Uncommon, 3 hits, faster
            {
                "color": (1, 0, 1, 1),
                "health": 4,
                "chance": 0.15,
                "speed_multiplier": 0.8,
            },  # Purple - Rare, 4 hits, slower
            {
                "color": (0, 1, 1, 1),
                "health": 6,
                "chance": 0.05,
                "speed_multiplier": 0.7,
            },  # Cyan - Very Rare, 6 hits, slowest
        ]

        # Balloon types with their properties
        self.balloon_types = {
            "small": {"scale": 0.2, "points": 1, "speed_multiplier": 1.2},
            "medium": {"scale": 0.3, "points": 2, "speed_multiplier": 1.0},
            "large": {"scale": 0.4, "points": 3, "speed_multiplier": 0.8},
        }

    def spawnBalloon(self):
        """Create a new balloon enemy"""
        # Create balloon model instance
        balloon_model = self.balloon_model.copyTo(self.game.render)

        # Choose random balloon type
        balloon_type = random.choice(list(self.balloon_types.keys()))
        balloon_props = self.balloon_types[balloon_type]

        # Set balloon size based on type
        balloon_model.setScale(balloon_props["scale"])

        # Choose balloon color based on spawn chances
        total_chance = sum(color["chance"] for color in self.balloon_colors)
        roll = random.uniform(0, total_chance)
        current_sum = 0
        chosen_color = None

        for color_data in self.balloon_colors:
            current_sum += color_data["chance"]
            if roll <= current_sum:
                chosen_color = color_data
                break

        # Set the balloon color
        color = chosen_color["color"]
        balloon_model.setColor(color[0], color[1], color[2], color[3])
        # Ensure color is applied to all nodes in the model
        for child in balloon_model.findAllMatches("**"):
            child.setColor(color[0], color[1], color[2], color[3])

        # Set the balloon position randomly around the player
        angle = random.uniform(0, 2 * math.pi)
        # Increased spawn distance range for more dynamic gameplay
        min_distance = 40
        max_distance = 60
        distance = random.uniform(min_distance, max_distance)
        player_pos = self.game.player.root.getPos()
        x = player_pos.x + distance * math.cos(angle)
        y = player_pos.y + distance * math.sin(angle)
        z = 2 + random.uniform(0, 4)  # Increased height variation

        # Constrain the balloon position to the play area
        x = max(-75, min(75, x))  # Increased play area to match ground size
        y = max(-75, min(75, y))

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

        # Store balloon and its properties
        self.balloons.append(
            {
                "model": balloon_model,
                "minimap_marker": marker,
                "color": color,
                "type": balloon_type,
                "health": chosen_color["health"],
                "max_health": chosen_color["health"],
                "points": balloon_props["points"],
                "speed_multiplier": balloon_props["speed_multiplier"] * chosen_color["speed_multiplier"],
            }
        )

    def takeDamage(self, balloon, damage):
        """Handle balloon taking damage"""
        balloon["health"] -= damage

        # Update balloon size based on remaining health
        health_ratio = balloon["health"] / balloon["max_health"]
        base_scale = self.balloon_types[balloon["type"]]["scale"]
        current_scale = base_scale * (
            0.5 + 0.5 * health_ratio
        )  # Scale between 50% and 100% of original size
        balloon["model"].setScale(current_scale)

        # Update opacity based on health
        # Start at 1.0 (fully opaque) and go down to 0.3 (semi-transparent)
        opacity = 0.3 + (0.7 * health_ratio)

        # Get the original color
        color = balloon["color"]

        # Apply the new color with updated opacity
        balloon["model"].setColor(color[0], color[1], color[2], opacity)
        for child in balloon["model"].findAllMatches("**"):
            child.setColor(color[0], color[1], color[2], opacity)

        if balloon["health"] <= 0:
            # Create pop effect
            self.game.projectileManager.createBalloonPopEffect(
                balloon["model"].getPos(), balloon["color"]
            )

            # Chance to spawn a coin
            if random.random() < 0.3:  # 30% chance
                self.game.coinManager.spawnFlyingCoin(balloon["model"].getPos())

            # Add score and coins
            self.game.score += balloon["points"]
            self.game.coins += balloon["points"]
            self.game.hud.updateScore(self.game.score)
            self.game.hud.updateCoins(self.game.coins)

            # Remove the balloon
            self.removeBalloon(balloon)

    def update(self, dt):
        """Update all balloons"""
        # Update spawn timer
        self.balloon_spawn_timer += dt

        # Spawn new balloons
        if self.balloon_spawn_timer > 1.0:  # Every 1 second
            self.balloon_spawn_timer = 0
            if (
                len(self.balloons) < 10 + self.game.score // 10
            ):  # More balloons as score increases
                self.spawnBalloon()

        # Update balloon positions
        for balloon in self.balloons[:]:
            # Move the balloon towards the player
            player_pos = self.game.player.root.getPos()
            balloon_pos = balloon["model"].getPos()
            direction = player_pos - balloon_pos
            direction.normalize()

            # Speed increases with score and varies by balloon type/color
            base_speed = 2 + (self.game.score / 100)  # Starts at 2, gradually increases
            balloon_speed = base_speed * balloon["speed_multiplier"]
            balloon["model"].setPos(balloon_pos + direction * dt * balloon_speed)

            # Bob up and down
            current_z = balloon["model"].getZ()
            balloon["model"].setZ(
                current_z
                + math.sin(self.game.taskMgr.globalClock.getFrameTime() * 2) * 0.02
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

    def removeBalloon(self, balloon):
        """Remove a balloon and its marker"""
        balloon["model"].removeNode()
        balloon["minimap_marker"].destroy()
        if balloon in self.balloons:
            self.balloons.remove(balloon)

    def reset(self):
        """Clear all balloons"""
        for balloon in self.balloons:
            balloon["model"].removeNode()
            balloon["minimap_marker"].destroy()
        self.balloons = []
        self.balloon_spawn_timer = 0
