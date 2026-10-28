from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts/search', methods=['GET'])
def search_post():
    global POSTS
    filtered_posts = []

    query_param = request.args.get('query_param', '')
    content = request.args.get('content', '')
    title = request.args.get('title', '')

    if query_param:
        filtered_posts = [
            post for post in POSTS
            if str(query_param) in str(post.get("title", "")) or str(query_param) in str(post.get("content", ""))
        ]
    elif content:
        filtered_posts = [
            post for post in POSTS
            if str(content) in str(post.get("content", ""))
        ]
    elif title:
        filtered_posts = [
            post for post in POSTS
            if str(title) in str(post.get("title", ""))
        ]

    return jsonify(filtered_posts), 200

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_posts(post_id):
    global POSTS

    data = request.json or {}

    has_post = [post for post in POSTS if post["id"] == post_id]
    if not has_post:
        return jsonify({"message": f"post with id {post_id} not found"}), 404

    title = data.get('title') or has_post[0]["title"]
    content = data.get('content') or has_post[0]["content"]

    POSTS = [post for post in POSTS if post["id"] != post_id]

    updated_post = {"id": post_id, "title": title, "content": content}
    POSTS.append(updated_post)

    return jsonify(updated_post), 200

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_posts(post_id):
    global POSTS

    has_post = [post for post in POSTS if post["id"] == post_id]
    if not has_post:
        return jsonify({"message": f"post with id {post_id} not found"}), 404

    POSTS = [post for post in POSTS if post["id"] != post_id]
    return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200


@app.route('/api/posts', methods=['POST'])
def add_posts():
    data = request.json or {}
    message = []

    title = data.get('title')
    if not title:
        message.append({'missing': 'title'})

    content = data.get('content')
    if not content:
        message.append({'missing': 'content'})

    if message:
        return jsonify(message), 400

    new_id = max((post["id"] for post in POSTS), default=0) + 1
    new_post = {"id": new_id, "title": str(title), "content": str(content)}
    POSTS.append(new_post)

    return jsonify(POSTS)


@app.route('/api/posts', methods=['GET'])
def get_posts():
    global POSTS

    sorted_posts = POSTS

    sort = request.args.get('sort', '')
    direction = request.args.get('direction', 'asc').lower()

    reverse_order = (direction == 'desc')

    if sort and 'title' in sort:
        sorted_posts = sorted(POSTS, key=lambda post: post.get("title", ""), reverse=reverse_order)
    elif sort and 'content' in sort:
        sorted_posts = sorted(POSTS, key=lambda post: post.get("content", ""), reverse=reverse_order)
    elif sort:
        return jsonify({ "error": f"{sort} ist keine gültige Sortierung"}), 400

    return jsonify(sorted_posts)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
