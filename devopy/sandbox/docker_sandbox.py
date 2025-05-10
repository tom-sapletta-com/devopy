#!/usr/bin/env python3
"""
Docker Sandbox - Moduł do bezpiecznego uruchamiania kodu w kontenerach Docker

Ten moduł zapewnia bezpieczne środowisko do uruchamiania kodu Python
generowanego na podstawie żądań użytkownika.
"""

import os
import uuid
import json
import time
import shutil
import logging
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

# Import menedżera zależności
try:
    from devopy.utils.dependency_manager import fix_code_dependencies
except ImportError:
    # Jeśli menedżer zależności nie jest dostępny, użyj funkcji zastępczej
    def fix_code_dependencies(code):
        return code

logger = logging.getLogger("devopy.sandbox.docker")


def check_docker_available() -> Tuple[bool, str]:
    """
    Sprawdza, czy Docker jest dostępny i działa poprawnie
    
    Returns:
        Tuple[bool, str]: (czy_dostępny, komunikat)
    """
    try:
        # Sprawdź, czy komenda docker jest dostępna
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return False, f"Docker nie jest dostępny: {result.stderr}"
        
        # Sprawdź, czy możemy uruchomić kontener
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return False, f"Docker nie działa poprawnie: {result.stderr}"
        
        return True, "Docker jest dostępny i działa poprawnie"
    except FileNotFoundError:
        return False, "Komenda docker nie została znaleziona"
    except subprocess.TimeoutExpired:
        return False, "Timeout podczas sprawdzania dostępności Dockera"
    except Exception as e:
        return False, f"Błąd podczas sprawdzania dostępności Dockera: {e}"


