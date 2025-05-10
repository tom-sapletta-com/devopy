#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testy jednostkowe dla modułu dependency_manager
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Dodaj ścieżkę do katalogu głównego projektu
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from devopy.utils.dependency_manager import (
    DependencyManager, 
    fix_code_dependencies, 
    install_missing_packages
)


class TestDependencyManager(unittest.TestCase):
    """Testy dla klasy DependencyManager"""

    def setUp(self):
        """Przygotowanie testów"""
        self.manager = DependencyManager()
        self.test_code_with_imports = """
import os
import sys
import numpy as np

def analyze_data(data):
    return np.mean(data)
"""
        self.test_code_without_imports = """
def analyze_data(data):
    return np.mean(data)
"""
        self.test_code_with_local_vars = """
x = 10
y = 20
result = x + y
print(result.format())
"""

    def test_analyze_code(self):
        """Test analizy kodu i wykrywania używanych modułów"""
        # Test z kodem zawierającym importy
        modules = self.manager.analyze_code(self.test_code_with_imports)
        self.assertIn("numpy", modules)
        self.assertIn("os", modules)
        self.assertIn("sys", modules)
        
        # Test z kodem bez importów
        modules = self.manager.analyze_code(self.test_code_without_imports)
        self.assertIn("numpy", modules)
        
        # Test z kodem zawierającym zmienne lokalne
        modules = self.manager.analyze_code(self.test_code_with_local_vars)
        self.assertNotIn("x", modules)
        self.assertNotIn("y", modules)
        self.assertNotIn("result", modules)

    def test_generate_imports(self):
        """Test generowania kodu importów"""
        modules = {"numpy", "pandas", "matplotlib"}
        imports = self.manager.generate_imports(modules)
        
        self.assertIn("import numpy", imports)
        self.assertIn("import pandas", imports)
        self.assertIn("import matplotlib", imports)
        
        # Sprawdź, czy importy są posortowane
        lines = imports.split("\n")
        self.assertEqual(sorted(lines), lines)

    def test_fix_missing_imports(self):
        """Test naprawiania brakujących importów"""
        # Test z kodem bez importów
        fixed_code = self.manager.fix_missing_imports(self.test_code_without_imports)
        self.assertIn("import numpy", fixed_code)
        
        # Test z kodem zawierającym już importy
        fixed_code = self.manager.fix_missing_imports(self.test_code_with_imports)
        self.assertEqual(fixed_code, self.test_code_with_imports)
        
        # Test z docstring i komentarzami
        code_with_docstring = '"""Test docstring."""\n# Komentarz\n' + self.test_code_without_imports
        fixed_code = self.manager.fix_missing_imports(code_with_docstring)
        self.assertIn('"""Test docstring."""', fixed_code)
        self.assertIn("# Komentarz", fixed_code)
        self.assertIn("import numpy", fixed_code)

    @patch('subprocess.check_call')
    @patch('importlib.import_module')
    def test_install_missing_packages(self, mock_import, mock_subprocess):
        """Test instalacji brakujących pakietów"""
        # Symuluj, że moduł nie jest zainstalowany
        mock_import.side_effect = ImportError("No module named 'missing_module'")
        
        # Test instalacji brakującego modułu
        modules = {"missing_module"}
        installed = self.manager.install_missing_packages(modules)
        
        # Sprawdź, czy próbowano zainstalować moduł
        mock_subprocess.assert_called_once()
        self.assertIn("missing_module", installed)
        
        # Test z modułem standardowym
        mock_import.reset_mock()
        mock_subprocess.reset_mock()
        modules = {"os"}  # Moduł standardowy
        installed = self.manager.install_missing_packages(modules)
        
        # Nie powinno być próby instalacji modułu standardowego
        mock_subprocess.assert_not_called()
        self.assertEqual(installed, [])
        
        # Test z modułem już zainstalowanym
        mock_import.reset_mock()
        mock_import.side_effect = None  # Moduł jest zainstalowany
        mock_subprocess.reset_mock()
        modules = {"installed_module"}
        installed = self.manager.install_missing_packages(modules)
        
        # Nie powinno być próby instalacji już zainstalowanego modułu
        mock_subprocess.assert_not_called()
        self.assertEqual(installed, [])


class TestHelperFunctions(unittest.TestCase):
    """Testy dla funkcji pomocniczych"""

    def test_fix_code_dependencies(self):
        """Test funkcji fix_code_dependencies"""
        code = """
def analyze_data(data):
    return np.mean(data)
"""
        fixed_code = fix_code_dependencies(code)
        self.assertIn("import numpy", fixed_code)

    @patch('devopy.utils.dependency_manager.DependencyManager.install_missing_packages')
    @patch('devopy.utils.dependency_manager.DependencyManager.analyze_code')
    def test_install_missing_packages(self, mock_analyze, mock_install):
        """Test funkcji install_missing_packages"""
        # Symuluj, że analiza kodu zwraca zbiór modułów
        mock_analyze.return_value = {"numpy", "pandas"}
        
        # Symuluj, że instalacja pakietów zwraca listę zainstalowanych modułów
        mock_install.return_value = ["numpy", "pandas"]
        
        code = """
import numpy as np
import pandas as pd

def analyze_data(data):
    return np.mean(data), pd.DataFrame(data)
"""
        installed = install_missing_packages(code)
        
        # Sprawdź, czy funkcje zostały wywołane z odpowiednimi argumentami
        mock_analyze.assert_called_once_with(code)
        mock_install.assert_called_once_with({"numpy", "pandas"}, None)
        
        # Sprawdź, czy funkcja zwróciła oczekiwany wynik
        self.assertEqual(installed, ["numpy", "pandas"])


if __name__ == '__main__':
    unittest.main()
