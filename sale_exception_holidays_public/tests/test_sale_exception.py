# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import timedelta

from odoo import Command, fields
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestSaleException(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.holiday_model = cls.env["hr.holidays.public"]
        cls.holiday_model_line = cls.env["hr.holidays.public.line"]

        # Remove possibly existing public holidays that would interfer.
        cls.holiday_model_line.search([]).unlink()
        cls.holiday_model.search([]).unlink()

        # Create holidays
        holiday_date = fields.Date.today() + timedelta(days=10)
        holiday_1 = cls.holiday_model.create(
            {"year": holiday_date.year, "country_id": cls.env.ref("base.sl").id}
        )
        cls.holiday_model_line.create(
            {"name": "holiday 5", "date": holiday_date, "year_id": holiday_1.id}
        )

        cls.holiday_date = holiday_date
        cls.holiday_1 = holiday_1

    def test_sale_order_exception(self):
        self.sale_exception_confirm = self.env["sale.exception.confirm"]

        exception = self.env.ref(
            "sale_exception_holidays_public.excep_commit_on_public_holiday"
        )
        exception.active = True

        partner = self.env.ref("base.res_partner_1")
        p = self.env.ref("product.product_product_6")
        so1 = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "partner_invoice_id": partner.id,
                "partner_shipping_id": partner.id,
                "order_line": [
                    Command.create(
                        {
                            "name": p.name,
                            "product_id": p.id,
                            "product_uom_qty": 2,
                            "product_uom": p.uom_id.id,
                            "price_unit": p.list_price,
                        },
                    )
                ],
                "pricelist_id": self.env.ref("product.list0").id,
            }
        )
        # Update freely without error
        so1.commitment_date = self.holiday_date
        so1.commitment_date = None

        # Update Delivery Date
        self.holiday_1.country_id = None
        so1.state = "sale"
        with self.assertRaises(ValidationError):
            so1.commitment_date = self.holiday_date
        so1.state = "draft"
        so1.commitment_date = self.holiday_date
        so1.action_confirm()
        self.assertTrue(so1.exceptions_summary)
