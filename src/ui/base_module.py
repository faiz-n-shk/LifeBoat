"""
Base module class for all feature modules
"""
from src.ui.widgets import ThemedFrame, ThemedLabel, ThemedButton, SearchBar
from src.core import config

class BaseModule(ThemedFrame):
    """Base class for all feature modules"""
    
    def __init__(self, master, title="Module", **kwargs):
        super().__init__(master, color_key="bg_primary", **kwargs)
        self.module_title = title
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
    
    def create_header(self, show_search=False, show_add_button=False, add_button_text="+ Add", add_callback=None):
        """make standard module header"""
        header = ThemedFrame(self, color_key="bg_primary")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        header.grid_columnconfigure(1, weight=1)
        
        title = ThemedLabel(
            header,
            text=self.module_title,
            font=(config.FONT_FAMILY, config.FONT_SIZE_XLARGE, "bold")
        )
        title.grid(row=0, column=0, sticky="w")
        
        if show_search:
            self.search_bar = SearchBar(header, callback=self.on_search, width=300)
            self.search_bar.grid(row=0, column=1, sticky="e", padx=(20, 0))
        
        if show_add_button and add_callback:
            ThemedButton(
                header,
                text=add_button_text,
                button_style="accent",
                command=add_callback
            ).grid(row=0, column=2, sticky="e", padx=(10, 0))
        
        return header
    
    def on_search(self, query):
        """Override this method to handle search"""
        pass
    
    def refresh(self):
        """Override this method to refresh module data"""
        pass
