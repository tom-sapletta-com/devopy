import sys
import types
import pytest
from devopy.utils.auto_install import ensure_packages

def test_explicit_package(monkeypatch):
    called = {}
    def fake_import(name, *args, **kwargs):
        called[name] = True
        if name == "fakepkg":
            raise ImportError()
    monkeypatch.setattr("builtins.__import__", fake_import)
    called_subprocess = {}
    def fake_subprocess_call(cmd, **kwargs):
        called_subprocess[tuple(cmd)] = True
        return 0
    monkeypatch.setattr("subprocess.check_call", fake_subprocess_call)
    @ensure_packages(["fakepkg"])
    def func():
        return True
    func()
    assert "fakepkg" in called
    assert (sys.executable, "-m", "pip", "install", "fakepkg") in called_subprocess

def test_auto_detect(monkeypatch):
    # Simulate import detection
    code = """
def func():
    import somepkg
    import anotherpkg.submod
    from thirdpkg import something
    return 42
"""
    import ast, inspect
    from devopy.utils import auto_install
    tree = ast.parse(code)
    pkgs = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                pkgs.add(n.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                pkgs.add(node.module.split('.')[0])
    assert "somepkg" in pkgs
    assert "anotherpkg" in pkgs
    assert "thirdpkg" in pkgs

def test_decorator_runs_function(monkeypatch):
    monkeypatch.setattr("builtins.__import__", lambda name, *a, **k: types.ModuleType(name))
    monkeypatch.setattr("subprocess.check_call", lambda *a, **k: 0)
    @ensure_packages()
    def add(a, b):
        return a + b
    assert add(2, 3) == 5
