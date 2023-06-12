# Copyright 2021 Akretion France (http://www.akretion.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import api, fields, models
from odoo.osv import expression


class SaleOrder(models.Model):
    _inherit = "sale.order"

    partner_shipping_id_domain = fields.Char(
        compute="_compute_partner_shipping_domain",
        readonly=True,
    )

    partner_invoice_id_domain = fields.Char(
        compute="_compute_partner_invoice_domain",
        readonly=True,
    )

    @api.depends("partner_id")
    def _compute_partner_shipping_domain(self):
        for rec in self:
            domain = [
                ("company_id", "in", [False, rec.partner_id.company_id.id]),
            ]
            if rec.partner_id:
                domain = expression.AND(
                    [domain, self._get_shipping_partner_domain(rec)]
                )
            rec.partner_shipping_id_domain = json.dumps(domain)

    @api.depends("partner_id")
    def _compute_partner_invoice_domain(self):
        for rec in self:
            domain = [
                ("company_id", "in", [False, rec.partner_id.company_id.id]),
            ]
            if rec.partner_id:
                domain = expression.AND([domain, self._get_invoice_partner_domain(rec)])
            rec.partner_invoice_id_domain = json.dumps(domain)

    def _get_invoice_partner_domain(self, rec):
        return [("id", "child_of", rec.commercial_partner_id.id)]

    def _get_shipping_partner_domain(self, rec):
        return [("id", "child_of", rec.commercial_partner_id.id)]
