import math
import random

from direct.interval.IntervalGlobal import Func, Sequence
from panda3d.core import Point3, TransparencyAttrib


class KatanaManager:
    def __init__(self, game):
        self.game = game
        self.katanas = []
        self.katana_size = 1.2
        self.katana_radius = 1.5
        self.katana_texture = self.game.loader.loadTexture("assets/katana.png")

        for _ in range(2):
            self.spawnKatana()

    def createKatanaModel(self):
        """Create a textured spinning cube as a katana pickup"""
        box = self.game.createBox(
            self.katana_size, self.katana_size * 0.25, self.katana_size * 0.1, (1, 1, 1, 1)
        )
        box.setTexture(self.katana_texture)
        box.setTransparency(TransparencyAttrib.M_alpha)
        return box

    def spawnKatana(self):
        katana = self.createKatanaModel()
        katana.reparentTo(self.game.render)

        x = random.uniform(-75, 75)
        y = random.uniform(-75, 75)
        z = 0.5
        katana.setPos(x, y, z)
        katana.setHpr(0, 90, 0)

        katana_spin = katana.hprInterval(2, Point3(360, 90, 0))
        katana_spin.loop()

        katana_bounce = Sequence(
            katana.posInterval(1, Point3(x, y, z + 0.3), blendType="easeInOut"),
            katana.posInterval(1, Point3(x, y, z), blendType="easeInOut"),
        )
        katana_bounce.loop()

        self.katanas.append({
            "model": katana,
            "spin": katana_spin,
            "bounce": katana_bounce,
            "pos": Point3(x, y, z)
        })

    def checkCollisions(self, player_pos):
        for katana in self.katanas[:]:
            model = katana["model"]
            if model.isEmpty():
                continue
            katana_pos = model.getPos()
            if (katana_pos - player_pos).length() < self.katana_radius:
                self.collectKatana(katana)

    def collectKatana(self, katana):
        katana["spin"].finish()
        katana["bounce"].finish()
        katana["model"].removeNode()
        if self.game.player.currentWeapon != "katana":
            self.katanas.remove(katana)
            self.game.player.hasKatana = True
            self.game.player.switchWeapon("katana")
