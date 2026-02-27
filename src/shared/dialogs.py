"""
Shared Dialog Components
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QDateEdit, QTimeEdit,
    QPushButton, QScrollArea, QWidget, QSizePolicy, QFrame, QMessageBox, QGraphicsDropShadowEffect,
    QComboBox, QSpinBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, QDate, QTime, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QPixmap, QColor, QCursor, QIcon, QFont

from src.core.config import config


class NoScrollComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()


class NoScrollSpinBox(QSpinBox):
    def wheelEvent(self, event):
        event.ignore()


class NoScrollDoubleSpinBox(QDoubleSpinBox):
    def wheelEvent(self, event):
        event.ignore()


class NoScrollDateEdit(QDateEdit):
    def wheelEvent(self, event):
        event.ignore()


def create_message_box(parent, title, text, icon=QMessageBox.Icon.Question, 
                       buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No):
    dialog = QDialog(parent)
    dialog.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
    dialog.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    dialog.setFixedWidth(450)
    
    outer_layout = QVBoxLayout(dialog)
    outer_layout.setContentsMargins(10, 10, 10, 10)
    
    container = QFrame()
    container.setObjectName("message-box-container")
    outer_layout.addWidget(container)
    
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(20)
    shadow.setXOffset(0)
    shadow.setYOffset(0)
    shadow.setColor(QColor(0, 0, 0, 100))
    container.setGraphicsEffect(shadow)
    
    container_layout = QVBoxLayout(container)
    container_layout.setContentsMargins(0, 0, 0, 0)
    container_layout.setSpacing(0)
    
    title_bar = QFrame()
    title_bar.setObjectName("message-box-title-bar")
    title_bar.setFixedHeight(50)
    title_bar_layout = QHBoxLayout(title_bar)
    title_bar_layout.setContentsMargins(20, 0, 10, 0)
    
    icon_label = QLabel()
    if icon == QMessageBox.Icon.Question:
        icon_label.setText("❓")
    elif icon == QMessageBox.Icon.Information:
        icon_label.setText("ℹ️")
    elif icon == QMessageBox.Icon.Warning:
        icon_label.setText("⚠️")
    elif icon == QMessageBox.Icon.Critical:
        icon_label.setText("❌")
    
    icon_font = QFont()
    icon_font.setPointSize(18)
    icon_label.setFont(icon_font)
    title_bar_layout.addWidget(icon_label)
    
    title_label = QLabel(title)
    title_label.setObjectName("message-box-title")
    font = QFont()
    font.setPointSize(14)
    font.setBold(True)
    title_label.setFont(font)
    title_bar_layout.addWidget(title_label)
    
    title_bar_layout.addStretch()
    container_layout.addWidget(title_bar)
    
    content_widget = QWidget()
    content_layout = QVBoxLayout(content_widget)
    content_layout.setContentsMargins(20, 20, 20, 20)
    
    message_label = QLabel(text)
    message_label.setWordWrap(True)
    message_label.setObjectName("message-box-text")
    font = QFont()
    font.setPointSize(11)
    message_label.setFont(font)
    content_layout.addWidget(message_label)
    
    button_layout = QHBoxLayout()
    button_layout.addStretch()
    
    result = [None]
    
    def close_with_animation(button_result):
        result[0] = button_result
        if config.get('appearance.enable_animations', True):
            dialog._fade_out_anim = QPropertyAnimation(dialog, b"windowOpacity")
            dialog._fade_out_anim.setDuration(150)
            dialog._fade_out_anim.setStartValue(1.0)
            dialog._fade_out_anim.setEndValue(0.0)
            dialog._fade_out_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
            if button_result in [QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.Ok]:
                dialog._fade_out_anim.finished.connect(dialog.accept)
            else:
                dialog._fade_out_anim.finished.connect(dialog.reject)
            dialog._fade_out_anim.start()
        else:
            if button_result in [QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.Ok]:
                dialog.accept()
            else:
                dialog.reject()
    
    if buttons & QMessageBox.StandardButton.Yes:
        yes_btn = QPushButton("Yes")
        yes_btn.setObjectName("message-box-btn-yes")
        yes_btn.setMinimumWidth(80)
        yes_btn.setMinimumHeight(35)
        yes_btn.clicked.connect(lambda: close_with_animation(QMessageBox.StandardButton.Yes))
        button_layout.addWidget(yes_btn)
    
    if buttons & QMessageBox.StandardButton.No:
        no_btn = QPushButton("No")
        no_btn.setObjectName("message-box-btn-no")
        no_btn.setMinimumWidth(80)
        no_btn.setMinimumHeight(35)
        no_btn.clicked.connect(lambda: close_with_animation(QMessageBox.StandardButton.No))
        button_layout.addWidget(no_btn)
    
    if buttons & QMessageBox.StandardButton.Ok:
        ok_btn = QPushButton("OK")
        ok_btn.setObjectName("message-box-btn-ok")
        ok_btn.setMinimumWidth(80)
        ok_btn.setMinimumHeight(35)
        ok_btn.clicked.connect(lambda: close_with_animation(QMessageBox.StandardButton.Ok))
        button_layout.addWidget(ok_btn)
    
    if buttons & QMessageBox.StandardButton.Cancel:
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("message-box-btn-cancel")
        cancel_btn.setMinimumWidth(80)
        cancel_btn.setMinimumHeight(35)
        cancel_btn.clicked.connect(lambda: close_with_animation(QMessageBox.StandardButton.Cancel))
        button_layout.addWidget(cancel_btn)
    
    content_layout.addLayout(button_layout)
    container_layout.addWidget(content_widget)
    
    from src.core.theme_manager import theme_manager
    from src.models.theme import Theme
    from src.core.database import db
    
    try:
        db.connect(reuse_if_open=True)
        theme_obj = Theme.get(Theme.name == theme_manager.current_theme)
        
        container.setStyleSheet(f"""
            QFrame#message-box-container {{
                background-color: {theme_obj.bg_primary};
                border: 2px solid {theme_obj.border};
                border-radius: 12px;
            }}
        """)
        
        title_bar.setStyleSheet(f"""
            QFrame#message-box-title-bar {{
                background-color: {theme_obj.bg_secondary};
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                border-bottom: 1px solid {theme_obj.border};
            }}
            QLabel#message-box-title {{
                color: {theme_obj.fg_primary};
            }}
        """)
        
        message_label.setStyleSheet(f"""
            QLabel#message-box-text {{
                color: {theme_obj.fg_primary};
            }}
        """)
        
        button_style = f"""
            QPushButton {{
                background-color: {theme_obj.accent};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: {theme_obj.accent_hover};
            }}
            QPushButton:pressed {{
                background-color: {theme_obj.accent};
                opacity: 0.8;
            }}
            QPushButton#message-box-btn-no, QPushButton#message-box-btn-cancel {{
                background-color: {theme_obj.bg_tertiary};
                color: {theme_obj.fg_primary};
                border: 1px solid {theme_obj.border};
            }}
            QPushButton#message-box-btn-no:hover, QPushButton#message-box-btn-cancel:hover {{
                background-color: {theme_obj.bg_secondary};
                border: 1px solid {theme_obj.accent};
            }}
            QPushButton#message-box-btn-no:pressed, QPushButton#message-box-btn-cancel:pressed {{
                background-color: {theme_obj.bg_tertiary};
            }}
        """
        
        for btn in [yes_btn if buttons & QMessageBox.StandardButton.Yes else None,
                    no_btn if buttons & QMessageBox.StandardButton.No else None,
                    ok_btn if buttons & QMessageBox.StandardButton.Ok else None,
                    cancel_btn if buttons & QMessageBox.StandardButton.Cancel else None]:
            if btn:
                btn.setStyleSheet(button_style)
        
        db.close()
    except:
        pass
    
    def keyPressEvent(event):
        if event.key() == Qt.Key.Key_Escape:
            result[0] = QMessageBox.StandardButton.Cancel
            if config.get('appearance.enable_animations', True):
                dialog._fade_out_anim = QPropertyAnimation(dialog, b"windowOpacity")
                dialog._fade_out_anim.setDuration(150)
                dialog._fade_out_anim.setStartValue(1.0)
                dialog._fade_out_anim.setEndValue(0.0)
                dialog._fade_out_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
                dialog._fade_out_anim.finished.connect(dialog.reject)
                dialog._fade_out_anim.start()
            else:
                dialog.reject()
        else:
            QDialog.keyPressEvent(dialog, event)
    
    dialog.keyPressEvent = keyPressEvent
    
    if config.get('appearance.enable_animations', True):
        dialog.setWindowOpacity(0.0)
        dialog._fade_in_anim = QPropertyAnimation(dialog, b"windowOpacity")
        dialog._fade_in_anim.setDuration(150)
        dialog._fade_in_anim.setStartValue(0.0)
        dialog._fade_in_anim.setEndValue(1.0)
        dialog._fade_in_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        dialog._fade_in_anim.start()
    else:
        dialog.setWindowOpacity(1.0)
    
    if parent:
        parent_geo = parent.window().geometry()
        dialog.adjustSize()
        dialog_geo = dialog.geometry()
        x = parent_geo.x() + (parent_geo.width() - dialog_geo.width()) // 2
        y = parent_geo.y() + (parent_geo.height() - dialog_geo.height()) // 2
        dialog.move(x, y)
    
    dialog.exec()
    return result[0] if result[0] is not None else QMessageBox.StandardButton.Cancel


def show_warning(parent, title, text):
    return create_message_box(parent, title, text, QMessageBox.Icon.Warning, QMessageBox.StandardButton.Ok)


def show_information(parent, title, text):
    return create_message_box(parent, title, text, QMessageBox.Icon.Information, QMessageBox.StandardButton.Ok)


def show_critical(parent, title, text):
    return create_message_box(parent, title, text, QMessageBox.Icon.Critical, QMessageBox.StandardButton.Ok)


def show_question(parent, title, text, buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No):
    return create_message_box(parent, title, text, QMessageBox.Icon.Question, buttons)


class BaseDialog(QDialog):
    
    def __init__(self, parent=None, title="Dialog", width=450, height=550):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(width)
        self.setFixedHeight(height)
        
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self._drag_pos = None
        
        self.outer_layout = QVBoxLayout(self)
        self.outer_layout.setContentsMargins(10, 10, 10, 10)
        
        self.container = QFrame()
        self.container.setObjectName("dialog-container")
        self.outer_layout.addWidget(self.container)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.container.setGraphicsEffect(shadow)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        self.title_bar = QFrame()
        self.title_bar.setObjectName("dialog-title-bar")
        self.title_bar.setFixedHeight(50)
        title_bar_layout = QHBoxLayout(self.title_bar)
        title_bar_layout.setContentsMargins(20, 0, 15, 0)
        title_bar_layout.setSpacing(10)
        
        self.title_label = QLabel(title)
        self.title_label.setObjectName("dialog-title")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.title_label.setFont(font)
        title_bar_layout.addWidget(self.title_label)
        
        title_bar_layout.addStretch()
        
        self.close_btn = QPushButton()
        self.close_btn.setObjectName("dialog-close-btn")
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.close_btn.clicked.connect(self.on_close)
        
        from src.core.path_manager import get_resource_path
        try:
            close_icon = QIcon(get_resource_path("assets/icons/cross_mark.svg"))
            self.close_btn.setIcon(close_icon)
            self.close_btn.setIconSize(QSize(16, 16))
        except:
            self.close_btn.setText("✕")
            font = QFont()
            font.setPointSize(12)
            self.close_btn.setFont(font)
        
        title_bar_layout.addWidget(self.close_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        container_layout.addWidget(self.title_bar)
        
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.content = QWidget()
        self.layout = QVBoxLayout(self.content)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        self.scroll.setWidget(self.content)
        self.main_layout.addWidget(self.scroll)
        container_layout.addLayout(self.main_layout)
        self.setLayout(self.outer_layout)
        
        self._apply_theme_styling()
    
    def _apply_theme_styling(self):
        from src.core.theme_manager import theme_manager
        from src.models.theme import Theme
        from src.core.database import db
        
        try:
            db.connect(reuse_if_open=True)
            theme_obj = Theme.get(Theme.name == theme_manager.current_theme)
            
            self.container.setStyleSheet(f"""
                QFrame#dialog-container {{
                    background-color: {theme_obj.bg_primary};
                    border: 2px solid {theme_obj.border};
                    border-radius: 12px;
                }}
            """)
            
            self.title_bar.setStyleSheet(f"""
                QFrame#dialog-title-bar {{
                    background-color: {theme_obj.bg_secondary};
                    border-top-left-radius: 10px;
                    border-top-right-radius: 10px;
                    border-bottom: 1px solid {theme_obj.border};
                }}
                QLabel#dialog-title {{
                    color: {theme_obj.fg_primary};
                }}
            """)
            
            self.close_btn.setStyleSheet(f"""
                QPushButton#dialog-close-btn {{
                    background-color: transparent;
                    border: none;
                    border-radius: 4px;
                    padding: 0px;
                    min-width: 28px;
                    max-width: 28px;
                    min-height: 28px;
                    max-height: 28px;
                }}
                QPushButton#dialog-close-btn:hover {{
                    background-color: {theme_obj.danger};
                }}
                QPushButton#dialog-close-btn:pressed {{
                    background-color: {theme_obj.danger};
                    opacity: 0.8;
                }}
            """)
            
            db.close()
        except:
            pass
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.title_bar.geometry().contains(event.pos() - self.container.pos()):
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super().mouseReleaseEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.on_close()
        else:
            super().keyPressEvent(event)
    
    def on_close(self):
        if config.get('appearance.enable_animations', True):
            self.animate_close()
        else:
            self.reject()
    
    def animate_close(self):
        self._fade_out_animation = QPropertyAnimation(self, b"windowOpacity")
        self._fade_out_animation.setDuration(150)
        self._fade_out_animation.setStartValue(1.0)
        self._fade_out_animation.setEndValue(0.0)
        self._fade_out_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._fade_out_animation.finished.connect(self.reject)
        self._fade_out_animation.start()
    
    def showEvent(self, event):
        super().showEvent(event)
        if config.get('appearance.enable_animations', True) and not event.spontaneous():
            self.setWindowOpacity(0.0)
            self._fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
            self._fade_in_animation.setDuration(150)
            self._fade_in_animation.setStartValue(0.0)
            self._fade_in_animation.setEndValue(1.0)
            self._fade_in_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self._fade_in_animation.start()
        else:
            self.setWindowOpacity(1.0)
    
    def add_title_field(self, label="Title:", placeholder="Enter title..."):
        title_label = QLabel(label)
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText(placeholder)
        self.layout.addWidget(title_label)
        self.layout.addWidget(self.title_input)
        return self.title_input
    
    def add_description_field(self, label="Description:", placeholder="Enter description (optional)...", 
                            min_height=60, max_height=200):
        desc_label = QLabel(label)
        self.description_input = QTextEdit()
        self.description_input.setMinimumHeight(min_height)
        self.description_input.setMaximumHeight(max_height)
        self.description_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.description_input.setPlaceholderText(placeholder)
        
        self._apply_description_styling()
        
        desc_container = QVBoxLayout()
        desc_container.setSpacing(0)
        desc_container.addWidget(self.description_input)
        
        resize_handle = QLabel()
        from src.core.path_manager import get_resource_path
        pixmap = QPixmap(get_resource_path("assets/icons/resize-grip.svg"))
        resize_handle.setPixmap(pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, 
                                              Qt.TransformationMode.SmoothTransformation))
        resize_handle.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        resize_handle.setFixedHeight(20)
        resize_handle.setStyleSheet("padding-right: 5px; padding-bottom: 2px;")
        resize_handle.setCursor(Qt.CursorShape.SizeVerCursor)
        
        resize_handle.mousePressEvent = lambda e: self._start_resize(e)
        resize_handle.mouseMoveEvent = lambda e: self._do_resize(e, min_height, max_height)
        
        desc_container.addWidget(resize_handle)
        
        self.layout.addWidget(desc_label)
        self.layout.addLayout(desc_container)
        return self.description_input
    
    def add_date_time_field(self, label="Date & Time:"):
        datetime_label = QLabel(label)
        self.layout.addWidget(datetime_label)
        
        datetime_row = QHBoxLayout()
        datetime_row.setSpacing(10)
        
        self.date_input = NoScrollDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        
        first_day = config.get('locale.week_starts_on', 'Monday')
        calendar_widget = self.date_input.calendarWidget()
        if calendar_widget:
            if first_day == "Sunday":
                calendar_widget.setFirstDayOfWeek(Qt.DayOfWeek.Sunday)
            else:
                calendar_widget.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        
        datetime_row.addWidget(self.date_input, 1)
        
        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime.currentTime())
        
        time_mode = config.get('datetime.time_mode', '12hr')
        if time_mode == '12hr':
            self.time_input.setDisplayFormat("hh:mm AP")
        else:
            self.time_input.setDisplayFormat("HH:mm")
        
        datetime_row.addWidget(self.time_input, 0)
        
        self.layout.addLayout(datetime_row)
        return self.date_input, self.time_input
    
    def add_buttons(self, save_text="Save", cancel_text="Cancel", on_save=None):
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton(cancel_text)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton(save_text)
        if on_save:
            save_btn.clicked.connect(on_save)
        else:
            save_btn.clicked.connect(self.accept)
        save_btn.setDefault(True)
        buttons_layout.addWidget(save_btn)
        
        self.layout.addLayout(buttons_layout)
        return save_btn, cancel_btn
    
    def get_datetime(self):
        if not hasattr(self, 'date_input') or not hasattr(self, 'time_input'):
            return None
        
        from datetime import datetime
        date = self.date_input.date()
        time = self.time_input.time()
        
        return datetime(date.year(), date.month(), date.day(), time.hour(), time.minute())
    
    def set_datetime(self, dt):
        if not hasattr(self, 'date_input') or not hasattr(self, 'time_input'):
            return
        
        if dt:
            self.date_input.setDate(QDate(dt.year, dt.month, dt.day))
            self.time_input.setTime(QTime(dt.hour, dt.minute))
    
    def _apply_description_styling(self):
        from src.core.theme_manager import theme_manager
        from src.models.theme import Theme
        from src.core.database import db
        
        theme = theme_manager.current_theme
        if theme:
            try:
                db.connect(reuse_if_open=True)
                theme_obj = Theme.get(Theme.name == theme)
                self.description_input.setStyleSheet(f"""
                    QTextEdit {{
                        background-color: {theme_obj.bg_secondary};
                        color: {theme_obj.fg_primary};
                        border: 2px solid {theme_obj.border};
                        border-radius: 6px;
                        padding: 8px 12px;
                    }}
                    QTextEdit::corner {{
                        background-color: {theme_obj.bg_tertiary};
                        border: 1px solid {theme_obj.border};
                    }}
                """)
                db.close()
            except:
                pass
    
    def _start_resize(self, event):
        self.resize_start_y = event.globalPosition().y()
        self.resize_start_height = self.description_input.height()
    
    def _do_resize(self, event, min_height, max_height):
        if hasattr(self, 'resize_start_y'):
            delta = event.globalPosition().y() - self.resize_start_y
            new_height = max(min_height, min(max_height, self.resize_start_height + delta))
            self.description_input.setFixedHeight(int(new_height))
