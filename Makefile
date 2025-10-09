.PHONY: audit-imports format format-check test-intake ci

audit-imports:
	python3 repair_portal/tools/py_import_audit.py
	python3 repair_portal/tools/js_import_audit.py

format:
	ruff check --fix repair_portal
	npx biome check repair_portal/public/js repair_portal/intake --write

format-check:
	ruff check repair_portal
	npx biome check repair_portal/public/js repair_portal/intake

test-intake:
	bench --site site1.local run-tests --app repair_portal --module repair_portal.intake

ci: audit-imports
	ruff check repair_portal
	npx biome check repair_portal/public/js repair_portal/intake
	$(MAKE) test-intake
