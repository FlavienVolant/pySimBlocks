from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor

from pySimBlocks.gui_qt.dialogs.block_dialog import BlockDialog
from pySimBlocks.gui_qt.graphics.port_item import PortItem
from pySimBlocks.gui_qt.model.block_instance import BlockInstance


class BlockItem(QGraphicsRectItem):
    WIDTH = 120
    HEIGHT = 60

    def __init__(self, instance: BlockInstance, pos, view):
        super().__init__(0, 0, self.WIDTH, self.HEIGHT)
        self.view = view
        self.instance = instance

        self.setPos(pos)
        self.setBrush(QBrush(QColor("#E6F2FF")))
        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
        self.setFlag(QGraphicsRectItem.ItemSendsScenePositionChanges)

        # Ports
        self.in_port = PortItem("in", "input", self, 0, self.HEIGHT / 2)
        self.out_port = PortItem("out", "output", self, self.WIDTH, self.HEIGHT / 2)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        painter.drawText(self.rect(), Qt.AlignCenter, self.instance.name)

    def mouseDoubleClickEvent(self, event):
        dialog = BlockDialog(self)
        dialog.exec()
        self.update()
        event.accept()

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for port in [self.in_port, self.out_port]:
                for c in port.connections:
                    c.update_position()
        return super().itemChange(change, value)


    def remove_all_connections(self):
        for port in [self.in_port, self.out_port]:
            for conn in port.connections[:]:
                conn.remove()
