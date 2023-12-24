from flask import Flask, request, jsonify
from service.monster_service import MonsterService
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="assets/.env")

uri = os.environ.get("MONGODB_URI")

monster_service = MonsterService(uri)

app = Flask(__name__)


@app.route('/books')
def get_books():
    return monster_service.get_source_books()


@app.route('/creatures', methods=['POST'])
def get_creatures():
    if request.content_type != 'application/json':
        return jsonify({'error': 'Invalid Content-Type. Expected application/json'}), 400
    try:
        page = int(request.args.get('page'))
        size = int(request.args.get('size'))
    except ValueError:
        return jsonify({'error': 'Verify your parameters.'}), 400

    return monster_service.get_dynamic(page, size, request.json)


if __name__ == '__main__':
    app.run()
