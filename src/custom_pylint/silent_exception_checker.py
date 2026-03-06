from typing import TYPE_CHECKING

from astroid import nodes
from pylint.checkers import BaseChecker

if TYPE_CHECKING:
    from pylint.lint import PyLinter


class SilentExceptionChecker(BaseChecker):
    name = "silent-exception"
    msgs = {
        "W9006": (
            "Exception without handling, only pass, detected. If checking if your object is a Reference, use Pyomo's built-in is_reference method instead.",
            "silent-exception-handling",
            "Exception blocks should not have a bare pass",
        )
    }

    def visit_tryexcept(self, node) -> None:
        for handler in node.handlers:
            if self._is_silent_exception(handler):
                self.add_message("silent-exception-handling", node=handler)

    def _is_silent_exception(self, handler: nodes.ExceptHandler) -> bool:
        """Check if exception handler only contains 'pass'."""
        if len(handler.body) != 1 or not isinstance(handler.body[0], nodes.Pass):
            return False

        # bare except:
        if not handler.type:
            return True

        # except Exception: / except BaseException:
        if isinstance(handler.type, nodes.Name):
            return handler.type.name in ("Exception", "BaseException")

        # except (ValueError, Exception): — flag if any element is broad
        if isinstance(handler.type, nodes.Tuple):
            return any(
                isinstance(el, nodes.Name) and el.name in ("Exception", "BaseException")
                for el in handler.type.elts
            )

        return False


def register(linter: "PyLinter") -> None:
    """Register the checker."""
    linter.register_checker(SilentExceptionChecker(linter))
