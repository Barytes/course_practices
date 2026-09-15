import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from miniharness.compact import compact_tool_results, total_chars
from miniharness.eval import default_scripted_model, run_eval
from miniharness.guards import GuardError, Guards
from miniharness.loop import run_agent
from miniharness.model import ScriptedModel
from miniharness.plugins import EventLog
from miniharness.ptc import PtcToolbelt, run_code, sdk_stub
from miniharness.tools import Toolbelt, Workspace
from miniharness.types import Message, ToolCall, system, tool_result, user


class ToolsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "a.txt").write_text("hello unique\nhello unique\n", encoding="utf-8")
        (self.tmp / "src").mkdir()
        (self.tmp / "src" / "b.py").write_text("x = 1\n", encoding="utf-8")
        self.belt = Toolbelt(Workspace(self.tmp))

    def _run(self, name, **args):
        return self.belt.run(ToolCall(id="t", name=name, args=args))

    def test_read_numbers_lines(self):
        out = self._run("read", path="a.txt")
        self.assertIn("1| hello unique", out)

    def test_edit_requires_unique(self):
        out = self._run("edit", path="a.txt", old="hello unique", new="hi")
        self.assertIn("appears 2 times", out)

    def test_edit_all(self):
        out = self._run("edit", path="a.txt", old="hello unique", new="hi", all=True)
        self.assertEqual(out, "ok")
        self.assertEqual((self.tmp / "a.txt").read_text(encoding="utf-8").count("hi"), 2)

    def test_path_escape_blocked(self):
        out = self._run("read", path="../secret")
        self.assertTrue(out.startswith("error:"))

    def test_glob_and_grep(self):
        files = self._run("glob", pat="**/*.py")
        self.assertIn("src/b.py", files.replace("\\", "/"))
        hits = self._run("grep", pat="x = 1")
        self.assertIn("src/b.py:1", hits.replace("\\", "/"))


class LoopTests(unittest.TestCase):
    def test_stops_when_no_tools(self):
        tmp = Path(tempfile.mkdtemp())
        model = ScriptedModel(
            [
                {"content": "looking", "tool_calls": [{"name": "glob", "args": {"pat": "*"}}]},
                {"content": "done"},
            ]
        )
        result = run_agent(model, Toolbelt(Workspace(tmp)), [user("what files?")])
        self.assertEqual(result.stop_reason, "completed")
        self.assertEqual(result.messages[-1].content, "done")
        kinds = [e["type"] for e in result.events]
        self.assertIn("tool_end", kinds)
        self.assertEqual(kinds[-1], "agent_end")

    def test_step_limit(self):
        tmp = Path(tempfile.mkdtemp())
        (tmp / "f.txt").write_text("n", encoding="utf-8")
        model = ScriptedModel(
            [{"content": "again", "tool_calls": [{"name": "read", "args": {"path": "f.txt"}}]}] * 5
        )
        result = run_agent(
            model,
            Toolbelt(Workspace(tmp)),
            [user("loop")],
            guards=Guards(max_steps=2, max_repeats=99),
        )
        self.assertEqual(result.stop_reason, "step_limit")

    def test_repeat_fingerprint(self):
        tmp = Path(tempfile.mkdtemp())
        (tmp / "f.txt").write_text("n", encoding="utf-8")
        model = ScriptedModel(
            [{"content": "again", "tool_calls": [{"name": "read", "args": {"path": "f.txt"}}]}] * 5
        )
        result = run_agent(
            model,
            Toolbelt(Workspace(tmp)),
            [user("loop")],
            guards=Guards(max_steps=20, max_repeats=3),
        )
        self.assertEqual(result.stop_reason, "repeat_loop")


class CompactTests(unittest.TestCase):
    def test_clips_old_tool_results(self):
        msgs = [system("s"), user("u")]
        for i in range(6):
            msgs.append(Message(role="assistant", content=f"c{i}", tool_calls=[ToolCall(f"id{i}", "read", {"path": "x"})]))
            msgs.append(tool_result(ToolCall(f"id{i}", "read", {"path": "x"}), "Z" * 800))
        compacted = compact_tool_results(msgs, max_chars=1000, keep_last_tools=2, head=20, tail=20)
        old = [m for m in compacted if m.role == "tool"][0]
        self.assertIn("omitted", old.content)
        self.assertLess(total_chars(compacted), total_chars(msgs))


class PluginTests(unittest.TestCase):
    def test_event_log_and_after_tool(self):
        tmp = Path(tempfile.mkdtemp())
        (tmp / "f.txt").write_text("hello", encoding="utf-8")

        class Clip:
            def before_model(self, messages):
                return messages

            def after_tool(self, call, result):
                return result[:5] + "…"

            def on_event(self, event):
                return None

        log = EventLog()
        model = ScriptedModel(
            [
                {"content": "", "tool_calls": [{"name": "read", "args": {"path": "f.txt"}}]},
                {"content": "ok"},
            ]
        )
        result = run_agent(model, Toolbelt(Workspace(tmp)), [user("r")], plugins=[log, Clip()])
        tool_msgs = [m for m in result.messages if m.role == "tool"]
        self.assertTrue(tool_msgs[0].content.endswith("…"))
        self.assertTrue(any(e["type"] == "tool_end" for e in log.events))


class PtcTests(unittest.TestCase):
    def test_script_composes_two_host_calls(self):
        tmp = Path(tempfile.mkdtemp())
        (tmp / "a.txt").write_text("alpha", encoding="utf-8")
        (tmp / "b.txt").write_text("beta", encoding="utf-8")
        belt = Toolbelt(Workspace(tmp), allow_bash=False)
        out = run_code(
            belt,
            "print(tools.read(path='a.txt'))\nprint(tools.read(path='b.txt'))\n",
        )
        self.assertIn("alpha", out)
        self.assertIn("beta", out)
        self.assertIn("class tools", sdk_stub())

    def test_loop_with_ptc_wrapper(self):
        tmp = Path(tempfile.mkdtemp())
        (tmp / "a.txt").write_text("alpha", encoding="utf-8")
        inner = Toolbelt(Workspace(tmp), allow_bash=False)
        model = ScriptedModel(
            [
                {
                    "content": "one program",
                    "tool_calls": [
                        {
                            "name": "run_code",
                            "args": {"source": "print(tools.read(path='a.txt').strip())"},
                        }
                    ],
                },
                {"content": "got it"},
            ]
        )
        result = run_agent(model, PtcToolbelt(inner), [user("read a")])
        self.assertEqual(result.stop_reason, "completed")
        tool_msgs = [m for m in result.messages if m.role == "tool"]
        self.assertIn("alpha", tool_msgs[0].content)


class EvalTests(unittest.TestCase):
    def test_scripted_fix_passes(self):
        fixture = ROOT / "labs" / "broken_calc"
        result = run_eval(fixture, default_scripted_model())
        self.assertTrue(result.passed, result.grader_output)
        self.assertEqual(result.stop_reason, "completed")


class GuardUnitTests(unittest.TestCase):
    def test_fingerprint_stable(self):
        g = Guards(max_repeats=2)
        call = ToolCall("1", "read", {"path": "a"})
        g.before_tool(call)
        with self.assertRaises(GuardError):
            g.before_tool(call)


if __name__ == "__main__":
    unittest.main()
