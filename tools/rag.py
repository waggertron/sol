#!/usr/bin/env python3
"""Small local RAG helper for the personality knowledge base.

The first implementation is deliberately dependency-free. It builds a
BM25-style lexical index over local Markdown/JSON files and prints ranked
chunks for research prompts.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_INDEX = Path("rag_index/index.json")
DEFAULT_PATHS = [
    Path("kb"),
    Path("sources"),
    Path("jsondb"),
    Path("assessments"),
    Path("docs"),
    Path("plans"),
    Path("README.md"),
]
TOKEN_RE = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_\-']*")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
SUPPORTED_SUFFIXES = {".md", ".txt", ".json"}
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "into",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "with",
}


@dataclass
class Chunk:
    id: str
    path: str
    heading: str
    text: str
    token_counts: dict[str, int]
    length: int


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    for raw in TOKEN_RE.findall(text.lower()):
        token = raw.strip("-'")
        if not token or token in STOPWORDS:
            continue
        if len(token) > 3 and token.endswith("s"):
            token = token[:-1]
        tokens.append(token)
    return tokens


def iter_files(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        if not path.exists():
            continue
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
            yield path
        elif path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_file() and child.suffix.lower() in SUPPORTED_SUFFIXES:
                    yield child


def normalize_json_text(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    return json.dumps(data, indent=2, sort_keys=True)


def read_text(path: Path) -> str:
    if path.suffix.lower() == ".json":
        return normalize_json_text(path)
    return path.read_text(encoding="utf-8")


def split_markdown_sections(text: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, list[str]]] = []
    current_heading = "Document"
    current_lines: list[str] = []

    for line in text.splitlines():
        match = HEADING_RE.match(line)
        if match:
            if current_lines:
                sections.append((current_heading, current_lines))
            current_heading = match.group(2).strip()
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_heading, current_lines))

    return [(heading, "\n".join(lines).strip()) for heading, lines in sections if "\n".join(lines).strip()]


def window_text(text: str, max_words: int = 260, overlap: int = 45) -> list[str]:
    words = text.split()
    if len(words) <= max_words:
        return [text.strip()]

    windows: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + max_words, len(words))
        windows.append(" ".join(words[start:end]).strip())
        if end == len(words):
            break
        start = max(0, end - overlap)
    return windows


def chunk_file(path: Path) -> list[Chunk]:
    text = read_text(path)
    sections = split_markdown_sections(text) if path.suffix.lower() == ".md" else [("Document", text)]
    chunks: list[Chunk] = []

    for section_index, (heading, section_text) in enumerate(sections):
        for window_index, window in enumerate(window_text(section_text)):
            tokens = tokenize(window)
            if not tokens:
                continue
            chunk_id = f"{path.as_posix()}::{section_index}:{window_index}"
            counts = Counter(tokens)
            chunks.append(
                Chunk(
                    id=chunk_id,
                    path=path.as_posix(),
                    heading=heading,
                    text=window,
                    token_counts=dict(counts),
                    length=sum(counts.values()),
                )
            )

    return chunks


def build_index(paths: Iterable[Path]) -> dict:
    chunks: list[Chunk] = []
    for path in iter_files(paths):
        chunks.extend(chunk_file(path))

    document_frequency: defaultdict[str, int] = defaultdict(int)
    for chunk in chunks:
        for token in chunk.token_counts:
            document_frequency[token] += 1

    avg_length = sum(chunk.length for chunk in chunks) / len(chunks) if chunks else 0
    return {
        "version": 1,
        "chunk_count": len(chunks),
        "avg_length": avg_length,
        "document_frequency": dict(document_frequency),
        "chunks": [chunk.__dict__ for chunk in chunks],
    }


def save_index(index: dict, index_path: Path) -> None:
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")


def load_index(index_path: Path) -> dict:
    if not index_path.exists():
        raise SystemExit(f"Index not found: {index_path}. Run `python3 tools/rag.py index` first.")
    return json.loads(index_path.read_text(encoding="utf-8"))


def bm25_scores(index: dict, query: str, k1: float = 1.5, b: float = 0.75) -> list[tuple[float, dict]]:
    query_counts = Counter(tokenize(query))
    if not query_counts:
        return []

    chunks = index["chunks"]
    total_chunks = max(1, len(chunks))
    avg_length = index.get("avg_length") or 1
    document_frequency = index["document_frequency"]
    scored: list[tuple[float, dict]] = []

    for chunk in chunks:
        score = 0.0
        length = chunk["length"] or 1
        counts = chunk["token_counts"]

        for token, query_weight in query_counts.items():
            tf = counts.get(token, 0)
            if not tf:
                continue
            df = document_frequency.get(token, 0)
            idf = math.log(1 + (total_chunks - df + 0.5) / (df + 0.5))
            denom = tf + k1 * (1 - b + b * length / avg_length)
            score += query_weight * idf * (tf * (k1 + 1) / denom)

        if score > 0:
            score *= min(1.0, length / 40)
            scored.append((score, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)
    return scored


def format_snippet(text: str, max_chars: int = 700) -> str:
    clean = re.sub(r"\s+", " ", text).strip()
    if len(clean) <= max_chars:
        return clean
    return clean[: max_chars - 3].rstrip() + "..."


def command_index(args: argparse.Namespace) -> None:
    paths = [Path(item) for item in args.paths] if args.paths else DEFAULT_PATHS
    index = build_index(paths)
    save_index(index, Path(args.index))
    print(f"Indexed {index['chunk_count']} chunks into {args.index}")


def command_search(args: argparse.Namespace) -> None:
    index = load_index(Path(args.index))
    results = bm25_scores(index, args.query)
    for rank, (score, chunk) in enumerate(results[: args.top_k], start=1):
        print(f"{rank}. score={score:.3f} path={chunk['path']} heading={chunk['heading']}")
        print(format_snippet(chunk["text"], args.max_chars))
        print()


def command_context(args: argparse.Namespace) -> None:
    index = load_index(Path(args.index))
    results = bm25_scores(index, args.query)
    for rank, (score, chunk) in enumerate(results[: args.top_k], start=1):
        print(f"[{rank}] {chunk['path']} | {chunk['heading']} | score={score:.3f}")
        print(chunk["text"].strip())
        print()


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local RAG helper for the knowledge base")
    parser.add_argument("--index", default=DEFAULT_INDEX.as_posix(), help="Path to the generated index")

    subparsers = parser.add_subparsers(dest="command", required=True)

    index_parser = subparsers.add_parser("index", help="Build a local retrieval index")
    index_parser.add_argument("paths", nargs="*", help="Files or directories to index")
    index_parser.set_defaults(func=command_index)

    search_parser = subparsers.add_parser("search", help="Search the local retrieval index")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--top-k", type=int, default=5, help="Number of chunks to return")
    search_parser.add_argument("--max-chars", type=int, default=700, help="Maximum snippet length")
    search_parser.set_defaults(func=command_search)

    context_parser = subparsers.add_parser("context", help="Print full retrieved context chunks")
    context_parser.add_argument("query", help="Search query")
    context_parser.add_argument("--top-k", type=int, default=6, help="Number of chunks to return")
    context_parser.set_defaults(func=command_context)

    return parser


def main() -> None:
    parser = make_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
