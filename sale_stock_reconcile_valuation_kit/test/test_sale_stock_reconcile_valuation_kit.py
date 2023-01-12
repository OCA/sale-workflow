# Copyright 2023 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import Date
from odoo.tests import Form
from odoo.tests.common import TransactionCase

from odoo.addons.stock_account.tests.test_stockvaluation import _create_accounting_data


class TestSaleStockReconcileValuationKit(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create Partner
        cls.partner = cls.env["res.partner"].create({"name": "Mr. Odoo"})

        # Create Accounts
        (
            cls.stock_input_account,
            cls.stock_output_account,
            cls.stock_valuation_account,
            cls.expense_account,
            cls.stock_journal,
        ) = _create_accounting_data(cls.env)

        # Create product category and product
        cls.avco_category = cls.env["product.category"].create(
            {
                "name": "AVCO",
                "property_cost_method": "average",
                "property_valuation": "real_time",
                "property_stock_account_input_categ_id": cls.stock_input_account.id,
                "property_stock_account_output_categ_id": cls.stock_output_account.id,
                "property_stock_journal": cls.stock_journal.id,
                "property_stock_valuation_account_id": cls.stock_valuation_account.id,
            }
        )

        kit, compo01, compo02 = cls.env["product.product"].create(
            [
                {
                    "name": name,
                    "standard_price": price,
                    "type": "product",
                    "categ_id": cls.avco_category.id,
                }
                for name, price in [("Kit", 0), ("Compo 01", 10), ("Compo 02", 20)]
            ]
        )

        cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": kit.product_tmpl_id.id,
                "type": "phantom",
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": p.id,
                            "product_qty": 1,
                        },
                    )
                    for p in [compo01, compo02]
                ],
            }
        )

        # Make company use anglo-saxon accounting
        cls.env.company.anglo_saxon_accounting = True

        # Create SO
        so_form = Form(cls.env["sale.order"])
        so_form.partner_id = cls.partner
        with so_form.order_line.new() as sol_form:
            sol_form.product_id = kit
        cls.so = so_form.save()
        cls.so.button_confirm()

        # Validate Picking
        action = cls.so.picking_ids.button_validate()
        wizard = Form(
            cls.env[action["res_model"]].with_context(action["context"])
        ).save()
        wizard.process()

        # Create Invoice
        action = cls.so.action_create_invoice()
        cls.invoice = cls.env["account.move"].browse(action["res_id"])
        cls.invoice.invoice_date = Date.today()
        cls.invoice.action_post()

    def test_account_kit_reconciled(self):
        lines = self.invoice.line_ids.filtered(
            lambda x: x.account_id == self.stock_output_account.id
        )
        for line in lines:
            self.assertTrue(line.reconciled)
