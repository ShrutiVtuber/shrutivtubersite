# Vendored — do not edit here

This is a byte-for-byte copy of `shrutisgametracker/server/shrutisguides/`,
the guide format's schema, validator and importer. It is here because the
backend image's build context is `backend/` and the format lives in another
repository that is not yet on GitHub.

⚠ Edit the ORIGINAL and re-copy. `tests/test_the_format_is_vendored_faithfully.py`
fails on the first byte of drift. When the guides repository is public, this
directory goes and `pyproject.toml` gains
`shrutisguides @ git+https://github.com/ShrutiVtuber/shrutis-guides@main#subdirectory=server`.
