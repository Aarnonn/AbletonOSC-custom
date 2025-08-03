# -*- coding: utf-8 -*-
"""
Browser API extension for AbletonOSC
-----------------------------------
Adds two endpoints:
  • /live/browser/search <text…>
  • /live/browser/load_device <track_index:int> <device_name…>
"""
import Live
from typing import List, Optional, Tuple, Any
from .handler import AbletonOSCHandler


class BrowserHandler(AbletonOSCHandler):
    def __init__(self, manager):
        super().__init__(manager)
        self.class_identifier = "browser"

    def init_api(self):
        """Initialize the browser API endpoints."""
        
        def browser_search_callback(params: Tuple[Any]):
            """Handle /live/browser/search requests."""
            query = " ".join(str(param) for param in params)
            app = Live.Application.get_application()
            results = self._search_items(app.browser, query)
            # Return list of item names
            return tuple(item.name for item in results)
        
        def browser_load_device_callback(params: Tuple[Any]):
            """Handle /live/browser/load_device requests."""
            if len(params) < 2:
                return ("error", "insufficient parameters")
            
            track_index = int(params[0])
            device_name = " ".join(str(param) for param in params[1:])
            
            try:
                song = Live.Application.get_application().get_document()
                if track_index >= len(song.tracks):
                    return ("error", f"track index {track_index} out of range")
                
                track = song.tracks[track_index]
                browser = Live.Application.get_application().browser
                
                target = self._first_exact_device(browser, device_name)
                if not target:
                    return ("error", f"device '{device_name}' not found")
                
                browser.load_item(target, track)
                return ("ok", device_name)
                
            except Exception as e:
                return ("error", str(e))

        # Register the OSC handlers
        self.osc_server.add_handler("/live/browser/search", browser_search_callback)
        self.osc_server.add_handler("/live/browser/load_device", browser_load_device_callback)

    ###########################################################################
    # Helper methods
    ###########################################################################

    def _search_items(self, browser: Live.Browser.Browser, query: str) -> List[Live.Browser.BrowserItem]:
        """Return all BrowserItems whose .name contains the query (case-insensitive)."""
        return [item for item in browser.search(query) if query.lower() in item.name.lower()]

    def _first_exact_device(self, browser: Live.Browser.Browser, name: str) -> Optional[Live.Browser.BrowserItem]:
        """Return the first device whose .name matches name (case-insensitive)."""
        for item in browser.search(name):
            if item.is_device and item.name.lower() == name.lower():
                return item
        return None