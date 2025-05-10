#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rozszerzenia API dla projektu Devopy

Ten moduł zawiera dodatkowe endpointy API wykorzystujące przeniesione moduły:
- Menedżer zależności
- Konwerter tekstu na kod
- Piaskownica Docker
"""

import os
import sys
import json
import logging
from pathlib import Path
from flask import Blueprint, request, jsonify

# Konfiguracja logowania
logger = logging.getLogger('devopy.api.extensions')

# Importy przeniesionych modułów
from devopy.utils.dependency_manager import fix_code_dependencies, install_missing_packages
from devopy.converters.text2python import convert_text_to_python, explain_python_code, improve_python_code
from devopy.sandbox.docker_sandbox import run_code_in_sandbox, run_service_in_sandbox, stop_sandbox_service, check_docker_available

# Utwórz Blueprint dla rozszerzeń API
api_extensions = Blueprint('api_extensions', __name__)


# Endpointy dla menedżera zależności
@api_extensions.route('/dependencies/fix', methods=['POST'])
def fix_dependencies():
    """Naprawia brakujące zależności w kodzie"""
    if not request.json or 'code' not in request.json:
        return jsonify({'error': 'Brak kodu do analizy'}), 400
    
    code = request.json.get('code')
    
    try:
        fixed_code = fix_code_dependencies(code)
        return jsonify({
            'success': True,
            'code': fixed_code
        })
    except Exception as e:
        logger.error(f"Błąd podczas naprawiania zależności: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_extensions.route('/dependencies/install', methods=['POST'])
def install_dependencies():
    """Instaluje brakujące pakiety"""
    if not request.json or 'code' not in request.json:
        return jsonify({'error': 'Brak kodu do analizy'}), 400
    
    code = request.json.get('code')
    venv_path = request.json.get('venv_path')
    
    try:
        installed = install_missing_packages(code, venv_path)
        return jsonify({
            'success': True,
            'installed': installed
        })
    except Exception as e:
        logger.error(f"Błąd podczas instalacji pakietów: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Endpointy dla konwertera tekstu na kod
@api_extensions.route('/convert/text2python', methods=['POST'])
def text_to_python_endpoint():
    """Konwertuje opis w języku naturalnym na kod Python"""
    if not request.json or 'prompt' not in request.json:
        return jsonify({'error': 'Brak opisu do konwersji'}), 400
    
    prompt = request.json.get('prompt')
    model_name = request.json.get('model', 'codellama:7b-code')
    
    try:
        code = convert_text_to_python(prompt, model_name)
        return jsonify({
            'success': True,
            'code': code
        })
    except Exception as e:
        logger.error(f"Błąd podczas konwersji tekstu na kod: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_extensions.route('/convert/explain', methods=['POST'])
def explain_code_endpoint():
    """Wyjaśnia kod Python w języku naturalnym"""
    if not request.json or 'code' not in request.json:
        return jsonify({'error': 'Brak kodu do wyjaśnienia'}), 400
    
    code = request.json.get('code')
    model_name = request.json.get('model', 'codellama:7b-code')
    
    try:
        explanation = explain_python_code(code, model_name)
        return jsonify({
            'success': True,
            'explanation': explanation
        })
    except Exception as e:
        logger.error(f"Błąd podczas wyjaśniania kodu: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_extensions.route('/convert/improve', methods=['POST'])
def improve_code_endpoint():
    """Ulepsza istniejący kod Python"""
    if not request.json or 'code' not in request.json:
        return jsonify({'error': 'Brak kodu do ulepszenia'}), 400
    
    code = request.json.get('code')
    model_name = request.json.get('model', 'codellama:7b-code')
    
    try:
        improved_code = improve_python_code(code, model_name)
        return jsonify({
            'success': True,
            'code': improved_code
        })
    except Exception as e:
        logger.error(f"Błąd podczas ulepszania kodu: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Endpointy dla piaskownicy Docker
@api_extensions.route('/sandbox/check', methods=['GET'])
def check_docker_endpoint():
    """Sprawdza, czy Docker jest dostępny"""
    try:
        available, message = check_docker_available()
        return jsonify({
            'available': available,
            'message': message
        })
    except Exception as e:
        logger.error(f"Błąd podczas sprawdzania dostępności Dockera: {e}")
        return jsonify({
            'available': False,
            'error': str(e)
        }), 500


@api_extensions.route('/sandbox/run', methods=['POST'])
def run_in_sandbox_endpoint():
    """Uruchamia kod Python w piaskownicy Docker"""
    if not request.json or 'code' not in request.json:
        return jsonify({'error': 'Brak kodu do uruchomienia'}), 400
    
    code = request.json.get('code')
    timeout = request.json.get('timeout', 30)
    
    try:
        result = run_code_in_sandbox(code, timeout)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Błąd podczas uruchamiania kodu w piaskownicy: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_extensions.route('/sandbox/service', methods=['POST'])
def run_service_endpoint():
    """Uruchamia usługę w piaskownicy Docker"""
    if not request.json or 'code' not in request.json:
        return jsonify({'error': 'Brak kodu do uruchomienia'}), 400
    
    code = request.json.get('code')
    port = request.json.get('port', 8000)
    expose_port = request.json.get('expose_port', True)
    
    try:
        result = run_service_in_sandbox(code, port, expose_port)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Błąd podczas uruchamiania usługi w piaskownicy: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_extensions.route('/sandbox/stop', methods=['POST'])
def stop_service_endpoint():
    """Zatrzymuje usługę uruchomioną w piaskownicy Docker"""
    if not request.json or 'container_name' not in request.json:
        return jsonify({'error': 'Brak nazwy kontenera do zatrzymania'}), 400
    
    container_name = request.json.get('container_name')
    
    try:
        result = stop_sandbox_service(container_name)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Błąd podczas zatrzymywania usługi: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Funkcja do rejestracji rozszerzeń API w aplikacji Flask
def register_extensions(app):
    """Rejestruje rozszerzenia API w aplikacji Flask"""
    app.register_blueprint(api_extensions, url_prefix='/api/v1')
    logger.info("Zarejestrowano rozszerzenia API")
    return app
