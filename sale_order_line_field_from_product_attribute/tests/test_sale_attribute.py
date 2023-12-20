from odoo import Command
from odoo.tests.common import Form, TransactionCase


class TestProjectCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pa = cls.env["product.attribute"].create(
            {
                "name": "Plaque Name",
                "create_variant": "no_variant",
                "store_in_field": cls.env.ref("sale.field_sale_order_line__name").id,
            }
        )
        cls.pa_value1 = cls.env["product.attribute.value"].create(
            {
                "attribute_id": cls.pa.id,
                "sequence": 1,
                "name": "Anonymous",
            }
        )
        cls.pa_value2 = cls.env["product.attribute.value"].create(
            {
                "attribute_id": cls.pa.id,
                "sequence": 2,
                "name": "Name",
                "is_custom": True,
            }
        )

        product_template_form = Form(cls.env["product.template"])
        product_template_form.name = "Test Product"
        cls.product_template = product_template_form.save()
        cls.product_template.write(
            {
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": cls.pa.id,
                            "value_ids": [
                                Command.set([cls.pa_value1.id, cls.pa_value2.id]),
                            ],
                        }
                    )
                ]
            }
        )
        cls.product_attr_line = cls.product_template.attribute_line_ids
        cls.attr_line_value1 = cls.product_attr_line.product_template_value_ids[0]
        cls.attr_line_value2 = cls.product_attr_line.product_template_value_ids[1]
        cls.product = cls.product_template.product_variant_id

        sale_order_form = Form(cls.env["sale.order"])
        sale_order_form.partner_id = cls.env.user.partner_id
        with sale_order_form.order_line.new() as line_form:
            line_form.product_id = cls.product
        cls.order = sale_order_form.save()
        cls.order_line = cls.order.order_line[0]

    def test_regular_value(self):
        vals = {
            "product_no_variant_attribute_value_ids": [
                Command.set([self.attr_line_value1.id])
            ]
        }
        self.order_line.write(vals)
        self.assertEqual(self.order_line.name, "Anonymous")

    def test_custom_value(self):
        vals = {
            "product_no_variant_attribute_value_ids": [
                Command.set([self.attr_line_value2.id])
            ],
            "product_custom_attribute_value_ids": [
                Command.create(
                    {
                        "custom_product_template_attribute_value_id": self.attr_line_value2.id,
                        "custom_value": "Sully",
                    }
                )
            ],
        }
        self.order_line.write(vals)
        self.assertEqual(self.order_line.name, "Sully")
