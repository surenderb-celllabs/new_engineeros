# import logging

# TRACE_LEVEL_NUM = 5  # below DEBUG (10)
# logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")

# def trace(self, message, *args, **kwargs):
#     if self.isEnabledFor(TRACE_LEVEL_NUM):
#         self._log(TRACE_LEVEL_NUM, message, args, **kwargs)

# logging.TRACE = TRACE_LEVEL_NUM
# logging.Logger.trace = trace

# SUCCESS_LEVEL_NUM = 25  # between WARNING (30) and INFO (20)
# logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")

# def success(self, message, *args, **kwargs):
#     if self.isEnabledFor(SUCCESS_LEVEL_NUM):
#         self._log(SUCCESS_LEVEL_NUM, message, args, **kwargs)

# logging.SUCCESS = SUCCESS_LEVEL_NUM
# logging.Logger.success = success

# NOTICE_LEVEL_NUM = 35  # above WARNING (30)
# logging.addLevelName(NOTICE_LEVEL_NUM, "NOTICE")

# def notice(self, message, *args, **kwargs):
#     if self.isEnabledFor(NOTICE_LEVEL_NUM):
#         self._log(NOTICE_LEVEL_NUM, message, args, **kwargs)

# logging.NOTICE = NOTICE_LEVEL_NUM
# logging.Logger.notice = notice


# class ColoredFormatter(logging.Formatter):
#     """
#     A custom formatter for log messages that adds color based on the log level.
#     """

#     BRIGHT_DARK_GREY = "\x1b[90m" # This is often displayed as a distinct dark grey
#     BLUE = "\x1b[96m"             # Bright Blue
#     YELLOW = "\x1b[93m"            # Bright Yellow
#     RED = "\x1b[91m"               # Bright Red
#     BOLD_RED = "\x1b[31;1m"        # Still bold red, using standard red with bold attribute
#     GREEN = "\x1b[92m"             # Bright Green
#     MAGENTA = "\x1b[95m"           # Bright Magenta
#     CYAN = "\x1b[94m"              # Bright Cyan
#     PURPLE = "\x1b[35m"            # Purple
#     RESET = "\x1b[0m"              # Resets all formatting attributes

#     FORMATS = {
#         logging.TRACE: CYAN + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + RESET,
#         logging.DEBUG: BRIGHT_DARK_GREY + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + RESET,
#         logging.INFO: BLUE + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + RESET,
#         logging.WARNING: YELLOW + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + RESET,
#         logging.ERROR: RED + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + RESET,
#         logging.CRITICAL: BOLD_RED + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + RESET,
#         logging.SUCCESS: GREEN + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + RESET,
#         logging.NOTICE: MAGENTA + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + RESET,
#     }

#     def format(self, record):
#         log_fmt = self.FORMATS.get(record.levelno, self.BRIGHT_DARK_GREY + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + self.RESET)
#         formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
#         return formatter.format(record)

# class ColoredLogger(logging.Logger):
#     """
#     A custom logger class that uses ColoredFormatter to output colored log messages.
#     """
#     def __init__(self, name, level=logging.NOTSET): # Default to NOTSET to allow handler to control
#         super().__init__(name, level)
#         if not self.handlers:
#             ch = logging.StreamHandler()
#             ch.setFormatter(ColoredFormatter())
#             self.addHandler(ch)




import logging
import sys


# ======================================================================
# Custom Log Levels
# ======================================================================

TRACE_LEVEL = 5
SUCCESS_LEVEL = 25
NOTICE_LEVEL = 35

logging.addLevelName(TRACE_LEVEL, "TRACE")
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")
logging.addLevelName(NOTICE_LEVEL, "NOTICE")

logging.TRACE = TRACE_LEVEL
logging.SUCCESS = SUCCESS_LEVEL
logging.NOTICE = NOTICE_LEVEL


def trace(self, message, *args, **kwargs):
    if self.isEnabledFor(TRACE_LEVEL):
        self._log(TRACE_LEVEL, message, args, **kwargs)


def success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL):
        self._log(SUCCESS_LEVEL, message, args, **kwargs)


def notice(self, message, *args, **kwargs):
    if self.isEnabledFor(NOTICE_LEVEL):
        self._log(NOTICE_LEVEL, message, args, **kwargs)


logging.Logger.trace = trace
logging.Logger.success = success
logging.Logger.notice = notice


# ======================================================================
# Color Themes
# ======================================================================



