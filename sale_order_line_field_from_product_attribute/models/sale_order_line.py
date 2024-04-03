# Copyright (C) 2023 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _store_attribute_in_field(self, vals):
        if "product_no_variant_attribute_value_ids" in vals:
            for sol in self:
                sol_pav = sol.product_no_variant_attribute_value_ids
                sol_pav_to_store = sol_pav.filtered("attribute_id.store_in_field")
                sol_pav_custom_values = sol.product_custom_attribute_value_ids
                pav_vals = {}
                for pav in sol_pav_to_store:

                    sol_pav_custom_value = sol_pav_custom_values.filtered(
                        lambda x: x.custom_product_template_attribute_value_id == pav
                    )
                    value = (
                        sol_pav_custom_value.custom_value
                        or pav.product_attribute_value_id.store_in_field_value
                        or pav.name
                    )
                    field_name = pav.attribute_id.store_in_field.name
                    # Support boolean fields
                    if type(sol._fields[field_name]).type == "boolean":
                        value = not (value.lower() in ["false", "0"])
                    pav_vals[field_name] = value
                if pav_vals:
                    super(SaleOrderLine, sol).write(pav_vals)
        return True

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._store_attribute_in_field(vals)
        return res

    def write(self, vals):
        res = super().write(vals)
        self._store_attribute_in_field(vals)
        return res
