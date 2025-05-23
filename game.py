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

from core.effects import Effects
from core.input import InputController
from entities.balloon import BalloonManager
from entities.coin import CoinManager
from entities.heart import HeartManager
from entities.katana import KatanaManager
from entities.player import Player
from entities.projectile import ProjectileManager
from ui.hud import HUD
from ui.menu import MenuManager
from ui.minimap import Minimap


class MonkeyDartGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.disableMouse()

        self.gameState = "menu"  # "menu", "playing", "gameover"

        self.score = 0
        self.coins = 0
        self.weaponType = "dart"
        self.owned_weapons = ["dart"]
        self.current_weapon_index = 0

        self.obstacles = []
        self.setupScene()
        self.player = Player(self)
        self.projectileManager = ProjectileManager(self)
        self.screenEffects = Effects(self)
        self.menuManager = MenuManager(self)
        self.hud = HUD(self)
        self.minimap = Minimap(self)
        self.inputController = InputController(self, self.player)
        self.playerInvulnerable = False

        self.player.initializeCamera()

        self.taskMgr.add(self.updateGame, "UpdateGameTask")

        props = WindowProperties()
        props.setCursorHidden(False)
        self.win.requestProperties(props)

        self.balloonManager = BalloonManager(self)
        self.coinManager = CoinManager(self)
        self.heartManager = HeartManager(self)
        self.katanaManager = KatanaManager(self)

    def pauseGame(self):
        self.gameState = "paused" if self.gameState == "playing" else "playing"
        if self.gameState == "paused":
            self.menuManager.showPauseMenu()
            self.inputController.hideMouseCursor(False)
        else:
            self.menuManager.hidePauseMenu()
            self.inputController.hideMouseCursor(True)

    def setupScene(self):
        cm = CardMaker("ground")
        cm.setFrame(-80, 80, -80, 80)
        cm.setUvRange((0, 0), (16, 16))
        ground = self.render.attachNewNode(cm.generate())
        ground.setP(-90)
        ground.setZ(-0.5)

        ground_texture = self.loader.loadTexture("assets/models/ground.png")
        ground.setTexture(ground_texture)
        ground.setTexScale(TextureStage.getDefault(), 16, 16)

        self.tree_model = self.loader.loadModel("assets/models/birch_tree.egg")
        self.sunflower_model = self.loader.loadModel("assets/models/sunflower.bam")
        self.cranberry_model = self.loader.loadModel(
            "assets/models/european_cranberry_bush.egg"
        )
        self.rock_model = self.loader.loadModel("assets/models/rock.bam")
        rock_texture = self.loader.loadTexture("assets/models/rock.png")
        self.rock_model.setTexture(rock_texture)

        for _ in range(50):
            tree = self.tree_model.copyTo(self.render)
            tx = random.uniform(-75, 75)
            ty = random.uniform(-75, 75)
            tree.setPos(tx, ty, -0.2)
            tree.setH(random.uniform(0, 360))
            self.obstacles.append((tree, 1.5, 3))
            tree.setScale(random.uniform(0.8, 1.2))

            sunflower = self.sunflower_model.copyTo(self.render)
            sx = random.uniform(-75, 75)
            sy = random.uniform(-75, 75)
            sunflower.setPos(sx, sy, -0.4)
            sunflower.setH(random.uniform(0, 360))
            sunflower.setScale(random.uniform(0.2, 0.3))

            rock = self.rock_model.copyTo(self.render)
            rx = random.uniform(-75, 75)
            ry = random.uniform(-75, 75)
            rock.setPos(rx, ry, -0.4)
            rock.setH(random.uniform(0, 360))
            rock.setScale(random.uniform(0.8, 1.2))
            self.obstacles.append((rock, 2.0, 0.5))

            cranberry = self.cranberry_model.copyTo(self.render)
            cx = random.uniform(-75, 75)
            cy = random.uniform(-75, 75)
            cranberry.setPos(cx, cy, 0.0)
            cranberry.setH(random.uniform(0, 360))
            cranberry.setScale(random.uniform(2.0, 3.0))
            self.obstacles.append((cranberry, 2.0, 1.7))

        ambientLight = AmbientLight("ambient light")
        ambientLight.setColor((0.3, 0.3, 0.3, 1))
        ambientLightNP = self.render.attachNewNode(ambientLight)
        self.render.setLight(ambientLightNP)

        directionalLight = DirectionalLight("directional light")
        directionalLight.setColor((0.8, 0.8, 0.8, 1))
        directionalLightNP = self.render.attachNewNode(directionalLight)
        directionalLightNP.setHpr(45, -45, 0)
        self.render.setLight(directionalLightNP)

        self.setBackgroundColor(0.5, 0.8, 0.9, 1)

    def createBox(self, width, depth, height, color=(1, 1, 1, 1)):
        box = NodePath("box")

        half_width = width / 2
        half_depth = depth / 2
        half_height = height / 2

        cm = CardMaker("bottom")
        cm.setFrame(-half_width, half_width, -half_depth, half_depth)
        bottom = box.attachNewNode(cm.generate())
        bottom.setP(-90)
        bottom.setZ(-half_height)
        bottom.setColor(*color)

        cm = CardMaker("top")
        cm.setFrame(-half_width, half_width, -half_depth, half_depth)
        top = box.attachNewNode(cm.generate())
        top.setP(90)
        top.setZ(half_height)
        top.setColor(*color)

        cm = CardMaker("front")
        cm.setFrame(-half_width, half_width, -half_height, half_height)
        front = box.attachNewNode(cm.generate())
        front.setY(half_depth)
        front.setColor(*color)

        cm = CardMaker("back")
        cm.setFrame(-half_width, half_width, -half_height, half_height)
        back = box.attachNewNode(cm.generate())
        back.setY(-half_depth)
        back.setH(180)
        back.setColor(*color)

        cm = CardMaker("left")
        cm.setFrame(-half_depth, half_depth, -half_height, half_height)
        left = box.attachNewNode(cm.generate())
        left.setX(-half_width)
        left.setH(90)
        left.setColor(*color)

        cm = CardMaker("right")
        cm.setFrame(-half_depth, half_depth, -half_height, half_height)
        right = box.attachNewNode(cm.generate())
        right.setX(half_width)
        right.setH(-90)
        right.setColor(*color)

        return box

    def updateGame(self, task):
        if self.gameState != "playing":
            return Task.cont
        self.screenEffects.balloonAlert()
        dt = task.time - task.lastTime if hasattr(task, "lastTime") else 0
        task.lastTime = task.time

        self.balloonManager.update(dt)
        self.projectileManager.update(dt)
        self.coinManager.checkCollisions(self.player.root.getPos())
        self.heartManager.checkCollisions(self.player.root.getPos())
        self.katanaManager.checkCollisions(self.player.root.getPos())
        return Task.cont

    def startGame(self):
        self.gameState = "playing"
        self.menuManager.hideMainMenu()
        self.hud.show()
        self.minimap.show()

        self.score = 0
        self.weaponType = "dart"
        self.current_weapon_index = 0

        self.player.reset()
        self.balloonManager.reset()
        self.projectileManager.reset()

        self.hud.updateScore(self.score)
        self.hud.updateCoins(self.coins)
        self.hud.updateWeapon(self.weaponType)
        self.hud.refreshHearts()

    def gameOver(self):
        self.gameState = "gameover"
        self.hud.hide()
        self.minimap.hide()
        self.inputController.hideMouseCursor(False)  # Show cursor

        self.menuManager.showGameOver(self.score)

    def restartGame(self):
        self.menuManager.hideGameOver()
        self.startGame()

    def returnToMenu(self):
        self.menuManager.hideGameOver()
        self.gameState = "menu"
        self.menuManager.showMainMenu()
        self.menuManager.hidePauseMenu()
        self.inputController.hideMouseCursor(False)

    def upgradeWeapon(self):
        if self.weaponType == "dart" and self.coins >= 50:
            self.coins -= 50
            self.weaponType = "katana"
            self.owned_weapons.append("katana")
            self.player.hasKatana = True
            self.player.switchWeapon(self.weaponType)

            self.hud.updateCoins(self.coins)
            self.hud.updateWeapon(self.weaponType)
            self.hud.disableUpgradeButton()

            self.projectileManager.createUpgradeEffect(
                self.player.weapon_holder.getPos(self.render)
            )

    def switchWeapon(self):
        if len(self.owned_weapons) > 1:
            self.current_weapon_index = (self.current_weapon_index + 1) % len(
                self.owned_weapons
            )
            self.weaponType = self.owned_weapons[self.current_weapon_index]
            self.player.switchWeapon(self.weaponType)
            self.hud.updateWeapon(self.weaponType)
