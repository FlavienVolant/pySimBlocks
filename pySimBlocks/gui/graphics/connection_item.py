# ******************************************************************************
#                                  pySimBlocks
#                     Copyright (c) 2026 Antoine Alessandrini
# ******************************************************************************
#  This program is free software: you can redistribute it and/or modify it
#  under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your
#  option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
#  for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ******************************************************************************
#  Authors: see Authors.txt
# ******************************************************************************

from PySide6.QtWidgets import QGraphicsItem, QGraphicsPathItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QPainterPath

from pySimBlocks.gui.graphics.port_item import PortItem
from pySimBlocks.gui.model.connection_instance import ConnectionInstance

class ConnectionItem(QGraphicsPathItem):
    def __init__(self, 
                 src_port: PortItem,
                 dst_port: PortItem,
                 instance: ConnectionInstance):
        super().__init__()
        self.setFlag(QGraphicsItem.ItemIsSelectable)

        self.src_port = src_port
        self.dst_port = dst_port
        self.instance = instance
        self.setPen(QPen(Qt.black, 2))
        self.update_position()

    def update_position(self):
        p1 = self.src_port.scenePos()
        p2 = self.dst_port.scenePos()

        dx = abs(p2.x() - p1.x()) * 0.5

        c1 = QPointF(p1.x() + dx, p1.y())
        c2 = QPointF(p2.x() - dx, p2.y())

        path = QPainterPath(p1)
        path.cubicTo(c1, c2, p2)
        self.setPath(path)
