# Copyright 2022 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import Form, SavepointCase


class TestSO(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.carrier_wizard = cls.env["choose.delivery.carrier"]
        cls.carrier = cls.env.ref("delivery.delivery_carrier")
        cls.product_1 = cls.env.ref("product.product_product_4b")
        cls.partner = cls.env.ref("base.res_partner_2")

    def test1(self):
        vals = {
            "partner_id": self.partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "product_id": self.product_1.id,
                        "product_uom": self.product_1.uom_id.id,
                        "product_uom_qty": 1.0,
                    },
                )
            ],
        }
        sale = self.env["sale.order"].create(vals)

        with self.assertRaises(ValidationError) as e:
            sale.action_confirm()
        self.assertIn("specify a delivery method to confirm", e.exception.args[0])

        delivery_wizard = Form(
            self.carrier_wizard.with_context(
                **{
                    "default_order_id": sale.id,
                    "default_carrier_id": self.carrier.id,
                }
            )
        )
        choose_delivery_carrier = delivery_wizard.save()
        choose_delivery_carrier.update_price()
        choose_delivery_carrier.button_confirm()
        sale.action_confirm()
