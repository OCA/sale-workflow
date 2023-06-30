# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields
from odoo.tests.common import TransactionCase


class TestSaleOrderChangeAnalytic(TransactionCase):
    """
    Tests for sale.order.change.analytic
    """

    def setUp(self):
        super().setUp()
        self.wizard_obj = self.env["sale.order.change.analytic"]
        self.sale_obj = self.env["sale.order"]
        self.tax_obj = self.env["account.tax"]
        self.partner_obj = self.env["res.partner"]
        self.analytic_obj = self.env["account.analytic.account"]
        self.adv_wizard_obj = self.env["sale.advance.payment.inv"]
        self.partner1 = self.partner_obj.create(
            {
                "name": "Iron man",
                "email": "iron-man@marvel.be",
            }
        )
        self.tax = self.tax_obj.search([], limit=1)
        self.product1 = self.env.ref("product.product_product_9")
        self.product2 = self.env.ref("product.product_product_11")
        (self.product1 | self.product2).write(
            {
                "invoice_policy": "order",
            }
        )
        self.analytic1 = self.analytic_obj.create(
            {
                "name": "Analytic account 1",
            }
        )
        self.analytic2 = self.analytic_obj.create(
            {
                "name": "Analytic account 2",
            }
        )

    def _create_sale_order(self, validate=True, invoice=True, invoice_validate=True):
        """
        Create a sale order and set an analytic account
        :param validate: bool
        :param invoice: bool
        :param invoice_validate: bool
        :return:
        """
        values = {
            "partner_id": self.partner1.id,
            "date_order": fields.Datetime.now(),
            "analytic_account_id": self.analytic1.id,
            "order_line": [
                (
                    0,
                    False,
                    {
                        "product_id": self.product1.id,
                        "name": self.product1.name,
                        "product_uom_qty": 10,
                        "price_unit": 20,
                        "tax_id": [(6, 0, self.tax.ids)],
                    },
                ),
                (
                    0,
                    False,
                    {
                        "product_id": self.product2.id,
                        "name": self.product2.name,
                        "product_uom_qty": 5,
                        "price_unit": 30,
                        "tax_id": [(6, 0, self.tax.ids)],
                    },
                ),
            ],
        }
        sale_order = self.sale_obj.create(values)
        if validate or invoice:
            sale_order.action_confirm()
        if invoice:
            context = {
                "active_model": sale_order._name,
                "active_ids": sale_order.ids,
                "active_id": sale_order.id,
                "open_invoices": True,
            }
            adv_wizard_obj = self.adv_wizard_obj.with_context(**context)
            adv_wizard = adv_wizard_obj.create(
                {
                    "advance_payment_method": "delivered",
                }
            )
            adv_wizard.create_invoices()
            self.assertTrue(sale_order.invoice_ids)
            if invoice_validate:
                sale_order.invoice_ids.action_post()
        self.sale_order = sale_order
        return sale_order

    def create_wizard(self, sale_order):
        """
        Create a wizard related to given sale order
        :param sale_order: sale.order recordset
        :return: sale.order.change.analytic recordset
        """
        wizard_obj = self.wizard_obj.with_context(
            active_id=sale_order.id,
            active_ids=sale_order.ids,
            active_model=sale_order._name,
        )
        fields_list = wizard_obj.fields_get().keys()
        values = wizard_obj.default_get(fields_list)
        values.update(
            {
                "new_analytic_account_id": self.analytic2.id,
            }
        )
        wizard = wizard_obj.create(values)
        self.wizard = wizard
        return wizard

    def test_update_analytic_account(self):
        """
        Ensure every analytic accounts are correctly updated
        :return:
        """
        sale_order = self._create_sale_order()
        wizard = self.create_wizard(sale_order)
        # Ensure it's correct before continue
        self.assertEqual(sale_order.analytic_account_id, self.analytic1)
        self.assertEqual(wizard.new_analytic_account_id, self.analytic2)
        invoices = sale_order.invoice_ids
        invoice_lines = invoices.mapped("invoice_line_ids")
        self.assertEqual(invoice_lines.mapped("analytic_account_id"), self.analytic1)
        wizard.action_update()
        self.assertEqual(sale_order.analytic_account_id, self.analytic2)
        self.assertEqual(invoice_lines.mapped("analytic_account_id"), self.analytic2)

    def test_update_analytic_account_on_unrelated_invoice_lines(self):
        """
        Ensure every analytic accounts are correctly updated
        :return:
        """
        sale_order = self._create_sale_order(invoice_validate=False)
        wizard = self.create_wizard(sale_order)
        # Ensure it's correct before continue
        self.assertEqual(sale_order.analytic_account_id, self.analytic1)
        self.assertEqual(wizard.new_analytic_account_id, self.analytic2)
        invoices = sale_order.invoice_ids
        invoice_line = fields.first(invoices.mapped("invoice_line_ids"))
        invoices.write(
            {
                "invoice_line_ids": [
                    (
                        0,
                        False,
                        {
                            "product_id": self.product1.id,
                            "name": self.product1.name,
                            "quantity": 1,
                            "analytic_account_id": self.analytic1.id,
                            "price_unit": 20,
                            "account_id": invoice_line.account_id.id,
                        },
                    ),
                ],
            }
        )
        invoices.action_post()
        invoice_lines = invoices.mapped("invoice_line_ids")
        self.assertEqual(invoice_lines.mapped("analytic_account_id"), self.analytic1)
        wizard.action_update()
        self.assertEqual(sale_order.analytic_account_id, self.analytic2)
        self.assertEqual(invoice_lines.mapped("analytic_account_id"), self.analytic2)
