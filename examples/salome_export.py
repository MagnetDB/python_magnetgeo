#!/usr/bin/env python

###
### This file is generated automatically by SALOME v9.9.0 with dump python functionality
###

import os

import salome

salome.salome_init()

os.chdir("/tmp")

###
### SHAPER component
###

from salome.shaper import model

model.begin()
partSet = model.moduleDocument()

### Create Part
Part_1 = model.addPart(partSet)
Part_1_doc = Part_1.document()

### Create Sketch
Sketch_1 = model.addSketch(Part_1_doc, model.defaultPlane("XOY"))

### Create SketchLine
SketchLine_1 = Sketch_1.addLine(59.34894259818733, 0, 0, 0)

### Create SketchProjection
SketchProjection_1 = Sketch_1.addProjection(model.selection("VERTEX", "PartSet/Origin"), False)
SketchPoint_1 = SketchProjection_1.createdFeature()
Sketch_1.setCoincident(SketchLine_1.endPoint(), SketchPoint_1.result())

### Create SketchLine
SketchLine_2 = Sketch_1.addLine(0, 0, 0, 41.49848942598186)

### Create SketchLine
SketchLine_3 = Sketch_1.addLine(0, 41.49848942598186, 59.34894259818733, 41.49848942598186)

### Create SketchLine
SketchLine_4 = Sketch_1.addLine(59.34894259818733, 41.49848942598186, 59.34894259818733, 0)
Sketch_1.setCoincident(SketchLine_4.endPoint(), SketchLine_1.startPoint())
Sketch_1.setCoincident(SketchLine_1.endPoint(), SketchLine_2.startPoint())
Sketch_1.setCoincident(SketchLine_2.endPoint(), SketchLine_3.startPoint())
Sketch_1.setCoincident(SketchLine_3.endPoint(), SketchLine_4.startPoint())
Sketch_1.setHorizontal(SketchLine_1.result())
Sketch_1.setVertical(SketchLine_2.result())
Sketch_1.setHorizontal(SketchLine_3.result())
Sketch_1.setVertical(SketchLine_4.result())

### Create SketchLine
SketchLine_5 = Sketch_1.addLine(59.95921450151058, -33.56495468277945, -10.22205438066466, -33.56495468277945)

### Create SketchLine
SketchLine_6 = Sketch_1.addLine(-10.22205438066466, -33.56495468277945, -10.22205438066466, -59.19637462235649)

### Create SketchLine
SketchLine_7 = Sketch_1.addLine(-10.22205438066466, -59.19637462235649, 59.95921450151058, -59.19637462235649)

### Create SketchLine
SketchLine_8 = Sketch_1.addLine(59.95921450151058, -59.19637462235649, 59.95921450151058, -33.56495468277945)
Sketch_1.setCoincident(SketchLine_8.endPoint(), SketchLine_5.startPoint())
Sketch_1.setCoincident(SketchLine_5.endPoint(), SketchLine_6.startPoint())
Sketch_1.setCoincident(SketchLine_6.endPoint(), SketchLine_7.startPoint())
Sketch_1.setCoincident(SketchLine_7.endPoint(), SketchLine_8.startPoint())
Sketch_1.setHorizontal(SketchLine_5.result())
Sketch_1.setVertical(SketchLine_6.result())
Sketch_1.setHorizontal(SketchLine_7.result())
Sketch_1.setVertical(SketchLine_8.result())

### Create SketchLine
SketchLine_9 = Sketch_1.addLine(-123.7326283987915, -10.6797583081571, -64.23111782477342, -10.6797583081571)

### Create SketchLine
SketchLine_10 = Sketch_1.addLine(-64.23111782477342, -10.6797583081571, -64.23111782477342, 21.3595166163142)

### Create SketchLine
SketchLine_11 = Sketch_1.addLine(-64.23111782477342, 21.3595166163142, -123.7326283987915, 21.3595166163142)

### Create SketchLine
SketchLine_12 = Sketch_1.addLine(-123.7326283987915, 21.3595166163142, -123.7326283987915, -10.6797583081571)
Sketch_1.setCoincident(SketchLine_12.endPoint(), SketchLine_9.startPoint())
Sketch_1.setCoincident(SketchLine_9.endPoint(), SketchLine_10.startPoint())
Sketch_1.setCoincident(SketchLine_10.endPoint(), SketchLine_11.startPoint())
Sketch_1.setCoincident(SketchLine_11.endPoint(), SketchLine_12.startPoint())
Sketch_1.setHorizontal(SketchLine_9.result())
Sketch_1.setVertical(SketchLine_10.result())
Sketch_1.setHorizontal(SketchLine_11.result())
Sketch_1.setVertical(SketchLine_12.result())

