from direct.gui.DirectGui import DirectFrame
from panda3d.core import CardMaker  # Added missing import


class Minimap:
    def __init__(self, game):
        self.game = game

        self.frame = DirectFrame(
            frameColor=(0, 0, 0, 0.5),
            frameSize=(0, 0.3, -0.3, 0),
            pos=(0.7, 0, -0.7),
            parent=game.aspect2d,
        )

        # Background
        cm = CardMaker("minimap_card")
        cm.setFrame(0, 0.28, -0.28, 0)
        self.map_card = self.frame.attachNewNode(cm.generate())
        self.map_card.setPos(0.01, 0, -0.01)
        self.map_card.setColor(0.2, 0.6, 0.2, 1)  # Green background for map

        # Player indicator on minimap
        self.player_marker = DirectFrame(
            frameColor=(0, 0, 0, 0),  # Transparent
            frameSize=(-0.01, 0.01, -0.01, 0.01),
            pos=(0.15, 0, -0.15),  # Center of the minimap
            parent=self.frame,
        )

        # Create the player square
        cm = CardMaker("player_square")
        cm.setFrame(-0.005, 0.005, -0.005, 0.005)  # Square shape
        self.player_square = self.player_marker.attachNewNode(cm.generate())
        self.player_square.setColor(1, 1, 0, 1)  # Yellow

        # Hide minimap initially
        self.hide()

    def updatePlayerMarker(self, player_pos, heading):
        map_scale = 0.14 / 75  # 0.14 is half the map size, 75 is half the terrain size
        self.player_marker.setPos(
            0.15 + player_pos.x * map_scale, 0, -0.15 - player_pos.y * map_scale
        )

        self.player_marker.setR(-heading)

    def show(self):
        self.frame.show()

    def hide(self):
        self.frame.hide()
