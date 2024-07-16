# Copyright 2024 Ecosoft Co., Ltd. (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class IrSequenceOption(models.Model):
    _inherit = "ir.sequence.option"

    model = fields.Selection(
        selection_add=[("sale.order", "sale.order")],
        ondelete={"sale.order": "cascade"},
    )
