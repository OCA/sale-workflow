# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

from odoo import SUPERUSER_ID, api


@openupgrade.logging()
def _fill_in_related_sale_line(env):
    query = """
        UPDATE purchase_order_line pol
            SET related_sale_line_id = sm.related_sale_line_id
            FROM stock_move sm
        WHERE pol.id = sm.created_purchase_line_id
        AND pol.related_sale_line_id IS NULL
        AND sm.related_sale_line_id IS NOT NULL
    """
    openupgrade.logged_query(env.cr, query)


def post_init_hook(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        _fill_in_related_sale_line(env)
