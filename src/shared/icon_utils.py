"""
Icon Utilities
Helper functions for loading and coloring SVG icons
"""
from PyQt6.QtGui import QPixmap, QIcon, QPainter, QColor
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtSvg import QSvgRenderer


def load_colored_svg(svg_path: str, color: str, size: tuple = (24, 24)) -> QPixmap:
    """
    Load an SVG and recolor it to the specified color
    
    Args:
        svg_path: Path to SVG file
        color: Hex color string (e.g., "#ffffff")
        size: Tuple of (width, height)
    
    Returns:
        Colored QPixmap
    """
    # Load SVG
    renderer = QSvgRenderer(svg_path)
    
    # Create pixmap
    pixmap = QPixmap(QSize(*size))
    pixmap.fill(Qt.GlobalColor.transparent)
    
    # Render SVG to pixmap
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    
    # Apply color overlay
    colored_pixmap = QPixmap(pixmap.size())
    colored_pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(colored_pixmap)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
    painter.drawPixmap(0, 0, pixmap)
    
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(colored_pixmap.rect(), QColor(color))
    painter.end()
    
    return colored_pixmap


def load_themed_icon(svg_path: str, size: tuple = (24, 24)) -> QPixmap:
    """
    Load an SVG and color it according to current theme's primary foreground color
    
    Args:
        svg_path: Path to SVG file
        size: Tuple of (width, height)
    
    Returns:
        Themed QPixmap
    """
    from src.core.theme_manager import theme_manager
    
    # Get current theme
    theme = theme_manager.get_theme_by_name(theme_manager.get_active_theme())
    
    if theme:
        color = theme.fg_primary
    else:
        color = "#ffffff"  # Fallback
    
    return load_colored_svg(svg_path, color, size)


def load_accent_icon(svg_path: str, size: tuple = (24, 24)) -> QPixmap:
    """
    Load an SVG and color it with the theme's accent color
    
    Args:
        svg_path: Path to SVG file
        size: Tuple of (width, height)
    
    Returns:
        Accent colored QPixmap
    """
    from src.core.theme_manager import theme_manager
    
    # Get current theme
    theme = theme_manager.get_theme_by_name(theme_manager.get_active_theme())
    
    if theme:
        color = theme.accent
    else:
        color = "#ff0000"  # Fallback
    
    return load_colored_svg(svg_path, color, size)
