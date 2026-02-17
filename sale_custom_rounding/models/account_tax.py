# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountTax(models.Model):
    _inherit = "account.tax"

    def _prepare_base_line_for_taxes_computation(self, record, **kwargs):
        res = super()._prepare_base_line_for_taxes_computation(record, **kwargs)

        # Protect against fake calls with record = None
        if record and record._name == "sale.order.line":
            order = record.order_id
            res["tax_calculation_rounding_method"] = (
                order.tax_calculation_rounding_method_override
                or order.company_id.tax_calculation_rounding_method
            )

        return res
