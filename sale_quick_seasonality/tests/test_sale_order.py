# Copyright 2022 Camptocamp SA
# @author: Damien Crier <damien.crier@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import Form

from .common import CommonCase


class TestSaleOrderCase(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "commitment_date": "2021-05-20 11:03:00",
                "commitment_date_end": "2021-05-21 11:21:00",
            }
        )

    def test_allowed_products(self):
        form = Form(self.order)
        self.partner.seasonal_config_id = self.seasonal_conf
        form.partner_id = self.partner
        # Reminder for configuration from product_seasonality.tests.common:
        # {
        #     "date_start": "2021-05-10",
        #     "date_end": "2021-05-16",
        #     "monday": True,
        #     "tuesday": True,
        #     "wednesday": True,
        #     "thursday": False,
        #     "friday": False,
        #     "saturday": False,
        #     "sunday": False,
        #     "product_id": cls.prod1.id,
        # },
        # {
        #     "date_start": "2021-05-12",
        #     "date_end": "2021-05-23",
        #     "monday": False,
        #     "tuesday": False,
        #     "wednesday": False,
        #     "thursday": True,
        #     "friday": True,
        #     "saturday": True,
        #     "sunday": True,
        #     "product_template_id": cls.prod2.product_tmpl_id.id,
        # },
        form.commitment_date = "2021-05-13"  # mon
        so_allowed_product_ids = sorted(form.season_allowed_product_ids._get_ids())
        form.save()
        add_product_action = self.order.add_product()
        add_product_allowed_product_ids = add_product_action["domain"][0][2]
        self.assertEqual(
            so_allowed_product_ids, sorted(add_product_allowed_product_ids)
        )