class DockerSandbox:
    """Klasa do zarządzania piaskownicami Docker dla kodu użytkownika"""

    def __init__(self, base_dir: Optional[Path] = None, docker_image: str = "python:3.9-slim", timeout: int = 30):
        """
        Inicjalizacja piaskownicy Docker

        Args:
            base_dir: Katalog bazowy dla plików piaskownicy (opcjonalny)
            docker_image: Obraz Docker do użycia
            timeout: Limit czasu wykonania w sekundach
        """
        if base_dir is None:
            # Użyj katalogu tymczasowego, jeśli nie podano katalogu bazowego
            base_dir = Path(tempfile.gettempdir()) / "devopy-sandbox"
            
        self.base_dir = Path(base_dir)
        self.docker_image = docker_image
        self.timeout = timeout
        self.container_id = None
        self.sandbox_id = str(uuid.uuid4())
        self.sandbox_dir = self.base_dir / self.sandbox_id

        # Utwórz katalog dla piaskownicy
        os.makedirs(self.sandbox_dir, exist_ok=True)
        logger.info(f"Utworzono piaskownicę Docker: {self.sandbox_id} w {self.sandbox_dir}")

    def extract_dependencies(self, code: str) -> List[str]:
        """
        Ekstrahuje zależności z kodu Python

        Args:
            code: Kod Python do analizy

        Returns:
            List[str]: Lista zależności
        """
        try:
            # Próba wyodrębnienia importów za pomocą AST
            import ast
            tree = ast.parse(code)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(name.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module.split('.')[0])
            
            # Filtruj standardowe moduły Pythona
            standard_libs = [
                'abc', 'argparse', 'array', 'ast', 'asyncio', 'base64', 'binascii',
                'builtins', 'collections', 'concurrent', 'contextlib', 'copy', 'csv',
                'datetime', 'decimal', 'difflib', 'enum', 'errno', 'fnmatch', 'functools',
                'gc', 'getopt', 'getpass', 'glob', 'gzip', 'hashlib', 'hmac', 'html',
                'http', 'importlib', 'inspect', 'io', 'itertools', 'json', 'logging',
                'math', 'mimetypes', 'multiprocessing', 'operator', 'os', 'pathlib',
                'pickle', 'platform', 'pprint', 'queue', 're', 'random', 'shutil',
                'signal', 'socket', 'sqlite3', 'statistics', 'string', 'struct',
                'subprocess', 'sys', 'tempfile', 'textwrap', 'threading', 'time',
                'traceback', 'types', 'typing', 'unittest', 'urllib', 'uuid', 'warnings',
                'weakref', 'xml', 'zipfile', 'zlib'
            ]
            
            # Zwróć tylko zewnętrzne zależności
            return [imp for imp in imports if imp not in standard_libs]
        except Exception as e:
            logger.warning(f"Błąd podczas ekstrahowania zależności: {e}")
            return []
    
    def prepare_code(self, code: str, filename: str = "user_code.py") -> Path:
        """
        Przygotowuje kod do wykonania w piaskownicy

        Args:
            code: Kod Python do wykonania
            filename: Nazwa pliku dla kodu

        Returns:
            Path: Ścieżka do pliku z kodem
        """
        # Napraw brakujące zależności w kodzie użytkownika
        code = fix_code_dependencies(code)
        
        # Ekstrahuj zależności
        dependencies = self.extract_dependencies(code)

        # Utwórz plik z zależnościami
        requirements_file = self.sandbox_dir / "requirements.txt"
        with open(requirements_file, "w") as f:
            f.write("\n".join(dependencies))
        
        # Utwórz skrypt instalacji zależności
        install_script = self.sandbox_dir / "install_dependencies.sh"
        with open(install_script, "w") as f:
            f.write("""#!/bin/bash
# Skrypt instalacji zależności
if [ -s /app/requirements.txt ]; then
    echo "Instalacja zależności..."
    pip install --no-cache-dir -r /app/requirements.txt
    echo "Zależności zainstalowane."
else
    echo "Brak zależności do instalacji."
fi
""")
        
        # Nadaj uprawnienia wykonywania
        os.chmod(install_script, 0o755)
        
        code_file = self.sandbox_dir / filename

        # Dodaj wrapper do przechwytywania wyjścia i błędów
        wrapped_code = f"""
import sys
import traceback
import json
import time
import importlib

# Funkcja do dynamicznego importowania modułów
def import_module_safe(module_name):
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None

# Funkcja do automatycznego importowania modułów
def auto_import():
    # Lista standardowych modułów do automatycznego importu w razie potrzeby
    auto_import_modules = [
        'time', 'datetime', 'os', 'sys', 're', 'json', 'math', 'random',
        'collections', 'itertools', 'functools', 'pathlib', 'shutil',
        'subprocess', 'threading', 'multiprocessing', 'urllib', 'http',
        'socket', 'email', 'csv', 'xml', 'html', 'sqlite3', 'logging'
    ]

    # Importuj wszystkie moduły z listy
    for module_name in auto_import_modules:
        if module_name not in globals():
            imported_module = import_module_safe(module_name)
            if imported_module:
                globals()[module_name] = imported_module

# Automatycznie zaimportuj standardowe moduły
auto_import()

# Przechwytywanie wyjścia
class OutputCapture:
    def __init__(self):
        self.output = []

    def write(self, text):
        self.output.append(text)

    def flush(self):
        pass

# Zapisz oryginalne strumienie
original_stdout = sys.stdout
original_stderr = sys.stderr

# Zastąp strumienie
stdout_capture = OutputCapture()
stderr_capture = OutputCapture()
sys.stdout = stdout_capture
sys.stderr = stderr_capture

# Wykonaj kod użytkownika
result = {{
    "success": False,
    "output": "",
    "error": "",
    "execution_time": 0
}}

try:
    start_time = time.time()

    # Kod użytkownika
{chr(10).join(['    ' + line for line in code.split(chr(10))])}

    execution_time = time.time() - start_time
    result["success"] = True
    result["execution_time"] = execution_time
except ImportError as e:
    # Próba automatycznego importu brakującego modułu
    missing_module = str(e).split("'")
    if len(missing_module) >= 2:
        module_name = missing_module[1]
        # Próba importu
        imported = import_module_safe(module_name)
        if imported:
            # Dodaj moduł do globals i spróbuj ponownie
            globals()[module_name] = imported
            try:
                # Ponowna próba wykonania kodu
                start_time = time.time()

                # Kod użytkownika
{chr(10).join(['                ' + line for line in code.split(chr(10))])}

                execution_time = time.time() - start_time
                result["success"] = True
                result["execution_time"] = execution_time
            except Exception as import_retry_error:
                result["error"] = f"Po próbie automatycznego importu: {{str(import_retry_error)}}"
                result["traceback"] = traceback.format_exc()
        else:
            result["error"] = f"Brakujący moduł: {{module_name}}. Nie można go automatycznie zaimportować."
            result["traceback"] = traceback.format_exc()
    else:
        result["error"] = str(e)
        result["traceback"] = traceback.format_exc()
except Exception as e:
    result["error"] = str(e)
    result["traceback"] = traceback.format_exc()

# Przywróć oryginalne strumienie
sys.stdout = original_stdout
sys.stderr = original_stderr

# Zapisz wyniki
result["output"] = "".join(stdout_capture.output)
result["error_output"] = "".join(stderr_capture.output)

# Zapisz wynik do pliku
with open("result.json", "w") as f:
    json.dump(result, f)

print(json.dumps(result))
"""

        with open(code_file, "w") as f:
            f.write(wrapped_code)

        return code_file

    def run(self, code: str) -> Dict[str, Any]:
        """
        Uruchamia kod w piaskownicy Docker

        Args:
            code: Kod Python do wykonania

        Returns:
            Dict: Wynik wykonania kodu
        """
        # Sprawdź, czy Docker jest dostępny
        docker_available, docker_message = check_docker_available()
        if not docker_available:
            logger.error(f"Docker nie jest dostępny: {docker_message}")
            return {
                "success": False,
                "error": f"Docker nie jest dostępny: {docker_message}",
                "output": "",
                "execution_time": 0
            }
        
        try:
            # Przygotuj kod
            code_file = self.prepare_code(code)

            # Utwórz kontener Docker
            container_name = f"devopy-sandbox-{self.sandbox_id}"

            # Uruchom kontener z instalacją zależności
            cmd = [
                "docker", "run",
                "--name", container_name,
                "--rm",  # Usuń kontener po zakończeniu
                "-v", f"{self.sandbox_dir}:/app",
                "-w", "/app",
                "--memory", "512m",  # Limit pamięci
                "--cpus", "0.5",  # Limit CPU
                self.docker_image,
                "bash", "-c", "/app/install_dependencies.sh && python /app/user_code.py"
            ]

            logger.info(f"Uruchamianie kodu w piaskownicy: {container_name}")

            # Uruchom z limitem czasu
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            try:
                stdout, stderr = process.communicate(timeout=self.timeout)

                # Sprawdź wynik
                if process.returncode != 0:
                    logger.warning(f"Kod zakończył się z błędem: {stderr}")
                    return {
                        "success": False,
                        "output": stdout,
                        "error": stderr,
                        "execution_time": self.timeout,
                        "container_name": container_name,
                        "sandbox_id": self.sandbox_id
                    }

                # Parsuj wynik JSON
                try:
                    result = json.loads(stdout)
                    # Dodaj informacje o kontenerze
                    result["container_name"] = container_name
                    result["sandbox_id"] = self.sandbox_id
                    return result
                except json.JSONDecodeError:
                    logger.warning(f"Nie można sparsować wyniku jako JSON: {stdout}")
                    return {
                        "success": True,
                        "output": stdout,
                        "error": "",
                        "execution_time": 0.1,  # Przybliżony czas wykonania
                        "container_name": container_name,
                        "sandbox_id": self.sandbox_id
                    }
            except subprocess.TimeoutExpired:
                # Zabij proces, jeśli przekroczył limit czasu
                process.kill()
                logger.warning(f"Kod przekroczył limit czasu wykonania: {self.timeout}s")
                
                # Spróbuj zatrzymać kontener, jeśli nadal działa
                try:
                    subprocess.run(["docker", "stop", container_name], timeout=5, capture_output=True)
                    logger.info(f"Zatrzymano kontener: {container_name}")
                except Exception as container_error:
                    logger.warning(f"Nie można zatrzymać kontenera: {container_error}")
                
                return {
                    "success": False,
                    "output": "",
                    "error": f"Kod przekroczył limit czasu wykonania: {self.timeout}s",
                    "execution_time": self.timeout,
                    "container_name": container_name,
                    "sandbox_id": self.sandbox_id,
                    "timeout": True
                }
        except FileNotFoundError as e:
            logger.error(f"Nie znaleziono pliku lub komendy: {e}")
            return {
                "success": False,
                "output": "",
                "error": f"Nie znaleziono pliku lub komendy: {e}",
                "execution_time": 0,
                "sandbox_id": self.sandbox_id
            }
        except PermissionError as e:
            logger.error(f"Brak uprawnień: {e}")
            return {
                "success": False,
                "output": "",
                "error": f"Brak uprawnień do uruchomienia kontenera Docker: {e}",
                "execution_time": 0,
                "sandbox_id": self.sandbox_id
            }
        except Exception as e:
            logger.error(f"Błąd podczas uruchamiania kodu w piaskownicy: {e}")
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "execution_time": 0,
                "sandbox_id": self.sandbox_id
            }
        finally:
            # Spróbuj wyczyścić kontener
            try:
                subprocess.run(
                    ["docker", "rm", "-f", container_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            except:
                pass

    def run_service(self, code: str, port: int = 8000, expose_port: bool = True) -> Dict[str, Any]:
        """
        Uruchamia kod jako usługę w piaskownicy Docker

        Args:
            code: Kod Python do wykonania
            port: Port, na którym działa usługa w kontenerze
            expose_port: Czy udostępnić port na hoście

        Returns:
            Dict: Wynik uruchomienia usługi
        """
        # Sprawdź, czy Docker jest dostępny
        docker_available, docker_message = check_docker_available()
        if not docker_available:
            logger.error(f"Docker nie jest dostępny: {docker_message}")
            return {
                "success": False,
                "error": f"Docker nie jest dostępny: {docker_message}",
                "output": "",
                "container_name": "",
                "sandbox_id": self.sandbox_id
            }
        
        try:
            # Przygotuj kod
            code_file = self.prepare_code(code, filename="service.py")

            # Utwórz kontener Docker
            container_name = f"devopy-service-{self.sandbox_id}"
            self.container_id = container_name

            # Przygotuj komendę Docker
            cmd = [
                "docker", "run",
                "--name", container_name,
                "-d",  # Uruchom w tle
                "-v", f"{self.sandbox_dir}:/app",
                "-w", "/app",
                "--memory", "512m",  # Limit pamięci
                "--cpus", "0.5",  # Limit CPU
            ]

            # Dodaj mapowanie portów, jeśli expose_port=True
            if expose_port:
                cmd.extend(["-p", f"{port}:{port}"])

            # Dodaj obraz i komendę z instalacją zależności
            cmd.extend([
                self.docker_image,
                "bash", "-c", "/app/install_dependencies.sh && python /app/service.py"
            ])

            logger.info(f"Uruchamianie usługi w piaskownicy: {container_name}")

            # Uruchom kontener
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if process.returncode != 0:
                logger.error(f"Błąd podczas uruchamiania usługi: {process.stderr}")
                return {
                    "success": False,
                    "error": process.stderr,
                    "output": process.stdout,
                    "container_name": container_name,
                    "sandbox_id": self.sandbox_id
                }

            # Pobierz ID kontenera
            container_id = process.stdout.strip()

            # Poczekaj chwilę na uruchomienie usługi
            time.sleep(2)

            # Sprawdź, czy kontener nadal działa
            check_process = subprocess.run(
                ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.ID}}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if not check_process.stdout.strip():
                # Kontener nie działa, pobierz logi
                logs_process = subprocess.run(
                    ["docker", "logs", container_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                logger.error(f"Usługa nie uruchomiła się poprawnie: {logs_process.stderr}")
                
                return {
                    "success": False,
                    "error": "Usługa nie uruchomiła się poprawnie",
                    "logs": logs_process.stdout + logs_process.stderr,
                    "container_name": container_name,
                    "sandbox_id": self.sandbox_id
                }

            # Usługa działa
            return {
                "success": True,
                "container_id": container_id,
                "container_name": container_name,
                "sandbox_id": self.sandbox_id,
                "port": port,
                "url": f"http://localhost:{port}" if expose_port else None,
                "message": f"Usługa uruchomiona w kontenerze {container_name}"
            }

        except Exception as e:
            logger.error(f"Błąd podczas uruchamiania usługi w piaskownicy: {e}")
            return {
                "success": False,
                "error": str(e),
                "container_name": "",
                "sandbox_id": self.sandbox_id
            }

    def stop_service(self, container_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Zatrzymuje usługę uruchomioną w piaskownicy

        Args:
            container_name: Nazwa kontenera do zatrzymania (opcjonalna)

        Returns:
            Dict: Wynik zatrzymania usługi
        """
        if container_name is None:
            container_name = self.container_id or f"devopy-service-{self.sandbox_id}"

        try:
            # Zatrzymaj kontener
            process = subprocess.run(
                ["docker", "stop", container_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if process.returncode != 0:
                logger.error(f"Błąd podczas zatrzymywania usługi: {process.stderr}")
                return {
                    "success": False,
                    "error": process.stderr,
                    "container_name": container_name,
                    "sandbox_id": self.sandbox_id
                }

            # Usuń kontener
            subprocess.run(
                ["docker", "rm", container_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            logger.info(f"Zatrzymano usługę: {container_name}")
            
            return {
                "success": True,
                "message": f"Usługa {container_name} zatrzymana",
                "container_name": container_name,
                "sandbox_id": self.sandbox_id
            }
        except Exception as e:
            logger.error(f"Błąd podczas zatrzymywania usługi: {e}")
            return {
                "success": False,
                "error": str(e),
                "container_name": container_name,
                "sandbox_id": self.sandbox_id
            }

    def cleanup(self):
        """Czyści zasoby piaskownicy"""
        try:
            # Sprawdź, czy kontener nadal istnieje i zatrzymaj go
            if self.container_id:
                try:
                    subprocess.run(
                        ["docker", "stop", self.container_id],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=5
                    )
                    logger.info(f"Zatrzymano kontener: {self.container_id}")
                except Exception as e:
                    logger.warning(f"Nie można zatrzymać kontenera {self.container_id}: {e}")
            
            # Sprawdź, czy istnieją kontenery z nazwą zawierającą sandbox_id i zatrzymaj je
            try:
                for prefix in ["devopy-sandbox-", "devopy-service-"]:
                    container_name = f"{prefix}{self.sandbox_id}"
                    subprocess.run(
                        ["docker", "stop", container_name],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=5
                    )
                    logger.info(f"Zatrzymano kontener: {container_name}")
            except Exception:
                # Ignoruj błędy - kontener może już nie istnieć
                pass
            
            # Usuń katalog piaskownicy
            if os.path.exists(self.sandbox_dir):
                shutil.rmtree(self.sandbox_dir, ignore_errors=True)
                logger.info(f"Wyczyszczono piaskownicę: {self.sandbox_id}")
        except Exception as e:
            logger.error(f"Błąd podczas czyszczenia piaskownicy: {e}")
        
        return {"success": True, "message": f"Wyczyszczono piaskownicę: {self.sandbox_id}"}


# Funkcje pomocnicze do użycia w innych modułach
def run_code_in_sandbox(code: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Uruchamia kod Python w piaskownicy Docker
    
    Args:
        code: Kod Python do wykonania
        timeout: Limit czasu wykonania w sekundach
        
    Returns:
        Dict[str, Any]: Wynik wykonania kodu
    """
    sandbox = DockerSandbox(timeout=timeout)
    try:
        return sandbox.run(code)
    finally:
        sandbox.cleanup()


def run_service_in_sandbox(code: str, port: int = 8000, expose_port: bool = True) -> Dict[str, Any]:
    """
    Uruchamia usługę w piaskownicy Docker
    
    Args:
        code: Kod Python usługi do uruchomienia
        port: Port, na którym działa usługa w kontenerze
        expose_port: Czy udostępnić port na hoście
        
    Returns:
        Dict[str, Any]: Wynik uruchomienia usługi
    """
    sandbox = DockerSandbox()
    return sandbox.run_service(code, port, expose_port)


def stop_sandbox_service(container_name: str) -> Dict[str, Any]:
    """
    Zatrzymuje usługę uruchomioną w piaskownicy
    
    Args:
        container_name: Nazwa kontenera do zatrzymania
        
    Returns:
        Dict[str, Any]: Wynik zatrzymania usługi
    """
    sandbox = DockerSandbox()
    return sandbox.stop_service(container_name)


if __name__ == "__main__":
    # Prosty interfejs wiersza poleceń
    import argparse
    
    # Konfiguracja logowania
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(description="Uruchamianie kodu Python w piaskownicy Docker")
    parser.add_argument("--code", help="Kod Python do wykonania")
    parser.add_argument("--file", help="Plik z kodem Python do wykonania")
    parser.add_argument("--service", action="store_true", help="Uruchom jako usługę")
    parser.add_argument("--port", type=int, default=8000, help="Port dla usługi")
    parser.add_argument("--stop", help="Zatrzymaj usługę o podanej nazwie kontenera")
    parser.add_argument("--timeout", type=int, default=30, help="Limit czasu wykonania w sekundach")
    
    args = parser.parse_args()
    
    if args.stop:
        # Zatrzymaj usługę
        result = stop_sandbox_service(args.stop)
        print(json.dumps(result, indent=2))
    elif args.code or args.file:
        # Pobierz kod
        if args.file:
            with open(args.file, 'r') as f:
                code = f.read()
        else:
            code = args.code
        
        # Uruchom kod lub usługę
        if args.service:
            result = run_service_in_sandbox(code, args.port)
        else:
            result = run_code_in_sandbox(code, args.timeout)
        
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()
