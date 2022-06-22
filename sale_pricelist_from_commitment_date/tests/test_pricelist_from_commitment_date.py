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

    def _import_file_and_check_price_unit(self, file_vals):
        file = "{}\r\n{}".format(
            ",".join(file_vals.keys()), ",".join(file_vals.values())
        )
        # Create the importer and run it
        res = (
            self.env["base_import.import"]
            .create(
                {
                    "res_model": "sale.order",
                    "file": file.encode("utf-8"),
                    "file_type": "text/csv",
                    "file_name": "data.csv",
                }
            )
            .do(
                fields=list(file_vals.keys()),
                columns=list(file_vals.keys()),
                options={
                    "quoting": '"',
                    "separator": ",",
                    "headers": True,
                    "encoding": "utf-8",
                    "datetime_format": "%Y-%m-%d %H:%M:%S",
                },
            )
        )
        # Check if the order line's price unit is the expected one
        order = self.env["sale.order"].browse(res["ids"])
        real_pu = order.order_line[-1].price_unit
        expected_pu = float(file_vals["order_line/price_unit"])
        self.assertEqual(real_pu, expected_pu)

    def test_00_pricelist(self):
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

    def test_01_import_create(self):
        """Tests whether prices are correctly set when creating a new SO"""
        # These are the values we'll use to create the file to import
        partner = self.env.ref("base.res_partner_2")
        product = self.env.ref("product.product_product_8")
        user = self.env.ref("base.user_demo")
        self._import_file_and_check_price_unit(
            {
                "id": "__import__.sale_order_test_pricelist_from_commitment_date",
                "name": "Test Pricelist From Commitment Date",
                "partner_id": partner.name,
                "user_id": user.name,
                "order_line/product_id": product.name,
                "order_line/product_uom_qty": "1",
                "order_line/price_unit": "300.00",
                "commitment_date": "2021-10-22 6:30:00",
            }
        )

    def test_02_import_write(self):
        """Tests whether prices are correctly set when updating a SO"""
        # These are the values we'll use to create the file to import
        product = self.env.ref("product.product_product_8")
        self._import_file_and_check_price_unit(
            {
                "id": self.sale.get_xml_id()[self.sale.id],
                "order_line/product_id": product.name,
                "order_line/product_uom_qty": "1",
                "order_line/price_unit": "300.00",
            }
        )
