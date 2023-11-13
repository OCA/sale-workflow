# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderType(models.Model):
    _inherit = "sale.order.type"

    @api.model
    def _get_quotation_domain_sequence_id(self):
        seq_type = self.env.ref("sale_quotation_number.seq_sale_quotation")
        return [("code", "=", seq_type.code)]

    quotation_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Quotation Sequence",
        copy=False,
        domain=_get_quotation_domain_sequence_id,
    )