### Create SketchLine
SketchLine_13 = Sketch_1.addLine(-141.7356495468278, 31.73413897280967, -180.487915407855, 31.73413897280967)

### Create SketchLine
SketchLine_14 = Sketch_1.addLine(-180.487915407855, 31.73413897280967, -180.487915407855, -14.03625377643504)

### Create SketchLine
SketchLine_15 = Sketch_1.addLine(-180.487915407855, -14.03625377643504, -141.7356495468278, -14.03625377643504)

### Create SketchLine
SketchLine_16 = Sketch_1.addLine(-141.7356495468278, -14.03625377643504, -141.7356495468278, 31.73413897280967)
Sketch_1.setCoincident(SketchLine_16.endPoint(), SketchLine_13.startPoint())
Sketch_1.setCoincident(SketchLine_13.endPoint(), SketchLine_14.startPoint())
Sketch_1.setCoincident(SketchLine_14.endPoint(), SketchLine_15.startPoint())
Sketch_1.setCoincident(SketchLine_15.endPoint(), SketchLine_16.startPoint())
Sketch_1.setHorizontal(SketchLine_13.result())
Sketch_1.setVertical(SketchLine_14.result())
Sketch_1.setHorizontal(SketchLine_15.result())
Sketch_1.setVertical(SketchLine_16.result())
model.do()

### Create Face
Face_1_objects = [model.selection("FACE", "Sketch_1/Face-SketchLine_5f-SketchLine_6f-SketchLine_7f-SketchLine_8f"),
                  model.selection("FACE", "Sketch_1/Face-SketchLine_4r-SketchLine_3r-SketchLine_2r-SketchLine_1r"),
                  model.selection("FACE", "Sketch_1/Face-SketchLine_9f-SketchLine_10f-SketchLine_11f-SketchLine_12f"),
                  model.selection("FACE", "Sketch_1/Face-SketchLine_13f-SketchLine_14f-SketchLine_15f-SketchLine_16f")]
Face_1 = model.addFace(Part_1_doc, Face_1_objects)

### Create Export
Export_1 = model.exportToXAO(Part_1_doc, 'shaper_95169b12.xao', model.selection("FACE", "Face_1_1"), 'XAO')

### Create Export
Export_2 = model.exportToXAO(Part_1_doc, 'shaper__ylaz8rk.xao', model.selection("FACE", "Face_1_2"), 'XAO')

### Create Export
Export_3 = model.exportToXAO(Part_1_doc, 'shaper_tfnq0q05.xao', model.selection("FACE", "Face_1_3"), 'XAO')

### Create Export
Export_4 = model.exportToXAO(Part_1_doc, 'shaper_qienyxeo.xao', model.selection("FACE", "Face_1_4"), 'XAO')

model.end()

###
### SHAPERSTUDY component
###

model.publishToShaperStudy()
import SHAPERSTUDY

Face_1_1, = SHAPERSTUDY.shape(model.featureStringId(Face_1))
Face_1_2, = SHAPERSTUDY.shape(model.featureStringId(Face_1, 1))
Face_1_3, = SHAPERSTUDY.shape(model.featureStringId(Face_1, 2))
Face_1_4, = SHAPERSTUDY.shape(model.featureStringId(Face_1, 3))
###
### GEOM component
###

from salome.geom import geomBuilder

geompy = geomBuilder.New()

O = geompy.MakeVertex(0, 0, 0)
OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)
(imported, Face_1_1, [], [], []) = geompy.ImportXAO("/tmp/shaper_95169b12.xao")
(imported, Face_1_2, [], [], []) = geompy.ImportXAO("/tmp/shaper__ylaz8rk.xao")
(imported, Face_1_3, [], [], []) = geompy.ImportXAO("/tmp/shaper_tfnq0q05.xao")
(imported, Face_1_4, [], [], []) = geompy.ImportXAO("/tmp/shaper_qienyxeo.xao")
Compound_1 = geompy.MakeCompound([Face_1_1, Face_1_2, Face_1_3, Face_1_4])
geompy.ExportBREP(Compound_1, "test_geom.brep" )
geompy.addToStudy( O, 'O' )
geompy.addToStudy( OX, 'OX' )
geompy.addToStudy( OY, 'OY' )
geompy.addToStudy( OZ, 'OZ' )
geompy.addToStudy( Face_1_1, 'Face_1_1' )
geompy.addToStudy( Face_1_2, 'Face_1_2' )
geompy.addToStudy( Face_1_3, 'Face_1_3' )
geompy.addToStudy( Face_1_4, 'Face_1_4' )
geompy.addToStudy( Compound_1, 'Compound_1' )


if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()
