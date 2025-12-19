from PySide6.QtWidgets import  QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPen, QFont


class PortItem(QGraphicsEllipseItem):
    R = 6

    def __init__(self, name, port_type, parent_block, x, y):
        super().__init__(-self.R, -self.R, 2 * self.R, 2 * self.R, parent_block)

        self.name = name
        self.port_type = port_type
        self.parent_block = parent_block
        self.connections = []

        self.setPos(x, y)
        self.setBrush(QBrush(QColor("white")))
        self.setPen(QPen(Qt.black, 1))
        self.setFlag(QGraphicsEllipseItem.ItemSendsScenePositionChanges)

        # -----------------------------
        # Port label (TEXT)
        # -----------------------------
        self.label = QGraphicsTextItem(name, parent_block)
        self.label.setDefaultTextColor(Qt.black)
        self.label.setFont(QFont("Sans Serif", 8))

        self._update_label_position()


    def _update_label_position(self):
        margin = 22
        label_rect = self.label.boundingRect()

        if self.port_type == "input":
            self.label.setPos(
                self.x() - label_rect.width() + margin,
                self.y() - label_rect.height() / 2,
            )
        else:  # output
            self.label.setPos(
                self.x() - margin - self.R,
                self.y() - label_rect.height() / 2,
            )


    def mousePressEvent(self, event):
        view = self.parent_block.view
        if view.pending_port is None:
            view.start_connection(self)
        else:
            view.finish_connection(self)
        event.accept()

    def is_compatible(self, other):
        return self.port_type != other.port_type

    def add_connection(self, conn):
        self.connections.append(conn)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemScenePositionHasChanged:
            for c in self.connections:
                c.update_position()
            self._update_label_position()

        return super().itemChange(change, value)
