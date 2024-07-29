# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.sale_tier_validation.tests.test_tier_validation import (
    TestSaleTierValidation,
)


@tagged("post_install", "-at_install")
class TestSaleTierValidationBlockPrint(TestSaleTierValidation):
    def test_block_print_unvalidated_sale_order(self):
        so = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Test line",
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    )
                ],
                "pricelist_id": self.customer.property_product_pricelist.id,
            }
        )

        report = self.env["report.sale.report_saleorder"]
        # Attempt to render the report before validation
        with self.assertRaises(ValidationError):
            report._get_report_values(docids=[so.id])
        so.request_validation()
        with self.assertRaises(ValidationError):
            report._get_report_values(docids=[so.id])
        so.with_user(self.test_user_1).validate_tier()
        # Attempt to render the report after validation
        report._get_report_values(docids=[so.id])
