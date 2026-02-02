# Copyright 2023 Manuel Regidor  <manuel.regidor@sygel.es> (Sygel)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import odoo


def migrate(cr, version):
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    sequence = env["ir.sequence"].search([("code", "=", "sale.quotation")], limit=1)
    orders = (
        env["sale.order"]
        .search(
            [
                ("state", "in", ["draft", "sent"]),
                ("company_id.keep_name_so", "=", False),
            ]
        )
        .filtered(lambda a: a.name[: len(sequence.prefix)] == sequence.prefix)
    )
    orders.write({"quotation_seq_used": True})
