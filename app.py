from flask import Flask, request, jsonify
import boto3
import uuid
from datetime import datetime
from botocore.exceptions import ClientError
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
# DynamoDB setup
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('tasks-hemanshu2026')


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200


@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()

    if not data or 'title' not in data:
        return jsonify({"error": "title is required"}), 400

    task_id = str(uuid.uuid4())
    task = {
        'task_id': task_id,
        'title': data['title'],
        'description': data.get('description', ''),
        'status': data.get('status', 'pending'),
        'created_at': datetime.utcnow().isoformat()
    }

    try:
        table.put_item(Item=task)
        return jsonify(task), 201
    except ClientError as e:
        return jsonify({"error": str(e)}), 500


@app.route('/tasks', methods=['GET'])
def list_tasks():
    try:
        response = table.scan()
        return jsonify(response.get('Items', [])), 200
    except ClientError as e:
        return jsonify({"error": str(e)}), 500


@app.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    try:
        response = table.get_item(Key={'task_id': task_id})
        item = response.get('Item')
        if not item:
            return jsonify({"error": "task not found"}), 404
        return jsonify(item), 200
    except ClientError as e:
        return jsonify({"error": str(e)}), 500


@app.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()

    try:
        response = table.get_item(Key={'task_id': task_id})
        if 'Item' not in response:
            return jsonify({"error": "task not found"}), 404

        update_expr = []
        expr_values = {}

        if 'title' in data:
            update_expr.append('title = :t')
            expr_values[':t'] = data['title']
        if 'description' in data:
            update_expr.append('description = :d')
            expr_values[':d'] = data['description']
        if 'status' in data:
            update_expr.append('#s = :s')
            expr_values[':s'] = data['status']

        if not update_expr:
            return jsonify({"error": "nothing to update"}), 400

        table.update_item(
            Key={'task_id': task_id},
            UpdateExpression='SET ' + ', '.join(update_expr),
            ExpressionAttributeValues=expr_values,
            ExpressionAttributeNames={'#s': 'status'} if 'status' in data else {}
        )

        response = table.get_item(Key={'task_id': task_id})
        return jsonify(response['Item']), 200
    except ClientError as e:
        return jsonify({"error": str(e)}), 500


@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        response = table.get_item(Key={'task_id': task_id})
        if 'Item' not in response:
            return jsonify({"error": "task not found"}), 404

        table.delete_item(Key={'task_id': task_id})
        return jsonify({"message": "task deleted"}), 200
    except ClientError as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)