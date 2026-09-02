To use this module:

## Configure Block Rules

1. Go to **Sales > Configuration > Partner Block Rules**
2. Create a new rule:
   - **Name**: Descriptive name (e.g., "Block Spam Emails")
   - **Partner Field**: Select which field to validate (email, phone, ZIP, VAT, etc.)
   - **Blocked Values**: Enter values to block (comma-separated list)
   - **Block Message**: Custom message displayed in chatter when triggered
3. Activate the rule
4. Any sale order created with a partner whose field value matches one of the
   blocked values will be automatically canceled

