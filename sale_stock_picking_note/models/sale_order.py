# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    picking_note = fields.Html(string="Picking Internal Note")
    picking_customer_note = fields.Text(string="Picking Customer Comments")
