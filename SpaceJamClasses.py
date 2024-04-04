from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.task.Task import TaskManager
from typing import Callable 
from CollideObjectBase import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.interval.LerpInterval import LerpFunc
from direct.particles.ParticleEffect import ParticleEffect 
import re 
import DefensePaths as defensePaths # new


class Planet(SphereCollideObject):
    def __init__(self, loader: Loader, render: NodePath, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(Planet, self).__init__(loader, modelPath, parentNode, nodeName, Vec3 (0,0,0), 1.2)
        
        # Load the model
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)
        
        # Set texture
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
        
        self.loader = loader
        self.render = render
# new 
class Orbiter(SphereCollideObject):
    numOrbits = 0
    velocity =0.005
    cloudTimer = 240
    
    def __init__(self, loader: Loader, taskMgr: TaskManager, modelPath: str, parentNode: NodePath, nodeName: str, scaleVec: Vec3, texPath: str, centralObject: PlacedObject, OrbitRadius: float, orbitType: str, staringAt: Vec3):
        super(Orbiter, self).__init__(loader, modelPath, parentNode, nodeName, Vec3 (0,0,0), 3.2)

        self.taskMgr = taskMgr
        self.orbitType = orbitType
        self.modelNode.setScale(scaleVec)
        tex = loader.loadTexture(texPath)
        self.OrbitObject = centralObject
        self.OrbitRadius = OrbitRadius
        self.staringAt = staringAt
        Orbiter.numOrbits += 1
        self.cloudClock = 0

        self.taskFlag = "Traveler-" + str(Orbiter.numOrbits)
        taskMgr.add(self.Orbit,self.taskFlag)

    def Orbit(self, task):
        if self.orbitType == "MLB":
            positionVec = defensePaths.BaseballSeams(task.time * Orbiter.velocity, self.numOrbits, 2.0)
            self.modelNode.setPos(positionVec + self.OrbitObject.modelNode.getPos())

        elif self.orbitType == "Cloud":
            if self.cloudClock < Orbiter.cloudTimer:
                self.cloudeClock += 1

            else:
                self.cloudTimer = 0
                positionVec = defensePaths.cloud()
                self.model.Node.setPos(positionVec * self.OrbitRadius + self.OrbitObject.modelNode.grtPos())
 
        self.modelNode.lookAt(self.staringAt.modelNode)
        return task.cont
#  
class Universe(InverseSphereCollideObject):
    def __init__(self, loader: Loader, render: NodePath, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(Universe, self).__init__(loader, modelPath, parentNode, nodeName,Vec3 (0, 0, 0), 1.2)
        
        # Load the model
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        # Set texture
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)

        # Set modelNode as the universe
        
        self.loader = loader
        self.render = render

