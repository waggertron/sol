import copy
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if TOOLS.as_posix() not in sys.path:
    sys.path.insert(0, TOOLS.as_posix())

import style_kit_store as store


BUNDLE_PATH = ROOT / "schemas" / "style_kit" / "v1" / "examples" / "valid-contract-bundle.json"


def load_valid_bundle() -> dict:
    return json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))


def concurrent_source(index: int) -> dict:
    source = copy.deepcopy(load_valid_bundle()["sources"][0])
    content = f"Self-authored concurrent sample {index}."
    source["id"] = f"src_concurrent_{index:03d}"
    source["title"] = f"Concurrent sample {index}"
    source["content"] = content
    source["content_sha256"] = hashlib.sha256(content.encode("utf-8")).hexdigest()
    source["consent"]["consent_id"] = f"consent_concurrent_{index:03d}"
    return source


class StyleKitStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "nested" / "style-kit-records.json"
        self.previous_db = os.environ.get(store.STYLE_KIT_DB_ENV)
        os.environ[store.STYLE_KIT_DB_ENV] = str(self.path)
        self.repository = store.JsonStyleKitRepository()
        self.bundle = load_valid_bundle()

    def tearDown(self) -> None:
        if self.previous_db is None:
            os.environ.pop(store.STYLE_KIT_DB_ENV, None)
        else:
            os.environ[store.STYLE_KIT_DB_ENV] = self.previous_db
        self.tmp.cleanup()

    def test_environment_selects_isolated_storage_and_empty_reads_do_not_write(self) -> None:
        self.assertEqual(self.repository.path, self.path)
        self.assertEqual(self.repository.load_bundle(), store.empty_bundle())
        self.assertFalse(self.path.exists())

        os.environ.pop(store.STYLE_KIT_DB_ENV)
        default_repository = store.JsonStyleKitRepository()
        self.assertEqual(default_repository.path, store.DEFAULT_STYLE_KIT_DB)
        self.assertEqual(default_repository.path.parent, ROOT / "tmp" / "style-kit")

    def test_create_and_read_every_contract_record(self) -> None:
        for collection in store.COLLECTIONS:
            record = self.bundle[collection][0]
            created = self.repository.create_record(collection, record)
            self.assertEqual(created["id"], record["id"])
            self.assertEqual(self.repository.get_record(collection, record["id"]), record)
            self.assertEqual(self.repository.list_records(collection), [record])

        stored = self.repository.load_bundle()
        self.assertEqual(stored, self.bundle)
        self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), 0o600)

    def test_returned_records_and_bundles_cannot_mutate_persisted_state(self) -> None:
        source = self.bundle["sources"][0]
        created = self.repository.create_record("sources", source)
        created["title"] = "Mutated return value"
        listed = self.repository.list_records("sources")
        listed[0]["title"] = "Mutated list value"
        loaded = self.repository.load_bundle()
        loaded["sources"][0]["title"] = "Mutated bundle value"
        self.assertEqual(self.repository.get_record("sources", source["id"])["title"], source["title"])

        replacement = copy.deepcopy(source)
        replacement["title"] = "Updated source title"
        replacement["provenance"]["source_version"] = 2
        replacement["updated_at"] = "2026-07-12T18:06:00Z"
        returned = self.repository.replace_record("sources", source["id"], replacement)
        returned["title"] = "Mutated replacement return"
        self.assertEqual(self.repository.get_record("sources", source["id"])["title"], "Updated source title")

    def test_replace_bundle_supports_valid_read_after_write(self) -> None:
        returned = self.repository.replace_bundle(self.bundle)
        returned["sources"].clear()
        self.assertEqual(self.repository.load_bundle(), self.bundle)
        self.assertEqual(self.repository.get_record("pilot_runs", "run_sample_v1")["mode"], "mock")

    def test_invalid_mutations_leave_repository_bytes_unchanged(self) -> None:
        source = self.bundle["sources"][0]
        self.repository.create_record("sources", source)
        original_bytes = self.path.read_bytes()

        invalid_observation = copy.deepcopy(self.bundle["observations"][0])
        invalid_observation["owner_id"] = "other_user"
        with self.assertRaisesRegex(ValueError, "owner does not match"):
            self.repository.create_record("observations", invalid_observation)
        self.assertEqual(self.path.read_bytes(), original_bytes)

        dangling_observation = copy.deepcopy(self.bundle["observations"][0])
        dangling_observation["source_id"] = "src_missing_v1"
        with self.assertRaisesRegex(ValueError, "unknown source"):
            self.repository.create_record("observations", dangling_observation)
        self.assertEqual(self.path.read_bytes(), original_bytes)

        invalid_lifecycle = copy.deepcopy(source)
        invalid_lifecycle["record_state"] = "deleted"
        invalid_lifecycle["export_state"] = "deleted"
        invalid_lifecycle["deleted_at"] = "2026-07-12T19:00:00Z"
        with self.assertRaisesRegex(ValueError, "remove content and checksum"):
            self.repository.replace_record("sources", source["id"], invalid_lifecycle)
        self.assertEqual(self.path.read_bytes(), original_bytes)

        external_bundle = copy.deepcopy(self.bundle)
        run = external_bundle["pilot_runs"][0]
        run["mode"] = "external"
        run["provider"]["uri"] = "https://provider.invalid/v1"
        run["external_provider_consent"] = True
        with self.assertRaisesRegex(ValueError, "external mode is not approved"):
            self.repository.replace_bundle(external_bundle)
        self.assertEqual(self.path.read_bytes(), original_bytes)

        with self.assertRaisesRegex(ValueError, "Duplicate Style Kit record id"):
            self.repository.create_record("sources", source)
        self.assertEqual(self.path.read_bytes(), original_bytes)

    def test_concurrent_in_process_creates_do_not_lose_records(self) -> None:
        sources = [concurrent_source(index) for index in range(12)]

        def create(source: dict) -> dict:
            return self.repository.create_record("sources", source)

        with ThreadPoolExecutor(max_workers=6) as executor:
            created = list(executor.map(create, sources))

        stored = self.repository.list_records("sources")
        self.assertEqual(len(created), 12)
        self.assertEqual(len(stored), 12)
        self.assertEqual({record["id"] for record in stored}, {record["id"] for record in sources})
        self.assertTrue(
            all(
                record["content_sha256"] == hashlib.sha256(record["content"].encode("utf-8")).hexdigest()
                for record in stored
            )
        )

    def test_corrupt_repository_fails_loudly_without_repair(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        invalid_bytes = b'{"bundle_version": "broken"'
        self.path.write_bytes(invalid_bytes)
        with self.assertRaisesRegex(ValueError, "Could not read Style Kit repository"):
            self.repository.load_bundle()
        self.assertEqual(self.path.read_bytes(), invalid_bytes)

    def test_unknown_collection_and_replacement_are_explicit_errors(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown Style Kit collection"):
            self.repository.list_records("unknown")
        missing = copy.deepcopy(self.bundle["sources"][0])
        missing["id"] = "src_missing_v1"
        with self.assertRaisesRegex(KeyError, "Unknown Style Kit record"):
            self.repository.replace_record("sources", "src_missing_v1", missing)


if __name__ == "__main__":
    unittest.main()
