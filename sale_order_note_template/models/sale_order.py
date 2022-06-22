# Copyright 2021 Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    terms_template_id = fields.Many2one(
        "sale.terms_template",
        string="Terms and conditions template",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    note = fields.Html(readonly=True, states={"draft": [("readonly", False)]})

    @api.onchange("terms_template_id")
    def _onchange_terms_template_id(self):
        if self.terms_template_id:
            self.note = self.terms_template_id.get_value(self)
