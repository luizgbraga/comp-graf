import math
import random

from direct.gui.DirectGui import DirectFrame
from direct.interval.IntervalGlobal import Func, Parallel, Sequence
from direct.interval.LerpInterval import LerpColorInterval
from panda3d.core import CardMaker, Point3


class BalloonManager:
    def __init__(self, game):
        self.game = game
        self.created = False
        self.balloons = []
        self.balloon_spawn_timer = 0
        self.bob_amplitude = 0.02
        self.balloon_growth_timer = 0
        self.balloon_model = self.game.loader.loadModel("assets/models/balloon.bam")

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

        self.balloon_types = {
            "small": {"scale": 0.2, "points": 1, "speed_multiplier": 1.2},
            "medium": {"scale": 0.3, "points": 2, "speed_multiplier": 1.0},
            "large": {"scale": 0.4, "points": 3, "speed_multiplier": 0.8},
        }

    def spawnBalloon(self):
        balloon_model = self.balloon_model.copyTo(self.game.render)
        balloon_type = random.choice(list(self.balloon_types.keys()))
        balloon_props = self.balloon_types[balloon_type]
        balloon_model.setScale(balloon_props["scale"])

        total_chance = sum(color["chance"] for color in self.balloon_colors)
        roll = random.uniform(0, total_chance)
        current_sum = 0
        chosen_color = None

        for color_data in self.balloon_colors:
            current_sum += color_data["chance"]
            if roll <= current_sum:
                chosen_color = color_data
                break

        color = chosen_color["color"]
        balloon_model.setColor(color[0], color[1], color[2], 1)

        for child in balloon_model.findAllMatches("**"):
            child.setColor(color[0], color[1], color[2], 1)

        angle = random.uniform(0, 2 * math.pi)

        min_distance = 40
        max_distance = 60
        distance = random.uniform(min_distance, max_distance)
        player_pos = self.game.player.root.getPos()
        x = player_pos.x + distance * math.cos(angle)
        y = player_pos.y + distance * math.sin(angle)
        z = 2 + random.uniform(0, 4)

        x = max(-75, min(75, x))
        y = max(-75, min(75, y))

        balloon_model.setPos(x, y, z)

        marker = DirectFrame(
            frameColor=(color[0], color[1], color[2], 1),
            frameSize=(-0.005, 0.005, -0.005, 0.005),
            parent=self.game.minimap.frame,
        )

        map_scale = 0.14 / 75
        marker.setPos(0.15 + x * map_scale, 0, -0.15 - y * map_scale)

        cm = CardMaker("balloon_square")
        cm.setFrame(-0.004, 0.004, -0.004, 0.004)
        balloon_square = marker.attachNewNode(cm.generate())
        balloon_square.setColor(color[0], color[1], color[2], 1)

        self.balloons.append(
            {
                "model": balloon_model,
                "minimap_marker": marker,
                "color": color,
                "type": balloon_type,
                "health": chosen_color["health"],
                "max_health": chosen_color["health"],
                "points": balloon_props["points"],
                "speed_multiplier": balloon_props["speed_multiplier"]
                * chosen_color["speed_multiplier"],
            }
        )

    def balloonHitEffect(self, balloon):
        for i in range(8):
            particle = self.game.createBox(0.1, 0.1, 0.1, balloon["color"])
            particle.reparentTo(self.game.render)
            particle.setPos(balloon["model"].getPos())
            angle = random.uniform(0, 2 * math.pi)
            height = random.uniform(0.5, 1.5)
            end_pos = Point3(
                balloon["model"].getPos().x + math.cos(angle) * 1.5,
                balloon["model"].getPos().y + math.sin(angle) * 1.5,
                balloon["model"].getPos().z + height,
            )

            particle_seq = Sequence(
                Parallel(
                    particle.posInterval(0.5, end_pos, blendType="easeOut"),
                    LerpColorInterval(
                        particle,
                        0.5,
                        (1, 0.5, 0, 0),
                        (
                            balloon["color"][0],
                            balloon["color"][1],
                            balloon["color"][2],
                            1,
                        ),
                    ),
                ),
                Func(particle.removeNode),
            )
            particle_seq.start()

        bobbing_effect = Sequence(
            balloon["model"].posInterval(
                0.5,
                Point3(
                    balloon["model"].getX(),
                    balloon["model"].getY(),
                    balloon["model"].getZ() + 0.2,
                ),
                blendType="easeInOut",
            ),
            balloon["model"].posInterval(
                0.5,
                Point3(
                    balloon["model"].getX(),
                    balloon["model"].getY(),
                    balloon["model"].getZ(),
                ),
                blendType="easeInOut",
            ),
        )
        bobbing_effect.loop()

    def takeDamage(self, balloon, damage):
        balloon["health"] -= damage

        health_ratio = balloon["health"] / balloon["max_health"]
        base_scale = self.balloon_types[balloon["type"]]["scale"]
        current_scale = base_scale * (0.5 + 0.5 * health_ratio)
        balloon["model"].setScale(current_scale)

        color = balloon["color"]
        balloon["model"].setColor(color[0], color[1], color[2], 1)
        for child in balloon["model"].findAllMatches("**"):
            child.setColor(color[0], color[1], color[2], 1)
        self.balloonHitEffect(balloon)

        if balloon["health"] <= 0:
            self.game.projectileManager.createBalloonPopEffect(
                balloon["model"].getPos(), balloon["color"]
            )
            if random.random() < 0.3:
                self.game.coinManager.spawnFlyingCoin(balloon["model"].getPos())

            self.game.score += balloon["points"]
            self.game.coins += balloon["points"]
            self.game.hud.updateScore(self.game.score)
            self.game.hud.updateCoins(self.game.coins)

            self.removeBalloon(balloon)
    def growBalloons(self):
        for balloon in self.balloons:
            # Increase health and max_health
            balloon["max_health"] += 1
            balloon["health"] += 1
            # Scale up slightly (e.g., 5% per growth)
            current_scale = balloon["model"].getScale()
            new_scale = None
            if current_scale.length() > 10.0:  # Prevent too large
                new_scale = current_scale
            else:
                new_scale = current_scale * 1.1  # 5% larger
            balloon["model"].setScale(new_scale)
    def update(self, dt):
        self.balloon_spawn_timer += dt
        self.balloon_growth_timer += dt

        # Spawn new balloons
        # if not self.created:
            # self.spawnBalloon()
            # self.created = True
        if self.balloon_spawn_timer > 1.0:  # Every 1 second
            self.balloon_spawn_timer = 0
            if len(self.balloons) < 10 + self.game.score // 10:
                self.spawnBalloon()
        if self.balloon_growth_timer > 10.0:
            self.balloon_growth_timer = 0
            self.growBalloons()
        for balloon in self.balloons[:]:
            player_pos = self.game.player.root.getPos()
            balloon_pos = balloon["model"].getPos()
            direction = player_pos - balloon_pos
            direction.normalize()

            base_speed = 2 + (self.game.score / 100)
            balloon_speed = base_speed * balloon["speed_multiplier"]
            balloon["model"].setPos(balloon_pos + direction * dt * balloon_speed)

            current_z = balloon["model"].getZ()
            balloon["model"].setZ(
                max(current_z, self.bob_amplitude + 1)
                + math.sin(self.game.taskMgr.globalClock.getFrameTime() * 2)
                * self.bob_amplitude
            )

            balloon_pos = balloon["model"].getPos()
            map_scale = 0.14 / 75
            x_pos = 0.15 + balloon_pos.x * map_scale
            y_pos = -0.15 - balloon_pos.y * map_scale

            x_pos = max(0.01, min(0.29, x_pos))
            y_pos = max(-0.29, min(-0.01, y_pos))

            balloon["minimap_marker"].setPos(x_pos, 0, y_pos)

            if (balloon_pos - player_pos).length() < 1.5:
                self.game.player.takesDamage(1)
                return

    def removeBalloon(self, balloon):
        balloon["model"].removeNode()
        balloon["minimap_marker"].destroy()
        if balloon in self.balloons:
            self.balloons.remove(balloon)

    def reset(self):
        for balloon in self.balloons:
            balloon["model"].removeNode()
            balloon["minimap_marker"].destroy()
        self.balloons = []
        self.balloon_spawn_timer = 0
