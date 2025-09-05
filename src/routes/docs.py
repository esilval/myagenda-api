from __future__ import annotations

import os
from flask import Blueprint, Response, current_app


bp = Blueprint("docs", __name__)


@bp.get("/openapi")
def get_openapi() -> Response:
    # Resolve path to docs/openapi.yaml relative to project root
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    spec_path = os.path.join(base_dir, "docs", "openapi.yaml")
    if not os.path.exists(spec_path):
        return Response("openapi.yaml not found", status=404)
    with open(spec_path, "r", encoding="utf-8") as f:
        content = f.read()
    return Response(content, mimetype="application/yaml")


@bp.get("/docs")
def swagger_ui() -> Response:
    # Minimal Swagger UI page that loads the spec from /openapi
    html = """
    <!doctype html>
    <html lang="es">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>MyAgenda API Docs</title>
      <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
    </head>
    <body>
      <div id="swagger-ui"></div>
      <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
      <script>
        window.onload = () => {
          window.ui = SwaggerUIBundle({
            url: '/openapi',
            dom_id: '#swagger-ui',
            presets: [SwaggerUIBundle.presets.apis],
            layout: 'BaseLayout'
          });
        };
      </script>
    </body>
    </html>
    """
    return Response(html, mimetype="text/html")


