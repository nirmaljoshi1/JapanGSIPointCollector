from qgis.gui import QgsRubberBand, QgsMapToolEmitPoint, QgsMapTool
from PyQt5 import QtGui
from qgis.core import QgsWkbTypes, QgsRectangle, QgsPointXY
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject

from shapely.wkt import loads
from shapely.geometry import mapping

class RectangleMapTool(QgsMapToolEmitPoint):
    def __init__(self, canvas, dlg):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        self.rubberBand = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        self.rubberBand.setColor(QtGui.QColor(0, 0, 255))
        self.rubberBand.setFillColor(QtGui.QColor(0, 0, 255, 50))
        self.rubberBand.setWidth(1)
        self.reset()
        self.dlg = dlg
    
    def reset(self):
        self.startPoint = self.endPoint = None
        self.isEmittingPoint = False
        self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
    
    def canvasPressEvent(self, e):
        self.startPoint = self.toMapCoordinates(e.pos())
        self.endPoint = self.startPoint
        self.isEmittingPoint = True
        self.showRect(self.startPoint, self.endPoint)
    
    def canvasReleaseEvent(self, e):
        self.isEmittingPoint = False
        r = self.rectangle()
        if r is not None:
            self.deactivate()
            self.reset()
            self.canvas.unsetMapTool(self)
            self.canvas.refresh()
            self.dlg.showNormal()
            """ ------------------ """
            
            self.wkt_ext = r.asWktCoordinates()
            # sp_pol = loads(self.wkt_ext)
            # json_ext = mapping(sp_pol)
            map_crs = QgsProject.instance().crs()
            target_crs = QgsCoordinateReferenceSystem('EPSG:4326')
            transform = QgsCoordinateTransform(map_crs, target_crs, QgsProject.instance())
            x1y1x2y2= self.wkt_ext

            x1y1x2y2 = [part.strip() for part in x1y1x2y2.replace(',', ' ').split()]
    
            boundingBoxXmin=float(x1y1x2y2[0])
            boundingBoxXmax=float(x1y1x2y2[2])

            boundingBoxYmin=float(x1y1x2y2[1])
            boundingBoxYmax=float(x1y1x2y2[3])

            pointMin = QgsPointXY(boundingBoxXmin, boundingBoxYmin)
            pointMax = QgsPointXY(boundingBoxXmax, boundingBoxYmax)


            # Transform the point to WGS84
            transformed_pointMin = transform.transform(pointMin)
            transformed_pointMax = transform.transform(pointMax)

            # Output the transformed coordinates
            # print("Transformed coordinates1 (WGS84): ", transformed_pointMin.x(), transformed_pointMin.y())
            # print("Transformed coordinates2 (WGS84): ", transformed_pointMax.x(), transformed_pointMax.y())
            x1y1x2y2=str(round(transformed_pointMin.x(),6))+" "+   str(round(transformed_pointMin.y(),6))+", "+   str(round(transformed_pointMax.x(),6))+" "+    str(round( transformed_pointMax.y(),6))
            

            self.dlg.teCoordinates.setPlainText(x1y1x2y2)

        
            """ ------------------ """
            
    def canvasMoveEvent(self, e):
        if not self.isEmittingPoint:
            return
    
        self.endPoint = self.toMapCoordinates(e.pos())
        self.showRect(self.startPoint, self.endPoint)
    
    def showRect(self, startPoint, endPoint):
        self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
        if startPoint.x() == endPoint.x() or startPoint.y() == endPoint.y():
            return
      
        self.point1 = QgsPointXY(startPoint.x(), startPoint.y())
        self.point2 = QgsPointXY(startPoint.x(), endPoint.y())
        self.point3 = QgsPointXY(endPoint.x(), endPoint.y())
        self.point4 = QgsPointXY(endPoint.x(), startPoint.y())
      
        self.rubberBand.addPoint(self.point1, False)
        self.rubberBand.addPoint(self.point2, False)
        self.rubberBand.addPoint(self.point3, False)
        self.rubberBand.addPoint(self.point4, False)
        self.rubberBand.addPoint(self.point1, True)    # true to update canvas
        
        self.rubberBand.show()

    def rectangle(self):
        if self.startPoint is None or self.endPoint is None:
            return None
        elif (self.startPoint.x() == self.endPoint.x() or self.startPoint.y() == self.endPoint.y()):
            return None
        return QgsRectangle(self.startPoint, self.endPoint)
    
    def deactivate(self):
        QgsMapTool.deactivate(self)
        self.deactivated.emit()
