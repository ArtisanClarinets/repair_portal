"""Context for the repair request webform."""


def get_context(context):
    """Provide a title for the repair request form."""
    context.title = "Submit Repair Request"
    return context
