"""UI components for codetok."""


class Colors:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class Icons:
    """Unicode icons for categories and log messages."""

    FILE = "📄"
    CODE = "💻"
    DOCS = "📚"
    CONFIG = "⚙️"
    OTHER = "📦"
    FOLDER = "📁"
    SEARCH = "🔍"
    STATS = "📊"
    TOKEN = "🔤"  # nosec
    SIZE = "💾"
    LINES = "📝"
    SUCCESS = "✅"
    WARNING = "⚠️"
    ERROR = "❌"
    INFO = "ℹ️"
    ARROW = "➤"
    BULLET = "•"
    PROGRESS = "⏳"
    SUMMARY = "🎯"
    DETAIL = "🔬"
    CATEGORY = "🏷️"
    CHART = "📈"


class Logger:
    """Enhanced logger with structured output and icons.

    Provides methods for formatted console logging with colors and icons.
    All methods are static for easy use without instantiation.
    """

    @staticmethod
    def header(text: str, icon: str = Icons.STATS) -> None:
        """Print a main header section.

        Args:
            text: Header text.
            icon: Optional icon to display.
        """
        line = "═" * 80
        print(f"\n{Colors.HEADER}{Colors.BOLD}{line}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{icon} {text.upper()}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{line}{Colors.ENDC}")

    @staticmethod
    def section(text: str, icon: str = Icons.CATEGORY) -> None:
        """Print a subsection header.

        Args:
            text: Section text.
            icon: Optional icon to display.
        """
        line = "─" * 60
        print(f"\n{Colors.OKBLUE}{Colors.BOLD}{line}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}{Colors.BOLD}{icon} {text}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}{line}{Colors.ENDC}")

    @staticmethod
    def info(text: str, icon: str = Icons.INFO) -> None:
        """Print an informational message.

        Args:
            text: Message text.
            icon: Optional icon to display.
        """
        print(f"{Colors.OKCYAN}{icon} {text}{Colors.ENDC}")

    @staticmethod
    def success(text: str, icon: str = Icons.SUCCESS) -> None:
        """Print a success message.

        Args:
            text: Message text.
            icon: Optional icon to display.
        """
        print(f"{Colors.OKGREEN}{icon} {text}{Colors.ENDC}")

    @staticmethod
    def warning(text: str, icon: str = Icons.WARNING) -> None:
        """Print a warning message.

        Args:
            text: Message text.
            icon: Optional icon to display.
        """
        print(f"{Colors.WARNING}{icon} {text}{Colors.ENDC}")

    @staticmethod
    def error(text: str, icon: str = Icons.ERROR) -> None:
        """Print an error message.

        Args:
            text: Message text.
            icon: Optional icon to display.
        """
        print(f"{Colors.FAIL}{icon} {text}{Colors.ENDC}")

    @staticmethod
    def stat(label: str, value: str, icon: str = Icons.BULLET) -> None:
        """Print a formatted statistic.

        Args:
            label: Statistic label.
            value: Statistic value.
            icon: Optional icon to display.
        """
        print(
            f"  {Colors.OKCYAN}{icon} {Colors.BOLD}{label}:{Colors.ENDC} "
            f"{Colors.OKGREEN}{value}{Colors.ENDC}"
        )
