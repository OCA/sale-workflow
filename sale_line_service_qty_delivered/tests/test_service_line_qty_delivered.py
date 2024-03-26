# Copyright 2022-2023 Michael Tietz (MT Software) <mtietz@mt-software.de>

from odoo.tests import Form, tagged

from .common import TestServiceQtyDeliveredCommon


@tagged("post_install", "-at_install")
class TestServiceQtyDelivered(TestServiceQtyDeliveredCommon):
    def test_delivery_qty_delivered(self):
        self._new_sale_order()
        self._check_qty_delivered(0)

        self.so.action_confirm()
        self._check_qty_delivered(0)

        self._deliver_order()
        self._check_qty_delivered(2)

        self._return_order()
        self._check_qty_delivered(0)

    def test_only_one_delivery_line(self):
        self._new_sale_order()
        self.so.order_line[0].unlink()
        self._check_qty_delivered(0)

        self.so.action_confirm()
        self._check_qty_delivered(1)

    def test_delivery_qty_delivered_policy_order(self):
        self.delivery.invoice_policy = "order"
        self._new_sale_order()
        self._check_qty_delivered(0)

        self.so.action_confirm()
        self._check_qty_delivered(0)

    def test_invoice_status(self):
        self._new_sale_order()
        self.so.order_line[1].is_delivery = True
        self.so.action_confirm()
        self._deliver_order()
        self.assertEqual(self.so.invoice_status, "to invoice")
        invoice = self.so._create_invoices(final=True)
        self.assertEqual(self.so.invoice_status, "invoiced")
        self._return_order()
        self.assertEqual(self.so.invoice_status, "to invoice")
        invoice = self.so._create_invoices(final=True)
        self.assertEqual(self.so.invoice_status, "no")
        invoice_form = Form(invoice)
        invoice_form.invoice_line_ids.remove(index=1)
        invoice = invoice_form.save()
        self.assertEqual(self.so.invoice_status, "to invoice")
