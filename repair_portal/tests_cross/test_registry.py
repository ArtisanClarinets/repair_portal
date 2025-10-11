from repair_portal.core import registry


def test_registry_enumerations_are_populated():
    assert "Repair Order" in registry.all_doctypes()
    assert "repair_order.created" in registry.all_topics()
    assert "Q_REPAIR_SLA" in registry.all_queues()
    assert "Technician" in registry.all_roles()
