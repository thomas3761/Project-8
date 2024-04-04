from panda3d.core import PandaNode, Loader , NodePath, CollisionNode, CollisionSphere, CollisionInvSphere, CollisionCapsule, Vec3

class PlacedObject(PandaNode):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str):
        self.modelNode = loader.loadModel(modelPath)
        
        if not isinstance(self.modelNode, NodePath):
            raise AssertionError(f"PlacedObject loader.loadModel({modelPath}) did not return a proper PandaNode!")
        
        self.modelNode.reparentTo(parentNode)
        self.modelNode.setName(nodeName)

class CollidableObject(PlacedObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str):
        super(CollidableObject, self).__init__(loader, modelPath, parentNode, nodeName)

        self.collisionNode = self.modelNode.attachNewNode(CollisionNode(nodeName + '_cNode'))

class InverseSphereCollideObject(CollidableObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, colPositionVec: Vec3, colRadius: float):
        super(InverseSphereCollideObject, self).__init__(loader, modelPath, parentNode, nodeName)

        self.collisionNode.node().addSolid(CollisionInvSphere(colPositionVec, colRadius))
        self.collisionNode.show()

class CollisionCapsuleObject(CollidableObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, ax: float, ay: float, az: float, bx: float, by: float, bz: float, r: float):
        super(CollisionCapsuleObject, self).__init__(loader, modelPath, parentNode, nodeName)

        self.collisionNode.node().addSolid(CollisionCapsule(Vec3(ax, ay, az), Vec3(bx, by, bz), r))
        self.collisionNode.show()

class SphereCollideObject(CollidableObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, center: Vec3, radius: float):
        super(SphereCollideObject,self).__init__(loader, modelPath, parentNode, nodeName)

        self.collisionNode.node().addSolid(CollisionSphere(center, radius))
        self.collisionNode.show()
        #self.modelPath.setCollideMask(1)
        