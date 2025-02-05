from flask_cors import CORS
from flask import Flask, Blueprint
    
def create_app(name: str = None, bps: list[Blueprint] = None, template_folder: str = None, static_folder: str = None, static_url_path: str = None) -> Flask:
    
    app = Flask(
        name if name else 'Self-Bootstrapping Model Service',
        template_folder = template_folder, 
        static_folder = static_folder,
        static_url_path = static_url_path
    )
    
    from ..app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    if bps is not None:
        for bp in bps:
            app.register_blueprint(bp)

    CORS(app)

    return app
