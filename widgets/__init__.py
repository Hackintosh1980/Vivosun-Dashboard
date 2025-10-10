# main_gui/widgets/__init__.py

from .footer_widget import create_footer

# Falls vorhanden – einfach auskommentieren wenn (noch) nicht da:
try:
    from .scatter_tool import open_scatter_window
except Exception:
    open_scatter_window = None

try:
    from .export_window import open_export_window
except Exception:
    open_export_window = None

try:
    from .enlarged_view import open_enlarged_view
except Exception:
    open_enlarged_view = None

__all__ = [
    "create_footer",
    "open_scatter_window",
    "open_export_window",
    "open_enlarged_view",
]
