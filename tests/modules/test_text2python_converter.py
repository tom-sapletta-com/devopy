#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testy jednostkowe dla modułu text2python
"""

import os
import sys
import json
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Dodaj ścieżkę do katalogu głównego projektu
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from devopy.converters.text2python import (
    Text2Python,
    convert_text_to_python,
    explain_python_code,
    improve_python_code
)


class TestText2Python(unittest.TestCase):
    """Testy dla klasy Text2Python"""

    def setUp(self):
        """Przygotowanie testów"""
        self.converter = Text2Python(model_name="test-model")
        self.test_prompt = "Napisz funkcję, która oblicza n-ty wyraz ciągu Fibonacciego"
        self.test_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

    @patch('subprocess.Popen')
    def test_ensure_model_available(self, mock_popen):
        """Test sprawdzania dostępności modelu"""
        # Symuluj, że model jest dostępny
        process_mock = MagicMock()
        process_mock.returncode = 0
        process_mock.communicate.return_value = ("test-model", "")
        mock_popen.return_value = process_mock
        
        result = self.converter.ensure_model_available()
        self.assertTrue(result)
        
        # Symuluj, że model nie jest dostępny
        process_mock.returncode = 0
        process_mock.communicate.return_value = ("other-model", "")
        mock_popen.return_value = process_mock
        
        result = self.converter.ensure_model_available()
        self.assertFalse(result)
        
        # Symuluj błąd
        process_mock.returncode = 1
        process_mock.communicate.return_value = ("", "Error")
        mock_popen.return_value = process_mock
        
        result = self.converter.ensure_model_available()
        self.assertFalse(result)

    @patch('subprocess.Popen')
    def test_text_to_python(self, mock_popen):
        """Test konwersji tekstu na kod Python"""
        # Symuluj, że model jest dostępny i generuje kod
        process_mock = MagicMock()
        process_mock.returncode = 0
        process_mock.communicate.return_value = (self.test_code, "")
        mock_popen.return_value = process_mock
        
        # Patch dla ensure_model_available
        with patch.object(self.converter, 'ensure_model_available', return_value=True):
            result = self.converter.text_to_python(self.test_prompt)
            
            # Sprawdź, czy wynik zawiera oczekiwane klucze
            self.assertTrue(result["success"])
            self.assertEqual(result["code"], self.test_code)
            self.assertEqual(result["error"], "")
            
            # Sprawdź, czy subprocess.Popen został wywołany z odpowiednimi argumentami
            mock_popen.assert_called_once()
            args, kwargs = mock_popen.call_args
            self.assertEqual(args[0][1], "run")
            self.assertEqual(args[0][2], "test-model")
        
        # Symuluj, że model nie jest dostępny
        mock_popen.reset_mock()
        with patch.object(self.converter, 'ensure_model_available', return_value=False):
            result = self.converter.text_to_python(self.test_prompt)
            
            # Sprawdź, czy wynik zawiera informację o błędzie
            self.assertFalse(result["success"])
            self.assertEqual(result["code"], "")
            self.assertIn("nie jest dostępny", result["error"])
            
            # Sprawdź, czy subprocess.Popen nie został wywołany
            mock_popen.assert_not_called()
        
        # Symuluj błąd podczas generowania kodu
        mock_popen.reset_mock()
        process_mock.returncode = 1
        process_mock.communicate.return_value = ("", "Error")
        mock_popen.return_value = process_mock
        
        with patch.object(self.converter, 'ensure_model_available', return_value=True):
            result = self.converter.text_to_python(self.test_prompt)
            
            # Sprawdź, czy wynik zawiera informację o błędzie
            self.assertFalse(result["success"])
            self.assertEqual(result["code"], "")
            self.assertEqual(result["error"], "Error")

    @patch('subprocess.Popen')
    def test_explain_code(self, mock_popen):
        """Test wyjaśniania kodu Python"""
        # Symuluj, że model jest dostępny i generuje wyjaśnienie
        process_mock = MagicMock()
        process_mock.returncode = 0
        process_mock.communicate.return_value = ("Wyjaśnienie kodu", "")
        mock_popen.return_value = process_mock
        
        # Patch dla ensure_model_available
        with patch.object(self.converter, 'ensure_model_available', return_value=True):
            result = self.converter.explain_code(self.test_code)
            
            # Sprawdź, czy wynik zawiera wyjaśnienie
            self.assertEqual(result, "Wyjaśnienie kodu")
            
            # Sprawdź, czy subprocess.Popen został wywołany z odpowiednimi argumentami
            mock_popen.assert_called_once()
            args, kwargs = mock_popen.call_args
            self.assertEqual(args[0][1], "run")
            self.assertEqual(args[0][2], "test-model")
        
        # Symuluj, że model nie jest dostępny
        mock_popen.reset_mock()
        with patch.object(self.converter, 'ensure_model_available', return_value=False):
            result = self.converter.explain_code(self.test_code)
            
            # Sprawdź, czy wynik zawiera informację o błędzie
            self.assertIn("nie jest dostępny", result)
            
            # Sprawdź, czy subprocess.Popen nie został wywołany
            mock_popen.assert_not_called()
        
        # Symuluj błąd podczas generowania wyjaśnienia
        mock_popen.reset_mock()
        process_mock.returncode = 1
        process_mock.communicate.return_value = ("", "Error")
        mock_popen.return_value = process_mock
        
        with patch.object(self.converter, 'ensure_model_available', return_value=True):
            result = self.converter.explain_code(self.test_code)
            
            # Sprawdź, czy wynik zawiera informację o błędzie
            self.assertIn("Nie udało się wygenerować wyjaśnienia", result)

    @patch('subprocess.Popen')
    def test_improve_code(self, mock_popen):
        """Test ulepszania kodu Python"""
        improved_code = """
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
"""
        # Symuluj, że model jest dostępny i generuje ulepszony kod
        process_mock = MagicMock()
        process_mock.returncode = 0
        process_mock.communicate.return_value = (improved_code, "")
        mock_popen.return_value = process_mock
        
        # Patch dla ensure_model_available
        with patch.object(self.converter, 'ensure_model_available', return_value=True):
            result = self.converter.improve_code(self.test_code)
            
            # Sprawdź, czy wynik zawiera oczekiwane klucze
            self.assertTrue(result["success"])
            self.assertEqual(result["code"], improved_code)
            self.assertEqual(result["error"], "")
            
            # Sprawdź, czy subprocess.Popen został wywołany z odpowiednimi argumentami
            mock_popen.assert_called_once()
            args, kwargs = mock_popen.call_args
            self.assertEqual(args[0][1], "run")
            self.assertEqual(args[0][2], "test-model")
        
        # Symuluj, że model nie jest dostępny
        mock_popen.reset_mock()
        with patch.object(self.converter, 'ensure_model_available', return_value=False):
            result = self.converter.improve_code(self.test_code)
            
            # Sprawdź, czy wynik zawiera informację o błędzie
            self.assertFalse(result["success"])
            self.assertEqual(result["code"], self.test_code)
            self.assertIn("nie jest dostępny", result["error"])
            
            # Sprawdź, czy subprocess.Popen nie został wywołany
            mock_popen.assert_not_called()


class TestHelperFunctions(unittest.TestCase):
    """Testy dla funkcji pomocniczych"""

    @patch('devopy.converters.text2python.Text2Python.text_to_python')
    def test_convert_text_to_python(self, mock_text_to_python):
        """Test funkcji convert_text_to_python"""
        # Symuluj, że konwersja się powiodła
        mock_text_to_python.return_value = {
            "success": True,
            "code": "def fibonacci(n):\n    return n",
            "error": "",
            "analysis": "OK"
        }
        
        prompt = "Napisz funkcję Fibonacci"
        result = convert_text_to_python(prompt)
        
        # Sprawdź, czy funkcja zwróciła oczekiwany wynik
        self.assertEqual(result, "def fibonacci(n):\n    return n")
        
        # Symuluj, że konwersja się nie powiodła
        mock_text_to_python.return_value = {
            "success": False,
            "code": "",
            "error": "Error",
            "analysis": "Error"
        }
        
        result = convert_text_to_python(prompt)
        
        # Sprawdź, czy funkcja zwróciła informację o błędzie
        self.assertIn("# Błąd konwersji", result)

    @patch('devopy.converters.text2python.Text2Python.explain_code')
    def test_explain_python_code(self, mock_explain_code):
        """Test funkcji explain_python_code"""
        # Symuluj, że wyjaśnienie się powiodło
        mock_explain_code.return_value = "Wyjaśnienie kodu"
        
        code = "def test(): pass"
        result = explain_python_code(code)
        
        # Sprawdź, czy funkcja zwróciła oczekiwany wynik
        self.assertEqual(result, "Wyjaśnienie kodu")

    @patch('devopy.converters.text2python.Text2Python.improve_code')
    def test_improve_python_code(self, mock_improve_code):
        """Test funkcji improve_python_code"""
        # Symuluj, że ulepszenie się powiodło
        mock_improve_code.return_value = {
            "success": True,
            "code": "def improved(): pass",
            "error": "",
            "analysis": "OK"
        }
        
        code = "def test(): pass"
        result = improve_python_code(code)
        
        # Sprawdź, czy funkcja zwróciła oczekiwany wynik
        self.assertEqual(result, "def improved(): pass")
        
        # Symuluj, że ulepszenie się nie powiodło
        mock_improve_code.return_value = {
            "success": False,
            "code": "",
            "error": "Error",
            "analysis": "Error"
        }
        
        result = improve_python_code(code)
        
        # Sprawdź, czy funkcja zwróciła oryginalny kod
        self.assertEqual(result, code)


if __name__ == '__main__':
    unittest.main()
