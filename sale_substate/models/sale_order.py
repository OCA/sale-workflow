# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import ClassVar

from odoo import fields, models


class BaseSubstateType(models.Model):
    _inherit = "base.substate.type"

    model = fields.Selection(
        selection_add=[("sale.order", "Sale order")], ondelete={"sale.order": "cascade"}
    )


class SaleOrder(models.Model):
    _inherit: ClassVar[list[str]] = ["sale.order", "base.substate.mixin"]
    _name = "sale.order"
