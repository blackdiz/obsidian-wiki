"""Canonical manifest source keys.

Vault-internal files use a portable ``vault://`` URI so a synced vault can be
maintained from machines whose local vault paths differ. External files keep
their expanded absolute paths.
"""

from __future__ import annotations

import os
from pathlib import Path

VAULT_URI_PREFIX = "vault://"


def _expand(path: str | os.PathLike[str]) -> str:
    return os.path.abspath(os.path.expanduser(os.path.expandvars(os.fspath(path))))


def _is_relative_key(key: str) -> bool:
    return not (
        key.startswith(VAULT_URI_PREFIX)
        or os.path.isabs(key)
        or key.startswith("~")
        or "$" in key
    )


def _as_vault_uri(relative_path: str) -> str:
    return VAULT_URI_PREFIX + relative_path.replace(os.sep, "/")


def canonical_source_key(vault: str | os.PathLike[str], source: str | os.PathLike[str]) -> str:
    """Return the manifest key for *source* scoped to *vault*.

    Existing ``vault://`` keys are normalized and returned unchanged in meaning.
    Relative non-URI keys are preserved for backward compatibility with history
    ingest roots that intentionally stored relative session paths.
    """
    raw = os.fspath(source)
    if raw.startswith(VAULT_URI_PREFIX):
        rel = raw[len(VAULT_URI_PREFIX):].lstrip("/")
        return _as_vault_uri(os.path.normpath(rel))
    if _is_relative_key(raw):
        return raw

    vault_abs = _expand(vault)
    source_abs = _expand(raw)
    try:
        if os.path.commonpath([vault_abs, source_abs]) == vault_abs:
            rel = os.path.relpath(source_abs, vault_abs)
            return _as_vault_uri(rel)
    except ValueError:
        pass
    return source_abs


def resolve_source_key(vault: str | os.PathLike[str], key: str) -> str:
    """Resolve a manifest key to a local filesystem path when possible."""
    if key.startswith(VAULT_URI_PREFIX):
        rel = key[len(VAULT_URI_PREFIX):].lstrip("/")
        return os.path.abspath(os.path.join(_expand(vault), rel))
    if _is_relative_key(key):
        return key
    return _expand(key)


def lookup_source_entry(
    sources: dict,
    vault: str | os.PathLike[str],
    source: str | os.PathLike[str],
) -> tuple[str | None, dict | None]:
    """Find an entry by canonical key with legacy absolute-key fallbacks."""
    raw = os.fspath(source)
    candidates = [canonical_source_key(vault, raw)]
    if not raw.startswith(VAULT_URI_PREFIX) and not _is_relative_key(raw):
        abs_key = _expand(raw)
        candidates.append(abs_key)
        candidates.append(os.path.abspath(raw))

    seen: set[str] = set()
    for key in candidates:
        if key in seen:
            continue
        seen.add(key)
        if key in sources:
            return key, sources[key]
    return None, None
