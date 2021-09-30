# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import SUPERUSER_ID, api


def _fill_in_related_sale_line(env):
    query = """
        UPDATE purchase_order_line pol
            SET related_sale_line_id =
                (SELECT related_sale_line_id
                    FROM stock_move WHERE created_purchase_line_id = pol.id)
            WHERE related_sale_line_id IS NULL
            AND EXISTS (
                SELECT 1 FROM stock_move
                WHERE created_purchase_line_id = pol.id);
    """
    env.cr.execute(query)


def post_init_hook(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        _fill_in_related_sale_line(env)
