import math
import random

from direct.interval.IntervalGlobal import Func, Sequence
from panda3d.core import (
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    NodePath,
    Point3,
)


class CoinManager:
    def __init__(self, game):
        self.game = game
        self.terrainCoins = []
        self.coin_radius = 2.5

        # Initialize terrain coins
        for _ in range(20):
            self.spawnCoinOnTerrain()

    def createCoinModel(self):
        """Create a 3D coin model using a cylinder"""
        format = GeomVertexFormat.getV3n3c4()
        vdata = GeomVertexData("coin", format, Geom.UHStatic)

        # Create writers for vertex data
        vertex = GeomVertexWriter(vdata, "vertex")
        normal = GeomVertexWriter(vdata, "normal")
        color = GeomVertexWriter(vdata, "color")

        # Coin parameters
        radius = 0.3
        thickness = 0.1
        segments = 32

        # Create vertices for top and bottom faces
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            next_angle = ((i + 1) / segments) * 2 * math.pi

            # Top face vertices
            vertex.addData3f(0, 0, thickness / 2)
            normal.addData3f(0, 0, 1)
            color.addData4f(1.0, 0.84, 0, 1)

            vertex.addData3f(
                radius * math.cos(angle), radius * math.sin(angle), thickness / 2
            )
            normal.addData3f(0, 0, 1)
            color.addData4f(1.0, 0.84, 0, 1)

            vertex.addData3f(
                radius * math.cos(next_angle),
                radius * math.sin(next_angle),
                thickness / 2,
            )
            normal.addData3f(0, 0, 1)
            color.addData4f(1.0, 0.84, 0, 1)

            # Bottom face vertices
            vertex.addData3f(0, 0, -thickness / 2)
            normal.addData3f(0, 0, -1)
            color.addData4f(1.0, 0.84, 0, 1)

            vertex.addData3f(
                radius * math.cos(next_angle),
                radius * math.sin(next_angle),
                -thickness / 2,
            )
            normal.addData3f(0, 0, -1)
            color.addData4f(1.0, 0.84, 0, 1)

            vertex.addData3f(
                radius * math.cos(angle), radius * math.sin(angle), -thickness / 2
            )
            normal.addData3f(0, 0, -1)
            color.addData4f(1.0, 0.84, 0, 1)

            # Side vertices
            vertex.addData3f(
                radius * math.cos(angle), radius * math.sin(angle), thickness / 2
            )
            normal.addData3f(math.cos(angle), math.sin(angle), 0)
            color.addData4f(1.0, 0.84, 0, 1)

            vertex.addData3f(
                radius * math.cos(next_angle),
                radius * math.sin(next_angle),
                thickness / 2,
            )
            normal.addData3f(math.cos(next_angle), math.sin(next_angle), 0)
            color.addData4f(1.0, 0.84, 0, 1)

            vertex.addData3f(
                radius * math.cos(angle), radius * math.sin(angle), -thickness / 2
            )
            normal.addData3f(math.cos(angle), math.sin(angle), 0)
            color.addData4f(1.0, 0.84, 0, 1)

            vertex.addData3f(
                radius * math.cos(next_angle),
                radius * math.sin(next_angle),
                thickness / 2,
            )
            normal.addData3f(math.cos(next_angle), math.sin(next_angle), 0)
            color.addData4f(1.0, 0.84, 0, 1)

            vertex.addData3f(
                radius * math.cos(next_angle),
                radius * math.sin(next_angle),
                -thickness / 2,
            )
            normal.addData3f(math.cos(next_angle), math.sin(next_angle), 0)
            color.addData4f(1.0, 0.84, 0, 1)

            vertex.addData3f(
                radius * math.cos(angle), radius * math.sin(angle), -thickness / 2
            )
            normal.addData3f(math.cos(angle), math.sin(angle), 0)
            color.addData4f(1.0, 0.84, 0, 1)

        # Create triangles
        prim = GeomTriangles(Geom.UHStatic)
        for i in range(segments * 4):  # 4 triangles per segment
            prim.addVertices(i * 3, i * 3 + 1, i * 3 + 2)

        # Create the geometry
        geom = Geom(vdata)
        geom.addPrimitive(prim)

        # Create a node to hold the geometry
        node = GeomNode("coin")
        node.addGeom(geom)

        return NodePath(node)

    def spawnCoinOnTerrain(self):
        """Create a collectible coin on the terrain"""
        # Create 3D coin model
        coin = self.createCoinModel()
        coin.reparentTo(self.game.render)

        # Place it randomly on the terrain
        x = random.uniform(-35, 35)
        y = random.uniform(-35, 35)
        z = 0.5  # Slightly above ground

        coin.setPos(x, y, z)
        # Rotate the coin to stand upright (90 degrees around X axis)
        coin.setHpr(0, 90, 0)

        # Add a spinning animation (now spinning around the vertical axis)
        coin_spin = coin.hprInterval(2, Point3(360, 90, 0))
        coin_spin.loop()

        # Add a slight up-down bounce
        coin_bounce = Sequence(
            coin.posInterval(1, Point3(x, y, z + 0.2), blendType="easeInOut"),
            coin.posInterval(1, Point3(x, y, z), blendType="easeInOut"),
        )
        coin_bounce.loop()

        # Store the coin and its animations
        self.terrainCoins.append(
            {
                "model": coin,
                "spin": coin_spin,
                "bounce": coin_bounce,
                "pos": Point3(x, y, z),
            }
        )

    def spawnFlyingCoin(self, position):
        """Create a coin that flies toward the player"""
        # Create a flying coin that moves toward the player
        coin = self.createCoinModel()
        coin.reparentTo(self.game.render)
        coin.setPos(position)
        # Rotate the flying coin to stand upright
        coin.setHpr(0, 90, 0)

        # Create animation for the coin to fly toward the player
        coin_pos = coin.getPos()
        player_pos = self.game.player.root.getPos()

        # Create a sequence to make the coin fly to the player and then disappear
        coin_sequence = Sequence(
            coin.posInterval(1.0, player_pos, startPos=coin_pos, blendType="easeIn"),
            Func(self.collectFlyingCoin, coin),
        )
        coin_sequence.start()

    def collectFlyingCoin(self, coin):
        """Handle collection of a flying coin"""
        # Create particle effect at player position
        self.createCoinCollectionEffect(self.game.player.root.getPos())

        # Add coins to player
        self.game.coins += 3
        self.game.hud.updateCoins(self.game.coins)

        # Remove the coin
        coin.removeNode()

    def checkCollisions(self, player_pos):
        """Check if player has collected any terrain coins"""
        for coin in self.terrainCoins[:]:
            coin_pos = coin["model"].getPos()
            if (coin_pos - player_pos).length() < self.coin_radius:
                self.collectTerrainCoin(coin)

    def collectTerrainCoin(self, coin):
        """Handle player collecting a terrain coin"""
        # Create collection effect
        self.createCoinCollectionEffect(coin["pos"])

        # Stop animations and remove the coin
        coin["spin"].finish()
        coin["bounce"].finish()
        coin["model"].removeNode()
        self.terrainCoins.remove(coin)

        # Add to player's coins
        self.game.coins += 5
        self.game.hud.updateCoins(self.game.coins)

        # Spawn a new coin elsewhere
        self.spawnCoinOnTerrain()

    def createCoinCollectionEffect(self, position):
        """Create effect for coin collection"""
        # Create a simple effect using small yellow cubes that explode outward
        for i in range(8):
            particle = self.game.createBox(
                0.1, 0.1, 0.1, (1.0, 0.84, 0, 1)
            )  # Gold color
            particle.reparentTo(self.game.render)
            particle.setPos(position)

            # Random direction
            angle = random.uniform(0, 2 * math.pi)
            height = random.uniform(0.5, 1.5)
            end_pos = Point3(
                position.x + math.cos(angle) * 1.5,
                position.y + math.sin(angle) * 1.5,
                position.z + height,
            )

            # Create animation sequence
            particle_seq = Sequence(
                particle.posInterval(0.5, end_pos, blendType="easeOut"),
                particle.scaleInterval(0.3, 0.01),  # Shrink to nothing
                Func(particle.removeNode),
            )
            particle_seq.start()
