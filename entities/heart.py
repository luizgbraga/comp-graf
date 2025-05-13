import random

from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3, TransparencyAttrib


class HeartManager:
    def __init__(self, game):
        self.game = game
        self.hearts = []
        self.heart_size = 0.8
        self.heart_radius = 1.5
        self.heart_texture = self.game.loader.loadTexture("assets/health.png")
        for _ in range(3):
            self.spawnHeart()

    def createHeartModel(self):
        box = self.game.createBox(
            self.heart_size, self.heart_size, self.heart_size, (1, 1, 1, 1)
        )
        box.setTexture(self.heart_texture)
        box.setTransparency(TransparencyAttrib.M_alpha)
        return box

    def spawnHeart(self):
        heart = self.createHeartModel()
        heart.reparentTo(self.game.render)

        x = random.uniform(-75, 75)
        y = random.uniform(-75, 75)
        z = 0.5
        heart.setPos(x, y, z)
        heart.setHpr(0, 90, 0)

        heart_spin = heart.hprInterval(2, Point3(360, 90, 0))
        heart_spin.loop()

        heart_bounce = Sequence(
            heart.posInterval(1, Point3(x, y, z + 0.3), blendType="easeInOut"),
            heart.posInterval(1, Point3(x, y, z), blendType="easeInOut"),
        )
        heart_bounce.loop()

        self.hearts.append(
            {
                "model": heart,
                "spin": heart_spin,
                "bounce": heart_bounce,
                "pos": Point3(x, y, z),
            }
        )

    def checkCollisions(self, player_pos):
        for heart in self.hearts[:]:
            model = heart["model"]
            if model.isEmpty():
                continue
            heart_pos = model.getPos()
            if (heart_pos - player_pos).length() < self.heart_radius:
                self.collectHeart(heart)

    def collectHeart(self, heart):
        heart["spin"].finish()
        heart["bounce"].finish()
        heart["model"].removeNode()

        if self.game.player.health < 3:
            self.hearts.remove(heart)
            self.game.player.health += 1
            self.game.hud.addHeart()
            self.spawnHeart()
