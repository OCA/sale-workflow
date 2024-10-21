# Copyright 2023 Ooops404
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)


from odoo.tests import Form, SavepointCase


class TestDeliveryZoneOnPartner(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Partner",
            }
        )
        monday = cls.env.ref("base_time_window.time_weekday_monday")
        tuesday = cls.env.ref("base_time_window.time_weekday_tuesday")
        wednesday = cls.env.ref("base_time_window.time_weekday_wednesday")
        cls.dz1 = cls.env["partner.delivery.zone"].create(
            {
                "name": "Test Zone 2",
                "order_delivery_cutoff_preference": "partner_cutoff",
                "cutoff_time": 8.5,
                "delivery_time_preference": "time_windows",
                "delivery_time_window_ids": [
                    (
                        0,
                        0,
                        {
                            "time_window_start": 9.5,
                            "time_window_end": 11,
                            "time_window_weekday_ids": [
                                (6, 0, [monday.id, wednesday.id])
                            ],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "time_window_start": 13,
                            "time_window_end": 15,
                            "time_window_weekday_ids": [(6, 0, [tuesday.id])],
                        },
                    ),
                ],
            }
        )
        cls.dz2 = cls.env["partner.delivery.zone"].create(
            {
                "name": "Test Zone 1",
                "order_delivery_cutoff_preference": "warehouse_cutoff",
                "delivery_time_preference": "workdays",
            }
        )

    def test_partner_onchange_delivery_zone(self):
        self.assertFalse(
            all(
                self.partner[field]
                for field in (
                    "order_delivery_cutoff_preference",
                    "delivery_time_preference",
                    "delivery_time_preference",
                    "delivery_time_window_ids",
                )
            )
        )

        f = Form(self.partner)
        f.delivery_zone_id = self.dz1
        f.save()

        self.assertEqual(
            self.partner.order_delivery_cutoff_preference,
            self.dz1.order_delivery_cutoff_preference,
        )
        self.assertEqual(
            self.partner.delivery_time_preference,
            self.dz1.delivery_time_preference,
        )
        self.assertEqual(
            self.partner.cutoff_time,
            self.dz1.cutoff_time,
        )
        self.assertCountEqual(
            self.partner.mapped("delivery_time_window_ids.time_window_start"),
            self.dz1.mapped("delivery_time_window_ids.time_window_start"),
        )
        self.assertCountEqual(
            self.partner.mapped("delivery_time_window_ids.time_window_end"),
            self.dz1.mapped("delivery_time_window_ids.time_window_end"),
        )
        self.assertCountEqual(
            self.partner.mapped("delivery_time_window_ids.time_window_weekday_ids"),
            self.dz1.mapped("delivery_time_window_ids.time_window_weekday_ids"),
        )

        f = Form(self.partner)
        f.delivery_zone_id = self.dz2
        f.save()

        self.assertEqual(
            self.partner.order_delivery_cutoff_preference,
            self.dz2.order_delivery_cutoff_preference,
        )
        self.assertEqual(
            self.partner.delivery_time_preference,
            self.dz2.delivery_time_preference,
        )
        self.assertFalse(self.partner.cutoff_time)
        self.assertFalse(self.partner.delivery_time_window_ids)
