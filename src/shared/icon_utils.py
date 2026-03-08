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


def save_themed_tick_icon(output_path: str, background_color: str, foreground_color: str):
    """
    Generate and save a themed tick icon
    
    Args:
        output_path: Where to save the themed icon
        background_color: Hex color of the background (accent color)
        foreground_color: Hex color for the tick (theme foreground)
    """
    import logging
    from pathlib import Path
    from src.core.path_manager import get_resource_path
    
    logger = logging.getLogger(__name__)
    
    try:
        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Calculate luminance to determine contrasting color
        bg_color = QColor(background_color)
        r, g, b = bg_color.red(), bg_color.green(), bg_color.blue()
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        
        # Use white for dark backgrounds, dark gray for light backgrounds
        tick_color = "#ffffff" if luminance < 0.5 else "#1a1a1a"
        
        # Load the tick icon with contrasting color
        tick_pixmap = load_colored_svg(
            get_resource_path("assets/icons/icon_tick.svg"),
            tick_color,
            size=(16, 16)
        )
        
        # Save to file with absolute path
        success = tick_pixmap.save(str(output_file.absolute()), "PNG")
        if success:
            logger.debug(f"Saved themed tick icon to: {output_file.absolute()}")
        else:
            logger.error(f"Failed to save themed tick icon to: {output_file.absolute()}")
    except Exception as e:
        logger.error(f"Error saving themed tick icon: {e}", exc_info=True)
