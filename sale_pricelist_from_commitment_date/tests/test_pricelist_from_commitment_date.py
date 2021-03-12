# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class PricelistFromCommitmentDate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # Pricelists.
        cls.pricelist_default = cls.env.ref("product.list0")
        cls.pricelist_parent = cls._create_price_list("Parent Pricelist")
        cls.pricelist = cls._create_price_list("Simple Pricelist")
        cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.pricelist.id,
                "applied_on": "3_global",
                "compute_price": "formula",
                "base": "pricelist",
                "base_pricelist_id": cls.pricelist_parent.id,
            }
        )
        # Test in the past to avoid to have date order in the interval
        cls._create_price_list_item(cls.pricelist, 10, "2020-03-05", "2020-03-09")
        cls._create_price_list_item(cls.pricelist, 20, "2020-03-10", "2020-03-14")
        # Parent item
        cls._create_price_list_item(
            cls.pricelist_parent, 30, "2020-03-15", "2020-03-20"
        )

        # Create the SO with 1 order line
        cls.sale = cls.env.ref("sale.sale_order_1")

    @classmethod
    def _create_price_list(cls, name):
        return cls.env["product.pricelist"].create(
            {
                "name": name,
                "active": True,
                "currency_id": cls.env.ref("base.USD").id,
                "company_id": cls.env.user.company_id.id,
            }
        )

    @classmethod
    def _create_price_list_item(cls, pricelist, price, date_start=None, date_end=None):
        values = {
            "pricelist_id": pricelist.id,
            "applied_on": "3_global",
            "base": "list_price",
            "compute_price": "fixed",
            "fixed_price": price,
        }
        if date_start:
            values["date_start"] = date_start
        if date_end:
            values["date_end"] = date_end
        return cls.env["product.pricelist.item"].create(values)

    def test_pricelist(self):
        sale = self.sale
        order_line = sale.order_line[0]
        product = order_line.product_id
        self.assertEqual(order_line.price_unit, product.list_price)
        # Change pricelist have no effect as no item match
        sale.pricelist_id = self.pricelist
        self.assertEqual(order_line.price_unit, product.list_price)
        # Test with commitment date
        sale.commitment_date = "2020-03-08"
        self.assertEqual(order_line.price_unit, 10)
        sale.commitment_date = "2020-03-12"
        self.assertEqual(order_line.price_unit, 20)
        # Parent price list must match
        sale.commitment_date = "2020-03-17"
        self.assertEqual(order_line.price_unit, 30)
        sale.date_order = "2020-03-08"
        # No change with changing order date
        self.assertEqual(order_line.price_unit, 30)
        # Call the recompute function to be sure we have no changes
        sale._apply_pricelist_from_commitment_date()
        self.assertEqual(order_line.price_unit, 30)
        # Remove commitment date, will match on date_order
        sale.commitment_date = False
        self.assertEqual(order_line.price_unit, 10)
        # Remove the order date, will match on default price
        sale.date_order = False
        # Simulate change of product as the date order must no change normally
        order_line.product_id_change()
        self.assertEqual(order_line.price_unit, product.list_price)
