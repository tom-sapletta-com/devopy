#!/usr/bin/env python3
"""
Simple matrix layout editor with mode switching functionality
"""
import os
import sys
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
        return render_template('editor.html')
    
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
    
    @app.route('/api/panel-content/<panel_id>')
    def get_panel_content(panel_id):
        """Endpoint for getting panel content based on mode"""
        mode = request.args.get('mode', 'development')
        logger.info(f"Getting content for panel {panel_id} in {mode} mode")
        
        content = generate_sample_content(panel_id, mode)
        
        return jsonify({
            'success': True,
            'panel_id': panel_id,
            'mode': mode,
            'content': content
        })
    
    @app.route('/api/layout', methods=['POST'])
    def update_layout():
        """Endpoint for updating the matrix layout configuration"""
        data = request.json
        layout = data.get('layout', {})
        
        logger.info(f"Updating layout: {layout}")
        
        return jsonify({
            'success': True,
            'layout': layout
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
    # Use PORT environment variable if available, otherwise find an available port
    import os
    import socket
    
    port = os.environ.get('PORT')
    if port:
        port = int(port)
        print(f"Starting matrix editor application on port {port} (from environment variable)")
    else:
        # Find an available port dynamically
        s = socket.socket()
        s.bind(('', 0))
        port = s.getsockname()[1]
        s.close()
        print(f"Starting matrix editor application on port {port} (dynamically assigned)")
    
    app = create_app()
    app.run(host='0.0.0.0', port=port, debug=True)
