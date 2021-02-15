# Copyright 2021 jeo Software - Jorge Obiols
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Ensure each company has at least one sale.order.type record
    for company in env["res.company"].search([]):
        if not env["sale.order.type"].search([("company_id", "=", company.id)]):
            env["sale.order.type"].create(
                {"name": "Normal Order", "company_id": company.id}
            )

    # Ensure each SO has filled the type_id, according to the sale order company
    sale_order_ids = env["sale.order"].search([("state", "!=", "draft")])
    for so in sale_order_ids:
        so.type_id = env["sale.order.type"].search(
            [("company_id", "in", [so.company_id.id, False])], limit=1
        )
