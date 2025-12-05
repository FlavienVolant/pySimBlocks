import os
import numpy as np

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mesh')

import Sofa

class FingerController(Sofa.Core.Controller):

    def __init__(self, actuator, mo, tip_index=121, name="FingerController"):
        super().__init__(name=name)

        self.mo = mo
        self.actuator = actuator
        self.tip_index = tip_index

        # Inputs & outputs dictionaries
        self.inputs = { "cable": None }
        self.outputs = { "tip": None }


    def onAnimateBeginEvent(self, event):

        # 1. READ INPUT -------------------------------------
        val = self.inputs["cable"]

        # Safe default for first initialization call
        if val is None:
            # ↓↓↓ Valeur par défaut pour l’initialisation
            val = 0.0

        # Convert input to Sofa format
        if isinstance(val, np.ndarray):
            processed = val.flatten().tolist()
        elif isinstance(val, (list, tuple)):
            processed = val
        else:
            processed = [float(val)]

        # Apply to actuator
        self.actuator.value = processed

        # 2. COMPUTE OUTPUT ---------------------------------
        tip = self.mo.position[self.tip_index].copy()
        self.outputs["tip"] = np.asarray(tip).reshape(-1, 1)


def createScene(rootNode):
    rootNode.addObject("RequiredPlugin", name='SoftRobots')
    rootNode.addObject("RequiredPlugin", name='SofaPython3')
    rootNode.addObject('RequiredPlugin', pluginName=[
                            "Sofa.Component.AnimationLoop",  # Needed to use components FreeMotionAnimationLoop
                            "Sofa.Component.Constraint.Lagrangian.Correction",  # Needed to use components GenericConstraintCorrection
                            "Sofa.Component.Constraint.Lagrangian.Solver",  # Needed to use components GenericConstraintSolver
                            "Sofa.Component.Engine.Select",  # Needed to use components BoxROI
                            "Sofa.Component.IO.Mesh",  # Needed to use components MeshSTLLoader, MeshVTKLoader
                            "Sofa.Component.LinearSolver.Direct",  # Needed to use components SparseLDLSolver
                            "Sofa.Component.Mass",  # Needed to use components UniformMass
                            "Sofa.Component.ODESolver.Backward",  # Needed to use components EulerImplicitSolver
                            "Sofa.Component.Setting",  # Needed to use components BackgroundSetting
                            "Sofa.Component.SolidMechanics.FEM.Elastic",  # Needed to use components TetrahedronFEMForceField
                            "Sofa.Component.SolidMechanics.Spring",  # Needed to use components RestShapeSpringsForceField
                            "Sofa.Component.Topology.Container.Constant",  # Needed to use components MeshTopology
                            "Sofa.Component.Visual",  # Needed to use components VisualStyle
                            "Sofa.GL.Component.Rendering3D",  # Needed to use components OglModel, OglSceneFrame
                            "Sofa.Component.StateContainer",
                            'Sofa.Component.Mapping.Linear'
                        ])
    rootNode.addObject('VisualStyle',
                       displayFlags='showVisualModels hideBehaviorModels showCollisionModels hideBoundingCollisionModels hideForceFields showInteractionForceFields hideWireframe')

    rootNode.addObject('FreeMotionAnimationLoop')
    rootNode.addObject('DefaultVisualManagerLoop')

    rootNode.addObject('GenericConstraintSolver', tolerance=1e-5, maxIterations=100)

    rootNode.gravity = [0, -9810, 0]
    rootNode.dt = 0.01

    ##########################################
    # FEM Model                              #
    ##########################################
    finger = rootNode.addChild('finger')
    finger.addObject('EulerImplicitSolver', name='odesolver', rayleighMass=0.1, rayleighStiffness=0.1)
    finger.addObject('SparseLDLSolver', template='CompressedRowSparseMatrixMat3x3d')

    # Add a component to load a VTK tetrahedral mesh and expose the resulting topology in the scene .
    finger.addObject('MeshVTKLoader', name='loader', filename=os.path.join(path, 'finger.vtk'))
    finger.addObject('MeshTopology', src='@loader', name='container')

    # Create a MechanicaObject component to stores the DoFs of the model
    finger.addObject('MechanicalObject', name='tetras', template='Vec3', showIndices=False, showIndicesScale=4e-5)

    finger.addObject('UniformMass', totalMass=0.075)
    finger.addObject('TetrahedronFEMForceField', template='Vec3', name='FEM', method='large', poissonRatio=0.45,
                     youngModulus=600)
    finger.addObject('BoxROI', name='roi', box=[-15, 0, 0, 5, 10, 15], drawBoxes=True)
    finger.addObject('RestShapeSpringsForceField', points=finger.roi.indices.getLinkPath(), stiffness=1e12)
    finger.addObject('GenericConstraintCorrection')

    ##########################################
    # Cable                                  #
    ##########################################

    cable = finger.addChild('cable')
    cable.addObject('MechanicalObject',
                    position=[
                        [-17.5, 12.5, 2.5],
                        [-32.5, 12.5, 2.5],
                        [-47.5, 12.5, 2.5],
                        [-62.5, 12.5, 2.5],
                        [-77.5, 12.5, 2.5],

                        [-85.5, 12.5, 6.5],
                        [-85.5, 12.5, 8.5],
                        [-83.5, 12.5, 4.5],
                        [-83.5, 12.5, 10.5],

                        [-77.5, 12.5, 12.5],
                        [-62.5, 12.5, 12.5],
                        [-47.5, 12.5, 12.5],
                        [-32.5, 12.5, 12.5],
                        [-17.5, 12.5, 12.5]])

    cable.addObject('CableConstraint', name="aCableActuator",
                    indices=list(range(0, 14)),
                    minForce=0,  # Set that the cable can't push
                    pullPoint=[0.0, 12.5, 2.5])
    cable.addObject('BarycentricMapping')

    controller = FingerController(actuator=cable.aCableActuator, mo=finger.tetras)
    finger.addObject(controller)

    ##########################################
    # Visualization                          #
    ##########################################
    fingerVisu = finger.addChild('visu')

    # Add to this empty node a rendering model made of triangles and loaded from a stl file.
    fingerVisu.addObject('MeshSTLLoader', filename=os.path.join(path, "finger.stl"), name="loader")
    fingerVisu.addObject('OglModel', src="@loader", color=[0.0, 0.7, 0.7, 1])
    fingerVisu.addObject('BarycentricMapping')

    return rootNode, controller