class Spaceship(SphereCollideObject):# / player
    def __init__(self, loader: Loader, render: NodePath, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float, taskManager: TaskManager, accept: Callable[[str, Callable], None], traverser):
        super(Spaceship,self).__init__(loader, modelPath, parentNode, nodeName, Vec3 (0, 0, 0), 1)
        
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        self.taskManager = taskManager
        self.loader = loader
        self.render = render
        self.accept = accept

        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
        #self.modelNode.setP(100)

        self.missileBay = 10
        self.missileDistance = 100

        self.setKeyBindings()

        self.cutExplode = 0
        self.ExplodeIntervals ={}
        self.traverser = traverser
        self.handler = CollisionHandlerEvent()
        self.handler.addInPattern('into')
        self.accept('into', self.HandleInto)

        self.setKeyBindings()
        
    def Thrust(self, keyDown):
        if keyDown:
            self.taskManager.add(self.ApplyThrust, 'Forward-thrust')
        else: 
            self.taskManager.remove('Forward-thrust')

    def ApplyThrust(self, task):
        rate = 5
        trajectory = self.render.getRelativeVector(self.modelNode, Vec3.forward())
        trajectory.normalize()
        self.modelNode.setFluidPos(self.modelNode.getPos() + trajectory * rate)
        return Task.cont
        
    def LeftTurn(self, keyDown):
        if keyDown:
            self.taskManager.add(self.ApplyLeftTurn, 'LeftTurn')
        else: 
            self.taskManager.remove('LeftTurn')

    def ApplyLeftTurn(self, task):
        # Half a degree every frame
        rate = 0.5
        self.modelNode.setH(self.modelNode.getH() + rate)
        return Task.cont
        
    def RightTurn(self, keyDown):
        if keyDown:
            self.taskManager.add(self.ApplyRightTurn, 'RightTurn')
        else:
            self.taskManager.remove('RightTurn')

    def ApplyRightTurn(self, task):
        # Half a degree every frame
        rate = 0.5  
        self.modelNode.setH(self.modelNode.getH() - rate)  
        return Task.cont
        
    def PitchForwd(self, keyDown):
        if keyDown:
            self.taskManager.add(self.ApplyPitchForwd, 'PitchForwd')
        else: 
            self.taskManager.remove('PitchForwd')

    def ApplyPitchForwd(self, task):
        # Half a degree every frame
        rate = 0.5  
        self.modelNode.setP(self.modelNode.getP() + rate)  
        return Task.cont
        
    def PitchBack(self, keyDown):
        if keyDown:
            self.taskManager.add(self.ApplyPitchBack, 'PitchBack')
        else: 
            self.taskManager.remove('PitchBack')

    def ApplyPitchBack(self, task):
        # Half a degree every frame
        rate = 0.5  
        self.modelNode.setP(self.modelNode.getP() - rate) 
        return Task.cont
        
    def RollLeft(self, keyDown):
        if keyDown:
            self.taskManager.add(self.ApplyRollLeft, 'RollLeft')
        else: 
            self.taskManager.remove('RollLeft')

    def ApplyRollLeft(self, task):
        # Half a degree every frame
        rate = 0.5  
        self.modelNode.setR(self.modelNode.getR() - rate)  
        return Task.cont

    def RollRight(self, keyDown):
        if keyDown:
            self.taskManager.add(self.ApplyRollRight, 'RollRight')
        else:
            self.taskManager.remove('RollRight')

    def ApplyRollRight(self, task):
        # Half a degree every frame
        rate = 0.5  
        self.modelNode.setR(self.modelNode.getR() + rate) 
        return Task.cont

    def Fire(self):
        if self.missileBay > 0:
            travRate = self.missileDistance
            aim = self.render.getRelativePoint(self.modelNode, Vec3.forward())
            aim.normalize()
            fireSolution = aim * travRate
            inFront = aim * 150
            travVec = fireSolution + self.modelNode.getPos()
            self.missileBay -= 1
            tag = 'Missile' + str(Missile.missileCount)
            posVec = self.modelNode.getPos() + inFront
            currentMissile = Missile(self.loader, './Assets/Phaser/phaser.egg', self.render, tag, posVec, 4.0)
            Missile.Intervals[tag] = currentMissile.modelNode.posInterval(2.0, travVec, startPos=posVec, fluid=1) 
            Missile.Intervals[tag].start()

            self.traverser.addCollider(currentMissile.collisionNode,self.handler)

        else:
            if not self.taskManager.hasTaskNamed('reload'):
                print('Initializing reload...')
                self.taskManager.doMethodLater(0,self.Reload, 'reload')
                return Task.cont
                   
    def Reload(self, task):
        if task.time > self.reloadTime:
            self.missileBay += 1
        
            if self.missileBay > 1:
                self.missileBay = 1

            print("Reload complete")
            return Task.done
        
        elif task.time <= self.reloadTime:
            print("Reload proceeding...")
            return Task.cont
           
    def setKeyBindings(self):  
        # All key Bindings for Spaceship move
        self.accept('space', self.Thrust, [1])
        self.accept('space-up', self.Thrust, [0])

        # Keys for left and right
        self.accept('arrow_left', self.LeftTurn, [1])
        self.accept('arrow_left-up', self.LeftTurn, [0])
        self.accept('arrow_right', self.RightTurn, [1])
        self.accept('arrow_right-up', self.RightTurn, [0])

        # Keys for up and down
        self.accept('arrow_up', self.PitchForwd, [1])
        self.accept('arrow_up-up', self.PitchForwd, [0])
        self.accept('arrow_down', self.PitchBack, [1])
        self.accept('arrow_down-up', self.PitchBack, [0])

        # Keys for rotating left and right
        self.accept('a', self.RollLeft, [1])
        self.accept('a-up', self.RollLeft, [0])
        self.accept('d', self.RollRight, [1])
        self.accept('d-up', self.RollRight, [0])

        #f to fire 
        self.accept('f', self.Fire)

    def checkIntervals(self, task):
        for i in Missile.Intervals:
            if not Missile.Intervals[i].isPlaying():
                Missile.cNodes[i].detachNode()
                Missile.fireModels[i].detachNode()
            del Missile.Intervals[i]
            del Missile.fireModels[i]
            del Missile.cNodes[i]
            del Missile.collisionSolids[i]

            print(i + 'has reached the end of it fire solution.')
            break
            return Task.cont
        
    def EnableHud(self):
        print("EnableHud method called")  # Add this line
        self.Hud = OnscreenImage(image="./Assets/Hud/Reticle3b.png", pos=Vec3(0, 0, 0), scale=0.1)
        self.Hud.setTransparency(TransparencyAttrib.MAlpha)
        self.EnableHud()

    def HandleInto(self, entry):
        fromNode = entry.getFromNodePath().getName()
        print("fromNode:" + fromNode)
        intoNode = entry.getIntoNodePath().getName()
        print("intoNode:" + intoNode)
        
        intoPosition = Vec3(entry.getSurfacePoint(self.render))
        
        tempVar = fromNode.split('_')
        shooter = tempVar [0]
        tempVar = intoNode.split('_')
        tempVar = intoNode.split('_')
        victim = tempVar [0]

        pattern = r'[0-9]'
        strippedString = re.sub(pattern, '', victim) 

        if (strippedString == "Drone"):
            print(shooter + ' is Done.')
            Missile.Intervals[shooter].finish()
            print(victim, ' hit at ', intoPosition)
        
        else:
            Missile.Intervals[shooter.finish]
              
