import astroid
import pytest
import pylint.testutils
from custom_pylint.silent_exception_checker import SilentExceptionChecker


class TestSilentExceptionChecker(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = SilentExceptionChecker

    # ------------------------------------------------------------------
    # POSITIVE tests — checker SHOULD emit a message
    # ------------------------------------------------------------------

    def test_bare_except_with_pass_is_flagged(self):
        """bare except: pass must be flagged."""
        code = astroid.parse("""
        try:
            x = 1
        except:
            pass
        """)
        try_node = code.body[0]
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(
                msg_id="silent-exception-handling",
                node=try_node.handlers[0],
            ),
            ignore_position=True,
        ):
            self.checker.visit_tryexcept(try_node)

    def test_except_exception_with_pass_is_flagged(self):
        """except Exception: pass must be flagged."""
        code = astroid.parse("""
        try:
            x = 1
        except Exception:
            pass
        """)
        try_node = code.body[0]
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(
                msg_id="silent-exception-handling",
                node=try_node.handlers[0],
            ),
            ignore_position=True,
        ):
            self.checker.visit_tryexcept(try_node)

    def test_except_base_exception_with_pass_is_flagged(self):
        """except BaseException: pass must be flagged."""
        code = astroid.parse("""
        try:
            x = 1
        except BaseException:
            pass
        """)
        try_node = code.body[0]
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(
                msg_id="silent-exception-handling",
                node=try_node.handlers[0],
            ),
            ignore_position=True,
        ):
            self.checker.visit_tryexcept(try_node)

    def test_except_exception_with_alias_and_pass_is_flagged(self):
        """except Exception as e: pass must also be flagged."""
        code = astroid.parse("""
        try:
            x = 1
        except Exception as e:
            pass
        """)
        try_node = code.body[0]
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(
                msg_id="silent-exception-handling",
                node=try_node.handlers[0],
            ),
            ignore_position=True,
        ):
            self.checker.visit_tryexcept(try_node)

    def test_multiple_handlers_only_silent_flagged(self):
        """Only the broad silent handler should be flagged, not the specific one."""
        code = astroid.parse("""
        try:
            x = 1
        except ValueError:
            print("ok")
        except Exception:
            pass
        """)
        try_node = code.body[0]
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(
                msg_id="silent-exception-handling",
                node=try_node.handlers[1],
            ),
            ignore_position=True,
        ):
            self.checker.visit_tryexcept(try_node)

    def test_except_tuple_including_exception_with_pass_is_flagged(self):
        """except (ValueError, Exception): pass — broad catch hidden in a tuple."""
        code = astroid.parse("""
        try:
            x = 1
        except (ValueError, Exception):
            pass
        """)
        try_node = code.body[0]
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(
                msg_id="silent-exception-handling",
                node=try_node.handlers[0],
            ),
            ignore_position=True,
        ):
            self.checker.visit_tryexcept(try_node)

    # ------------------------------------------------------------------
    # NEGATIVE tests — checker should NOT emit any message
    # ------------------------------------------------------------------

    def test_except_exception_with_logging_not_flagged(self):
        """except Exception with a log call is not silent — no message."""
        code = astroid.parse("""
        try:
            x = 1
        except Exception:
            print("error")
        """)
        try_node = code.body[0]
        with self.assertNoMessages():
            self.checker.visit_tryexcept(try_node)

    def test_except_exception_with_raise_not_flagged(self):
        """except Exception: raise is fine — not a silent swallow."""
        code = astroid.parse("""
        try:
            x = 1
        except Exception:
            raise
        """)
        try_node = code.body[0]
        with self.assertNoMessages():
            self.checker.visit_tryexcept(try_node)

    def test_except_specific_exception_with_pass_not_flagged(self):
        """except ValueError: pass should NOT be flagged."""
        code = astroid.parse("""
        try:
            x = 1
        except ValueError:
            pass
        """)
        try_node = code.body[0]
        with self.assertNoMessages():
            self.checker.visit_tryexcept(try_node)

    def test_except_exception_with_multiple_statements_not_flagged(self):
        """More than one statement in the body — not flagged."""
        code = astroid.parse("""
        try:
            x = 1
        except Exception:
            pass
            print("done")
        """)
        try_node = code.body[0]
        with self.assertNoMessages():
            self.checker.visit_tryexcept(try_node)

    def test_bare_except_with_non_pass_body_not_flagged(self):
        """Bare except with a real body — not flagged."""
        code = astroid.parse("""
        try:
            x = 1
        except:
            x = 0
        """)
        try_node = code.body[0]
        with self.assertNoMessages():
            self.checker.visit_tryexcept(try_node)

    def test_except_tuple_without_broad_exception_not_flagged(self):
        """except (ValueError, TypeError): pass — no broad exception, not flagged."""
        code = astroid.parse("""
        try:
            x = 1
        except (ValueError, TypeError):
            pass
        """)
        try_node = code.body[0]
        with self.assertNoMessages():
            self.checker.visit_tryexcept(try_node)

    def test_no_tryexcept(self):
        """No try/except at all — not flagged."""
        code = astroid.parse("""
        x = 1
        """)
        with self.assertNoMessages():
            for node in code.body:
                assert not hasattr(node, "handlers")
