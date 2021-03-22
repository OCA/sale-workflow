# © 2018  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TaxCase(TransactionCase):
    def setUp(self):
        super(TaxCase, self).setUp()
        self.ht_plist = self.env.ref("sale_order_pricelist_tax.ht_pricelist")
        self.ttc_plist = self.env.ref("sale_order_pricelist_tax.ttc_pricelist")
        self.fp_exp = self.env.ref("sale_order_pricelist_tax.fiscal_position_exp")
        self.product = self.env.ref("sale_order_pricelist_tax.ak_product")

    def _create_sale_order(self, pricelist):
        # Creating a sale order
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_10").id,
                "pricelist_id": pricelist.id,
            }
        )
        vals = {
            "product_uom_qty": 1,
            "product_id": self.product.id,
            "order_id": sale.id,
        }
        vals = self.env["sale.order.line"].play_onchanges(vals, vals.keys())
        sale.write({"order_line": [(0, 0, vals)]})
        return sale

    def test_tax_ht(self):
        sale = self._create_sale_order(self.ht_plist)
        self.assertEqual(sale.order_line[0].price_unit, 10)
        self.assertEqual(sale.amount_total, 12)
        self.assertEqual(sale.amount_untaxed, 10)

    def test_tax_ht_update(self):
        sale = self._create_sale_order(self.ttc_plist)
        sale.pricelist_id = self.ht_plist
        sale.update_prices()
        self.assertEqual(sale.order_line[0].price_unit, 10)
        self.assertEqual(sale.amount_total, 12)
        self.assertEqual(sale.amount_untaxed, 10)

    def test_tax_ht_fp(self):
        sale = self._create_sale_order(self.ht_plist)

        # Set fiscal position
        sale.write({"fiscal_position_id": self.fp_exp.id})
        sale.update_prices()
        self.assertEqual(sale.order_line[0].price_unit, 10)
        self.assertEqual(sale.amount_total, 10)
        self.assertEqual(sale.amount_untaxed, 10)

        # Remove fiscal position
        sale.write({"fiscal_position_id": False})
        sale.update_prices()
        self.assertEqual(sale.order_line[0].price_unit, 10)
        self.assertEqual(sale.amount_total, 12)
        self.assertEqual(sale.amount_untaxed, 10)

    def test_tax_ttc(self):
        sale = self._create_sale_order(self.ttc_plist)
        self.assertEqual(sale.order_line[0].price_unit, 12)
        self.assertEqual(sale.amount_total, 12)
        self.assertEqual(sale.amount_untaxed, 10)

    def test_tax_ttc_fp(self):
        sale = self._create_sale_order(self.ttc_plist)

        # Set fiscal position
        sale.write({"fiscal_position_id": self.fp_exp.id})
        sale.update_prices()
        self.assertEqual(sale.order_line[0].price_unit, 10)
        self.assertEqual(sale.amount_total, 10)
        self.assertEqual(sale.amount_untaxed, 10)

        # Remove fiscal position
        sale.write({"fiscal_position_id": False})
        sale.update_prices()
        self.assertEqual(sale.order_line[0].price_unit, 12)
        self.assertEqual(sale.amount_total, 12)
        self.assertEqual(sale.amount_untaxed, 10)
