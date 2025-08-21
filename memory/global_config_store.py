# # global_config.py
# from threading import RLock
#
# class GlobalConfig:
#     def __init__(self):
#         self._lock = RLock()
#         self._config = {}
#
#     def set(self, new_config):
#         with self._lock:
#             self._config = new_config
#
#     def get(self):
#         with self._lock:
#             return self._config
#
# global_config = GlobalConfig()


from contextvars import ContextVar

# Thread- and async-safe config store
_config_var = ContextVar("config_var", default={})

class GlobalConfig:
    def set(self, new_config: dict):
        _config_var.set(new_config)

    def get(self) -> dict:
        return _config_var.get()

global_config = GlobalConfig()
