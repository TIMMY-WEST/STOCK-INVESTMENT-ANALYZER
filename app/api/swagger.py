# -*- coding: utf-8 -*-
"""Swagger UI configuration module.

Provides OpenAPI 3.0 specification and displays API documentation with Swagger UI.
"""

import os

from flask import (
    Blueprint,
    current_app,
    jsonify,
    make_response,
    render_template_string,
    request,
)
import yaml


# Swagger UIブループリント作成
swagger_bp = Blueprint("swagger", __name__, url_prefix="/api/docs")

# Swagger UI HTMLテンプレート
SWAGGER_UI_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Stock Investment Analyzer API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css" />
    <style>
        html {
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }
        *, *:before, *:after {
            box-sizing: inherit;
        }
        body {
            margin:0;
            background: #fafafa;
        }
        .swagger-ui .topbar {
            background-color: #2c3e50;
        }
        .swagger-ui .topbar .download-url-wrapper {
            display: none;
        }
        .swagger-ui .info .title {
            color: #2c3e50;
        }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                url: '{{ spec_url }}',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                validatorUrl: null,
                tryItOutEnabled: true,
                supportedSubmitMethods: ['get', 'post', 'put', 'delete', 'patch'],
                docExpansion: 'list',
                defaultModelsExpandDepth: 1,
                defaultModelExpandDepth: 1,
                displayRequestDuration: true,
                filter: true,
                showExtensions: true,
                showCommonExtensions: true,
                requestInterceptor: function(request) {
                    // リクエストヘッダーにContent-Typeを追加
                    if (request.method !== 'GET' && request.method !== 'DELETE') {
                        request.headers['Content-Type'] = 'application/json';
                    }
                    return request;
                },
                responseInterceptor: function(response) {
                    // レスポンスログ出力（開発時のデバッグ用）
                    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                        console.log('API Response:', response);
                    }
                    return response;
                }
            });

            // カスタムCSS適用
            const style = document.createElement('style');
            style.textContent = `
                .swagger-ui .scheme-container {
                    background: #fff;
                    box-shadow: 0 1px 2px 0 rgba(0,0,0,.15);
                }
                .swagger-ui .info .title {
                    font-size: 36px;
                    margin: 0;
                }
                .swagger-ui .info .description {
                    font-size: 14px;
                    margin: 20px 0;
                }
                .swagger-ui .opblock.opblock-post {
                    border-color: #49cc90;
                    background: rgba(73,204,144,.1);
                }
                .swagger-ui .opblock.opblock-get {
                    border-color: #61affe;
                    background: rgba(97,175,254,.1);
                }
                .swagger-ui .opblock.opblock-put {
                    border-color: #fca130;
                    background: rgba(252,161,48,.1);
                }
                .swagger-ui .opblock.opblock-delete {
                    border-color: #f93e3e;
                    background: rgba(249,62,62,.1);
                }
            `;
            document.head.appendChild(style);
        };
    </script>
