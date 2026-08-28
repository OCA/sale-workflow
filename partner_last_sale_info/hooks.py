# Copyright 2026 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def pre_init_hook(env):
    """Create columns with empty values before module installation."""
    env.cr.execute(
        """
        ALTER TABLE res_partner
        ADD COLUMN IF NOT EXISTS last_sale_order_date TIMESTAMP,
        ADD COLUMN IF NOT EXISTS last_sale_order_id INTEGER;
    """
    )
