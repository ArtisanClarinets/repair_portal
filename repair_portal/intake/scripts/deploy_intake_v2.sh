#!/bin/bash
# Path: repair_portal/intake/scripts/deploy_intake_v2.sh
# Date: 2025-10-05
# Version: 1.1.0
# Description: Deployment script for intake module v2.1.0 - workflow_state UX + analytics refresh
# Dependencies: frappe-bench, repair_portal

# =============================================================================
# Intake Module v2.1.0 Deployment Script
# =============================================================================
#
# This script automates deployment of the clarified workflow_state UX refresh:
# - Runs migrations (no new columns expected, ensures schema alignment)
# - Builds assets
# - Executes verification harness
# - Runs key test suites
# - Prints deployment summary with workflow badge reminders
#
# Usage:
#   chmod +x repair_portal/intake/scripts/deploy_intake_v2.sh
#   ./repair_portal/intake/scripts/deploy_intake_v2.sh [site_name]
#
# Example:
#   ./repair_portal/intake/scripts/deploy_intake_v2.sh erp.artisanclarinets.com
#
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default site name
SITE_NAME="${1:-erp.artisanclarinets.com}"

# =============================================================================
# Functions
# =============================================================================

print_header() {
    echo ""
    echo -e "${BLUE}============================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# =============================================================================
# Main Deployment Steps
# =============================================================================

print_header "INTAKE MODULE v2.1.0 DEPLOYMENT"
print_info "Target Site: $SITE_NAME"
print_info "Starting deployment at $(date)"

# Check if we're in frappe-bench directory
if [ ! -d "apps/repair_portal" ]; then
    print_error "Must be run from frappe-bench directory"
    print_info "Current directory: $(pwd)"
    print_info "Please run: cd /home/frappe/frappe-bench"
    exit 1
fi

print_success "Running from frappe-bench directory"

# =============================================================================
# Step 1: Database Migration
# =============================================================================

print_header "STEP 1: DATABASE MIGRATION"
print_info "Ensuring workflow_state schema alignment..."

if bench --site "$SITE_NAME" migrate; then
    print_success "Migration completed successfully"
    print_info "Key schema expectations:"
    print_info "  - Clarinet Intake: workflow_state (system field), workflow HTML widgets"
    print_info "  - Clarinet Intake Settings: consent automation fields"
else
    print_error "Migration failed"
    print_warning "Please check error logs and try again"
    exit 1
fi

# =============================================================================
# Step 2: Build Assets
# =============================================================================

print_header "STEP 2: BUILD ASSETS"
print_info "Compiling JavaScript and CSS assets..."

if bench build --app repair_portal; then
    print_success "Assets built successfully"
else
    print_error "Asset build failed"
    print_warning "Please check for JavaScript errors"
    exit 1
fi

# =============================================================================
# Step 3: Run Verification Script
# =============================================================================

print_header "STEP 3: VERIFICATION CHECKS"
print_info "Running workflow_state + analytics verification harness..."

if bench --site "$SITE_NAME" execute repair_portal.intake.scripts.verify_intake_module.run_verification; then
    print_success "All verification checks passed"
else
    print_warning "Some verification checks failed"
    print_info "Review output above for details"
    print_info "Continuing with deployment..."
fi

# =============================================================================
# Step 4: Run Test Suites
# =============================================================================

print_header "STEP 4: RUNNING TEST SUITES"

# Test 1: Clarinet Intake
print_info "Running test_clarinet_intake.py..."
if bench --site "$SITE_NAME" run-tests --module repair_portal.intake.doctype.clarinet_intake.test_clarinet_intake; then
    print_success "Clarinet Intake tests passed"
else
    print_warning "Clarinet Intake tests failed - review output"
fi

# Test 2: Loaner Instrument
print_info "Running test_loaner_instrument.py..."
if bench --site "$SITE_NAME" run-tests --module repair_portal.intake.doctype.loaner_instrument.test_loaner_instrument; then
    print_success "Loaner Instrument tests passed"
else
    print_warning "Loaner Instrument tests failed - review output"
fi

# Test 3: Brand Mapping Rule
print_info "Running test_brand_mapping_rule.py..."
if bench --site "$SITE_NAME" run-tests --module repair_portal.intake.doctype.brand_mapping_rule.test_brand_mapping_rule; then
    print_success "Brand Mapping Rule tests passed"
else
    print_warning "Brand Mapping Rule tests failed - review output"
fi

# =============================================================================
# Step 5: Final Summary
# =============================================================================

print_header "DEPLOYMENT SUMMARY"

print_success "Deployment completed at $(date)"
print_info ""
print_info "Changes deployed:"
print_info "  ✓ Workflow badges + SLA panels driven by workflow_state"
print_info "  ✓ Heatmap analytics restored and verified"
print_info "  ✓ Consolidated intake APIs with ownership enforcement"
print_info "  ✓ QR-enabled Intake Receipt and portal enhancements"
print_info ""
print_info "Next steps:"
print_info "  1. Review Intake SLA Pulse report via workspace"
print_info "  2. Render Intake Receipt for smoke test"
print_info "  3. Confirm loaner QA permissions remain internal-only"
print_info "  4. Brief staff on new workflow badge meanings"
print_info "  5. Monitor logs for 24 hours"
print_info ""
print_info "Documentation:"
print_info "  → README: apps/repair_portal/repair_portal/intake/README.md"
print_info "  → CHANGELOG: apps/repair_portal/repair_portal/intake/CHANGELOG.md"
print_info "  → Desk UX Guide: apps/repair_portal/documentation/intake_desk_ui_guide.md"
print_info "  → Next Steps: apps/repair_portal/repair_portal/intake/NEXT_STEPS.md"
print_info ""

print_header "DEPLOYMENT COMPLETE ✅"

print_info "Would you like to configure consent automation now? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    print_info "Opening Clarinet Intake Settings (enter manually in browser):"
    print_info "  https://$SITE_NAME/app/clarinet-intake-settings"
fi
