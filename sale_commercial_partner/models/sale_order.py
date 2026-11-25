# Copyright 2016-2022 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    commercial_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer Entity",
        related="partner_id.commercial_partner_id",
        store=True,
        index=True,
    )
    commercial_partner_invoice_id = fields.Many2one(
        comodel_name="res.partner",
        related="partner_invoice_id.commercial_partner_id",
        string="Invoice Entity",
        store=True,
    )
    partner_invoice_domain = fields.Binary(compute="_compute_partner_domains")
    partner_shipping_domain = fields.Binary(compute="_compute_partner_domains")

    @api.depends("commercial_partner_id", "company_id")
    def _compute_partner_domains(self):
        for order in self:
            order.partner_invoice_domain = []
            order.partner_shipping_domain = []
            if order.company_id.use_invoice_commercial_partner_filter:
                order.partner_invoice_domain = [
                    ("commercial_partner_id", "=", order.commercial_partner_id.id)
                ]
            if order.company_id.use_shipping_commercial_partner_filter:
                order.partner_shipping_domain = [
                    ("commercial_partner_id", "=", order.commercial_partner_id.id)
                ]
