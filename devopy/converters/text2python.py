#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moduł do konwersji tekstu na kod Python.

Ten moduł umożliwia konwersję opisu w języku naturalnym na kod Python
przy użyciu modeli LLM (Large Language Models).
"""

import os
import re
import sys
import json
import logging
import subprocess
from typing import Dict, List, Any, Optional, Tuple, Union

# Konfiguracja logowania
logger = logging.getLogger('devopy.converters.text2python')

class Text2Python:
    """Klasa do konwersji tekstu na kod Python"""
    
    def __init__(self, model_name="codellama:7b-code", code_dir=None):
        """Inicjalizacja klasy
        
        Args:
            model_name: Nazwa modelu LLM do użycia
            code_dir: Katalog z kodem (opcjonalny)
        """
        self.model_name = model_name
        self.code_dir = code_dir
        logger.info(f"Inicjalizacja Text2Python z modelem {model_name}")
        if code_dir:
            logger.info(f"Katalog kodu: {code_dir}")
        
    def ensure_model_available(self) -> bool:
        """Sprawdza, czy model jest dostępny
        
        Returns:
            bool: True jeśli model jest dostępny, False w przeciwnym razie
        """
        try:
            # Sprawdź, czy Ollama jest zainstalowane i czy model jest dostępny
            cmd = ["ollama", "list"]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Błąd podczas sprawdzania dostępności modelu: {stderr}")
                return False
            
            # Sprawdź, czy model jest na liście
            return self.model_name in stdout
            
        except Exception as e:
            logger.error(f"Błąd podczas sprawdzania dostępności modelu: {e}")
            return False
    
    def text_to_python(self, prompt: str) -> Dict[str, Any]:
        """Konwertuje opis w języku naturalnym na kod Python
        
        Args:
            prompt: Opis zadania w języku naturalnym
            
        Returns:
            Dict[str, Any]: Słownik zawierający wygenerowany kod i metadane
        """
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return {
                    "success": False,
                    "code": "",
                    "error": f"Model {self.model_name} nie jest dostępny",
                    "analysis": "Problem z modelem"
                }
            
            logger.info(f"Generowanie kodu dla zapytania: {prompt}...")
            
            # Przygotuj zapytanie do modelu
            system_prompt = """Jesteś ekspertem w konwersji opisu w języku naturalnym na kod Python.
Twoim zadaniem jest wygenerowanie funkcji Python, która realizuje opisane zadanie.
Generuj tylko kod Python, bez dodatkowych wyjaśnień. Kod powinien być kompletny i gotowy do uruchomienia.
Funkcja powinna być nazwana 'execute' i powinna zwracać wynik działania.
Zapewnij, że kod jest logiczny i realizuje dokładnie to, o co prosi użytkownik."""
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\nUtwórz funkcję Python, która realizuje następujące zadanie:\n{prompt}\n\nKod Python:"
            
            # Wywołaj model LLM
            cmd = [
                "ollama", "run", self.model_name,
                combined_prompt
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Błąd podczas generowania kodu: {stderr}")
                return {
                    "success": False,
                    "code": "",
                    "error": stderr,
                    "analysis": "Błąd generowania"
                }
            
            # Wyodrębnij kod Python z odpowiedzi
            code = stdout.strip()
            
            # Jeśli kod jest otoczony znacznikami ```python i ```, usuń je
            code = re.sub(r'^```python\n|^```\n|\n```$', '', code, flags=re.MULTILINE)
            
            # Dodaj automatyczne importy
            try:
                from devopy.utils.dependency_manager import fix_code_dependencies
                code = fix_code_dependencies(code)
            except ImportError:
                logger.warning("Nie można automatycznie dodać importów - moduł dependency_manager niedostępny")
            
            return {
                "success": True,
                "code": code,
                "error": "",
                "analysis": "Kod wygenerowany pomyślnie"
            }
            
        except Exception as e:
            logger.error(f"Błąd podczas konwersji tekstu na kod: {e}")
            return {
                "success": False,
                "code": "",
                "error": str(e),
                "analysis": "Wyjątek podczas generowania"
            }
    
    def explain_code(self, code: str) -> str:
        """Generuje wyjaśnienie kodu w języku naturalnym
        
        Args:
            code: Kod Python do wyjaśnienia
            
        Returns:
            str: Wyjaśnienie kodu w języku naturalnym
        """
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return f"Nie można wygenerować wyjaśnienia, ponieważ model {self.model_name} nie jest dostępny."
            
            # Przygotuj zapytanie do modelu
            system_prompt = 'Jesteś ekspertem w wyjaśnianiu kodu Python. Twoim zadaniem jest wyjaśnienie działania podanego kodu w prosty i zrozumiały sposób. Wyjaśnienie powinno być krótkie, ale kompletne, opisujące co kod robi krok po kroku.'
            
            prompt = f"Wyjaśnij działanie następującego kodu Python:\n\n```python\n{code}\n```"
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Wywołaj model LLM
            cmd = [
                "ollama", "run", self.model_name,
                combined_prompt
            ]
            
            logger.info("Generowanie wyjaśnienia kodu...")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Błąd podczas generowania wyjaśnienia: {stderr}")
                return f"Nie udało się wygenerować wyjaśnienia: {stderr}"
            
            return stdout.strip()
            
        except Exception as e:
            logger.error(f"Błąd podczas generowania wyjaśnienia: {e}")
            return f"Nie udało się wygenerować wyjaśnienia: {str(e)}"
    
    def improve_code(self, code: str) -> Dict[str, Any]:
        """Ulepsza istniejący kod Python
        
        Args:
            code: Kod Python do ulepszenia
            
        Returns:
            Dict[str, Any]: Słownik zawierający ulepszony kod i metadane
        """
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return {
                    "success": False,
                    "code": code,
                    "error": f"Model {self.model_name} nie jest dostępny",
                    "analysis": "Problem z modelem"
                }
            
            # Przygotuj zapytanie do modelu
            system_prompt = """Jesteś ekspertem w optymalizacji i ulepszaniu kodu Python.
