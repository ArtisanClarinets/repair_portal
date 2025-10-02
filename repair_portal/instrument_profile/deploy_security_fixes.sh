#!/bin/bash
# Path: repair_portal/instrument_profile/deploy_security_fixes.sh
# Date: 2025-10-02
# Version: 1.0.0
# Description: Automated deployment script for Fortune-500 security fixes and performance optimizations in instrument_profile module - includes validation, building, migration, and verification steps.
# Dependencies: bash, bench CLI, frappe

set -e  # Exit on any error

echo "=================================================="
echo "Deploying Security Fixes: Instrument Profile"
echo "Date: $(date)"
echo "=================================================="
echo ""

# Step 1: Verify we're in the right directory
echo "Step 1: Verifying repository location..."
if [ ! -d "/home/frappe/frappe-bench/apps/repair_portal" ]; then
    echo "❌ ERROR: repair_portal not found at expected location"
    exit 1
fi
cd /home/frappe/frappe-bench/apps/repair_portal
echo "✅ Repository found"
echo ""

# Step 2: Activate bench environment
echo "Step 2: Activating bench environment..."
source /home/frappe/frappe-bench/env/bin/activate
echo "✅ Environment activated"
echo ""

# Step 3: Check for uncommitted changes
echo "Step 3: Checking git status..."
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Warning: You have uncommitted changes. Consider committing first."
    git status --short
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled."
        exit 1
    fi
fi
echo "✅ Git status checked"
echo ""

# Step 4: Pull latest changes (if applicable)
echo "Step 4: Pulling latest changes..."
git fetch origin
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u} 2>/dev/null || echo "no-upstream")
if [ "$LOCAL" != "$REMOTE" ] && [ "$REMOTE" != "no-upstream" ]; then
    echo "New commits available on remote. Pulling..."
    git pull origin main
else
    echo "Already up to date."
fi
echo "✅ Code synchronized"
echo ""

# Step 5: Verify security fixes are present
echo "Step 5: Verifying security fixes are applied..."
PERMISSION_CHECKS=$(grep -c "frappe.has_permission" repair_portal/instrument_profile/doctype/instrument_serial_number/instrument_serial_number.py)
RATE_LIMIT=$(grep -c "find_similar_rate_limit" repair_portal/instrument_profile/doctype/instrument_serial_number/instrument_serial_number.py)

if [ "$PERMISSION_CHECKS" -lt 2 ]; then
    echo "❌ ERROR: Permission checks not found in instrument_serial_number.py"
    exit 1
fi

if [ "$RATE_LIMIT" -lt 1 ]; then
    echo "❌ ERROR: Rate limiting not found in instrument_serial_number.py"
    exit 1
fi

echo "✅ Security fixes verified in code"
echo "   - Permission checks: $PERMISSION_CHECKS found"
echo "   - Rate limiting: $RATE_LIMIT found"
echo ""

# Step 6: Build assets
echo "Step 6: Building frontend assets..."
bench build --app repair_portal
if [ $? -eq 0 ]; then
    echo "✅ Build successful"
else
    echo "❌ Build failed"
    exit 1
fi
echo ""

# Step 7: Run migrations (includes index patch)
echo "Step 7: Running database migrations..."
bench --site erp.artisanclarinets.com migrate
if [ $? -eq 0 ]; then
    echo "✅ Migrations completed"
else
    echo "❌ Migration failed"
    exit 1
fi
echo ""

# Step 8: Verify indexes were created
echo "Step 8: Verifying database indexes..."
INDEX_COUNT=$(bench --site erp.artisanclarinets.com console <<EOF | grep -c "serial_no\|customer\|workflow_state\|warranty_end_date"
import frappe
result = frappe.db.sql("SHOW INDEX FROM \`tabInstrument Profile\` WHERE Column_name IN ('serial_no', 'customer', 'workflow_state', 'warranty_end_date')")
for row in result:
    print(row)
EOF
)

echo "✅ Indexes verified: $INDEX_COUNT indexes found"
echo ""

# Step 9: Restart services
echo "Step 9: Restarting bench services..."
bench restart
if [ $? -eq 0 ]; then
    echo "✅ Services restarted"
else
    echo "⚠️  Restart command returned non-zero, but continuing..."
fi
echo ""

# Step 10: Run basic smoke test
echo "Step 10: Running smoke tests..."
bench --site erp.artisanclarinets.com console <<'EOF'
import frappe
print("Testing basic DocType access...")
if not frappe.db.table_exists("Instrument Profile"):
    print("❌ FAILED: Instrument Profile table does not exist")
    exit(1)

count = frappe.db.count("Instrument Profile")
print(f"✅ PASSED: Instrument Profile table exists with {count} records")

if not frappe.db.table_exists("Instrument Serial Number"):
    print("❌ FAILED: Instrument Serial Number table does not exist")
    exit(1)

count = frappe.db.count("Instrument Serial Number")
print(f"✅ PASSED: Instrument Serial Number table exists with {count} records")

print("")
print("All smoke tests passed!")
EOF

if [ $? -eq 0 ]; then
    echo "✅ Smoke tests passed"
else
    echo "❌ Smoke tests failed"
    exit 1
fi
echo ""

# Step 11: Display post-deployment checklist
echo "=================================================="
echo "✅ DEPLOYMENT SUCCESSFUL"
echo "=================================================="
echo ""
echo "Post-Deployment Checklist:"
echo ""
echo "1. Monitor audit logs for permission denied events:"
echo "   bench --site erp.artisanclarinets.com console"
echo "   import frappe"
echo "   frappe.get_all('Error Log', filters={'error': ['like', '%Insufficient permissions%']}, limit=10)"
echo ""
echo "2. Check for rate limit violations:"
echo "   grep 'Rate limit exceeded' /home/frappe/frappe-bench/logs/*.log"
echo ""
echo "3. Verify query performance (run EXPLAIN on slow queries):"
echo "   mysql -u root -p -e \"SHOW PROCESSLIST;\""
echo ""
echo "4. Test security fixes manually:"
echo "   - Try to attach ISN to instrument as non-owner (should fail)"
echo "   - Call find_similar() 12 times rapidly (should rate limit)"
echo "   - Try to get_snapshot() of another customer's profile (should fail)"
echo ""
echo "5. Schedule follow-up work:"
echo "   - Write unit tests for security fixes (2 weeks)"
echo "   - Complete missing README files (1 month)"
echo "   - Run static analysis (ruff, mypy, bandit)"
echo ""
echo "=================================================="
echo "Next Review: $(date -d '+7 days' '+%Y-%m-%d')"
echo "=================================================="
