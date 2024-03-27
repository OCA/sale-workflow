# Copyright 2023 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import Date
from odoo.tests import Form
from odoo.tests.common import TransactionCase

from odoo.addons.stock_account.tests.test_stockvaluation import _create_accounting_data


class TestSaleStockReconcileValuationKit(TransactionCase):
    def setUp(self):
        super(TestSaleStockReconcileValuationKit, self).setUp()
        # Create Partner
        self.partner = self.env["res.partner"].create({"name": "Mr. Odoo"})

        # Create Accounts
        (
            self.stock_input_account,
            self.stock_output_account,
            self.stock_valuation_account,
            self.expense_account,
            self.stock_journal,
        ) = _create_accounting_data(self.env)

        # Create product category and product
        self.avco_category = self.env["product.category"].create(
            {
                "name": "AVCO",
                "property_cost_method": "average",
                "property_valuation": "real_time",
                "property_stock_account_input_categ_id": self.stock_input_account.id,
                "property_stock_account_output_categ_id": self.stock_output_account.id,
                "property_stock_journal": self.stock_journal.id,
                "property_stock_valuation_account_id": self.stock_valuation_account.id,
            }
        )

        kit, compo01, compo02 = self.env["product.product"].create(
            [
                {
                    "name": name,
                    "standard_price": price,
                    "type": "product",
                    "categ_id": self.avco_category.id,
                }
                for name, price in [("Kit", 0), ("Compo 01", 10), ("Compo 02", 20)]
            ]
        )

        self.env["mrp.bom"].create(
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
        self.env.company.anglo_saxon_accounting = True

        # Create SO
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.partner
        with so_form.order_line.new() as sol_form:
            sol_form.product_id = kit
        self.so = so_form.save()
        self.so.action_confirm()

        # Set & Validate Picking
        for ml in self.so.picking_ids.move_ids:
            ml.quantity_done = 1
        self.so.picking_ids.button_validate()

        self.invoice = self.so._create_invoices()
        self.invoice.invoice_date = Date.today()
        self.invoice.action_post()

    def test_account_kit_reconciled(self):
        lines = self.invoice.line_ids.filtered(
            lambda x: x.account_id.id == self.stock_output_account.id
        )
        for line in lines:
            self.assertTrue(line.reconciled)
