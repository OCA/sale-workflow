# Copyright 2014 Camptocamp SA (author: Guewen Baconnier)
# Copyright 2020 Camptocamp SA (author: Simone Orsi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.sale_automatic_workflow.tests.common import TestAutomaticWorkflowMixin


class TestAutomaticWorkflowStockMixin(TestAutomaticWorkflowMixin):
    """Extend to add stock related workflow."""

    def create_sale_order(self, workflow, override=None, product_type="product"):
        # Override to create stock operations for each product
        order = super().create_sale_order(
            workflow, override=override, product_type=product_type
        )
        # Create inventory
        for line in order.order_line:
            if line.product_id.type == "product":
                inventory = self.env["stock.quant"].create(
                    {
                        "product_id": line.product_id.id,
                        "location_id": self.env.ref("stock.stock_location_stock").id,
                        "inventory_quantity": line.product_uom_qty,
                    }
                )
                inventory._apply_inventory()
        return order

    def create_full_automatic(self, override=None):
        # Override to include default stock related values
        if not override:
            override = {}
        vals = {
            "picking_policy": "one",
            "validate_picking": True,
        }
        vals.update(override)
        return super().create_full_automatic(override=vals)
