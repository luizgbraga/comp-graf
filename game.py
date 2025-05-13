import random

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import (
    AmbientLight,
    CardMaker,
    DirectionalLight,
    NodePath,
    TextureStage,
    WindowProperties,
)

from core.input import InputController
from entities.balloon import BalloonManager
from entities.coin import CoinManager
from entities.player import Player
from entities.projectile import ProjectileManager
from ui.hud import HUD
from ui.menu import MenuManager
from ui.minimap import Minimap


class MonkeyDartGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Disable the default camera control
        self.disableMouse()

        # Game states
        self.gameState = "menu"  # "menu", "playing", "gameover"

        # Game variables
        self.score = 0
        self.coins = 0
        self.weaponType = "dart"
        self.owned_weapons = ["dart"]  # Start with dart gun
        self.current_weapon_index = 0

        # Create all components in a specific order to avoid dependency issues
        self.obstacles = []
        self.setupScene()
        self.player = Player(self)
        self.balloonManager = BalloonManager(self)
        self.projectileManager = ProjectileManager(self)
        self.coinManager = CoinManager(self)
        self.menuManager = MenuManager(self)
        self.hud = HUD(self)
        self.minimap = Minimap(self)
        self.inputController = InputController(self, self.player)

        # Initialize player's camera after HUD is created
        self.player.initializeCamera()

        # Add tasks
        self.taskMgr.add(self.updateGame, "UpdateGameTask")

        # Make sure cursor is visible for menu
        props = WindowProperties()
        props.setCursorHidden(False)
        self.win.requestProperties(props)

    def setupScene(self):
        # Create a simple ground plane
        cm = CardMaker("ground")
        cm.setFrame(-80, 80, -80, 80)  # Doubled the size from -40,40 to -80,80
        cm.setUvRange(
            (0, 0), (16, 16)
        )  # Doubled the UV mapping to maintain texture density
        ground = self.render.attachNewNode(cm.generate())
        ground.setP(-90)  # Rotate it to be flat
        ground.setZ(-0.5)

        # Load and apply ground texture
        ground_texture = self.loader.loadTexture("assets/models/ground.png")
        ground.setTexture(ground_texture)
        ground.setTexScale(
            TextureStage.getDefault(), 16, 16
        )  # Doubled the texture tiling to match new size

        # Load the tree model
        self.tree_model = self.loader.loadModel("assets/models/birch_tree.egg")
        # Load the tree textures
        leaf_texture = self.loader.loadTexture("assets/models/tex/tree_birch_leaf.png")
        bark_texture = self.loader.loadTexture("assets/models/tex/tree_bark_65102.jpg")
        self.tree_model.setTexture(leaf_texture)
        # Apply bark texture to the trunk if the model supports multiple textures
        if self.tree_model.find("**/trunk").is_empty():
            self.tree_model.setTexture(
                bark_texture, 1
            )  # Apply to second texture stage if available

        # Load the sunflower model
        self.sunflower_model = self.loader.loadModel("assets/models/sunflower.bam")

        # Load the rock model
        self.rock_model = self.loader.loadModel("assets/models/rock.bam")
        # Load and apply rock texture
        rock_texture = self.loader.loadTexture("assets/models/rock.png")
        self.rock_model.setTexture(rock_texture)

        # Create trees, sunflowers, and rocks
        for _ in range(50):  # Doubled the number of objects to maintain density
            # Trees
            tree = self.tree_model.copyTo(self.render)
            tx = random.uniform(-75, 75)  # Adjusted range to match new ground size
            ty = random.uniform(-75, 75)
            tree.setPos(tx, ty, -0.2)  # Moved down slightly
            # Random rotation for variety
            tree.setH(random.uniform(0, 360))
            # Scale the tree to be larger with random size between 2 and 4
            tree.setScale(random.uniform(2.0, 4.0))
            self.obstacles.append((tree, 1.5, 5.0))

            # Sunflowers
            sunflower = self.sunflower_model.copyTo(self.render)
            sx = random.uniform(-75, 75)  # Adjusted range to match new ground size
            sy = random.uniform(-75, 75)
            sunflower.setPos(sx, sy, -0.4)
            sunflower.setH(random.uniform(0, 360))
            sunflower.setScale(random.uniform(0.2, 0.3))  # Made flowers smaller

            # Rocks
            rock = self.rock_model.copyTo(self.render)
            rx = random.uniform(-75, 75)  # Adjusted range to match new ground size
            ry = random.uniform(-75, 75)
            rock.setPos(rx, ry, -0.4)
            rock.setH(random.uniform(0, 360))
            rock.setScale(random.uniform(0.8, 1.2))  # Random size variation
            self.obstacles.append((rock, 2.0, 1.7))

        # Set up lighting
        ambientLight = AmbientLight("ambient light")
        ambientLight.setColor((0.3, 0.3, 0.3, 1))
        ambientLightNP = self.render.attachNewNode(ambientLight)
        self.render.setLight(ambientLightNP)

        directionalLight = DirectionalLight("directional light")
        directionalLight.setColor((0.8, 0.8, 0.8, 1))
        directionalLightNP = self.render.attachNewNode(directionalLight)
        directionalLightNP.setHpr(45, -45, 0)
        self.render.setLight(directionalLightNP)

        # Set a sky blue background color
        self.setBackgroundColor(0.5, 0.8, 0.9, 1)

    def createBox(self, width, depth, height, color=(1, 1, 1, 1)):
        """Create a box with the given dimensions and color"""
        box = NodePath("box")

        # Create the box's body using 6 cards
        half_width = width / 2
        half_depth = depth / 2
        half_height = height / 2

        # Bottom
        cm = CardMaker("bottom")
        cm.setFrame(-half_width, half_width, -half_depth, half_depth)
        bottom = box.attachNewNode(cm.generate())
        bottom.setP(-90)
        bottom.setZ(-half_height)
        bottom.setColor(*color)

        # Top
        cm = CardMaker("top")
        cm.setFrame(-half_width, half_width, -half_depth, half_depth)
        top = box.attachNewNode(cm.generate())
        top.setP(90)
        top.setZ(half_height)
        top.setColor(*color)

        # Front
        cm = CardMaker("front")
        cm.setFrame(-half_width, half_width, -half_height, half_height)
        front = box.attachNewNode(cm.generate())
        front.setY(half_depth)
        front.setColor(*color)

        # Back
        cm = CardMaker("back")
        cm.setFrame(-half_width, half_width, -half_height, half_height)
        back = box.attachNewNode(cm.generate())
        back.setY(-half_depth)
        back.setH(180)
        back.setColor(*color)

        # Left
        cm = CardMaker("left")
        cm.setFrame(-half_depth, half_depth, -half_height, half_height)
        left = box.attachNewNode(cm.generate())
        left.setX(-half_width)
        left.setH(90)
        left.setColor(*color)

        # Right
        cm = CardMaker("right")
        cm.setFrame(-half_depth, half_depth, -half_height, half_height)
        right = box.attachNewNode(cm.generate())
        right.setX(half_width)
        right.setH(-90)
        right.setColor(*color)

        return box

    def updateGame(self, task):
        """Main game update loop"""
        if self.gameState != "playing":
            return Task.cont

        # Get the time since the last frame
        dt = task.time - task.lastTime if hasattr(task, "lastTime") else 0
        task.lastTime = task.time

        # Let each system update itself
        self.balloonManager.update(dt)
        self.projectileManager.update(dt)
        self.coinManager.checkCollisions(self.player.root.getPos())
        return Task.cont

    def startGame(self):
        """Start or restart the game"""
        self.gameState = "playing"
        self.menuManager.hideMainMenu()
        self.hud.show()
        self.minimap.show()

        # Reset game variables
        self.score = 0
        # self.coins = 0  # Removed to maintain coins across plays
        self.weaponType = "dart"
        self.current_weapon_index = 0

        # Reset managers
        self.player.reset()
        self.balloonManager.reset()
        self.projectileManager.reset()

        # Update HUD
        self.hud.updateScore(self.score)
        self.hud.updateCoins(self.coins)
        self.hud.updateWeapon(self.weaponType)

    def gameOver(self):
        """Handle game over state"""
        self.gameState = "gameover"
        self.hud.hide()
        self.minimap.hide()
        self.inputController.hideMouseCursor(False)  # Show cursor

        # Show game over screen
        self.menuManager.showGameOver(self.score)

    def restartGame(self):
        """Restart the game from game over screen"""
        self.menuManager.hideGameOver()
        self.startGame()

    def returnToMenu(self):
        """Return to the main menu"""
        self.menuManager.hideGameOver()
        self.gameState = "menu"
        self.menuManager.showMainMenu()
        self.inputController.hideMouseCursor(False)  # Show cursor

    def upgradeWeapon(self):
        """Upgrade weapon from dart to katana"""
        if self.weaponType == "dart" and self.coins >= 50:
            self.coins -= 50
            self.weaponType = "katana"
            self.owned_weapons.append("katana")  # Add katana to owned weapons

            # Update player weapon
            self.player.switchWeapon(self.weaponType)

            # Update HUD
            self.hud.updateCoins(self.coins)
            self.hud.updateWeapon(self.weaponType)
            self.hud.disableUpgradeButton()

            # Create upgrade effect
            self.projectileManager.createUpgradeEffect(
                self.player.weapon_holder.getPos(self.render)
            )

    def switchWeapon(self):
        """Switch to the next owned weapon"""
        if len(self.owned_weapons) > 1:
            self.current_weapon_index = (self.current_weapon_index + 1) % len(
                self.owned_weapons
            )
            self.weaponType = self.owned_weapons[self.current_weapon_index]
            self.player.switchWeapon(self.weaponType)
            self.hud.updateWeapon(self.weaponType)
