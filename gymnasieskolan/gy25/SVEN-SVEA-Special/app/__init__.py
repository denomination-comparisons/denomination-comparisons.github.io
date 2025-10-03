from flask import Flask, redirect, url_for, request
from dotenv import load_dotenv
import os
from .config import config
from .models.models import db

def create_app(config_name='default'):
    # Load environment variables
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    load_dotenv(dotenv_path=dotenv_path)

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)

    # Initialize extensions (placeholders, assume installed)
    # from flask_talisman import Talisman
    # talisman = Talisman(app)
    # from flask_login import LoginManager
    # login_manager = LoginManager(app)
    # from flask_caching import Cache
    # cache = Cache(app, config={'CACHE_TYPE': 'redis'})
    from flask_socketio import SocketIO
    socketio = SocketIO(app)
    from flask_babel import Babel
    babel = Babel(app)

    # --- Register Blueprints ---
    from .routes.tools_routes import tools_bp
    from .routes.teacher_routes import teacher_bp
    from .routes.student_routes import student_bp
    from .assignments.routes import assignments
    from .writing.routes import writing
    from .speaking.routes import speaking
    from .ai_chat.routes import ai_chat
    from .immersive.routes import immersive
    from .integrations.routes import integrations
    app.register_blueprint(tools_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(assignments, url_prefix='/assignments')
    app.register_blueprint(writing, url_prefix='/writing')
    app.register_blueprint(speaking, url_prefix='/speaking')
    app.register_blueprint(ai_chat, url_prefix='/ai_chat')
    app.register_blueprint(immersive, url_prefix='/immersive')
    app.register_blueprint(integrations, url_prefix='/integrations')

    # --- Register Custom Jinja Filter ---
    from .filters import format_datetime
    app.jinja_env.filters['format_datetime'] = format_datetime

    # --- Babel Locale Selector ---
    @babel.localeselector
    def get_locale():
        return request.accept_languages.best_match(['sv', 'en', 'ar'])  # Swedish default

    # --- Main Redirect ---
    @app.route('/')
    def index():
        return redirect(url_for('student.dashboard'))

    return app