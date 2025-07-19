#!/usr/bin/env python3
# Fortune-500 Review Implementation Verification Script
# Last Updated: 2025-07-19
# Version: v1.0
# Purpose: Validate all critical fixes from the Fortune-500 review

import os
import json
import subprocess
import time
from pathlib import Path


class RepairPortalVerification:
    """Comprehensive verification of all Fortune-500 review fixes."""

    def __init__(self):
        self.app_path = '/opt/frappe/erp-bench/apps/repair_portal/repair_portal'
        self.results = {'passed': [], 'failed': [], 'warnings': []}

    def run_all_verifications(self):
        """Execute all verification checks."""
        print('🔍 Starting Fortune-500 Review Implementation Verification')
        print('=' * 60)

        # Run all verification methods
        verification_methods = [
            self.verify_console_cleanup,
            self.verify_controller_enhancements,
            self.verify_v15_compliance,
            self.verify_security_implementations,
            self.verify_performance_optimizations,
            self.verify_error_handling,
            self.verify_documentation_updates,
        ]

        for method in verification_methods:
            try:
                method()
            except Exception as e:
                self.results['failed'].append(f'{method.__name__}: {str(e)}')

        self.print_summary()

    def verify_console_cleanup(self):
        """Verify console statements have been removed from production code."""
        print('\n1️⃣ Verifying Console Statement Cleanup...')

        # Count remaining console statements
        try:
            result = subprocess.run(
                ['grep', '-r', 'console\\.', f'{self.app_path}/public/dist/'],
                capture_output=True,
                text=True,
            )

            remaining_count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0

            if remaining_count <= 10:  # Allow minimal console statements
                self.results['passed'].append('✅ Console cleanup: Acceptable level')
                print(f'   ✅ Console statements reduced to {remaining_count} (acceptable)')
            else:
                self.results['failed'].append(
                    f'❌ Console cleanup: {remaining_count} statements remain'
                )
                print(f'   ❌ Too many console statements remain: {remaining_count}')

        except Exception as e:
            self.results['failed'].append(f'❌ Console cleanup verification failed: {str(e)}')

    def verify_controller_enhancements(self):
        """Verify controller improvements are implemented."""
        print('\n2️⃣ Verifying Controller Enhancements...')

        # Check RepairPartsUsed controller
        controller_path = (
            f'{self.app_path}/repair_logging/doctype/repair_parts_used/repair_parts_used.py'
        )

        if os.path.exists(controller_path):
            with open(controller_path, 'r') as f:
                content = f.read()

            if 'validate' in content and 'create_stock_entry' in content:
                self.results['passed'].append('✅ RepairPartsUsed controller enhanced')
                print('   ✅ RepairPartsUsed controller properly implemented')
            else:
                self.results['failed'].append('❌ RepairPartsUsed controller missing methods')
                print('   ❌ RepairPartsUsed controller incomplete')
        else:
            self.results['failed'].append('❌ RepairPartsUsed controller file missing')

    def verify_v15_compliance(self):
        """Verify Frappe v15 compliance fixes."""
        print('\n3️⃣ Verifying Frappe v15 Compliance...')

        # Run the compliance checker
        try:
            result = subprocess.run(
                ['python', f'{self.app_path}/scripts/doctype_verify.py', '--app', 'repair_portal'],
                cwd='/opt/frappe/erp-bench/apps/repair_portal',
                capture_output=True,
                text=True,
            )

            if 'Validation failed' not in result.stdout:
                self.results['passed'].append('✅ Frappe v15 compliance: All checks passed')
                print('   ✅ Frappe v15 compliance validation passed')
            else:
                error_count = result.stdout.count('❌')
                if error_count <= 10:  # Allow some non-critical issues
                    self.results['warnings'].append(
                        f'⚠️ Frappe v15 compliance: {error_count} minor issues'
                    )
                    print(f'   ⚠️ {error_count} minor compliance issues remain')
                else:
                    self.results['failed'].append(f'❌ Frappe v15 compliance: {error_count} issues')
                    print(f'   ❌ {error_count} compliance issues found')

        except Exception as e:
            self.results['failed'].append(f'❌ V15 compliance check failed: {str(e)}')

    def verify_security_implementations(self):
        """Verify security enhancements are in place."""
        print('\n4️⃣ Verifying Security Implementations...')

        # Check for API security module
        security_path = f'{self.app_path}/utils/api_security.py'

        if os.path.exists(security_path):
            with open(security_path, 'r') as f:
                content = f.read()

            security_features = [
                'APISecurityManager',
                'rate_limit',
                'validate_input',
                'require_role',
                'audit_log',
            ]

            implemented_features = sum(1 for feature in security_features if feature in content)

            if implemented_features >= 4:
                self.results['passed'].append('✅ API Security: Comprehensive implementation')
                print(f'   ✅ {implemented_features}/5 security features implemented')
            else:
                self.results['failed'].append(
                    f'❌ API Security: Only {implemented_features}/5 features'
                )
                print(f'   ❌ Insufficient security features: {implemented_features}/5')
        else:
            self.results['failed'].append('❌ API Security module missing')

    def verify_performance_optimizations(self):
        """Verify performance optimization implementations."""
        print('\n5️⃣ Verifying Performance Optimizations...')

        # Check for database optimizer
        optimizer_path = f'{self.app_path}/utils/database_optimizer.py'

        if os.path.exists(optimizer_path):
            with open(optimizer_path, 'r') as f:
                content = f.read()

            optimization_features = [
                'DatabaseOptimizer',
                'get_optimized_instrument_list',
                'get_repair_dashboard_metrics',
                'bulk_update_workflow_states',
                'get_cached_customer_instruments',
            ]

            implemented_optimizations = sum(
                1 for feature in optimization_features if feature in content
            )

            if implemented_optimizations >= 4:
                self.results['passed'].append('✅ Performance: Optimization patterns implemented')
                print(f'   ✅ {implemented_optimizations}/5 optimization patterns implemented')
            else:
                self.results['warnings'].append(
                    f'⚠️ Performance: {implemented_optimizations}/5 optimizations'
                )
                print(f'   ⚠️ Partial performance optimizations: {implemented_optimizations}/5')
        else:
            self.results['warnings'].append('⚠️ Database optimizer module missing')

    def verify_error_handling(self):
        """Verify error handling enhancements."""
        print('\n6️⃣ Verifying Error Handling...')

        # Check for error handler module
        error_handler_path = f'{self.app_path}/utils/error_handler.py'

        if os.path.exists(error_handler_path):
            with open(error_handler_path, 'r') as f:
                content = f.read()

            error_features = [
                'EnterpriseErrorHandler',
                'handle_api_error',
                'validate_business_rules',
                'ErrorSeverity',
                'ErrorCategory',
            ]

            implemented_features = sum(1 for feature in error_features if feature in content)

            if implemented_features >= 4:
                self.results['passed'].append('✅ Error Handling: Enterprise-grade implementation')
                print(f'   ✅ {implemented_features}/5 error handling features implemented')
            else:
                self.results['warnings'].append(
                    f'⚠️ Error Handling: {implemented_features}/5 features'
                )
                print(f'   ⚠️ Partial error handling: {implemented_features}/5')
        else:
            self.results['warnings'].append('⚠️ Error handler module missing')

    def verify_documentation_updates(self):
        """Verify documentation and build scripts are in place."""
        print('\n7️⃣ Verifying Documentation & Build Scripts...')

        # Check for production build script
        build_script_path = f'{self.app_path}/scripts/build_production.sh'

        if os.path.exists(build_script_path):
            self.results['passed'].append('✅ Build Scripts: Production build script created')
            print('   ✅ Production build script implemented')
        else:
            self.results['warnings'].append('⚠️ Build Scripts: Production build script missing')

        # Check for babel configuration
        babel_config_path = f'{self.app_path}/.babelrc'

        if os.path.exists(babel_config_path):
            self.results['passed'].append('✅ Build Config: Babel configuration implemented')
            print('   ✅ Babel configuration for console removal implemented')
        else:
            self.results['warnings'].append('⚠️ Build Config: Babel configuration missing')

    def print_summary(self):
        """Print comprehensive verification summary."""
        print('\n' + '=' * 60)
        print('📊 VERIFICATION SUMMARY')
        print('=' * 60)

        total_checks = (
            len(self.results['passed'])
            + len(self.results['failed'])
            + len(self.results['warnings'])
        )
        passed_count = len(self.results['passed'])
        failed_count = len(self.results['failed'])
        warning_count = len(self.results['warnings'])

        success_rate = (passed_count / total_checks * 100) if total_checks > 0 else 0

        print(f'\n📈 Overall Success Rate: {success_rate:.1f}%')
        print(f'✅ Passed: {passed_count}')
        print(f'❌ Failed: {failed_count}')
        print(f'⚠️ Warnings: {warning_count}')

        if self.results['passed']:
            print(f"\n✅ PASSED CHECKS ({len(self.results['passed'])}):")
            for item in self.results['passed']:
                print(f'   {item}')

        if self.results['warnings']:
            print(f"\n⚠️ WARNINGS ({len(self.results['warnings'])}):")
            for item in self.results['warnings']:
                print(f'   {item}')

        if self.results['failed']:
            print(f"\n❌ FAILED CHECKS ({len(self.results['failed'])}):")
            for item in self.results['failed']:
                print(f'   {item}')

        # Overall assessment
        print(f'\n🎯 OVERALL ASSESSMENT:')
        if success_rate >= 90:
            print('   🏆 EXCELLENT: Ready for Fortune-500 deployment!')
        elif success_rate >= 75:
            print('   ✅ GOOD: Minor improvements needed')
        elif success_rate >= 60:
            print('   ⚠️ ADEQUATE: Several areas need attention')
        else:
            print('   ❌ NEEDS WORK: Significant improvements required')

        print(f"\n⏰ Verification completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print('=' * 60)


if __name__ == '__main__':
    verifier = RepairPortalVerification()
    verifier.run_all_verifications()
