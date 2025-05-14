from flask import Flask
from extensions import db, login_manager
from models.user import User
from routes.auth import auth_bp
from routes.professor import professor_bp
from routes.student import student_bp
from routes.profile import profile_bp
from routes.main import main_bp
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def create_app():
    print("⏳ Iniciando creación de la app Flask...")

    # Inicialización directa para Render
    app = Flask(__name__)


    try:
        # Configuración básica
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///tutoring.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['UPLOAD_FOLDER'] = 'static/uploads/profile_pics'

        # Crear carpeta de carga si no existe
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Inicializar extensiones
        db.init_app(app)
        login_manager.init_app(app)

        # Configurar login manager
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        # Registrar blueprints
        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(professor_bp)
        app.register_blueprint(student_bp)
        app.register_blueprint(profile_bp)

#         # Ruta de prueba
#         @app.route('/ping')
#         def ping():
#             return 'pong'

#         # Crear las tablas si no existen
#         with app.app_context():
#             db.create_all()

#         print("✅ Flask app cargada correctamente")

    except Exception as e:
        print("❌ ERROR al iniciar Flask:", e)

    print("✅ Flask app cargada correctamente")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

...

app = create_app() 