</body>
</html>
"""


@swagger_bp.route("/")
def swagger_ui():
    """Display Swagger UI page.

    Returns:
        str: Swagger UI HTML page
    """
    try:
        # OpenAPI仕様書のURLを生成
        spec_url = f"{request.url_root.rstrip('/')}/api/docs/openapi.json"

        return render_template_string(SWAGGER_UI_TEMPLATE, spec_url=spec_url)
    except Exception as e:
        current_app.logger.error(
            f"Swagger UI page generation failed: {str(e)}"
        )
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Swagger UIページの生成に失敗しました",
                    "error": {"code": "SWAGGER_UI_ERROR", "message": str(e)},
                }
            ),
            500,
        )


@swagger_bp.route("/openapi.json")
def openapi_spec():
    """Provide OpenAPI 3.0 specification in JSON format.

    Returns:
        dict: OpenAPI specification (JSON format)
    """
    try:
        # OpenAPI仕様書ファイルのパス
        # 本番環境とテスト環境でパスを調整
        import sys

        if (
            "pytest" in sys.modules
            or "test" in current_app.name
            or current_app.config.get("TESTING")
        ):
            # テスト環境の場合 - tests/unit/api/openapi.yamlを使用
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            spec_file_path = os.path.join(
                project_root, "tests", "unit", "api", "openapi.yaml"
            )
        else:
            # 本番環境の場合
            spec_file_path = os.path.join(
                current_app.root_path, "api", "openapi.yaml"
            )

        # ファイルの存在確認
        if not os.path.exists(spec_file_path):
            current_app.logger.error(
                f"OpenAPI spec file not found: {spec_file_path}"
            )
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "OpenAPI仕様書ファイルが見つかりません",
                        "error": {
                            "code": "SPEC_FILE_NOT_FOUND",
                            "message": f"ファイルパス: {spec_file_path}",
                        },
                    }
                ),
                404,
            )

        # YAMLファイルを読み込み
        with open(spec_file_path, "r", encoding="utf-8") as file:
            spec_data = yaml.safe_load(file)

        # サーバーURLを動的に設定
        if "servers" in spec_data:
            # 現在のリクエストのベースURLを取得
            from flask import request

            base_url = f"{request.scheme}://{request.host}"

            # 既存のサーバー設定を更新
            for server in spec_data["servers"]:
                if (
                    "localhost" in server["url"]
                    or "127.0.0.1" in server["url"]
                ):
                    server["url"] = base_url

        return jsonify(spec_data)

    except yaml.YAMLError as e:
        current_app.logger.error(f"YAML parsing error: {str(e)}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "OpenAPI仕様書の解析に失敗しました",
                    "error": {"code": "YAML_PARSE_ERROR", "message": str(e)},
                }
            ),
            500,
        )
    except Exception as e:
        current_app.logger.error(f"OpenAPI spec generation failed: {str(e)}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "OpenAPI仕様書の生成に失敗しました",
                    "error": {
                        "code": "SPEC_GENERATION_ERROR",
                        "message": str(e),
                    },
                }
            ),
            500,
        )


@swagger_bp.route("/openapi.yaml")
def openapi_yaml():
    """Provide OpenAPI specification in YAML format.

    Returns:
        str: OpenAPI specification (YAML format)
    """
    try:
        # OpenAPI仕様書ファイルのパス
        # 本番環境とテスト環境でパスを調整
        if "test" in current_app.name or current_app.root_path.endswith(
            "tests/api"
        ):
            # テスト環境の場合
            spec_file_path = os.path.join(
                current_app.root_path, "openapi.yaml"
            )
        else:
            # 本番環境の場合
            spec_file_path = os.path.join(
                current_app.root_path, "api", "openapi.yaml"
            )

        # ファイルの存在確認
        if not os.path.exists(spec_file_path):
            current_app.logger.error(
                f"OpenAPI spec file not found: {spec_file_path}"
            )
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "OpenAPI仕様書ファイルが見つかりません",
                        "error": {
                            "code": "SPEC_FILE_NOT_FOUND",
                            "message": f"ファイルパス: {spec_file_path}",
                        },
                    }
                ),
                404,
            )

        # YAMLファイルを読み込み
        with open(spec_file_path, "r", encoding="utf-8") as file:
            yaml_content = file.read()

        # レスポンスを作成
        response = make_response(yaml_content)
        response.headers["Content-Type"] = "application/x-yaml"
        response.headers["Cache-Control"] = "public, max-age=3600"

        return response

    except Exception as e:
        current_app.logger.error(f"OpenAPI YAML generation failed: {str(e)}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "OpenAPI仕様書（YAML）の生成に失敗しました",
                    "error": {
                        "code": "YAML_GENERATION_ERROR",
                        "message": str(e),
                    },
                }
            ),
            500,
        )


@swagger_bp.route("/redoc/")
def redoc_ui():
    """Display ReDoc UI page (alternative documentation viewer).

    Returns:
        str: ReDoc UI HTML page
    """
    redoc_template = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>Stock Investment Analyzer API Documentation - ReDoc</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
        <style>
            body {
                margin: 0;
                padding: 0;
            }
        </style>
    </head>
    <body>
        <redoc spec-url="{{ spec_url }}"></redoc>
        <script src="https://cdn.jsdelivr.net/npm/redoc@2.1.3/bundles/redoc.standalone.js"></script>
    </body>
    </html>
    """

    try:
        from flask import request

        spec_url = f"{request.url_root.rstrip('/')}/api/docs/openapi.json"

        return render_template_string(redoc_template, spec_url=spec_url)
    except Exception as e:
        current_app.logger.error(f"ReDoc UI page generation failed: {str(e)}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "ReDoc UIページの生成に失敗しました",
                    "error": {"code": "REDOC_UI_ERROR", "message": str(e)},
                }
            ),
            500,
        )


@swagger_bp.route("/health")
def docs_health():
    """Perform health check for documentation service.

    Returns:
        dict: Health check result
    """
    try:
        # OpenAPI仕様書ファイルの存在確認
        spec_file_path = os.path.join(
            current_app.root_path, "..", "docs", "api", "openapi.md"
        )

        spec_file_exists = os.path.exists(spec_file_path)

        return jsonify(
            {
                "status": "success",
                "message": "ドキュメントサービスは正常に動作しています",
                "data": {
                    "service": "swagger-docs",
                    "status": "healthy",
                    "spec_file_exists": spec_file_exists,
                    "spec_file_path": spec_file_path,
                    "endpoints": {
                        "swagger_ui": "/api/docs/",
                        "openapi_spec": "/api/docs/openapi.json",
                        "redoc_ui": "/api/docs/redoc",
                    },
                },
            }
        )
    except Exception as e:
        current_app.logger.error(f"Docs health check failed: {str(e)}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "ドキュメントサービスのヘルスチェックに失敗しました",
                    "error": {
                        "code": "DOCS_HEALTH_CHECK_ERROR",
                        "message": str(e),
                    },
                }
            ),
            500,
        )


# エラーハンドラー
@swagger_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return (
        jsonify(
            {
                "status": "error",
                "message": "ページが見つかりません",
                "error": {
                    "code": "NOT_FOUND",
                    "message": "リクエストされたページまたはリソースが見つかりません",
                },
            }
        ),
        404,
    )


@swagger_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return (
        jsonify(
            {
                "status": "error",
                "message": "内部サーバーエラーが発生しました",
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "サーバー内部でエラーが発生しました",
                },
            }
        ),
        500,
    )
