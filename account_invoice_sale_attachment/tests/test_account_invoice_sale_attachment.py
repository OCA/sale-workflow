# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import Form, TransactionCase


class TestAccountInvoiceSaleAttachment(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, discard_logo_check=True))
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env.ref("product.product_product_1")
        cls.product.invoice_policy = "order"
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "state": "sale",
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 2,
                            "price_unit": 100,
                        }
                    )
                ],
            }
        )
        cls.so_attachment = cls.env["ir.attachment"].create(
            {
                "name": "SO036.pdf",
                "type": "binary",
                "mimetype": "application/pdf",
                "datas": "",
                "res_id": cls.sale_order.id,
                "res_model": cls.sale_order._name,
                "res_field": "sale_document_attachment",
            }
        )
        cls.sale_order.action_confirm()
        cls.invoice = cls.sale_order._create_invoices()

    def _create_invoice_send_wizard_form(self):
        action = self.invoice.action_invoice_sent()
        return Form(
            self.env[action.get("res_model")].with_context(**action.get("context"))
        )

    def test_1(self):
        wizard_form = self._create_invoice_send_wizard_form()
        self.assertEqual(len(wizard_form.attachment_ids), 2)
        wizard = wizard_form.save()
        self.assertIn(self.so_attachment, wizard.attachment_ids)

    def test_2(self):
        """check it works even for multiple orders linked to one invoice"""
        sale_order_2 = self.sale_order.copy()
        sale_order_2.action_confirm()
        self.invoice.write(
            {
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "quantity": 2,
                            "price_unit": 100,
                            "sale_line_ids": [Command.link(sale_order_2.order_line.id)],
                        }
                    )
                ]
            }
        )
        so_attachment_2 = self.env["ir.attachment"].create(
            {
                "name": "SO036.pdf",
                "type": "binary",
                "mimetype": "application/pdf",
                "datas": "",
                "res_id": sale_order_2.id,
                "res_model": sale_order_2._name,
                "res_field": "sale_document_attachment",
            }
        )
        self.assertEqual(
            len(self.invoice.invoice_line_ids.sale_line_ids.mapped("order_id")), 2
        )
        wizard_form = self._create_invoice_send_wizard_form()
        self.assertEqual(len(wizard_form.attachment_ids), 3)
        wizard = wizard_form.save()
        self.assertIn(self.so_attachment, wizard.attachment_ids)
        self.assertIn(so_attachment_2, wizard.attachment_ids)
