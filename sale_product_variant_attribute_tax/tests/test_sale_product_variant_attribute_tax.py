# Copyright 2016-2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import Form, common


class TestSaleProductVariantAttributeTax(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tax = cls.env["account.tax"].create(
            {"name": "Tax by attribute value", "amount": 10}
        )
        cls.tax2 = cls.env["account.tax"].create(
            {"name": "Replacement Tax", "amount": 10}
        )
        cls.fiscal_position = cls.env["account.fiscal.position"].create(
            {
                "name": "Test fiscal position",
                "tax_ids": [
                    (0, 0, {"tax_src_id": cls.tax.id, "tax_dest_id": cls.tax2.id},),
                ],
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test", "property_account_position_id": False}
        )
        cls.attribute = cls.env["product.attribute"].create({"name": "Test attribute"})
        cls.attribute_value = cls.env["product.attribute.value"].create(
            {
                "name": "Test value",
                "attribute_id": cls.attribute.id,
                "tax_ids": [(6, 0, cls.tax.ids)],
            }
        )
        cls.attribute_value2 = cls.env["product.attribute.value"].create(
            {"name": "Test value 2", "attribute_id": cls.attribute.id}
        )
        obj = cls.env["product.template"].with_context(check_variant_creation=True)
        cls.product_template = obj.create(
            {
                "name": "Test template",
                "no_create_variants": "yes",
                "taxes_id": False,
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.attribute.id,
                            "value_ids": [(6, 0, cls.attribute_value.ids)],
                        },
                    ),
                ],
            }
        )
        order_form = Form(cls.env["sale.order"])
        order_form.partner_id = cls.partner
        with order_form.order_line.new() as order_line_form:
            order_line_form.product_tmpl_id = cls.product_template
        cls.order = order_form.save()
        cls.order_line = cls.order.order_line

    def test_select_attribute_wo_tax(self):
        self.order_line.product_attribute_ids[0].value_id = self.attribute_value2.id
        self.order_line._onchange_product_attribute_ids_configurator()
        self.assertFalse(self.order_line.tax_id)

    def test_select_attribute_with_tax(self):
        self.order_line.product_attribute_ids[0].value_id = self.attribute_value.id
        self.order_line._onchange_product_attribute_ids_configurator()
        self.assertEqual(self.order_line.tax_id, self.tax)

    def test_select_attribute_with_tax_fp_mapped(self):
        self.order_line.product_attribute_ids[0].value_id = self.attribute_value.id
        self.order.fiscal_position_id = self.fiscal_position
        self.order_line._onchange_product_attribute_ids_configurator()
        self.assertEqual(self.order_line.tax_id, self.tax2)
