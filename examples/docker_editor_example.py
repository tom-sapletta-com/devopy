#!/usr/bin/env python3
"""Flask application for matrix layout editor with mode switching
"""
import os
import sys
import traceback
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory, url_for

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
def create_app():
    """Create and configure the Flask application"""
    logger = logging.getLogger('matrix_editor')
    logger.info("Creating Flask application")
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'),
                static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'))
    logger.debug(f"Current working directory: {os.getcwd()}")
    logger.debug(f"Template folder: {app.template_folder}")
    logger.debug(f"Static folder: {app.static_folder}")
    
    @app.route('/')
    def index():
        """Render the main editor page"""
        logger.info("Rendering main editor page")
        logger.debug(f"Available templates: {os.listdir(app.template_folder) if os.path.exists(app.template_folder) else 'Template folder not found'}")
        return render_template('editor.html')
    
    @app.route('/api/status')
    def app_status():
        """Endpoint returning application status"""
        logger.info("Requesting application status")
        return jsonify({
            'ready': True,
            'status': 'running',
            'version': '1.0.0'
        })
    
    @app.route('/api/modes')
    def get_modes():
        """Endpoint returning available modes"""
        logger.info("Requesting available modes")
        return jsonify({
            'modes': [
                {'id': 'development', 'name': 'Development', 'description': 'Standard editor features'},
                {'id': 'testing', 'name': 'Testing', 'description': 'Test lists and results'},
                {'id': 'monitoring', 'name': 'Monitoring', 'description': 'System resource usage and logs'},
                {'id': 'production', 'name': 'Production', 'description': 'Deployment status and alerts'}
            ]
        })
    
    @app.route('/api/execute-code', methods=['POST'])
    def execute_code():
        """Endpoint for executing code (simulated)"""
        try:
            data = request.json
            code = data.get('code', '')
            mode = data.get('mode', 'development')
            
            if not code:
                return jsonify({'error': 'No code provided'})
            
            # Simulate code execution based on mode
            result = {
                'success': True,
                'mode': mode,
                'output': f"Executed in {mode} mode: {len(code)} characters of code",
                'execution_time': 0.5
            }
            
            return jsonify(result)
        except Exception as e:
            return jsonify({
                'error': str(e),
                'traceback': traceback.format_exc()
            })
    
    @app.route('/api/update-layout', methods=['POST'])
    def update_layout():
        """Endpoint for updating the matrix layout configuration"""
        try:
            data = request.json
            layout = data.get('layout', {})
            
            # Simulate layout update
            logger.info(f"Updating layout: {layout}")
            
            return jsonify({
                'success': True,
                'layout': layout
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            })
    
    @app.route('/api/save-content', methods=['POST'])
    def save_content():
        """Endpoint for saving content in the editor"""
        try:
            data = request.json
            content = data.get('content', '')
            panel_id = data.get('panel_id', '')
            mode = data.get('mode', 'development')
            
            if not panel_id:
                return jsonify({
                    'success': False,
                    'error': 'No panel ID provided'
                })
            
            # Simulate saving content
            logger.info(f"Saving content for panel {panel_id} in {mode} mode")
            
            return jsonify({
                'success': True,
                'panel_id': panel_id,
                'mode': mode,
                'content_length': len(content)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            })
    
    @app.route('/api/get-panel-content')
    def get_panel_content():
        """Endpoint for getting panel content based on mode"""
        try:
            panel_id = request.args.get('panel_id', '')
            mode = request.args.get('mode', 'development')
            
            if not panel_id:
                return jsonify({
                    'success': False,
                    'error': 'No panel ID specified'
                })
            
            # Generate sample content based on panel and mode
            content = generate_sample_content(panel_id, mode)
            
            return jsonify({
                'success': True,
                'panel_id': panel_id,
                'mode': mode,
                'content': content
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            })
    
    def generate_sample_content(panel_id, mode):
        """Generate sample content for panels based on mode"""
        content_map = {
            'media': {
                'development': 'Media panel in Development mode - Upload and manage media files',
                'testing': 'Media panel in Testing mode - Test media files and formats',
                'monitoring': 'Media panel in Monitoring mode - Media usage statistics',
                'production': 'Media panel in Production mode - Production media assets'
            },
            'edit': {
                'development': 'Edit panel in Development mode - Code editor with syntax highlighting',
                'testing': 'Edit panel in Testing mode - Test case editor',
                'monitoring': 'Edit panel in Monitoring mode - Log viewer and analyzer',
                'production': 'Edit panel in Production mode - Deployment configuration'
            },
            'preview': {
                'development': 'Preview panel in Development mode - Live preview of code',
                'testing': 'Preview panel in Testing mode - Test results and coverage',
                'monitoring': 'Preview panel in Monitoring mode - System metrics and graphs',
                'production': 'Preview panel in Production mode - Production status'
            },
            'communication': {
                'development': 'Communication panel in Development mode - Team chat',
                'testing': 'Communication panel in Testing mode - Test reports',
                'monitoring': 'Communication panel in Monitoring mode - Alerts and notifications',
                'production': 'Communication panel in Production mode - Deployment logs'
            }
        }
        
        return content_map.get(panel_id, {}).get(mode, f"Default content for {panel_id} in {mode} mode")
    
    return app

if __name__ == '__main__':
    # Find an available port dynamically
    import socket
    s = socket.socket()
    s.bind(('', 0))
    available_port = s.getsockname()[1]
    s.close()
    
    print(f"Starting application on port {available_port}")
    app = create_app()
    app.run(host='0.0.0.0', port=available_port, debug=True)
