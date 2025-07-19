import pytest
from unittest.mock import MagicMock

import frappe
from repair_portal.intake.doctype.clarinet_intake.clarinet_intake import ClarinetIntake


class TestClarinetIntake:
    def test_instrument_auto_creation(self, mocker):
        mocker.patch('frappe.db.get_value', return_value=None)
        mock_new_doc = mocker.patch('frappe.new_doc')
        mock_instrument_doc = MagicMock()
        mock_new_doc.return_value = mock_instrument_doc

        clarinet_intake = ClarinetIntake(
            serial_no='12345',
            instrument_type='Clarinet',
            brand='Yamaha',
            model='YCL-255',
            owner='John Doe',
            date_purchased='2025-07-01',
        )
        clarinet_intake.ensure_instrument_exists()

        mock_new_doc.assert_called_once_with('Instrument')
        mock_instrument_doc.save.assert_called_once_with(ignore_permissions=True)

    def test_consent_form_validation(self, mocker):
        mock_throw = mocker.patch('frappe.throw')

        clarinet_intake = ClarinetIntake(intake_type='Repair', consent_form=None)
        with pytest.raises(frappe.ValidationError):
            clarinet_intake.ensure_consent_for_repair()

        mock_throw.assert_called_once_with(
            'Consent/Liability Waiver must be attached for Repair intakes.'
        )

    def test_initial_setup_linking(self, mocker):
        mock_new_doc = mocker.patch('frappe.new_doc')
        mock_setup_doc = MagicMock()
        mock_new_doc.return_value = mock_setup_doc

        clarinet_intake = ClarinetIntake(
            intake_type='Inventory',
            instrument='Instrument-001',
            name='Intake-001',
            owner='John Doe',
        )
        clarinet_intake.ensure_initial_setup_for_inventory()

        mock_new_doc.assert_called_once_with('Clarinet Initial Setup')
        mock_setup_doc.save.assert_called_once_with(ignore_permissions=True)

    def test_instrument_creation_failure(self, mocker):
        mocker.patch('frappe.db.get_value', return_value=None)
        mock_new_doc = mocker.patch('frappe.new_doc', side_effect=Exception('Creation failed'))
        mock_log_error = mocker.patch('frappe.log_error')
        mock_throw = mocker.patch('frappe.throw')

        clarinet_intake = ClarinetIntake(
            serial_no='12345',
            instrument_type='Clarinet',
            brand='Yamaha',
            model='YCL-255',
            owner='John Doe',
            date_purchased='2025-07-01',
        )
        with pytest.raises(frappe.ValidationError):
            clarinet_intake.before_save()

        mock_log_error.assert_called_once()
        mock_throw.assert_called_once()

    def test_missing_consent_form_exception(self, mocker):
        mock_throw = mocker.patch('frappe.throw')

        clarinet_intake = ClarinetIntake(intake_type='Repair', consent_form=None)
        with pytest.raises(frappe.ValidationError):
            clarinet_intake.ensure_consent_for_repair()

        mock_throw.assert_called_once_with(
            'Consent/Liability Waiver must be attached for Repair intakes.'
        )

    def test_initial_setup_creation_failure(self, mocker):
        mocker.patch('frappe.db.get_value', return_value=None)
        mock_new_doc = mocker.patch(
            'frappe.new_doc', side_effect=Exception('Setup creation failed')
        )
        mock_log_error = mocker.patch('frappe.log_error')
        mock_throw = mocker.patch('frappe.throw')

        clarinet_intake = ClarinetIntake(
            intake_type='Inventory', instrument=None, name='Intake-001', owner='John Doe'
        )
        with pytest.raises(frappe.ValidationError):
            clarinet_intake.before_save()

        mock_log_error.assert_called_once()
        mock_throw.assert_called_once()
