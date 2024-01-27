# Copyright 2023 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests import Form, common


class TestSaleOrderRevision(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.revision_model = cls.env["sale.order"]
        cls.partner = cls.env["res.partner"].create({"name": "Mr Odoo"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "invoice_policy": "order"}
        )

    def _create_tester(self):
        sale_form = Form(self.revision_model)
        sale_form.partner_id = self.partner
        with sale_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.product_uom_qty = 10
            line_form.price_unit = 10
        return sale_form.save()

    def test_revision_keeps_stock(self):
        sale = self._create_tester()
        sale.action_confirm()
        original_pickings = sale.picking_ids
        sale.action_cancel_create_revision()
        self.assertEqual(
            sale.current_revision_id.picking_ids,
            original_pickings,
            "Deliveries shold be reattached to the new Sale Order revision",
        )