class SpaceStation(CollisionCapsuleObject):
    def __init__(self, loader: Loader, render: NodePath, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float, radius: float):
        super(SpaceStation, self).__init__(loader, modelPath, parentNode, nodeName,1, -1, 5, 1, -1, -5, 0)

        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)
        self.loader = loader
        self.render = render
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
        
        #self.station = loader.loadModel("./Assets/SpaceStation1B/spaceStation.x")

class Missile(SphereCollideObject):

    fireModels ={}
    cNodes = {}
    collisionSolids = {}
    Intervals = {}
    missileCount = 0

    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, posVec: Vec3, scaleVec: float = 1):
        super(Missile, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 3.0)
  
        self.modelNode.setScale(scaleVec)
        self.modelNode.setPos(posVec)
        self.modelNode.setName(nodeName)

        Missile.missileCount += 1

        Missile.fireModels[nodeName] = self.modelNode
        Missile.cNodes[nodeName]=self.collisionNode
        Missile.collisionSolids[nodeName] = self.collisionNode.node().getSolid(0)
        Missile.cNodes[nodeName].show()

        print("Fire torpedo #" + str(Missile.missileCount))

class DroneShowBase(SphereCollideObject):
    def __init__(self, loader: Loader, render: NodePath, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(DroneShowBase, self).__init__(loader, modelPath, parentNode, nodeName, posVec, scaleVec)  

        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)
        
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
        
        self.loader = loader
        self.render = render

    def DroneDestroy(self, hitId, hitPosition):
        nodeId = self.render.find(hitId)
        nodeId.detachNode()

        self.explodeNode.setPos(hitPosition)
        self.Explode(hitPosition)

    def Explode(self, impactPoint):
        self.cntExplode += 1
        tag ='particles' + str(self.cntExplode)

        self.explodeIntervals[tag] = LerpFunc(self.ExplodeLight, fromData = 0, toData =1, duration = 4.0, extraArgs = [impactPoint])
        self.explodeIntervals[tag].start()

    def ExplodeLight(self, t, explosionPosition):
        if t == 1.0 and self.explodeEffect:
            self.explodeEffect.disable.disable()
        
        elif t == 0:
            self.explodeEffect.seart(self.explodeNode)

    def SetParticles(self):
        base.enableParticles()
        self.explodeEffect = ParticleEffect()
        self.explodeEffect.loadConfig("./Assets/ParticleEffect/Explosions/     need to choues one         ")
        self.explodeEffect.setScale(20)
        self.explodeNode = self.render.AttachNewNode('ExplodeEffect')
#
    # # of Drone
    droneCount = 0