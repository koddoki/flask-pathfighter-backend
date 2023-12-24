from typing import Optional, Dict

from bson import json_util
from flask import Response, jsonify

from client.monster_client import MonsterClient


class MonsterService:
    def __init__(self, uri):
        self.monster_client = MonsterClient(uri)

    def get_source_books(self):
        pipeline = [
            {
                "$project": {
                    "truncatedSource": {
                        "$arrayElemAt": [
                            {
                                "$split": [
                                    "$meta.source",
                                    " pg",
                                ],
                            },
                            0,
                        ],
                    },
                },
            },
            {
                "$group": {
                    "_id": "$truncatedSource",
                },
            },
            {
                "$project": {
                    "_id": 0,
                    "truncatedSource": "$_id",
                },
            },
        ]
        response = self.monster_client.aggregate_pipeline(pipeline)
        book_names = []
        for book in response:
            truncated_source = book.get('truncatedSource')
            if truncated_source:
                book_names.append(truncated_source)

        return book_names

    def get_dynamic(self, page: int, size: int, query_options: Optional[Dict] = None):
        query_options = query_options or {}
        filters = query_options.get("filters", {})
        sort = query_options.get("sort", {})

        match_stage = {
            "$match": {
                key: {"$regex": str(value), "$options": "i"} if isinstance(value, str) else {"$eq": value}
                for key, value in filters.items()
            }
        }

        sort_stage = {"$sort": {key: value for key, value in sort.items()}}

        pipeline = [
            match_stage,
            sort_stage,
            {
                "$skip": page * size
            },
            {
                "$limit": size
            }
        ]

        try:
            cursor = self.monster_client.aggregate_pipeline(pipeline)
            response = json_util.dumps(list(cursor), indent=2)

            return Response(response=response,
                            status=200,
                            mimetype='application/json')
        except Exception as e:
            print(f'Error: {str(e)}')
            return jsonify({'error': 'Internal Server Error.'}), 500


