#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testy jednostkowe dla modułu docker_sandbox
"""

import os
import sys
import json
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Dodaj ścieżkę do katalogu głównego projektu
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from devopy.sandbox.docker_sandbox import (
    DockerSandbox,
    run_code_in_sandbox,
    run_service_in_sandbox,
    stop_sandbox_service,
    check_docker_available
)


class TestDockerSandbox(unittest.TestCase):
    """Testy dla klasy DockerSandbox"""

    def setUp(self):
        """Przygotowanie testów"""
        # Użyj katalogu tymczasowego dla testów
        self.base_dir = Path(os.path.dirname(__file__)).parent / "test_data" / "sandbox"
        os.makedirs(self.base_dir, exist_ok=True)
        
        # Utwórz instancję DockerSandbox z zamockowanymi metodami
        with patch('devopy.sandbox.docker_sandbox.subprocess.run'), \
             patch('devopy.sandbox.docker_sandbox.subprocess.Popen'):
            self.sandbox = DockerSandbox(
                base_dir=self.base_dir,
                docker_image="python:3.9-slim",
                timeout=10
            )
        
        self.test_code = """
print("Hello from Docker Sandbox!")
"""
        self.test_service_code = """
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Docker Service!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
"""

    def test_initialization(self):
        """Test inicjalizacji DockerSandbox"""
        self.assertIsNotNone(self.sandbox)
        self.assertEqual(self.sandbox.docker_image, "python:3.9-slim")
        self.assertEqual(self.sandbox.timeout, 10)
        self.assertTrue(self.sandbox.base_dir.exists())
        self.assertIsNotNone(self.sandbox.sandbox_id)
        self.assertTrue(self.sandbox.sandbox_dir.exists())

    def test_prepare_code(self):
        """Test przygotowania kodu do wykonania"""
        with patch('devopy.sandbox.docker_sandbox.fix_code_dependencies', return_value=self.test_code):
            code_file = self.sandbox.prepare_code(self.test_code)
            
            # Sprawdź, czy plik został utworzony
            self.assertTrue(code_file.exists())
            
            # Sprawdź, czy plik zawiera kod
            with open(code_file, 'r') as f:
                content = f.read()
                self.assertIn("# Kod użytkownika", content)
                self.assertIn("print(\"Hello from Docker Sandbox!\")", content)

    @patch('devopy.sandbox.docker_sandbox.check_docker_available')
    @patch('devopy.sandbox.docker_sandbox.subprocess.Popen')
    def test_run(self, mock_popen, mock_check_docker):
        """Test uruchamiania kodu w piaskownicy"""
        # Symuluj, że Docker jest dostępny
        mock_check_docker.return_value = (True, "Docker jest dostępny")
        
        # Symuluj, że kod został wykonany pomyślnie
        process_mock = MagicMock()
        process_mock.returncode = 0
        process_mock.communicate.return_value = (
            json.dumps({
                "success": True,
                "output": "Hello from Docker Sandbox!",
                "error": "",
                "execution_time": 0.1
            }),
            ""
        )
        mock_popen.return_value = process_mock
        
        # Patch dla prepare_code
        with patch.object(self.sandbox, 'prepare_code') as mock_prepare:
            mock_prepare.return_value = self.base_dir / "user_code.py"
            
            # Uruchom kod
            result = self.sandbox.run(self.test_code)
            
            # Sprawdź, czy wynik zawiera oczekiwane klucze
            self.assertTrue(result["success"])
            self.assertEqual(result["output"], "Hello from Docker Sandbox!")
            self.assertEqual(result["error"], "")
            
            # Sprawdź, czy subprocess.Popen został wywołany z odpowiednimi argumentami
            mock_popen.assert_called_once()
            args, kwargs = mock_popen.call_args
            self.assertIn("docker", args[0])
            self.assertIn("run", args[0])
        
        # Symuluj, że Docker nie jest dostępny
        mock_check_docker.return_value = (False, "Docker nie jest dostępny")
        
        # Uruchom kod
        result = self.sandbox.run(self.test_code)
        
        # Sprawdź, czy wynik zawiera informację o błędzie
        self.assertFalse(result["success"])
        self.assertEqual(result["output"], "")
        self.assertIn("Docker nie jest dostępny", result["error"])
        
        # Symuluj, że kod zakończył się z błędem
        mock_check_docker.return_value = (True, "Docker jest dostępny")
        process_mock.returncode = 1
        process_mock.communicate.return_value = ("", "Error")
        
        # Patch dla prepare_code
        with patch.object(self.sandbox, 'prepare_code') as mock_prepare:
            mock_prepare.return_value = self.base_dir / "user_code.py"
            
            # Uruchom kod
            result = self.sandbox.run(self.test_code)
            
            # Sprawdź, czy wynik zawiera informację o błędzie
            self.assertFalse(result["success"])
            self.assertEqual(result["output"], "")
            self.assertEqual(result["error"], "Error")

    @patch('devopy.sandbox.docker_sandbox.check_docker_available')
    @patch('devopy.sandbox.docker_sandbox.subprocess.run')
    @patch('devopy.sandbox.docker_sandbox.time.sleep')
    def test_run_service(self, mock_sleep, mock_run, mock_check_docker):
        """Test uruchamiania usługi w piaskownicy"""
        # Symuluj, że Docker jest dostępny
        mock_check_docker.return_value = (True, "Docker jest dostępny")
        
        # Symuluj, że usługa została uruchomiona pomyślnie
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="container-id"),  # docker run
            MagicMock(returncode=0, stdout="container-id"),  # docker ps
        ]
        
        # Patch dla prepare_code
        with patch.object(self.sandbox, 'prepare_code') as mock_prepare:
            mock_prepare.return_value = self.base_dir / "service.py"
            
            # Uruchom usługę
            result = self.sandbox.run_service(self.test_service_code, port=8000)
            
            # Sprawdź, czy wynik zawiera oczekiwane klucze
            self.assertTrue(result["success"])
            self.assertEqual(result["container_id"], "container-id")
            self.assertEqual(result["port"], 8000)
            self.assertEqual(result["url"], "http://localhost:8000")
            
            # Sprawdź, czy subprocess.run został wywołany z odpowiednimi argumentami
            self.assertEqual(mock_run.call_count, 2)
            args, kwargs = mock_run.call_args_list[0]
            self.assertIn("docker", args[0])
            self.assertIn("run", args[0])
        
        # Symuluj, że Docker nie jest dostępny
        mock_check_docker.return_value = (False, "Docker nie jest dostępny")
        
        # Uruchom usługę
        result = self.sandbox.run_service(self.test_service_code)
        
        # Sprawdź, czy wynik zawiera informację o błędzie
        self.assertFalse(result["success"])
        self.assertEqual(result["container_name"], "")
        self.assertIn("Docker nie jest dostępny", result["error"])
        
        # Symuluj, że usługa nie uruchomiła się poprawnie
        mock_check_docker.return_value = (True, "Docker jest dostępny")
        mock_run.reset_mock()
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="container-id"),  # docker run
            MagicMock(returncode=0, stdout=""),  # docker ps (pusty wynik)
            MagicMock(returncode=0, stdout="logs", stderr="error"),  # docker logs
        ]
        
        # Patch dla prepare_code
        with patch.object(self.sandbox, 'prepare_code') as mock_prepare:
            mock_prepare.return_value = self.base_dir / "service.py"
            
            # Uruchom usługę
            result = self.sandbox.run_service(self.test_service_code)
            
            # Sprawdź, czy wynik zawiera informację o błędzie
            self.assertFalse(result["success"])
            self.assertIn("Usługa nie uruchomiła się poprawnie", result["error"])
            self.assertIn("logs", result["logs"])

    @patch('devopy.sandbox.docker_sandbox.subprocess.run')
    def test_stop_service(self, mock_run):
        """Test zatrzymywania usługi"""
        # Symuluj, że usługa została zatrzymana pomyślnie
        mock_run.return_value = MagicMock(returncode=0)
        
        # Zatrzymaj usługę
        result = self.sandbox.stop_service("test-container")
        
        # Sprawdź, czy wynik zawiera oczekiwane klucze
        self.assertTrue(result["success"])
        self.assertEqual(result["container_name"], "test-container")
        
        # Sprawdź, czy subprocess.run został wywołany z odpowiednimi argumentami
        mock_run.assert_called()
        args, kwargs = mock_run.call_args_list[0]
        self.assertIn("docker", args[0])
        self.assertIn("stop", args[0])
        self.assertIn("test-container", args[0])
        
        # Symuluj, że zatrzymanie usługi nie powiodło się
        mock_run.reset_mock()
        mock_run.return_value = MagicMock(returncode=1, stderr="Error")
        
        # Zatrzymaj usługę
        result = self.sandbox.stop_service("test-container")
        
        # Sprawdź, czy wynik zawiera informację o błędzie
        self.assertFalse(result["success"])
        self.assertEqual(result["container_name"], "test-container")
        self.assertEqual(result["error"], "Error")

    @patch('devopy.sandbox.docker_sandbox.subprocess.run')
    @patch('devopy.sandbox.docker_sandbox.shutil.rmtree')
    def test_cleanup(self, mock_rmtree, mock_run):
        """Test czyszczenia zasobów piaskownicy"""
        # Symuluj, że czyszczenie powiodło się
        mock_run.return_value = MagicMock(returncode=0)
        
        # Ustaw ID kontenera
        self.sandbox.container_id = "test-container"
        
        # Wyczyść zasoby
        result = self.sandbox.cleanup()
        
        # Sprawdź, czy wynik zawiera oczekiwane klucze
        self.assertTrue(result["success"])
        self.assertIn("Wyczyszczono piaskownicę", result["message"])
        
        # Sprawdź, czy subprocess.run został wywołany z odpowiednimi argumentami
        mock_run.assert_called()
        args, kwargs = mock_run.call_args_list[0]
        self.assertIn("docker", args[0])
        self.assertIn("stop", args[0])
        self.assertIn("test-container", args[0])
        
        # Sprawdź, czy katalog piaskownicy został usunięty
        mock_rmtree.assert_called_once_with(self.sandbox.sandbox_dir, ignore_errors=True)


class TestHelperFunctions(unittest.TestCase):
    """Testy dla funkcji pomocniczych"""

    @patch('devopy.sandbox.docker_sandbox.subprocess.run')
    def test_check_docker_available(self, mock_run):
        """Test funkcji check_docker_available"""
        # Symuluj, że Docker jest dostępny
        mock_run.return_value = MagicMock(returncode=0)
        
        available, message = check_docker_available()
        
        # Sprawdź, czy funkcja zwróciła oczekiwany wynik
        self.assertTrue(available)
        self.assertIn("Docker jest dostępny", message)
        
        # Symuluj, że komenda docker nie jest dostępna
        mock_run.side_effect = FileNotFoundError("No such file or directory")
        
        available, message = check_docker_available()
        
        # Sprawdź, czy funkcja zwróciła informację o błędzie
        self.assertFalse(available)
        self.assertIn("Komenda docker nie została znaleziona", message)
        
        # Symuluj, że Docker nie działa poprawnie
        mock_run.side_effect = None
        mock_run.return_value = MagicMock(returncode=1, stderr="Error")
        
        available, message = check_docker_available()
        
        # Sprawdź, czy funkcja zwróciła informację o błędzie
        self.assertFalse(available)
        self.assertIn("Docker nie jest dostępny", message)

    @patch('devopy.sandbox.docker_sandbox.DockerSandbox')
    def test_run_code_in_sandbox(self, mock_sandbox):
        """Test funkcji run_code_in_sandbox"""
        # Symuluj, że kod został wykonany pomyślnie
        mock_instance = MagicMock()
        mock_instance.run.return_value = {
            "success": True,
            "output": "Hello from Docker Sandbox!",
            "error": "",
            "execution_time": 0.1
        }
        mock_sandbox.return_value = mock_instance
        
        code = "print('Hello from Docker Sandbox!')"
        result = run_code_in_sandbox(code, timeout=10)
        
        # Sprawdź, czy funkcja zwróciła oczekiwany wynik
        self.assertTrue(result["success"])
        self.assertEqual(result["output"], "Hello from Docker Sandbox!")
        
        # Sprawdź, czy DockerSandbox został utworzony z odpowiednimi argumentami
        mock_sandbox.assert_called_once_with(timeout=10)
        
        # Sprawdź, czy metoda run została wywołana z odpowiednimi argumentami
        mock_instance.run.assert_called_once_with(code)
        
        # Sprawdź, czy metoda cleanup została wywołana
        mock_instance.cleanup.assert_called_once()

    @patch('devopy.sandbox.docker_sandbox.DockerSandbox')
    def test_run_service_in_sandbox(self, mock_sandbox):
        """Test funkcji run_service_in_sandbox"""
        # Symuluj, że usługa została uruchomiona pomyślnie
        mock_instance = MagicMock()
        mock_instance.run_service.return_value = {
            "success": True,
            "container_id": "container-id",
            "port": 8000,
            "url": "http://localhost:8000"
        }
        mock_sandbox.return_value = mock_instance
        
        code = "from flask import Flask\napp = Flask(__name__)"
        result = run_service_in_sandbox(code, port=8000, expose_port=True)
        
        # Sprawdź, czy funkcja zwróciła oczekiwany wynik
        self.assertTrue(result["success"])
        self.assertEqual(result["container_id"], "container-id")
        self.assertEqual(result["port"], 8000)
        
        # Sprawdź, czy DockerSandbox został utworzony
        mock_sandbox.assert_called_once()
        
        # Sprawdź, czy metoda run_service została wywołana z odpowiednimi argumentami
        mock_instance.run_service.assert_called_once_with(code, 8000, True)

    @patch('devopy.sandbox.docker_sandbox.DockerSandbox')
    def test_stop_sandbox_service(self, mock_sandbox):
        """Test funkcji stop_sandbox_service"""
        # Symuluj, że usługa została zatrzymana pomyślnie
        mock_instance = MagicMock()
        mock_instance.stop_service.return_value = {
            "success": True,
            "container_name": "test-container",
            "message": "Usługa zatrzymana"
        }
        mock_sandbox.return_value = mock_instance
        
        result = stop_sandbox_service("test-container")
        
        # Sprawdź, czy funkcja zwróciła oczekiwany wynik
        self.assertTrue(result["success"])
        self.assertEqual(result["container_name"], "test-container")
        
        # Sprawdź, czy DockerSandbox został utworzony
        mock_sandbox.assert_called_once()
        
        # Sprawdź, czy metoda stop_service została wywołana z odpowiednimi argumentami
        mock_instance.stop_service.assert_called_once_with("test-container")


if __name__ == '__main__':
    unittest.main()
