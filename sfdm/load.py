"""Step 3 - Load: upsert transformed records into Dataverse, parents first.

"Upsert" = update the record if one with the same Salesforce Id already exists,
otherwise create it. That makes the load safe to re-run after fixing a problem.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import config
from .transform import read_transformed


def load(client, in_dir: Path = config.TRANSFORM_DIR, id_map_file: Path | None = config.ID_MAP_FILE):
    mapping = config.load_mapping()
    id_map: dict[str, dict[str, str]] = {}
    results: dict[str, dict] = {}

    for name in mapping["load_order"]:
        obj = mapping["objects"][name]
        entity_set, pk, key_column = obj["entity_set"], obj["target"] + "id", obj["key_column"]
        stats = {"created": 0, "updated": 0, "failed": 0, "errors": []}
        id_map[name] = {}

        for rec in read_transformed(name, in_dir):
            payload = dict(rec.payload)
            for navigation, (parent, parent_sf_id) in rec.lookups.items():
                parent_guid = id_map.get(parent, {}).get(parent_sf_id)
                if parent_guid:
                    parent_set = mapping["objects"][parent]["entity_set"]
                    payload[f"{navigation}@odata.bind"] = f"/{parent_set}({parent_guid})"
            try:
                guid = client.find_by_key(entity_set, pk, key_column, rec.sf_id)
                if guid:
                    client.update(entity_set, guid, payload)
                    stats["updated"] += 1
                else:
                    guid = client.create(entity_set, payload)
                    stats["created"] += 1
                id_map[name][rec.sf_id] = guid
            except Exception as exc:  # keep going; report every failure at the end
                stats["failed"] += 1
                stats["errors"].append({"sf_id": rec.sf_id, "error": str(exc)})

        results[name] = stats
        print(f"  {name:<12} created {stats['created']:>4}  updated {stats['updated']:>4}  failed {stats['failed']:>4}")

    if id_map_file:
        id_map_file.parent.mkdir(parents=True, exist_ok=True)
        id_map_file.write_text(json.dumps(id_map, indent=2))
    return results, id_map
