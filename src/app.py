from flask import Flask
import os
from flask_cors import CORS
from dotenv import load_dotenv
from .routes.users import bp as users_bp
from .routes.auth import bp as auth_bp
from .routes.clients import bp as clients_bp
from .routes.companies import bp as companies_bp
from .routes.docs import bp as docs_bp


load_dotenv()
app = Flask(__name__)
# CORS configurable por variable de entorno CORS_ORIGINS (separada por comas). Por defecto: "*".
_cors_origins_env = os.getenv("CORS_ORIGINS", "*")
if _cors_origins_env.strip() == "*":
    _cors_origins = "*"
else:
    _cors_origins = [o.strip() for o in _cors_origins_env.split(",") if o.strip()]
    if not _cors_origins:
        _cors_origins = "*"
CORS(app, resources={r"/*": {"origins": _cors_origins}}, supports_credentials=False)
app.register_blueprint(users_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(clients_bp)
app.register_blueprint(companies_bp)
app.register_blueprint(docs_bp)


@app.get("/")
def healthcheck():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

