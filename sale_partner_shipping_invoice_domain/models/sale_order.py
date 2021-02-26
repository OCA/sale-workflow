# Copyright 2021 Akretion France (http://www.akretion.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    partner_invoice_id = fields.Many2one(
        domain="['&', ('company_id', 'in', [False, company_id]), "
        "('id', 'child_of', commercial_partner_id)]"
    )
    partner_shipping_id = fields.Many2one(
        domain="['&', "
        "('company_id', 'in', [False, company_id]), "
        "('id', 'child_of', commercial_partner_id)]"
    )
