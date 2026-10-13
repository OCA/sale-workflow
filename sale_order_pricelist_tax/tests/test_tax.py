# © 2018  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TaxCase:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context={"test_pricelist_tax": True})
        cls.env.user.groups_id += cls.env.ref("product.group_product_pricelist")
        cls._create_taxes()
        cls._create_product()
        cls._create_pricelists()
        cls._create_fiscal_positions()

    @classmethod
    def _create_taxes(cls):
        account_tax = cls.env["account.tax"]
        cls.tax_exc = account_tax.create(
            {
                "name": "Test Sale Tax 20%",
                "type_tax_use": "sale",
                "amount": 20.0,
                "price_include_override": "tax_excluded",
            }
        )
        cls.tax_inc = account_tax.create(
            {
                "name": "Test Sale Tax 20% included",
                "type_tax_use": "sale",
                "amount": 20.0,
                "price_include_override": "tax_included",
            }
        )
        cls.tax_exp = account_tax.create(
            {
                "name": "Test Export 0%",
                "type_tax_use": "sale",
                "amount": 0.0,
                "price_include_override": "tax_excluded",
            }
        )
        cls.tax_pap_1 = account_tax.create(
            {
                "name": "Test Papeete Sale Tax 16% included",
                "type_tax_use": "sale",
                "amount": 16.0,
                "price_include_override": "tax_included",
            }
        )
        cls.tax_pap_2 = account_tax.create(
            {
                "name": "Test Papeete Sale Tax 1% included",
                "type_tax_use": "sale",
                "amount": 1.0,
                "price_include_override": "tax_included",
            }
        )
        cls.tax_exc.equivalent_tax_inc_id = cls.tax_inc

    @classmethod
    def _create_product(cls):
        cls.product = cls.env["product.product"].create(
            {
                "name": "ak product",
                "type": "consu",
                "list_price": 10.0,
                "taxes_id": [(6, 0, cls.tax_inc.ids)],
            }
        )

    @classmethod
    def _create_pricelists(cls):
        cls.ht_plist = cls.env["product.pricelist"].create(
            {"name": "Prix HT", "price_include_taxes": False}
        )
        cls.ttc_plist = cls.env["product.pricelist"].create(
            {"name": "Prix TTC", "price_include_taxes": True}
        )
        cls.env["product.pricelist.item"].create(
            [
                {
                    "pricelist_id": cls.ht_plist.id,
                    "applied_on": "0_product_variant",
                    "compute_price": "fixed",
                    "fixed_price": 10.0,
                    "product_id": cls.product.id,
                },
                {
                    "pricelist_id": cls.ttc_plist.id,
                    "applied_on": "0_product_variant",
                    "compute_price": "fixed",
                    "fixed_price": 12.0,
                    "product_id": cls.product.id,
                },
            ]
        )

    @classmethod
    def _create_fiscal_positions(cls):
        fiscal_position = cls.env["account.fiscal.position"]
        cls.fp_exp = fiscal_position.create(
            {"name": "Import/Export", "sequence": 50, "auto_apply": False}
        )
        cls.fp_papeete = fiscal_position.create(
            {"name": "Papeete", "sequence": 50, "auto_apply": False}
        )
        cls.env["account.fiscal.position.tax"].create(
            [
                {
                    "position_id": cls.fp_exp.id,
                    "tax_src_id": cls.tax_exc.id,
                    "tax_dest_id": cls.tax_exp.id,
                },
                {
                    "position_id": cls.fp_exp.id,
                    "tax_src_id": cls.tax_inc.id,
                    "tax_dest_id": cls.tax_exp.id,
                },
                {
                    "position_id": cls.fp_papeete.id,
                    "tax_src_id": cls.tax_inc.id,
                    "tax_dest_id": cls.tax_pap_1.id,
                },
                {
                    "position_id": cls.fp_papeete.id,
                    "tax_src_id": cls.tax_inc.id,
                    "tax_dest_id": cls.tax_pap_2.id,
                },
            ]
        )

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
        sale.action_update_prices()
        self.assertEqual(sale.order_line[0].price_unit, 10)
        self.assertEqual(sale.amount_total, 12)
        self.assertEqual(sale.amount_untaxed, 10)

    def test_tax_ht_fp(self):
        sale = self._create_sale_order(self.ht_plist)

        # Set fiscal position
        sale.write({"fiscal_position_id": self.fp_exp.id})
        sale.action_update_prices()
        self.assertEqual(sale.order_line[0].price_unit, 10)
        self.assertEqual(sale.amount_total, 10)
        self.assertEqual(sale.amount_untaxed, 10)

        # Remove fiscal position
        sale.write({"fiscal_position_id": False})
        sale.action_update_prices()
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
        sale.action_update_prices()
        self.assertEqual(sale.order_line[0].price_unit, 10)
        self.assertEqual(sale.amount_total, 10)
        self.assertEqual(sale.amount_untaxed, 10)

        # Remove fiscal position
        sale.write({"fiscal_position_id": False})
        sale.action_update_prices()
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
        sale.action_update_prices()
        self.assertEqual(sale.order_line[0].price_unit, 12)
        self.assertEqual(sale.amount_total, 12)
        self.assertEqual(sale.amount_untaxed, 10.26)


class TaxCaseBaseTaxInc(TaxCase, TransactionCase):
    allow_inherited_tests_method = True

    def test_missing_tax(self):
        self.tax_exc.equivalent_tax_inc_id = False

        with self.assertRaises(UserError) as m:
            self._create_sale_order(self.ht_plist)

        self.assertEqual(
            m.exception.args[0],
            "Equivalent tax exclude for 'Test Sale Tax 20% included' is missing",
        )


class TaxCaseBaseTaxExc(TaxCase, TransactionCase):
    allow_inherited_tests_method = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product.taxes_id = cls.tax_exc

    def test_missing_tax(self):
        self.tax_exc.equivalent_tax_inc_id = False
        with self.assertRaises(UserError) as m:
            self._create_sale_order(self.ttc_plist)
        self.assertEqual(
            m.exception.args[0],
            "Equivalent tax include for 'Test Sale Tax 20%' is missing",
        )
