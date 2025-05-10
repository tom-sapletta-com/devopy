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
import importlib.util
from typing import Dict, List, Any, Optional, Tuple, Union

# Konfiguracja logowania
logger = logging.getLogger('devopy.converters.text2python')

# Lista dostępnych modeli LLM
AVAILABLE_MODELS = {
    "ollama": [
        "codellama:7b-code",
        "llama3:8b",
        "mistral:7b",
        "codellama:13b-code",
        "codellama:34b-code"
    ],
    "openai": [
        "gpt-3.5-turbo",
        "gpt-4"
    ],
    "fallback": [
        "template" # Szablon kodu bez użycia LLM
    ]
}

# Sprawdź, czy OpenAI API jest dostępne
def is_openai_available():
    try:
        return importlib.util.find_spec("openai") is not None
    except ImportError:
        return False

class Text2Python:
    """Klasa do konwersji tekstu na kod Python"""
    
    def __init__(self, model_name="codellama:7b-code", code_dir=None, api_key=None):
        """Inicjalizacja klasy
        
        Args:
            model_name: Nazwa modelu LLM do użycia
            code_dir: Katalog z kodem (opcjonalny)
            api_key: Klucz API dla modeli wymagających uwierzytelnienia (np. OpenAI)
        """
        self.model_name = model_name
        self.code_dir = code_dir
        self.api_key = api_key
        
        # Określ typ modelu na podstawie nazwy
        if any(model_name == m for m in AVAILABLE_MODELS["ollama"]):
            self.model_type = "ollama"
        elif any(model_name == m for m in AVAILABLE_MODELS["openai"]):
            self.model_type = "openai"
        else:
            self.model_type = "fallback"
            
        logger.info(f"Inicjalizacja Text2Python z modelem {model_name} (typ: {self.model_type})")
        if code_dir:
            logger.info(f"Katalog kodu: {code_dir}")
        
    def ensure_model_available(self) -> bool:
        """Sprawdza, czy model jest dostępny
        
        Returns:
            bool: True jeśli model jest dostępny, False w przeciwnym razie
        """
        try:
            # Sprawdź dostępność w zależności od typu modelu
            if self.model_type == "ollama":
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
                    logger.error(f"Błąd podczas sprawdzania dostępności modelu Ollama: {stderr}")
                    return False
                
                # Sprawdź, czy model jest na liście
                return self.model_name in stdout
            
            elif self.model_type == "openai":
                # Sprawdź, czy biblioteka OpenAI jest zainstalowana
                if not is_openai_available():
                    logger.error("Biblioteka OpenAI nie jest zainstalowana")
                    return False
                
                # Sprawdź, czy klucz API jest dostępny
                if not self.api_key and not os.environ.get("OPENAI_API_KEY"):
                    logger.error("Brak klucza API dla OpenAI")
                    return False
                
                return True
            
            elif self.model_type == "fallback":
                # Fallback zawsze jest dostępny
                return True
            
            else:
                logger.error(f"Nieznany typ modelu: {self.model_type}")
                return False
                
        except Exception as e:
            logger.error(f"Błąd podczas sprawdzania dostępności modelu: {e}")
            return False
    
    def _generate_with_ollama(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        """Generuje kod przy użyciu Ollama
        
        Args:
            prompt: Opis zadania w języku naturalnym
            system_prompt: Instrukcja systemowa dla modelu
            
        Returns:
            Dict[str, Any]: Wynik generowania
        """
        try:
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
            
            return {
                "success": True,
                "code": code,
                "error": "",
                "analysis": "Kod wygenerowany pomyślnie z Ollama"
            }
        except Exception as e:
            logger.error(f"Błąd podczas generowania kodu z Ollama: {e}")
            return {
                "success": False,
                "code": "",
                "error": str(e),
                "analysis": "Wyjątek podczas generowania z Ollama"
            }
    
    def _generate_with_openai(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        """Generuje kod przy użyciu OpenAI API
        
        Args:
            prompt: Opis zadania w języku naturalnym
            system_prompt: Instrukcja systemowa dla modelu
            
        Returns:
            Dict[str, Any]: Wynik generowania
        """
        try:
            import openai
            
            # Ustaw klucz API
            if self.api_key:
                openai.api_key = self.api_key
            
            # Przygotuj zapytanie
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Utwórz funkcję Python, która realizuje następujące zadanie:\n{prompt}"}
            ]
            
            # Wywołaj model
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=messages,
                temperature=0.2,
                max_tokens=1000
            )
            
            # Pobierz kod z odpowiedzi
            code = response.choices[0].message.content.strip()
            
            # Jeśli kod jest otoczony znacznikami ```python i ```, usuń je
            code = re.sub(r'^```python\n|^```\n|\n```$', '', code, flags=re.MULTILINE)
            
            return {
                "success": True,
                "code": code,
                "error": "",
                "analysis": "Kod wygenerowany pomyślnie z OpenAI"
            }
        except Exception as e:
            logger.error(f"Błąd podczas generowania kodu z OpenAI: {e}")
            return {
                "success": False,
                "code": "",
                "error": str(e),
                "analysis": "Wyjątek podczas generowania z OpenAI"
            }
    
    def _generate_fallback(self, prompt: str) -> Dict[str, Any]:
        """Generuje kod bez użycia LLM (fallback)
        
        Args:
            prompt: Opis zadania w języku naturalnym
            
        Returns:
            Dict[str, Any]: Wynik generowania
        """
        try:
            # Prosty szablon funkcji
            code = f"""def execute(*args, **kwargs):
    # Funkcja wygenerowana na podstawie opisu: {prompt}
    # TODO: Zaimplementuj funkcję zgodnie z opisem
    # Opis: {prompt}
    
    result = None
    print("Wykonuję zadanie: " + "{prompt}")
    print("Argumenty: " + str(args) + ", " + str(kwargs))
    
    # Przykładowa implementacja - do zastąpienia
    result = "Wynik dla zadania: " + "{prompt}"
    
    return result
"""
            
            return {
                "success": True,
                "code": code,
                "error": "",
                "analysis": "Wygenerowano szablon kodu (fallback)"
            }
        except Exception as e:
            logger.error(f"Błąd podczas generowania szablonu kodu: {e}")
            return {
                "success": False,
                "code": "",
                "error": str(e),
                "analysis": "Wyjątek podczas generowania szablonu"
            }
    
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
                # Spróbuj użyć fallbacku
                logger.warning(f"Model {self.model_name} nie jest dostępny. Używam fallbacku.")
                result = self._generate_fallback(prompt)
                return result
            
            logger.info(f"Generowanie kodu dla zapytania: {prompt}...")
            
            # Przygotuj zapytanie do modelu
            system_prompt = """Jesteś ekspertem w konwersji opisu w języku naturalnym na kod Python.
Twoim zadaniem jest wygenerowanie funkcji Python, która realizuje opisane zadanie.
Generuj tylko kod Python, bez dodatkowych wyjaśnień. Kod powinien być kompletny i gotowy do uruchomienia.
Funkcja powinna być nazwana 'execute' i powinna zwracać wynik działania.
Zapewnij, że kod jest logiczny i realizuje dokładnie to, o co prosi użytkownik."""
            
            # Generuj kod w zależności od typu modelu
            if self.model_type == "ollama":
                result = self._generate_with_ollama(prompt, system_prompt)
            elif self.model_type == "openai":
                result = self._generate_with_openai(prompt, system_prompt)
            else:  # fallback
                result = self._generate_fallback(prompt)
            
            # Jeśli generowanie się powiodło, dodaj automatyczne importy
            if result["success"] and result["code"]:
                try:
                    from devopy.utils.dependency_manager import fix_code_dependencies
                    result["code"] = fix_code_dependencies(result["code"])
                except ImportError:
                    logger.warning("Nie można automatycznie dodać importów - moduł dependency_manager niedostępny")
            
            return result
            
        except Exception as e:
            logger.error(f"Błąd podczas konwersji tekstu na kod: {e}")
            return {
                "success": False,
                "code": "",
                "error": str(e),
                "analysis": "Wyjątek podczas generowania"
            }
    
    def _explain_with_ollama(self, code: str, system_prompt: str) -> str:
        """Generuje wyjaśnienie kodu przy użyciu Ollama
        
        Args:
            code: Kod Python do wyjaśnienia
            system_prompt: Instrukcja systemowa dla modelu
            
        Returns:
            str: Wyjaśnienie kodu
        """
        try:
            prompt = f"Wyjaśnij działanie następującego kodu Python:\n\n```python\n{code}\n```"
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\n{prompt}"
            
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
                logger.error(f"Błąd podczas generowania wyjaśnienia: {stderr}")
                return f"Nie udało się wygenerować wyjaśnienia: {stderr}"
            
            return stdout.strip()
            
        except Exception as e:
            logger.error(f"Błąd podczas generowania wyjaśnienia z Ollama: {e}")
            return f"Nie udało się wygenerować wyjaśnienia: {str(e)}"
    
    def _explain_with_openai(self, code: str, system_prompt: str) -> str:
        """Generuje wyjaśnienie kodu przy użyciu OpenAI API
        
        Args:
            code: Kod Python do wyjaśnienia
            system_prompt: Instrukcja systemowa dla modelu
            
        Returns:
            str: Wyjaśnienie kodu
        """
        try:
            import openai
            
            # Ustaw klucz API
            if self.api_key:
                openai.api_key = self.api_key
            
            # Przygotuj zapytanie
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Wyjaśnij działanie następującego kodu Python:\n\n```python\n{code}\n```"}
            ]
            
            # Wywołaj model
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=messages,
                temperature=0.3,
                max_tokens=1000
            )
            
            # Pobierz wyjaśnienie z odpowiedzi
            explanation = response.choices[0].message.content.strip()
            
            return explanation
            
        except Exception as e:
            logger.error(f"Błąd podczas generowania wyjaśnienia z OpenAI: {e}")
            return f"Nie udało się wygenerować wyjaśnienia: {str(e)}"
    
    def _explain_fallback(self, code: str) -> str:
        """Generuje proste wyjaśnienie kodu bez użycia LLM
        
        Args:
            code: Kod Python do wyjaśnienia
            
        Returns:
            str: Wyjaśnienie kodu
        """
        try:
            # Prosta analiza kodu
            lines = code.strip().split('\n')
            function_name = None
            docstring = None
            has_loops = False
            has_conditionals = False
            has_functions = False
            returns_value = False
            
            # Szukaj funkcji, pętli, warunków itp.
            for line in lines:
                if 'def ' in line:
                    has_functions = True
                    # Wyodrębnij nazwę funkcji
                    parts = line.split('def ')[1].split('(')[0].strip()
                    function_name = parts if parts else function_name
                elif 'for ' in line or 'while ' in line:
                    has_loops = True
                elif 'if ' in line or 'elif ' in line or 'else:' in line:
                    has_conditionals = True
                elif 'return ' in line:
                    returns_value = True
                elif '"""' in line and docstring is None:
                    # Próba wyodrębnienia docstringa
                    try:
                        start_idx = lines.index(line)
                        if '"""' in lines[start_idx+1]:
                            docstring = lines[start_idx+1].strip('""" ')
                    except:
                        pass
            
            # Generuj proste wyjaśnienie
            explanation = "Analiza kodu Python:\n\n"
            
            if function_name:
                explanation += f"- Kod zawiera funkcję o nazwie '{function_name}'\n"
            else:
                explanation += "- Kod zawiera skrypt bez zdefiniowanych funkcji\n"
            
            if docstring:
                explanation += f"- Opis funkcji: {docstring}\n"
            
            if has_loops:
                explanation += "- Kod zawiera pętle (for/while)\n"
            
            if has_conditionals:
                explanation += "- Kod zawiera instrukcje warunkowe (if/elif/else)\n"
            
            if returns_value:
                explanation += "- Kod zwraca wartość (return)\n"
            
            explanation += "\nAby uzyskać dokładniejsze wyjaśnienie, zalecane jest użycie modelu LLM."
            
            return explanation
            
        except Exception as e:
            logger.error(f"Błąd podczas generowania prostego wyjaśnienia: {e}")
            return f"Nie udało się wygenerować wyjaśnienia: {str(e)}"
    
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
                logger.warning(f"Model {self.model_name} nie jest dostępny. Używam fallbacku do wyjaśnienia kodu.")
                return self._explain_fallback(code)
            
            # Przygotuj zapytanie do modelu
            system_prompt = 'Jesteś ekspertem w wyjaśnianiu kodu Python. Twoim zadaniem jest wyjaśnienie działania podanego kodu w prosty i zrozumiały sposób. Wyjaśnienie powinno być krótkie, ale kompletne, opisujące co kod robi krok po kroku.'
            
            logger.info("Generowanie wyjaśnienia kodu...")
            
            # Generuj wyjaśnienie w zależności od typu modelu
            if self.model_type == "ollama":
                return self._explain_with_ollama(code, system_prompt)
            elif self.model_type == "openai":
                return self._explain_with_openai(code, system_prompt)
            else:  # fallback
                return self._explain_fallback(code)
            
        except Exception as e:
            logger.error(f"Błąd podczas generowania wyjaśnienia: {e}")
            return f"Nie udało się wygenerować wyjaśnienia: {str(e)}"
    
    def _improve_with_ollama(self, code: str, system_prompt: str) -> Dict[str, Any]:
        """Ulepsza kod przy użyciu Ollama
        
        Args:
            code: Kod Python do ulepszenia
            system_prompt: Instrukcja systemowa dla modelu
            
        Returns:
            Dict[str, Any]: Wynik ulepszania
        """
        try:
            prompt = f"Ulepsz następujący kod Python:\n\n```python\n{code}\n```\n\nUlepszony kod:"
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\n{prompt}"
            
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
                logger.error(f"Błąd podczas ulepszania kodu: {stderr}")
                return {
                    "success": False,
                    "code": code,  # Zwracamy oryginalny kod
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
                "analysis": "Kod ulepszony pomyślnie z Ollama"
            }
            
        except Exception as e:
            logger.error(f"Błąd podczas ulepszania kodu z Ollama: {e}")
            return {
                "success": False,
                "code": code,  # Zwracamy oryginalny kod
                "error": str(e),
                "analysis": "Wyjątek podczas ulepszania z Ollama"
            }
    
    def _improve_with_openai(self, code: str, system_prompt: str) -> Dict[str, Any]:
        """Ulepsza kod przy użyciu OpenAI API
        
        Args:
            code: Kod Python do ulepszenia
            system_prompt: Instrukcja systemowa dla modelu
            
        Returns:
            Dict[str, Any]: Wynik ulepszania
        """
        try:
            import openai
            
            # Ustaw klucz API
            if self.api_key:
                openai.api_key = self.api_key
            
            # Przygotuj zapytanie
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Ulepsz następujący kod Python:\n\n```python\n{code}\n```"}
            ]
            
            # Wywołaj model
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=messages,
                temperature=0.2,
                max_tokens=1000
            )
            
            # Pobierz ulepszony kod z odpowiedzi
            improved_code = response.choices[0].message.content.strip()
            
            # Jeśli kod jest otoczony znacznikami ```python i ```, usuń je
            improved_code = re.sub(r'^```python\n|^```\n|\n```$', '', improved_code, flags=re.MULTILINE)
            
            return {
                "success": True,
                "code": improved_code,
                "error": "",
                "analysis": "Kod ulepszony pomyślnie z OpenAI"
            }
            
        except Exception as e:
            logger.error(f"Błąd podczas ulepszania kodu z OpenAI: {e}")
            return {
                "success": False,
                "code": code,  # Zwracamy oryginalny kod
                "error": str(e),
                "analysis": "Wyjątek podczas ulepszania z OpenAI"
            }
    
    def _improve_fallback(self, code: str) -> Dict[str, Any]:
        """Ulepsza kod bez użycia LLM (fallback)
        
        Args:
            code: Kod Python do ulepszenia
            
        Returns:
            Dict[str, Any]: Wynik ulepszania
        """
        try:
            # Proste ulepszenia kodu
            lines = code.strip().split('\n')
            improved_lines = []
            
            for line in lines:
                # Usunięcie zbędnych spacji na końcu linii
                line = line.rstrip()
                
                # Dodanie spacji wokół operatorów
                for op in ['=', '+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=']:
                    if op in line and f'"{op}"' not in line and f"'{op}'" not in line:
                        line = line.replace(op, f" {op} ")
                
                # Usunięcie podwójnych spacji
                while '  ' in line:
                    line = line.replace('  ', ' ')
                
                improved_lines.append(line)
            
            improved_code = '\n'.join(improved_lines)
            
            # Dodaj komentarz o ulepszeniach
            improved_code = "# Kod ulepszony przez fallback mechanizm\n" + improved_code
            
            return {
                "success": True,
                "code": improved_code,
                "error": "",
                "analysis": "Kod ulepszony przez fallback mechanizm (podstawowe formatowanie)"
            }
            
        except Exception as e:
            logger.error(f"Błąd podczas ulepszania kodu fallback: {e}")
            return {
                "success": False,
                "code": code,  # Zwracamy oryginalny kod
                "error": str(e),
                "analysis": "Wyjątek podczas ulepszania fallback"
            }
    
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
                logger.warning(f"Model {self.model_name} nie jest dostępny. Używam fallbacku do ulepszenia kodu.")
                result = self._improve_fallback(code)
                return result
            
            # Przygotuj zapytanie do modelu
            system_prompt = """Jesteś ekspertem w optymalizacji i ulepszaniu kodu Python.
Twoim zadaniem jest ulepszenie podanego kodu Python, aby był bardziej wydajny, czytelny i zgodny z dobrymi praktykami.
Zachowaj dokładnie tę samą funkcjonalność, ale popraw styl, wydajność i czytelność.
Generuj tylko kod Python, bez dodatkowych wyjaśnień."""
            
            logger.info("Ulepszanie kodu...")
            
            # Generuj ulepszony kod w zależności od typu modelu
            if self.model_type == "ollama":
                result = self._improve_with_ollama(code, system_prompt)
            elif self.model_type == "openai":
                result = self._improve_with_openai(code, system_prompt)
            else:  # fallback
                result = self._improve_fallback(code)
            
            # Jeśli generowanie się powiodło, dodaj automatyczne importy
            if result["success"] and result["code"]:
                try:
                    from devopy.utils.dependency_manager import fix_code_dependencies
                    result["code"] = fix_code_dependencies(result["code"])
                except ImportError:
                    logger.warning("Nie można automatycznie dodać importów - moduł dependency_manager niedostępny")
            
            return result
            
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
