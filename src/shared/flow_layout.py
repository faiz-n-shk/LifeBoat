"""
Flow Layout
Custom layout that wraps widgets automatically
"""
from PyQt6.QtWidgets import QLayout, QLayoutItem, QWidget, QSizePolicy
from PyQt6.QtCore import Qt, QRect, QSize, QPoint


class FlowLayout(QLayout):
    """Layout that arranges widgets in a flow, wrapping to new rows as needed"""
    
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        
        self.setSpacing(spacing)
        self.item_list = []
    
    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)
    
    def addItem(self, item):
        self.item_list.append(item)
    
    def count(self):
        return len(self.item_list)
    
    def itemAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list[index]
        return None
    
    def takeAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list.pop(index)
        return None
    
    def expandingDirections(self):
        return Qt.Orientation(0)
    
    def hasHeightForWidth(self):
        return True
    
    def heightForWidth(self, width):
        height = self.do_layout(QRect(0, 0, width, 0), True)
        return height
    
    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.do_layout(rect, False)
    
    def sizeHint(self):
        return self.minimumSize()
    
    def minimumSize(self):
        size = QSize()
        
        for item in self.item_list:
            size = size.expandedTo(item.minimumSize())
        
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size
    
    def do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()
        
        # First pass: calculate row heights and group items by row
        rows = []
        current_row = []
        current_row_height = 0
        current_x = x
        
        for item in self.item_list:
            widget = item.widget()
            space_x = spacing + widget.style().layoutSpacing(
                QSizePolicy.ControlType.PushButton,
                QSizePolicy.ControlType.PushButton,
                Qt.Orientation.Horizontal
            )
            
            item_width = item.sizeHint().width()
            item_height = item.sizeHint().height()
            next_x = current_x + item_width + space_x
            
            # Check if we need to wrap to next row
            if next_x - space_x > rect.right() and len(current_row) > 0:
                # Save current row
                rows.append((current_row, current_row_height))
                # Start new row
                current_row = [(item, item_width, item_height)]
                current_row_height = item_height
                current_x = x + item_width + space_x
            else:
                # Add to current row
                current_row.append((item, item_width, item_height))
                current_row_height = max(current_row_height, item_height)
                current_x = next_x
        
        # Don't forget the last row
        if current_row:
            rows.append((current_row, current_row_height))
        
        # Second pass: position items with consistent row heights
        if not test_only:
            current_y = y
            
            for row_items, row_height in rows:
                current_x = x
                
                for item, item_width, item_height in row_items:
                    widget = item.widget()
                    space_x = spacing + widget.style().layoutSpacing(
                        QSizePolicy.ControlType.PushButton,
                        QSizePolicy.ControlType.PushButton,
                        Qt.Orientation.Horizontal
                    )
                    
                    # Set geometry with consistent row height
                    item.setGeometry(QRect(QPoint(current_x, current_y), QSize(item_width, row_height)))
                    current_x += item_width + space_x
                
                space_y = spacing + widget.style().layoutSpacing(
                    QSizePolicy.ControlType.PushButton,
                    QSizePolicy.ControlType.PushButton,
                    Qt.Orientation.Vertical
                )
                current_y += row_height + space_y
            
            return current_y - rect.y()
        else:
            # Calculate total height for test mode
            total_height = 0
            for row_items, row_height in rows:
                if total_height > 0:
                    widget = row_items[0][0].widget()
                    space_y = spacing + widget.style().layoutSpacing(
                        QSizePolicy.ControlType.PushButton,
                        QSizePolicy.ControlType.PushButton,
                        Qt.Orientation.Vertical
                    )
                    total_height += space_y
                total_height += row_height
            
            return total_height
