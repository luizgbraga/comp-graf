from panda3d.core import Point3, NodePath, TransparencyAttrib, CardMaker, Texture, PNMImage
import math

class Effects:
    def __init__(self, game):
        self.game = game
        self.max_border_dist = 0.3
        self.pulse_speed = 2.0
        self.overlay = self._create_gradient_overlay()
        self.overlay.hide()
    
    def create_border_gradient_texture(self, size=512, max_distance=0.3):
        img = PNMImage(size, size, 4)
        for y in range(size):
            for x in range(size):
                # Normalize to [-1, 1]
                nx = (x / (size - 1)) * 2 - 1
                ny = (y / (size - 1)) * 2 - 1
                # Distance to nearest border
                dist_left   = abs(nx + 1)
                dist_right  = abs(1 - nx)
                dist_top    = abs(1 - ny)
                dist_bottom = abs(ny + 1)
                min_dist = min(dist_left, dist_right, dist_top, dist_bottom)
                intensity = max(0.0, min(1.0, 1.0 - (min_dist / max_distance)))
                img.setXelA(x, y, 1.0, 0.0, 0.0, intensity)  # Red with alpha
        tex = Texture("border_gradient")
        tex.load(img)
        tex.setFormat(Texture.F_rgba)
        return tex
    def _create_gradient_overlay(self):
        # Generate the border gradient texture
        tex = self.create_border_gradient_texture(size=512, max_distance=self.max_border_dist)

        cm = CardMaker("overlay")
        cm.setFrameFullscreenQuad()
        quad = NodePath(cm.generate())
        quad.reparentTo(self.game.render2d)
        quad.setTransparency(TransparencyAttrib.M_alpha)
        quad.setTexture(tex)
        quad.setColor(1, 1, 1, 1)  # Base color
        return quad
    def _create_fullscreen_overlay(self):

        cm = CardMaker("overlay")
        cm.setFrame(-1, 1, -1, 1)
        quad = NodePath(cm.generate())
        quad.reparentTo(self.game.aspect2d)
        quad.setColor(1, 0, 0, 0)
        quad.setTransparency(TransparencyAttrib.M_alpha)
        return quad

    def balloonAlert(self):
        # Determine whether to show effect based on balloons
        clock = self.game.taskMgr.globalClock
        pulse = 0.2 + 0.8 * (math.sin(clock.getFrameTime() * self.pulse_speed) ** 2)
        has_alert = False

        for balloon in self.game.balloonManager.balloons:
            dist = (balloon["model"].getPos(self.game.render) - self.game.player.root.getPos(self.game.render)).length()
            if dist < 6:  # Trigger distance
                has_alert = True
                break

        if has_alert:
            self.overlay.setColor(1, 1, 1, pulse)  # Alpha modulated by pulse
            self.overlay.show()
        else:
            self.overlay.hide()
