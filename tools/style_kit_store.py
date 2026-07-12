#!/usr/bin/env python3
"""Contract-validated local repository for Creative Style Kit records."""

from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import threading
from typing import Any, Callable, Protocol

from validate_style_kit_contracts import SCHEMA_FILES, validate_contract_bundle


ROOT = Path(__file__).resolve().parents[1]
STYLE_KIT_DB_ENV = "SOL_STYLE_KIT_DB"
DEFAULT_STYLE_KIT_DB = ROOT / "tmp" / "style-kit" / "style-kit-records.json"
BUNDLE_VERSION = "sol.style-kit.contract-bundle.v1"
COLLECTIONS = tuple(SCHEMA_FILES)
MUTATION_LOCK = threading.RLock()


class StyleKitRepository(Protocol):
    """Persistence operations required by the first Style Kit backend boundary."""

    def load_bundle(self) -> dict[str, Any]: ...

    def replace_bundle(self, bundle: dict[str, Any]) -> dict[str, Any]: ...

    def mutate_bundle(
        self,
        mutation: Callable[[dict[str, Any]], dict[str, Any]],
    ) -> dict[str, Any]: ...

    def list_records(self, collection: str) -> list[dict[str, Any]]: ...

    def get_record(self, collection: str, record_id: str) -> dict[str, Any] | None: ...

    def create_record(self, collection: str, record: dict[str, Any]) -> dict[str, Any]: ...

    def replace_record(
        self,
        collection: str,
        record_id: str,
        record: dict[str, Any],
    ) -> dict[str, Any]: ...

    def mutate_record(
        self,
        collection: str,
        record_id: str,
        mutation: Callable[[dict[str, Any]], dict[str, Any]],
    ) -> dict[str, Any]: ...


def empty_bundle() -> dict[str, Any]:
    return {
        "bundle_version": BUNDLE_VERSION,
        **{collection: [] for collection in COLLECTIONS},
    }


def configured_db_path() -> Path:
    configured = os.environ.get(STYLE_KIT_DB_ENV)
    return Path(configured) if configured else DEFAULT_STYLE_KIT_DB


def validate_collection(collection: str) -> None:
    if collection not in COLLECTIONS:
        raise ValueError(f"Unknown Style Kit collection: {collection}")


def validate_bundle(bundle: dict[str, Any]) -> None:
    errors = validate_contract_bundle(bundle)
    if errors:
        formatted = "\n- ".join(errors)
        raise ValueError(f"Invalid Style Kit bundle:\n- {formatted}")


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2, sort_keys=True) + "\n"
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        temporary_path.chmod(0o600)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


class JsonStyleKitRepository:
    """Single-process JSONDB provider with whole-bundle contract validation."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = Path(path) if path is not None else configured_db_path()

    def _load_unlocked(self) -> dict[str, Any]:
        if not self.path.exists():
            return empty_bundle()
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Could not read Style Kit repository {self.path}: {exc}") from exc
        if not isinstance(loaded, dict):
            raise ValueError("Style Kit repository root must be a JSON object")
        validate_bundle(loaded)
        return loaded

    def load_bundle(self) -> dict[str, Any]:
        with MUTATION_LOCK:
            return deepcopy(self._load_unlocked())

    def replace_bundle(self, bundle: dict[str, Any]) -> dict[str, Any]:
        candidate = deepcopy(bundle)
        if not isinstance(candidate, dict):
            raise ValueError("Style Kit bundle must be a JSON object")
        with MUTATION_LOCK:
            validate_bundle(candidate)
            atomic_write_json(self.path, candidate)
            return deepcopy(candidate)

    def mutate_bundle(
        self,
        mutation: Callable[[dict[str, Any]], dict[str, Any]],
    ) -> dict[str, Any]:
        """Apply one whole-graph mutation under validation and the repository lock."""
        with MUTATION_LOCK:
            current = self._load_unlocked()
            candidate = deepcopy(mutation(deepcopy(current)))
            if not isinstance(candidate, dict):
                raise ValueError("Style Kit bundle mutation must return a JSON object")
            validate_bundle(candidate)
            atomic_write_json(self.path, candidate)
            return deepcopy(candidate)

    def list_records(self, collection: str) -> list[dict[str, Any]]:
        validate_collection(collection)
        with MUTATION_LOCK:
            return deepcopy(self._load_unlocked()[collection])

    def get_record(self, collection: str, record_id: str) -> dict[str, Any] | None:
        validate_collection(collection)
        with MUTATION_LOCK:
            for record in self._load_unlocked()[collection]:
                if record.get("id") == record_id:
                    return deepcopy(record)
        return None

    def create_record(self, collection: str, record: dict[str, Any]) -> dict[str, Any]:
        validate_collection(collection)
        candidate_record = deepcopy(record)
        record_id = candidate_record.get("id")
        if not isinstance(record_id, str) or not record_id:
            raise ValueError("Style Kit record id is required")
        with MUTATION_LOCK:
            bundle = self._load_unlocked()
            if any(existing.get("id") == record_id for existing in bundle[collection]):
                raise ValueError(f"Duplicate Style Kit record id in {collection}: {record_id}")
            bundle[collection].append(candidate_record)
            validate_bundle(bundle)
            atomic_write_json(self.path, bundle)
            return deepcopy(candidate_record)

    def replace_record(
        self,
        collection: str,
        record_id: str,
        record: dict[str, Any],
    ) -> dict[str, Any]:
        validate_collection(collection)
        candidate_record = deepcopy(record)
        if candidate_record.get("id") != record_id:
            raise ValueError("Replacement record id must match the requested record id")
        with MUTATION_LOCK:
            bundle = self._load_unlocked()
            for index, existing in enumerate(bundle[collection]):
                if existing.get("id") == record_id:
                    bundle[collection][index] = candidate_record
                    validate_bundle(bundle)
                    atomic_write_json(self.path, bundle)
                    return deepcopy(candidate_record)
        raise KeyError(f"Unknown Style Kit record in {collection}: {record_id}")

    def mutate_record(
        self,
        collection: str,
        record_id: str,
        mutation: Callable[[dict[str, Any]], dict[str, Any]],
    ) -> dict[str, Any]:
        """Apply one validated record mutation while holding the repository lock."""
        validate_collection(collection)
        with MUTATION_LOCK:
            bundle = self._load_unlocked()
            for index, existing in enumerate(bundle[collection]):
                if existing.get("id") != record_id:
                    continue
                candidate_record = deepcopy(mutation(deepcopy(existing)))
                if candidate_record.get("id") != record_id:
                    raise ValueError("Mutation cannot change a Style Kit record id")
                bundle[collection][index] = candidate_record
                validate_bundle(bundle)
                atomic_write_json(self.path, bundle)
                return deepcopy(candidate_record)
        raise KeyError(f"Unknown Style Kit record in {collection}: {record_id}")