THEMES = {
    # ============================================================
    # 5 Original Themes
    # ============================================================

    "NEON_CYBERPUNK": {
        "TRACE":     "\033[38;5;87m",
        "DEBUG":     "\033[38;5;39m",
        "INFO":      "\033[38;5;51m",
        "SUCCESS":   "\033[38;5;82m",
        "NOTICE":    "\033[38;5;207m",
        "WARNING":   "\033[38;5;226m",
        "ERROR":     "\033[38;5;196m",
        "CRITICAL":  "\033[1;38;5;201m",
    },

    "PASTEL_BREEZE": {
        "TRACE":     "\033[38;5;153m",
        "DEBUG":     "\033[38;5;110m",
        "INFO":      "\033[38;5;116m",
        "SUCCESS":   "\033[38;5;120m",
        "NOTICE":    "\033[38;5;182m",
        "WARNING":   "\033[38;5;222m",
        "ERROR":     "\033[38;5;210m",
        "CRITICAL":  "\033[1;38;5;199m",
    },

    "MATRIX_GREEN": {
        "TRACE":     "\033[38;5;28m",
        "DEBUG":     "\033[38;5;34m",
        "INFO":      "\033[38;5;40m",
        "SUCCESS":   "\033[1;38;5;46m",
        "NOTICE":    "\033[38;5;82m",
        "WARNING":   "\033[38;5;118m",
        "ERROR":     "\033[38;5;154m",
        "CRITICAL":  "\033[1;38;5;190m",
    },

    "FIRESTORM": {
        "TRACE":     "\033[38;5;208m",
        "DEBUG":     "\033[38;5;172m",
        "INFO":      "\033[38;5;214m",
        "SUCCESS":   "\033[38;5;190m",
        "NOTICE":    "\033[38;5;220m",
        "WARNING":   "\033[1;38;5;226m",
        "ERROR":     "\033[38;5;196m",
        "CRITICAL":  "\033[1;38;5;160m",
    },

    "MONOCHROME_PRO": {
        "TRACE":     "\033[38;5;240m",
        "DEBUG":     "\033[38;5;245m",
        "INFO":      "\033[38;5;250m",
        "SUCCESS":   "\033[38;5;47m",
        "NOTICE":    "\033[38;5;252m",
        "WARNING":   "\033[38;5;11m",
        "ERROR":     "\033[38;5;196m",
        "CRITICAL":  "\033[1;38;5;15m",
    },

    # ============================================================
    # 10 New Themes
    # ============================================================

    "VAPORWAVE_SUNSET": {
        "TRACE":    "\033[38;5;123m",
        "DEBUG":    "\033[38;5;99m",
        "INFO":     "\033[38;5;45m",
        "SUCCESS":  "\033[38;5;213m",
        "NOTICE":   "\033[38;5;177m",
        "WARNING":  "\033[38;5;219m",
        "ERROR":    "\033[38;5;198m",
        "CRITICAL": "\033[1;38;5;201m",
    },

    "MIDNIGHT_PURPLE": {
        "TRACE":    "\033[38;5;60m",
        "DEBUG":    "\033[38;5;61m",
        "INFO":     "\033[38;5;99m",
        "SUCCESS":  "\033[38;5;171m",
        "NOTICE":   "\033[38;5;141m",
        "WARNING":  "\033[38;5;105m",
        "ERROR":    "\033[38;5;165m",
        "CRITICAL": "\033[1;38;5;207m",
    },

    "OCEAN_DEEP": {
        "TRACE":    "\033[38;5;31m",
        "DEBUG":    "\033[38;5;25m",
        "INFO":     "\033[38;5;33m",
        "SUCCESS":  "\033[38;5;37m",
        "NOTICE":   "\033[38;5;38m",
        "WARNING":  "\033[38;5;81m",
        "ERROR":    "\033[38;5;75m",
        "CRITICAL": "\033[1;38;5;87m",
    },

    "FOREST_EARTH": {
        "TRACE":    "\033[38;5;58m",   # Bark
        "DEBUG":    "\033[38;5;64m",   # Moss
        "INFO":     "\033[38;5;71m",   # Forest green
        "SUCCESS":  "\033[38;5;106m",  # Bright leaf
        "NOTICE":   "\033[38;5;143m",  # Soft leaf
        "WARNING":  "\033[38;5;179m",  # Soil yellow
        "ERROR":    "\033[38;5;130m",  # Clay red
        "CRITICAL": "\033[1;38;5;166m",# Fire ember
    },

    "ICE_NORDIC": {
        "TRACE":    "\033[38;5;117m",
        "DEBUG":    "\033[38;5;110m",
        "INFO":     "\033[38;5;159m",
        "SUCCESS":  "\033[38;5;195m",
        "NOTICE":   "\033[38;5;189m",
        "WARNING":  "\033[38;5;153m",
        "ERROR":    "\033[38;5;111m",
        "CRITICAL": "\033[1;38;5;195m",
    },

    "GOLDEN_BLACK": {
        "TRACE":    "\033[38;5;238m", # dim grey
        "DEBUG":    "\033[38;5;240m",
        "INFO":     "\033[38;5;244m",
        "SUCCESS":  "\033[38;5;178m", # soft gold
        "NOTICE":   "\033[38;5;220m", # brighter gold
        "WARNING":  "\033[1;38;5;226m",# neon gold
        "ERROR":    "\033[38;5;178m",
        "CRITICAL": "\033[1;38;5;220m",
    },

    "SUNRISE": {
        "TRACE":    "\033[38;5;224m", # morning pink
        "DEBUG":    "\033[38;5;186m",
        "INFO":     "\033[38;5;222m",
        "SUCCESS":  "\033[38;5;229m",
        "NOTICE":   "\033[38;5;227m",
        "WARNING":  "\033[38;5;214m",
        "ERROR":    "\033[38;5;203m",
        "CRITICAL": "\033[1;38;5;197m",
    },

    "AURORA_BOREALIS": {
        "TRACE":    "\033[38;5;121m",
        "DEBUG":    "\033[38;5;50m",
        "INFO":     "\033[38;5;87m",
        "SUCCESS":  "\033[38;5;46m",
        "NOTICE":   "\033[38;5;120m",
        "WARNING":  "\033[38;5;154m",
        "ERROR":    "\033[38;5;203m",
        "CRITICAL": "\033[1;38;5;197m",
    },

    "LAVA_INFERNO": {
        "TRACE":    "\033[38;5;202m",
        "DEBUG":    "\033[38;5;166m",
        "INFO":     "\033[38;5;208m",
        "SUCCESS":  "\033[38;5;214m",
        "NOTICE":   "\033[38;5;172m",
        "WARNING":  "\033[1;38;5;220m",
        "ERROR":    "\033[38;5;196m",
        "CRITICAL": "\033[1;38;5;160m",
    },

    "RETRO_TERMINAL": {
        "TRACE":    "\033[38;5;64m",
        "DEBUG":    "\033[38;5;70m",
        "INFO":     "\033[38;5;76m",
        "SUCCESS":  "\033[1;38;5;82m",
        "NOTICE":   "\033[38;5;190m",
        "WARNING":  "\033[38;5;226m",
        "ERROR":    "\033[38;5;196m",
        "CRITICAL": "\033[1;38;5;196m",
    },

    "GRAY_GREEN_YELLOW_RED": {
        # --------------------
        # GRAYS (low-severity)
        # --------------------
        "TRACE":    "\033[38;5;245m",   # Light gray
        "DEBUG":    "\033[38;5;250m",   # Brighter gray
        "INFO":     "\033[38;5;252m",   # Very light gray

        # --------------------
        # GREEN (positive)
        # --------------------
        "SUCCESS":  "\033[1;38;5;82m",  # Bright neon green

        # --------------------
        # YELLOW (attention)
        # --------------------
        "NOTICE":   "\033[1;38;5;226m", # Bright yellow
        "WARNING":  "\033[38;5;220m",   # Light golden yellow

        # --------------------
        # RED (errors)
        # --------------------
        "ERROR":    "\033[38;5;196m",   # Bright red
        "CRITICAL": "\033[1;38;5;197m", # Light bold hot red
    }

}


