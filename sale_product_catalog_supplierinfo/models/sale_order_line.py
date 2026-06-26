# Copyright 2026 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_product_price_context(self):
        """Make the line vendor available to the pricelist price computation.

        ``product_pricelist_supplierinfo`` reads ``force_filter_supplier_id``
        from the product context to pick the supplier info used by
        ``supplierinfo`` based pricelist rules. Forwarding the line vendor here
        makes those rules compute the tariff price for the line's vendor without
        adding a hard dependency on that module (the key is simply ignored when
        it is not installed).
        """
        context = super()._get_product_price_context()
        if self.vendor_id:
            # A partner record is expected (the module default is
            # ``rule.filter_supplier_id``), not an id.
            context["force_filter_supplier_id"] = self.vendor_id
        return context
