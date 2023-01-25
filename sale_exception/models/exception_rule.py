# Copyright 2011 Akretion, Sodexis
# Copyright 2018 Akretion
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ExceptionRule(models.Model):
    _inherit = "exception.rule"

    model = fields.Selection(
        selection_add=[
            ("sale.order", "Sale order"),
            ("sale.order.line", "Sale order line"),
        ],
        ondelete={
            "sale.order": "cascade",
            "sale.order.line": "cascade",
        },
    )
    sale_ids = fields.Many2many("sale.order", string="Sales")
