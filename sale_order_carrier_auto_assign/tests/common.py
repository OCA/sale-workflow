# Copyright 2020 Camptocamp SA
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrderCarrierAutoAssignCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.settings = cls.env["res.config.settings"].create({})
        cls.product_storable = cls.env["product.product"].create(
            {
                "name": "Test product storable",
                "type": "consu",
                "weight": 1.0,
            }
        )
        cls.product_service = cls.env["product.product"].create(
            {
                "name": "Test product service",
                "type": "service",
            }
        )
        cls.delivery_local_delivery = cls.env["delivery.carrier"].create(
            {
                "name": "Local Delivery",
                "delivery_type": "fixed",
                "product_id": cls.env["product.product"]
                .create(
                    {
                        "name": "Delivery Product",
                        "type": "service",
                    }
                )
                .id,
                "fixed_price": 10.0,
                "free_over": False,
            }
        )
        cls.delivery_carrier_alternative = cls.env["delivery.carrier"].create(
            {
                "name": "Alternative Carrier",
                "delivery_type": "fixed",
                "product_id": cls.env["product.product"]
                .create(
                    {
                        "name": "Alternative Delivery Product",
                        "type": "service",
                    }
                )
                .id,
                "fixed_price": 15.0,
                "free_over": False,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test partner",
                "property_delivery_carrier_id": cls.delivery_local_delivery.id,
            }
        )

    @classmethod
    def _create_sale_order(cls):
        sale_order_form = Form(cls.env["sale.order"])
        sale_order_form.partner_id = cls.partner
        with sale_order_form.order_line.new() as line_form:
            line_form.product_id = cls.product_storable
        return sale_order_form.save()