RESET = "\033[0m"


# ======================================================================
# Colored Formatter (theme-aware)
# ======================================================================

class ColoredFormatter(logging.Formatter):
    BASE = "%(asctime)s - %(name)s - %(levelname)s - %(lineno)s - %(message)s"
    DATEFMT = "%Y-%m-%d %H:%M:%S"

    # Active theme name
    active_theme = "NEON_CYBERPUNK"

    @classmethod
    def set_theme(cls, theme_name: str):
        if theme_name not in THEMES:
            raise ValueError(f"Unknown theme '{theme_name}'. Available: {list(THEMES.keys())}")
        cls.active_theme = theme_name

    def format(self, record):
        theme = THEMES[self.active_theme]

        # Pick color based on level
        if record.levelno == TRACE_LEVEL:
            color = theme["TRACE"]
        elif record.levelno == logging.DEBUG:
            color = theme["DEBUG"]
        elif record.levelno == logging.INFO:
            color = theme["INFO"]
        elif record.levelno == SUCCESS_LEVEL:
            color = theme["SUCCESS"]
        elif record.levelno == NOTICE_LEVEL:
            color = theme["NOTICE"]
        elif record.levelno == logging.WARNING:
            color = theme["WARNING"]
        elif record.levelno == logging.ERROR:
            color = theme["ERROR"]
        elif record.levelno == logging.CRITICAL:
            color = theme["CRITICAL"]
        else:
            color = RESET

        fmt = color + self.BASE + RESET
        formatter = logging.Formatter(fmt, datefmt=self.DATEFMT)
        return formatter.format(record)


# ======================================================================
# Custom Logger Class
# ======================================================================

class ColoredLogger(logging.Logger):

    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)

        if not self.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(ColoredFormatter())
            self.addHandler(handler)


logging.setLoggerClass(ColoredLogger)


# ======================================================================
# Public API: get_logger() and set_theme()
# ======================================================================

def get_logger(name="ColoredLogger", level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger


def set_theme(theme_name: str):
    """
    Changes theme at runtime for ALL loggers.
    """
    ColoredFormatter.set_theme(theme_name)


# ======================================================================
# Demo (only runs when executed directly)
# ======================================================================

if __name__ == "__main__":
    log = get_logger("Demo")

    for theme in THEMES.keys():
        print("\n\n==============================================")
        print(f"   THEME: {theme}")
        print("==============================================\n")
        set_theme(theme)

        log.trace("Trace message")
        log.debug("Debug message")
        log.info("Info message")
        log.success("Success message")
        log.notice("Notice message")
        log.warning("Warning message")
        log.error("Error message")
        log.critical("Critical message")





