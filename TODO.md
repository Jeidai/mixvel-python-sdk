# Optimization & Async Migration TODO

## Completed
- [x] Replace the legacy `requests` usage inside `src/mixvel/client.py` with an `httpx.Client` so the SDK can benefit from modern connection pooling and timeouts.

## Near-term optimizations
- [ ] Introduce configurable client-level timeouts and retries in `mixvel.client.Client.__init__` to better handle flaky gateways without forcing every caller to wrap requests manually.
- [ ] Share a compiled Jinja2 environment or cache rendered templates in `mixvel/client.py` to avoid re-reading the template directory for every request.
- [ ] Add structured logging hooks (e.g., per-request correlation IDs) inside `mixvel/client.py::__request` so downstream systems can trace latency hotspots.
- [ ] Expand unit tests under `tests/` with transport stubs to validate error-handling paths (login failures, malformed XML) without requiring live HTTP calls.

## Async transition plan
- [ ] Introduce an `AsyncClient` next to the synchronous client (e.g., `src/mixvel/async_client.py`) that mirrors the public API but uses `httpx.AsyncClient`.
- [ ] Move request serialization/deserialization helpers (template rendering, XML parsing) into reusable functions so both sync and async clients share the same logic.
- [ ] Update the high-level parsers in `mixvel/_parsers.py` to ensure they are coroutine-friendly (no blocking I/O, explicit type hints for async contexts).
- [ ] Provide async-ready examples (`examples/async_quickstart.py`) and README documentation describing how to `await` each workflow step.
- [ ] Add an async pytest suite that leverages `pytest-asyncio` to exercise the new client without live network access, using `httpx.MockTransport` for determinism.
