import json
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from db import Link, get_session
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


def serialize_link(link):
    """Chuyển đổi đối tượng Link thành dictionary"""
    headers_value = link.headers if hasattr(link, 'headers') and link.headers is not None else "{}"
    return {
        "id": link.id,
        "url": link.url,
        "status": link.status,
        "last_checked": link.last_checked.strftime("%Y-%m-%d %H:%M:%S") if link.last_checked else None,
        "headers": json.loads(headers_value)
    }


@app.route("/")
def root():
    return redirect("/docs")


@app.route("/docs")
def docs():
    # Return a simple HTML page with API documentation or redirect to a proper docs page
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Documentation</title>
    </head>
    <body>
        <h1>API Documentation</h1>
        <ul>
            <li><a href="/api/ping">GET /api/ping</a> - Ping all URLs and update status</li>
            <li><a href="/api/list">GET /api/list</a> - Get all URLs</li>
            <li>POST /api/add - Add new URL (use form data)</li>
            <li>PUT /api/update/<id> - Update URL and headers</li>
            <li>DELETE /api/delete/<id> - Delete URL by ID</li>
        </ul>
    </body>
    </html>
    """
    return html_content


@app.route("/api/ping", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "TRACE"])
def ping():
    db = get_session()
    links = db.query(Link).all()
    result = []
    for link in links:
        headers_value = link.headers if hasattr(link, 'headers') and link.headers is not None else "{}"
        headers = json.loads(headers_value)
        try:
            response = requests.get(str(link.url), headers=headers, timeout=10)
            status = bool(response.status_code == 200)
        except Exception:
            status = False
        
        # Update the link attributes
        link.status = status
        link.last_checked = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
        db.add(link)  # Cập nhật đối tượng vào session
        result.append(serialize_link(link))
    db.commit()  # Commit tất cả thay đổi sau khi xử lý xong tất cả links
    db.close()
    return jsonify({"success": True, "data": result})


@app.route("/api/list", methods=["GET"])
def list_links():
    db = get_session()
    links = db.query(Link).all()
    db.close()

    links_serialized = [serialize_link(link) for link in links]
    return jsonify({"success": True, "data": links_serialized})


@app.route("/api/add", methods=["POST"])
def add_link():
    data = request.get_json()
    if not data:
        # Handle form data as fallback
        url = request.form.get('url')
        id_value = request.form.get('id')
        headers = request.form.get('headers', '{}')
    else:
        url = data.get('url')
        id_value = data.get('id')
        headers = data.get('headers', {})
    
    if not url or not id_value:
        return jsonify({"success": False, "data": None}), 400
    
    db = get_session()
    # Convert headers dict to JSON string
    headers_json = json.dumps(headers) if isinstance(headers, dict) else headers
    link = Link(id=id_value, url=url, headers=headers_json)
    db.add(link)
    db.commit()
    db.refresh(link)  # Đảm bảo lấy dữ liệu mới nhất từ DB
    db.close()
    return jsonify({"success": True, "data": serialize_link(link)})


@app.route("/api/update/<id>", methods=["PUT"])
def update_link(id):
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "data": None, "message": "No data provided"}), 400
    
    db = get_session()
    link = db.query(Link).filter(Link.id == id).first()
    if not link:
        db.close()
        return jsonify({"success": False, "data": None, "message": "Link not found"}), 404
    
    # Update fields if provided
    if 'url' in data:
        link.url = data['url']
    if 'headers' in data:
        headers = data['headers']
        headers_json = json.dumps(headers) if isinstance(headers, dict) else headers
        link.headers = headers_json
    
    db.add(link)
    db.commit()
    db.refresh(link)
    db.close()
    
    return jsonify({"success": True, "data": serialize_link(link)})


@app.route("/api/delete/<id>", methods=["DELETE"])
def delete_link(id):
    db = get_session()
    link = db.query(Link).filter(Link.id == id).first()
    if link:
        db.delete(link)
        db.commit()
        db.close()
        return jsonify({"success": True, "data": serialize_link(link)})
    else:
        db.close()
        return jsonify({"success": False, "data": None}), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