Twoim zadaniem jest ulepszenie podanego kodu Python, aby był bardziej wydajny, czytelny i zgodny z dobrymi praktykami.
Zwróć tylko ulepszony kod, bez dodatkowych wyjaśnień."""
            
            prompt = f"Ulepsz następujący kod Python:\n\n```python\n{code}\n```"
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Wywołaj model LLM
            cmd = [
                "ollama", "run", self.model_name,
                combined_prompt
            ]
            
            logger.info("Ulepszanie kodu...")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Błąd podczas ulepszania kodu: {stderr}")
                return {
                    "success": False,
                    "code": code,
                    "error": stderr,
                    "analysis": "Błąd ulepszania"
                }
            
            # Wyodrębnij kod Python z odpowiedzi
            improved_code = stdout.strip()
            
            # Jeśli kod jest otoczony znacznikami ```python i ```, usuń je
            improved_code = re.sub(r'^```python\n|^```\n|\n```$', '', improved_code, flags=re.MULTILINE)
            
            return {
                "success": True,
                "code": improved_code,
                "error": "",
                "analysis": "Kod ulepszony pomyślnie"
            }
            
        except Exception as e:
            logger.error(f"Błąd podczas ulepszania kodu: {e}")
            return {
                "success": False,
                "code": code,
                "error": str(e),
                "analysis": "Wyjątek podczas ulepszania"
            }

    def __str__(self):
        """Reprezentacja tekstowa obiektu"""
        return f"Text2Python(model={self.model_name})"


# Funkcje pomocnicze do użycia w innych modułach
def convert_text_to_python(prompt: str, model_name: str = "codellama:7b-code") -> str:
    """
    Konwertuje opis w języku naturalnym na kod Python
    
    Args:
        prompt: Opis zadania w języku naturalnym
        model_name: Nazwa modelu LLM do użycia
        
    Returns:
        str: Wygenerowany kod Python
    """
    converter = Text2Python(model_name=model_name)
    result = converter.text_to_python(prompt)
    
    if result["success"]:
        return result["code"]
    else:
        logger.error(f"Błąd konwersji: {result['error']}")
        return f"# Błąd konwersji: {result['error']}"


def explain_python_code(code: str, model_name: str = "codellama:7b-code") -> str:
    """
    Generuje wyjaśnienie kodu Python w języku naturalnym
    
    Args:
        code: Kod Python do wyjaśnienia
        model_name: Nazwa modelu LLM do użycia
        
    Returns:
        str: Wyjaśnienie kodu w języku naturalnym
    """
    converter = Text2Python(model_name=model_name)
    return converter.explain_code(code)


def improve_python_code(code: str, model_name: str = "codellama:7b-code") -> str:
    """
    Ulepsza istniejący kod Python
    
    Args:
        code: Kod Python do ulepszenia
        model_name: Nazwa modelu LLM do użycia
        
    Returns:
        str: Ulepszony kod Python
    """
    converter = Text2Python(model_name=model_name)
    result = converter.improve_code(code)
    
    if result["success"]:
        return result["code"]
    else:
        logger.error(f"Błąd ulepszania: {result['error']}")
        return code  # Zwróć oryginalny kod w przypadku błędu


if __name__ == "__main__":
    # Prosty interfejs wiersza poleceń
    import argparse
    
    parser = argparse.ArgumentParser(description="Konwersja tekstu na kod Python")
    parser.add_argument("prompt", help="Opis zadania w języku naturalnym")
    parser.add_argument("--model", default="codellama:7b-code", help="Nazwa modelu LLM do użycia")
    parser.add_argument("--explain", action="store_true", help="Wyjaśnij wygenerowany kod")
    parser.add_argument("--improve", action="store_true", help="Ulepsz istniejący kod")
    parser.add_argument("--output", help="Ścieżka do pliku wyjściowego")
    
    args = parser.parse_args()
    
    # Konfiguracja logowania
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    converter = Text2Python(model_name=args.model)
    
    if args.improve:
        # Traktuj prompt jako ścieżkę do pliku z kodem do ulepszenia
        if os.path.exists(args.prompt):
            with open(args.prompt, 'r', encoding='utf-8') as f:
                code = f.read()
            
            result = converter.improve_code(code)
            
            if result["success"]:
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        f.write(result["code"])
                else:
                    print(result["code"])
            else:
                print(f"Błąd: {result['error']}")
                sys.exit(1)
        else:
            print(f"Błąd: Plik {args.prompt} nie istnieje")
            sys.exit(1)
    else:
        # Konwersja tekstu na kod
        result = converter.text_to_python(args.prompt)
        
        if result["success"]:
            if args.explain:
                explanation = converter.explain_code(result["code"])
                print(f"# Wyjaśnienie:\n# {explanation.replace('\n', '\n# ')}\n\n{result['code']}")
            else:
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        f.write(result["code"])
                else:
                    print(result["code"])
        else:
            print(f"Błąd: {result['error']}")
            sys.exit(1)
