import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if TOOLS.as_posix() not in sys.path:
    sys.path.insert(0, TOOLS.as_posix())

import validate_style_kit_contracts as validator


BUNDLE_PATH = ROOT / "schemas" / "style_kit" / "v1" / "examples" / "valid-contract-bundle.json"


class StyleKitContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bundle = json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))

    def test_valid_cross_linked_bundle_passes(self) -> None:
        self.assertEqual(validator.validate_contract_bundle(self.bundle), [])

    def test_schema_rejects_missing_owner(self) -> None:
        invalid = copy.deepcopy(self.bundle)
        del invalid["observations"][0]["owner_id"]
        errors = validator.validate_contract_bundle(invalid)
        self.assertTrue(any("owner_id" in error and "required property" in error for error in errors))

    def test_schema_enforces_rating_and_timestamp_boundaries(self) -> None:
        invalid = copy.deepcopy(self.bundle)
        invalid["evaluation_events"][0]["feels_like_me"] = 6
        invalid["evaluation_events"][0]["created_at"] = "not-a-timestamp"
        errors = validator.validate_contract_bundle(invalid)
        self.assertTrue(any("feels_like_me" in error and "greater than" in error for error in errors))
        self.assertTrue(any("created_at" in error and "UTC timestamp" in error for error in errors))

    def test_cross_record_validation_rejects_unknown_and_unapproved_guidance(self) -> None:
        invalid = copy.deepcopy(self.bundle)
        invalid["pilot_runs"][0]["variants"][1]["guidance_refs"] = ["guide_missing_v1"]
        invalid["pilot_runs"][0]["context_sha256"] = validator.context_sha256(invalid["pilot_runs"][0])
        errors = validator.validate_contract_bundle(invalid)
        self.assertTrue(any("unknown guidance guide_missing_v1" in error for error in errors))

        proposed = copy.deepcopy(self.bundle)
        proposed["generation_guidance"][0]["user_state"] = "proposed"
        errors = validator.validate_contract_bundle(proposed)
        self.assertTrue(any("not user-approved" in error for error in errors))

    def test_consent_scope_is_enforced_across_records(self) -> None:
        invalid = copy.deepcopy(self.bundle)
        invalid["sources"][0]["consent"]["allowed_uses"].remove("local_generation")
        errors = validator.validate_contract_bundle(invalid)
        self.assertTrue(any("does not allow local generation" in error for error in errors))

    def test_source_deletion_requires_redaction_and_observation_invalidation(self) -> None:
        invalid = copy.deepcopy(self.bundle)
        source = invalid["sources"][0]
        source["record_state"] = "deleted"
        source["export_state"] = "deleted"
        source["deleted_at"] = "2026-07-12T19:00:00Z"
        errors = validator.validate_contract_bundle(invalid)
        self.assertTrue(any("remove content and checksum" in error for error in errors))
        self.assertTrue(any("must be invalidated" in error for error in errors))
        self.assertTrue(any("must be disabled" in error for error in errors))

    def test_external_mode_remains_unapproved_by_default(self) -> None:
        invalid = copy.deepcopy(self.bundle)
        run = invalid["pilot_runs"][0]
        run["mode"] = "external"
        run["provider"]["uri"] = "https://provider.invalid/v1"
        run["external_provider_consent"] = True
        errors = validator.validate_contract_bundle(invalid)
        self.assertTrue(any("external mode is not approved" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
