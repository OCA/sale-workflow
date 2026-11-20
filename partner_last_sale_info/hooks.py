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


def post_init_hook(env):
    """Populate the last sale info of existing partners in one pass."""
    env.cr.execute(
        """
        UPDATE res_partner AS partner
        SET last_sale_order_id = latest.id,
            last_sale_order_date = latest.date_order
        FROM (
            SELECT DISTINCT ON (partner_id) partner_id, id, date_order
            FROM sale_order
            WHERE state = 'sale'
            ORDER BY partner_id, date_order DESC, id DESC
        ) AS latest
        WHERE partner.id = latest.partner_id
        """
    )
