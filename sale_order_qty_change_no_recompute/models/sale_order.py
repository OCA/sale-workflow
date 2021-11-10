# Copyright 2021 Tecnativa - Víctor Martínez
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools import config


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _onchange_eval(self, field_name, onchange, result):
        """Remove the trigger for the undesired onchange method with this field.

        We have to act at this place, as `_onchange_methods` is defined as a
        property, and thus it can't be inherited due to the conflict of
        inheritance between Python and Odoo ORM, so we can consider this as a HACK.
        """
        ctx = self.env.context
        if field_name in {"product_uom_qty", "product_uom"} and (
            not config["test_enable"]
            or (config["test_enable"] and ctx.get("prevent_onchange_quantity", False))
        ):
            cls = type(self)
            for method in self._onchange_methods.get(field_name, ()):
                if method == cls.product_uom_change:
                    self._onchange_methods[field_name].remove(method)
                    break
        return super()._onchange_eval(field_name, onchange, result)
