# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, SavepointCase


class TestSaleInvoiceDeliveryState(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.product = cls.env.ref("product.product_product_6")
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.partner.write({"invoice_policy": "fully"})

    def test_sale_invoice_status(self):
        sale = self._create_sale_order(self.partner, self.product)
        sale.action_confirm()
        self.assertTrue(sale.picking_ids)
        pick = sale.picking_ids
        pick.move_lines.write({"quantity_done": 7})
        wiz_act = pick.button_validate()
        wiz = Form(
            self.env[wiz_act["res_model"]].with_context(wiz_act["context"])
        ).save()
        wiz.process()
        self.assertEqual(sale.invoice_status, "no")

    def _create_sale_order(self, partner, product):
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = product
            line_form.product_uom_qty = 10
        return order_form.save()
