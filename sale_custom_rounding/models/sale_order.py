# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    tax_calculation_rounding_method_override = fields.Selection(
        [
            ("round_per_line", "Round per Line"),
            ("round_globally", "Round Globally"),
        ],
        store=True,
        readonly=False,
        help="How total tax amount is computed. If no value selected, "
        "the method defined in the company is used.",
    )

    @api.onchange("partner_id", "partner_invoice_id")
    def _onchange_partner_rounding(self):
        partner = self.partner_invoice_id or self.partner_id
        self.tax_calculation_rounding_method_override = (
            partner.tax_calculation_rounding_method or False
        )

    def _prepare_invoice(self):
        vals = super()._prepare_invoice()
        vals["tax_calculation_rounding_method"] = (
            self._get_effective_rounding_method() or ""
        )
        return vals

    def _get_invoice_grouping_keys(self):
        return super()._get_invoice_grouping_keys() + [
            "tax_calculation_rounding_method"
        ]

    def _get_effective_rounding_method(self):
        return (
            self.tax_calculation_rounding_method_override
            or self.company_id.tax_calculation_rounding_method
        )
