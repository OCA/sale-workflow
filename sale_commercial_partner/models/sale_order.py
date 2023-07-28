# Copyright 2016-2022 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    commercial_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer Entity",
        related="partner_id.commercial_partner_id",
        store=True,
        index=True,
    )
