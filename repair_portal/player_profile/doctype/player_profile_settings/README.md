# Player Profile Settings

The **Player Profile Settings** single DocType controls marketing integrations for the Player Profile module.

## Fields

| Field | Type | Description |
| --- | --- | --- |
| `newsletter_email_group` | Link (Email Group) | Email Group used for newsletter opt-ins; defaults to **Player Newsletter**. |

## Behavior

- The Player Profile controller reads this setting to determine which Email Group should receive opt-in updates.
- When the value is blank, the controller falls back to the default **Player Newsletter** group and creates it on-demand if missing.

## Permissions

- **System Manager** and **Repair Manager** can update the setting.
- All changes are tracked via Frappe's audit trail (`track_changes`, `track_seen`, `track_views`).

## Administration

1. Navigate to *Player Profile Settings* from the Awesome Bar.
2. Choose the Email Group that should store newsletter subscribers.
3. Save the document. The Player Profile controller will start syncing to the new group immediately.

If you remove or rename the configured group, update this setting to prevent subscription errors.
