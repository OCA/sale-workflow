# © 2018  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests import Form
from odoo.tests.common import SavepointCase


class TaxCase:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ht_plist = cls.env.ref("sale_order_pricelist_tax.ht_pricelist")
        cls.ttc_plist = cls.env.ref("sale_order_pricelist_tax.ttc_pricelist")
        cls.fp_exp = cls.env.ref("sale_order_pricelist_tax.fiscal_position_exp")
        cls.fp_papeete = cls.env.ref("sale_order_pricelist_tax.fiscal_position_papeete")
        cls.product = cls.env.ref("sale_order_pricelist_tax.ak_product")
        cls.tax_exc = cls.env.ref("sale_order_pricelist_tax.account_tax_sale_1")
        cls.tax_inc = cls.env.ref("sale_order_pricelist_tax.account_tax_sale_2")

    def _create_sale_order(self, pricelist):
        order_form = Form(self.env["sale.order"].with_context(tracking_disable=True))
        order_form.partner_id = self.env.ref("base.res_partner_10")
        order_form.pricelist_id = pricelist
        with order_form.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = 1.0
        return order_form.save()

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

    def test_papeete_case(self):
        """Papeete case is a special French case.
        We have to replace the 20% tax inc by two taxes 16% tax inc and 1% tax inc
        When we replace a tax inc by an other tax inc we expect to keep the same
        total tax inc amount.
        """
        sale = self._create_sale_order(self.ttc_plist)

        # Set fiscal position
        sale.write({"fiscal_position_id": self.fp_papeete.id})
        sale.update_prices()
        self.assertEqual(sale.order_line[0].price_unit, 12)
        self.assertEqual(sale.amount_total, 12)
        self.assertEqual(sale.amount_untaxed, 10.26)


class TaxCaseBaseTaxInc(TaxCase, SavepointCase):
    def test_missing_tax(self):
        self.tax_exc.equivalent_tax_inc_id = False
        with self.assertRaises(UserError) as m:
            self._create_sale_order(self.ht_plist)
        self.assertEqual(
            m.exception.name,
            "Equivalent tax exclude for 'Demo Sale Tax 20% included' is missing",
        )


class TaxCaseBaseTaxExc(TaxCase, SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product.taxes_id = cls.tax_exc

    def test_missing_tax(self):
        self.tax_exc.equivalent_tax_inc_id = False
        with self.assertRaises(UserError) as m:
            self._create_sale_order(self.ttc_plist)
        self.assertEqual(
            m.exception.name,
            "Equivalent tax include for 'Demo Sale Tax 20%' is missing",
        )
