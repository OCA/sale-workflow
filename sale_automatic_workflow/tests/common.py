# Copyright 2014 Camptocamp SA (author: Guewen Baconnier)
# Copyright 2020 Camptocamp SA (author: Simone Orsi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))


class TestAutomaticWorkflowMixin(object):
    def create_sale_order(self, workflow, override=None):
        sale_obj = self.env["sale.order"]

        partner_values = {"name": "Imperator Caius Julius Caesar Divus"}
        partner = self.env["res.partner"].create(partner_values)

        product_values = {"name": "Bread", "list_price": 5, "type": "product"}
        product = self.env["product.product"].create(product_values)
        self.product_uom_unit = self.env.ref("uom.product_uom_unit")
        values = {
            "partner_id": partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": product.name,
                        "product_id": product.id,
                        "product_uom": self.product_uom_unit.id,
                        "price_unit": product.list_price,
                        "product_uom_qty": 1,
                    },
                )
            ],
            "workflow_process_id": workflow.id,
        }
        if override:
            values.update(override)
        order = sale_obj.create(values)
        # Create inventory for add stock qty to lines
        # With this commit https://goo.gl/fRTLM3 the moves that where
        # force-assigned are not transferred in the picking
        for line in order.order_line:
            if line.product_id.type == "product":
                inventory = self.env["stock.inventory"].create(
                    {
                        "name": "Inventory for move %s" % line.name,
                        "line_ids": [
                            (
                                0,
                                0,
                                {
                                    "product_id": line.product_id.id,
                                    "product_qty": line.product_uom_qty,
                                    "location_id": self.env.ref(
                                        "stock.stock_location_stock"
                                    ).id,
                                },
                            )
                        ],
                    }
                )
                inventory.action_start()
                inventory.action_validate()
        return order

    def create_full_automatic(self, override=None):
        workflow_obj = self.env["sale.workflow.process"]
        values = workflow_obj.create(
            {
                "name": "Full Automatic",
                "picking_policy": "one",
                "validate_order": True,
                "validate_picking": True,
                "create_invoice": True,
                "validate_invoice": True,
                "invoice_date_is_order_date": True,
            }
        )
        if override:
            values.update(override)
        return values

    def run_job(self):
        self.env["automatic.workflow.job"].run()
