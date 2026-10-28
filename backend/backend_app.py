import json
from datetime import datetime, date

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL="/api/docs"  # (1) swagger endpoint e.g. HTTP://localhost:5002/api/docs
API_URL="/static/masterblog.json" # (2) ensure you create this dir and file

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API'
    }
)


app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

__json_file = "blog.json"

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]

SCHEMA = {
    "id": {
        "type": int,
        "required": True
    },
    "title": {
        "type": str,
        "required": True
    },
    "content": {
        "type": str,
        "required": True
    },
    "author": {
        "type": str,
        "required": False
    },
    "date": {
        "type": datetime,
        "required": True
    }
}


def validate_payload(data, schema):
    if not isinstance(data, dict):
        return "Payload muss ein JSON-Objekt sein", 400

    # 1. Auf unbekannte / unerlaubte Felder prüfen
    for field in data.keys():
        if field not in schema:
            return f"Unbekanntes oder nicht erlaubtes Feld '{field}'", 400

    # 2. Schema-Regeln durchgehen (Pflichtfelder & Typen)
    for field, rules in schema.items():
        expected_type = rules["type"]
        is_required = rules["required"]

        # Prüfen, ob ein Pflichtfeld fehlt
        if is_required and field not in data:
            return f"Pflichtfeld '{field}' fehlt", 400

        # Wenn das Feld vorhanden (und nicht None) ist, Typ prüfen
        if field in data and data[field] is not None:
            val = data[field]

            # Spezielle Prüfung für datetime-Strings
            if expected_type == datetime and isinstance(val, str):
                try:
                    datetime.fromisoformat(val)
                except ValueError:
                    return f"Feld '{field}' muss ein gültiger ISO-Datumsstring sein", 400

            # Allgemeine Typprüfung
            elif not isinstance(val, expected_type):
                return f"Feld '{field}' muss vom Typ {expected_type.__name__} sein", 400

    return None, None

def write_json(data):
    data = sorted(data, key=lambda post: post["id"])
    with open(__json_file, "w", encoding="utf-8") as json_data:
        json.dump(data, json_data, indent=4)

def read_json():
    with open(__json_file, "r", encoding="utf-8") as json_data:
        return json.load(json_data)

@app.route('/api/posts/search', methods=['GET'])
def search_post():

    this_posts = read_json()
    filtered_posts = []

    query_param = request.args.get('query_param', '')
    content = request.args.get('content', '')
    title = request.args.get('title', '')
    author = request.args.get('author', '')

    if query_param:
        filtered_posts = [
            post for post in this_posts
            if str(query_param) in str(post.get("title", ""))
               or str(query_param) in str(post.get("content", ""))
               or str(query_param) in str(post.get("author", ""))
        ]
    elif content:
        filtered_posts = [
            post for post in this_posts
            if str(content) in str(post.get("content", ""))
        ]
    elif title:
        filtered_posts = [
            post for post in this_posts
            if str(title) in str(post.get("title", ""))
        ]
    elif author:
        filtered_posts = [
            post for post in this_posts
            if str(title) in str(post.get("author", ""))
        ]

    return jsonify(filtered_posts), 200


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_posts(post_id):

    this_posts = read_json()

    data = request.json or {}

    this_post = [post for post in this_posts if post["id"] == post_id]
    if not this_post:
        return jsonify({"message": f"post with id {post_id} not found"}), 404

    this_posts = [post for post in this_posts if post["id"] != post_id]

    filtered_data = {k: v for k, v in data.items() if v is not None and v != ""}
    updated_post = {**this_post[0], **filtered_data}
    if not updated_post.get("date"):
        updated_post["date"] = datetime(1970, 1, 1).date().isoformat()

    error_msg, status_code = validate_payload(updated_post, SCHEMA)
    if error_msg:
        return jsonify({"error": error_msg}), status_code

    this_posts.append(updated_post)
    write_json(this_posts)

    return jsonify(updated_post), 200

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_posts(post_id):
    this_posts = read_json()

    has_post = [post for post in this_posts if post["id"] == post_id]
    if not has_post:
        return jsonify({"message": f"post with id {post_id} not found"}), 404

    this_posts = [post for post in this_posts if post["id"] != post_id]
    write_json(this_posts)

    return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200


@app.route('/api/posts', methods=['POST'])
def add_posts():

    this_posts = read_json()
    data = request.json or {}

    # id erzeugen
    this_id = max((post.get("id", 0) for post in this_posts), default=0) + 1
    data.update({"id": this_id})

    # aktuelles Datum erzeugen
    this_date = date.today().isoformat()
    data.update({"date": this_date})

    error_msg, status_code = validate_payload(data, SCHEMA)
    if error_msg:
        return jsonify({"error": error_msg}), status_code

    this_posts.append(data)

    write_json(this_posts)

    return jsonify(this_posts)


@app.route('/api/posts', methods=['GET'])
def get_posts():

    this_posts = read_json()

    sort = request.args.get('sort', '')
    direction = request.args.get('direction', 'asc').lower()

    reverse_order = (direction == 'desc')

    if sort and 'title' in sort:
        this_posts = sorted(this_posts, key=lambda post: post.get("title", ""), reverse=reverse_order)
    elif sort and 'content' in sort:
        this_posts = sorted(this_posts, key=lambda post: post.get("content", ""), reverse=reverse_order)
    elif sort and 'author' in sort:
        this_posts = sorted(this_posts, key=lambda post: post.get("author", ""), reverse=reverse_order)
    elif sort and 'date' in sort:
        this_posts = sorted(this_posts, key=lambda post: post.get("date", ""), reverse=reverse_order)
    elif sort:
        return jsonify({ "error": f"{sort} ist keine gültige Sortierung"}), 400

    return jsonify(this_posts)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
