class AMSTray:
    def __init__(self, tray_json):
        self._json = tray_json

    def is_empty(self):
        return self.get_type() == None

    def _get(self, key, default = None):
        return self._json[key] if key in self._json else default

    def get_id(self):
        return int(self._get("id", -1))

    def get_type(self):
        return self._get("tray_type")

    def get_color(self):
        return self._get("tray_color")

    def get_info_idx(self):
        return self._get("tray_info_idx")

    def get_nozzle_temps(self):
        return [ int(self._get("nozzle_temp_min", 0)), int(self._get("nozzle_temp_max", 0))]

    def __eq__(self, other):
        return self.get_id() == other.get_id() and self.get_type() == other.get_type() and self.get_color() == other.get_color() and self.get_info_idx() == other.get_info_idx() and self.get_nozzle_temps() == other.get_nozzle_temps()
                
    def __str__(self):
        return "<empty>" if self.is_empty() else f"({self.get_id()}, {self.get_type()}, {self.get_color()}, {self.get_info_idx()}, {self.get_nozzle_temps()})"

