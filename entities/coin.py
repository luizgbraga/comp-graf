import math
import random

from direct.interval.IntervalGlobal import Func, Sequence
from panda3d.core import CardMaker, Point3


class CoinManager:
    def __init__(self, game):
        self.game = game
        self.terrainCoins = []

        # Initialize terrain coins
        for _ in range(20):
            self.spawnCoinOnTerrain()

    def spawnCoinOnTerrain(self):
        """Create a collectible coin on the terrain"""
        # Create visible coin using a simple disc
        cm = CardMaker("coin")
        cm.setFrame(-0.3, 0.3, -0.3, 0.3)
        coin = self.game.render.attachNewNode(cm.generate())
        coin.setBillboardPointEye()  # Make it always face the camera
        coin.setColor(1.0, 0.84, 0, 1)  # Gold color

        # Place it randomly on the terrain
        x = random.uniform(-35, 35)
        y = random.uniform(-35, 35)
        z = 0.5  # Slightly above ground

        coin.setPos(x, y, z)

        # Add a spinning animation
        coin_spin = coin.hprInterval(2, Point3(360, 0, 0))
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
        cm = CardMaker("flying_coin")
        cm.setFrame(-0.3, 0.3, -0.3, 0.3)
        coin = self.game.render.attachNewNode(cm.generate())
        coin.setBillboardPointEye()  # Make it always face the camera
        coin.setColor(1.0, 0.84, 0, 1)  # Gold color
        coin.setPos(position)

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
            if (coin_pos - player_pos).length() < 1.5:
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
