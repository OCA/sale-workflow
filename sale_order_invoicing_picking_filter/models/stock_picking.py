# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    invoiced = fields.Boolean(
        compute="_compute_invoiced", store=True, readonly=False, copy=False
    )

    @api.depends("invoice_ids", "invoice_ids.state")
    def _compute_invoiced(self):
        invoiced_pickings = self.filtered(
            lambda a: a.sale_id
            and a.invoice_ids
            and any(invoice.state != "cancel" for invoice in a.invoice_ids)
            and a.picking_type_code in ["incoming", "outgoing"]
        )
        invoiced_pickings.write({"invoiced": True})
        (self - invoiced_pickings).write({"invoiced": False})
