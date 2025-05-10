#!/usr/bin/env python3
"""Example showing how to use the editor_sandbox decorator for automatic Docker sandbox setup
"""
import os
import sys
import json
import traceback
from flask import Flask, request, jsonify, render_template, send_from_directory, url_for
from devopy.decorators.editor_sandbox import editor_sandbox, EditorDockerSandbox

@editor_sandbox(
    base_image="python:3.12-slim",
    packages=["flask", "requests", "numpy", "pandas", "matplotlib"],
    ports={5001: 5001},
    volumes={os.path.dirname(os.path.abspath(__file__)): "/app/examples"},
    env_vars={"PYTHONUNBUFFERED": "1", "FLASK_ENV": "development"}
)
def create_app(sandbox=None):
    """Creates a Flask application with Docker sandbox integration"""
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'),
                static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'))
    
    @app.route('/')
    def index():
        """Main page with the editor interface"""
        return render_template('editor.html')
    
    @app.route('/api/docker-status')
    def docker_status():
        """Endpoint returning Docker sandbox status"""
        if not sandbox or not sandbox.ready:
            return jsonify({
                'ready': False,
                'error': 'Docker sandbox is not ready'
            })
        
        return jsonify({
            'ready': True,
            'status': sandbox.status,
            'container_id': sandbox.container_id,
            'base_image': sandbox.base_image
        })
    
    @app.route('/api/docker-execute', methods=['POST'])
    def docker_execute():
        """Endpoint for executing commands in the Docker sandbox"""
        if not sandbox or not sandbox.ready:
            return jsonify({
                'error': 'Docker sandbox is not ready'
            })
        
        try:
            data = request.json
            command = data.get('command', '')
            
            if not command:
                return jsonify({'error': 'No command provided'})
            
            # Split command into arguments list
            command_args = command.split()
            
            # Execute command in container
            result = sandbox.execute(command_args)
            
            return jsonify(result)
        except Exception as e:
            return jsonify({
                'error': str(e),
                'traceback': traceback.format_exc()
            })
    
    @app.route('/api/execute-python', methods=['POST'])
    def execute_python():
        """Endpoint for executing Python code in the Docker sandbox"""
        if not sandbox or not sandbox.ready:
            return jsonify({
                'error': 'Docker sandbox is not ready'
            })
        
        try:
            data = request.json
            code = data.get('code', '')
            
            if not code:
                return jsonify({'error': 'No code provided'})
            
            # Save code to temporary file in container
            code_escaped = code.replace("'", "'\\''")
            setup_result = sandbox.execute([
                "bash", "-c", f"echo '{code_escaped}' > /tmp/temp_code.py"
            ])
            
            if setup_result.get('returncode', 1) != 0:
                return jsonify({
                    'error': 'Failed to create temporary file',
                    'stderr': setup_result.get('stderr', '')
                })
            
            # Execute Python code
            result = sandbox.execute(["python", "/tmp/temp_code.py"])
            
            # Remove temporary file
            sandbox.execute(["rm", "/tmp/temp_code.py"])
            
            return jsonify(result)
        except Exception as e:
            return jsonify({
                'error': str(e),
                'traceback': traceback.format_exc()
            })
    
    @app.route('/api/restart-container', methods=['POST'])
    def restart_container():
        """Endpoint for restarting the Docker container"""
        if not sandbox:
            return jsonify({
                'success': False,
                'error': 'Docker sandbox is not available'
            })
        
        try:
            # Stop current container
            sandbox.cleanup()
            
            # Start new container
            sandbox.start()
            
            return jsonify({
                'success': True,
                'container_id': sandbox.container_id
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            })
    
    @app.route('/api/save-file', methods=['POST'])
    def save_file():
        """Endpoint for saving files in the container"""
        if not sandbox or not sandbox.ready:
            return jsonify({
                'success': False,
                'error': 'Docker sandbox is not ready'
            })
        
        try:
            data = request.json
            filename = data.get('filename', '')
            content = data.get('content', '')
            
            if not filename:
                return jsonify({
                    'success': False,
                    'error': 'No filename provided'
                })
            
            # Security check to prevent directory traversal
            if '..' in filename or filename.startswith('/'):
                return jsonify({
                    'success': False,
                    'error': 'Invalid filename'
                })
            
            # Save file in container
            content_escaped = content.replace("'", "'\\''")
            result = sandbox.execute([
                "bash", "-c", f"echo '{content_escaped}' > /app/{filename}"
            ])
            
            if result.get('returncode', 1) != 0:
                return jsonify({
                    'success': False,
                    'error': 'Failed to save file',
                    'stderr': result.get('stderr', '')
                })
            
            return jsonify({
                'success': True,
                'filename': filename
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            })
    
    @app.route('/api/get-example')
    def get_example():
        """Endpoint for getting example files"""
        try:
            example_file = request.args.get('file', '')
            
            if not example_file:
                return jsonify({
                    'success': False,
                    'error': 'No file specified'
                })
            
            # Security check to prevent directory traversal
            if '..' in example_file or example_file.startswith('/'):
                return jsonify({
                    'success': False,
                    'error': 'Invalid filename'
                })
            
            # Get example file path
            example_path = os.path.join(app.static_folder, 'examples', example_file)
            
            # Check if file exists
            if not os.path.isfile(example_path):
                return jsonify({
                    'success': False,
                    'error': f'Example file {example_file} not found'
                })
            
            # Read file content
            with open(example_path, 'r') as f:
                content = f.read()
            
            return jsonify({
                'success': True,
                'content': content,
                'filename': example_file
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            })
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=True)
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        """Strona główna edytora"""
        return render_template_string(HTML_TEMPLATE)
    
    @app.route('/api/docker-status')
    def docker_status():
        """Endpoint zwracający status piaskownicy Docker"""
        if not sandbox or not sandbox.ready:
            return jsonify({
                'ready': False,
                'error': 'Piaskownica Docker nie jest gotowa'
            })
        
        return jsonify({
            'ready': True,
            'status': sandbox.status,
            'container_id': sandbox.container_id,
            'base_image': sandbox.base_image
        })
    
    @app.route('/api/docker-execute', methods=['POST'])
    def docker_execute():
        """Endpoint do wykonywania poleceń w piaskownicy Docker"""
        if not sandbox or not sandbox.ready:
            return jsonify({
                'error': 'Piaskownica Docker nie jest gotowa'
            })
        
        try:
            data = request.json
            command = data.get('command', '')
            
            if not command:
                return jsonify({'error': 'Nie podano polecenia'})
            
            # Podziel polecenie na listę argumentów
            command_args = command.split()
            
            # Wykonaj polecenie w kontenerze
            result = sandbox.execute(command_args)
            
            return jsonify(result)
        except Exception as e:
            return jsonify({
                'error': str(e),
                'traceback': traceback.format_exc()
            })
    
    @app.route('/api/execute-python', methods=['POST'])
    def execute_python():
        """Endpoint do wykonywania kodu Python w piaskownicy Docker"""
        if not sandbox or not sandbox.ready:
            return jsonify({
                'error': 'Piaskownica Docker nie jest gotowa'
            })
        
        try:
            data = request.json
            code = data.get('code', '')
            
            if not code:
                return jsonify({'error': 'Nie podano kodu'})
            
            # Zapisz kod do tymczasowego pliku w kontenerze
            code_escaped = code.replace("'", "'\\''")
            setup_result = sandbox.execute([
                "bash", "-c", f"echo '{code_escaped}' > /tmp/temp_code.py"
            ])
            
            if setup_result.get('returncode', 1) != 0:
                return jsonify({
                    'error': 'Nie udało się utworzyć pliku tymczasowego',
                    'stderr': setup_result.get('stderr', '')
                })
            
            # Wykonaj kod Python
            result = sandbox.execute(["python", "/tmp/temp_code.py"])
            
            # Usuń tymczasowy plik
            sandbox.execute(["rm", "/tmp/temp_code.py"])
            
            return jsonify(result)
        except Exception as e:
            return jsonify({
                'error': str(e),
                'traceback': traceback.format_exc()
            })
    
    @app.route('/api/restart-container', methods=['POST'])
    def restart_container():
        """Endpoint do restartowania kontenera Docker"""
        if not sandbox:
            return jsonify({
                'success': False,
                'error': 'Piaskownica Docker nie jest dostępna'
            })
        
        try:
            # Zatrzymaj bieżący kontener
            sandbox.cleanup()
            
            # Uruchom nowy kontener
            sandbox.start()
            
            return jsonify({
                'success': True,
                'container_id': sandbox.container_id
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            })
    
    @app.route('/api/save-file', methods=['POST'])
    def save_file():
        """Endpoint do zapisywania plików w kontenerze"""
        if not sandbox or not sandbox.ready:
            return jsonify({
                'success': False,
                'error': 'Piaskownica Docker nie jest gotowa'
            })
        
        try:
            data = request.json
            filename = data.get('filename', '')
            content = data.get('content', '')
            
            if not filename:
                return jsonify({
                    'success': False,
                    'error': 'Nie podano nazwy pliku'
                })
            
            # Zabezpieczenie przed wyjściem poza katalog
            if '..' in filename or filename.startswith('/'):
                return jsonify({
                    'success': False,
                    'error': 'Nieprawidłowa nazwa pliku'
                })
            
            # Zapisz plik w kontenerze
            content_escaped = content.replace("'", "'\\''")
            result = sandbox.execute([
                "bash", "-c", f"echo '{content_escaped}' > /app/{filename}"
            ])
            
            if result.get('returncode', 1) != 0:
                return jsonify({
                    'success': False,
                    'error': 'Nie udało się zapisać pliku',
                    'stderr': result.get('stderr', '')
                })
            
            return jsonify({
                'success': True,
                'filename': filename
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            })
    
    @app.route('/api/list-files', methods=['GET'])
    def list_files():
        """Endpoint do listowania plików w kontenerze"""
        if not sandbox or not sandbox.ready:
            return jsonify({
                'success': False,
                'error': 'Piaskownica Docker nie jest gotowa'
            })
        
        try:
            # Listuj pliki w katalogu /app
            result = sandbox.execute(["ls", "-la", "/app"])
            
            if result.get('returncode', 1) != 0:
                return jsonify({
                    'success': False,
                    'error': 'Nie udało się wylistować plików',
                    'stderr': result.get('stderr', '')
                })
            
            return jsonify({
                'success': True,
                'files': result.get('stdout', '')
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            })
    
    @app.route('/api/install-package', methods=['POST'])
    def install_package():
        """Endpoint do instalowania pakietów Python w kontenerze"""
        if not sandbox or not sandbox.ready:
            return jsonify({
                'success': False,
                'error': 'Piaskownica Docker nie jest gotowa'
            })
        
        try:
            data = request.json
            package = data.get('package', '')
            
            if not package:
                return jsonify({
                    'success': False,
                    'error': 'Nie podano nazwy pakietu'
                })
            
            # Instalacja pakietu
            result = sandbox.execute(["pip", "install", package])
            
            return jsonify({
                'success': result.get('returncode', 1) == 0,
                'stdout': result.get('stdout', ''),
                'stderr': result.get('stderr', '')
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            })
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=True)
