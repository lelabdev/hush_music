# app.py
from flask import Flask
import os
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Crée le dossier uploads si absent
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Enregistre les routes
    from routes.main import bp as main_bp

    app.register_blueprint(main_bp)

    return app


# === Pour local : python app.py ===
if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=50000, debug=True)
