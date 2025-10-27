# Operational Runbook

## Environment Detection
```bash
SITE="$(ls -1d /home/frappe/frappe-bench/sites/*.* | head -n1 | xargs -n1 basename)"
export SITE
```

## Phase 0 — Safe Refresh Cycle
```bash
source /home/frappe/frappe-bench/env/bin/activate
cd /home/frappe/frappe-bench/apps/repair_portal
python scripts/schema_guard.py
bench --site "$SITE" migrate
bench build
bench restart
bench --site "$SITE" run-tests --module repair_portal.tests -x -q
```

## Database Backup and Restore
```bash
cd /home/frappe/frappe-bench
bench --site "$SITE" backup
LATEST_BACKUP="$(ls -1t sites/$SITE/private/backups/*.sql.gz | head -n1)"
bench --site "$SITE" --force restore "$LATEST_BACKUP"
```

## Asset Rebuild and Cache Flush
```bash
cd /home/frappe/frappe-bench
bench --site "$SITE" clear-cache
bench --site "$SITE" clear-website-cache
bench build
```

## Scheduler Health
```bash
cd /home/frappe/frappe-bench
bench --site "$SITE" doctor
bench --site "$SITE" list-jobs
bench --site "$SITE" show-pending-jobs
bench --site "$SITE" log --tail 200 --only scheduler.log
```

## Portal Verification (Customer Perspective)
```bash
cd /home/frappe/frappe-bench
bench --site "$SITE" execute repair_portal.tests.utils.portal_login_smoke --kwargs '{"role": "Customer"}'
bench --site "$SITE" execute repair_portal.tests.utils.assert_customer_portal_guards
```

## Application Build & Restart Cycle
```bash
cd /home/frappe/frappe-bench
bench build --app repair_portal
bench restart
```

## Test Suite (App Only)
```bash
cd /home/frappe/frappe-bench
bench --site "$SITE" run-tests --module repair_portal.tests --profile
```

## Customer Approval & Payment Simulation
```bash
cd /home/frappe/frappe-bench
bench --site "$SITE" execute repair_portal.tests.utils.portal_login_smoke --kwargs '{"role": "Customer"}'
bench --site "$SITE" execute repair_portal.tools.approval_demo.run
```

## Sanity Check
```bash
source /home/frappe/frappe-bench/env/bin/activate
SITE="$(ls -1d /home/frappe/frappe-bench/sites/*.* | head -n1 | xargs -n1 basename)"
cd /home/frappe/frappe-bench/apps/repair_portal
python scripts/schema_guard.py
bench --site "$SITE" run-tests --module repair_portal.tests -q
bench --site "$SITE" doctor
```
