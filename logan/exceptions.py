
# ==========================================================
#    EXCEPTIONS
# ==========================================================

class LoganFileNotExistsError       (Exception):                pass
class LoganLoadFileError            (Exception):                pass
class LoganConfigFileNotExistsError (LoganFileNotExistsError):  pass
class LoganLoadConfigError          (LoganLoadFileError):       pass
class LoganPathNotFound             (Exception):                pass
class LoganActionAttrsMissingError  (Exception):                pass
class LoganActionPathMissingError   (Exception):                pass


