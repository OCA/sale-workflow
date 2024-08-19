# Copyright 2021 Tecnativa - Víctor Martínez
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

    def _create_sale_invoice(self, sale):
        SaleInv = self.env["sale.advance.payment.inv"].with_context(active_ids=sale.ids)
        popup = SaleInv.create({"advance_payment_method": "delivered"})
        popup.create_invoices()

    def test_action_cancel_create_revision(self):
        sale = self._create_tester()
        sale.action_confirm()
        self._create_sale_invoice(sale)
        sale.action_cancel_create_revision()
        self.assertEqual(sale.state, "cancel", "Original SO was cancelled")
        self.assertTrue(sale.current_revision_id, "A new SO version was created")
        self.assertEqual(
            sale.current_revision_id.invoice_ids,
            sale.invoice_ids,
            "The Sale Order revision keeps a link to the original invoices",
        )
