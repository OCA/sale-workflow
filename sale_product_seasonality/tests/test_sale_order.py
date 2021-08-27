# Copyright 2021 Camptocamp SA
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
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

    def test_create(self):
        self.assertRecordValues(
            self.order,
            [
                {
                    # Default config
                    "seasonal_config_id": self.order.company_id.default_seasonal_config_id.id,
                    # Dates get rounded
                    "commitment_date": fields.Datetime.to_datetime(
                        "2021-05-20 11:05:00"
                    ),
                    "commitment_date_end": fields.Datetime.to_datetime(
                        "2021-05-21 11:20:00"
                    ),
                }
            ],
        )

    def test_write(self):
        self.order.write(
            {
                "commitment_date": "2021-05-30 10:13:20",
                "commitment_date_end": "2021-06-05 14:24:05",
            }
        )
        self.assertRecordValues(
            self.order,
            [
                {
                    # Dates get rounded
                    "commitment_date": fields.Datetime.to_datetime(
                        "2021-05-30 10:15:00"
                    ),
                    "commitment_date_end": fields.Datetime.to_datetime(
                        "2021-06-05 14:25:00"
                    ),
                }
            ],
        )

    def test_onchange_dates(self):
        form = Form(self.order)
        form.commitment_date = "2021-05-30 10:13:20"
        # rounded
        self.assertEqual(
            form.commitment_date, fields.Datetime.to_datetime("2021-05-30 10:15:00")
        )
        # commitment_date_end default
        self.assertEqual(
            form.commitment_date_end, fields.Datetime.to_datetime("2021-05-30 10:15:00")
        )
        # commitment_date_end change rounding
        form.commitment_date_end = "2021-06-05 14:24:05"
        self.assertEqual(
            form.commitment_date_end, fields.Datetime.to_datetime("2021-06-05 14:25:00")
        )

    def test_onchange_partner(self):
        form = Form(self.order.browse())
        new_partner = self.partner.copy(
            {
                "name": "New Partner w/ New Conf",
                "seasonal_config_id": self.seasonal_conf.copy().id,
            }
        )
        form.partner_id = self.partner
        # initial partner had no specific conf
        self.assertEqual(
            form.seasonal_config_id, self.env.company.default_seasonal_config_id
        )
        form.partner_id = new_partner
        self.assertEqual(form.seasonal_config_id, new_partner.seasonal_config_id)

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
        form.commitment_date = "2021-05-09"
        # no product available before
        self.assertFalse(form.season_allowed_product_ids)
        form.commitment_date = "2021-05-13"  # thu
        self.assertEqual(
            sorted(form.season_allowed_product_ids._get_ids()),
            sorted(self.prod2.product_tmpl_id.product_variant_ids.ids),
        )
        form.commitment_date = "2021-05-10"  # mon
        self.assertEqual(form.season_allowed_product_ids._get_ids(), self.prod1.ids)
        # enable Thu on line 1 and find them all
        line = self.seasonal_conf.config_for_product(self.prod1)
        line.thursday = True
        form.commitment_date = "2021-05-13"  # mon
        self.assertEqual(
            sorted(form.season_allowed_product_ids._get_ids()),
            sorted((self.prod1 + self.prod2.product_tmpl_id.product_variant_ids).ids),
        )
