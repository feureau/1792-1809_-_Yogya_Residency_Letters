import os
import re
import json

def test_upgrade_sample():
    with open('scripts/entity_database.json', 'r', encoding='utf-8') as f:
        entities = json.load(f)

    print(f"Loaded {len(entities)} entities from database.")

if __name__ == '__main__':
    test_upgrade_sample()
