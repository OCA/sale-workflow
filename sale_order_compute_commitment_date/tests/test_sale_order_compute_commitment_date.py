# Copyright 2025 APSL Nagarro
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.tests.common import TransactionCase


class TestSaleCommitmentDate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.SaleOrder = cls.env["sale.order"]
        cls.SaleOrderLine = cls.env["sale.order.line"]
        cls.ProductTemplate = cls.env["product.template"]
        cls.ProductAttribute = cls.env["product.attribute"]
        cls.ProductAttributeValue = cls.env["product.attribute.value"]
        cls.ResourceCalendar = cls.env["resource.calendar"]
        cls.ResourceCalendarLeaves = cls.env["resource.calendar.leaves"]
        cls.Partner = cls.env["res.partner"]
        cls.company = cls.env.ref("base.main_company")
        cls.calendar = cls.ResourceCalendar.create(
            {
                "name": "Test Working Calendar (Mon-Fri)",
                "company_id": cls.company.id,
                "hours_per_day": 8.0,
                "tz": "Europe/Madrid",
                "attendance_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Monday Morning",
                            "dayofweek": "0",
                            "hour_from": 8,
                            "hour_to": 12,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Monday Afternoon",
                            "dayofweek": "0",
                            "hour_from": 13,
                            "hour_to": 17,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Tuesday Morning",
                            "dayofweek": "1",
                            "hour_from": 8,
                            "hour_to": 12,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Tuesday Afternoon",
                            "dayofweek": "1",
                            "hour_from": 13,
                            "hour_to": 17,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Wednesday Morning",
                            "dayofweek": "2",
                            "hour_from": 8,
                            "hour_to": 12,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Wednesday Afternoon",
                            "dayofweek": "2",
                            "hour_from": 13,
                            "hour_to": 17,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Thursday Morning",
                            "dayofweek": "3",
                            "hour_from": 8,
                            "hour_to": 12,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Thursday Afternoon",
                            "dayofweek": "3",
                            "hour_from": 13,
                            "hour_to": 17,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Friday Morning",
                            "dayofweek": "4",
                            "hour_from": 8,
                            "hour_to": 12,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Friday Afternoon",
                            "dayofweek": "4",
                            "hour_from": 13,
                            "hour_to": 17,
                        },
                    ),
                ],
            }
        )
        cls.company.resource_calendar_id = cls.calendar

        cls.color_attribute = cls.ProductAttribute.create(
            {"name": "Color", "display_type": "radio"}
        )
        cls.red_value = cls.ProductAttributeValue.create(
            {
                "name": "Red",
                "attribute_id": cls.color_attribute.id,
                "lead_time": 2,
            }
        )
        cls.blue_value = cls.ProductAttributeValue.create(
            {
                "name": "Blue",
                "attribute_id": cls.color_attribute.id,
                "lead_time": 0,
            }
        )

        cls.product_template_a = cls.ProductTemplate.create(
            {
                "name": "Product A",
                "sale_delay": 5,
                "type": "consu",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.color_attribute.id,
                            "value_ids": [
                                (6, 0, [cls.red_value.id, cls.blue_value.id])
                            ],
                        },
                    )
                ],
            }
        )

        cls.product_a_red = cls.env["product.product"].search(
            [
                ("product_tmpl_id", "=", cls.product_template_a.id),
                (
                    "product_template_attribute_value_ids.product_attribute_value_id",
                    "=",
                    cls.red_value.id,
                ),
            ],
            limit=1,
        )
        cls.product_a_blue = cls.env["product.product"].search(
            [
                ("product_tmpl_id", "=", cls.product_template_a.id),
                (
                    "product_template_attribute_value_ids.product_attribute_value_id",
                    "=",
                    cls.blue_value.id,
                ),
            ],
            limit=1,
        )

        cls.product_template_a.attribute_extend_lead_time = True

        cls.test_partner = cls.Partner.create({"name": "Test Partner for Sales"})

        cls.test_creation_date = datetime(2025, 6, 25, 10, 0, 0)

        cls.order = cls.SaleOrder.create(
            {
                "partner_id": cls.test_partner.id,
                "date_order": cls.test_creation_date,
            }
        )
        cls.SaleOrderLine.create(
            {
                "order_id": cls.order.id,
                "product_id": cls.product_a_red.id,
                "product_uom_qty": 1,
            }
        )

        cls.order_2 = cls.SaleOrder.create(
            {
                "partner_id": cls.test_partner.id,
                "date_order": cls.test_creation_date,
            }
        )
        cls.SaleOrderLine.create(
            {
                "order_id": cls.order_2.id,
                "product_id": cls.product_a_red.id,
                "product_uom_qty": 1,
            }
        )

    def test_01_commitment_date_draft_order_calculation(self):
        self.order._compute_commitment_date()

        expected_lead_time_days = 5 + 2

        expected_commitment_date = self.order._get_date_with_lead_time_from_calendar(
            self.test_creation_date, expected_lead_time_days
        )

        self.assertIsNotNone(
            self.order.commitment_date,
            "Commitment date should be calculated for a draft order.",
        )
        self.assertEqual(
            self.order.commitment_date.date(),
            expected_commitment_date.date(),
            "Commitment date for draft order should be calculated correctly based "
            "on date_order.",
        )
        self.assertEqual(
            self.order.commitment_date.date(),
            datetime(2025, 7, 4).date(),
            "Commitment date for draft should be July 4, 2025.",
        )

    def test_02_commitment_date_confirmed_order_calculation(self):
        self.ResourceCalendarLeaves.create(
            {
                "name": "Test Holiday",
                "calendar_id": self.calendar.id,
                "date_from": datetime(2025, 6, 30, 0, 0, 0),
                "date_to": datetime(2025, 6, 30, 23, 59, 59),
            }
        )

        self.assertIsNotNone(
            self.order_2.commitment_date,
            "Commitment date should be calculated in draft.",
        )
        self.assertEqual(
            self.order_2.commitment_date.date(),
            datetime(2025, 7, 4).date(),
            "Initial commitment date in draft should remain July 4, 2025, "
            "since it was already fixed before the holiday was created "
            "and draft recomputes do not overwrite an existing value.",
        )

        self.order_2.action_confirm()

        expected_lead_time_days = 5 + 2

        expected_commitment_date_final = (
            self.order_2._get_date_with_lead_time_from_calendar(
                self.order_2.date_order, expected_lead_time_days
            )
        )

        self.assertEqual(
            self.order_2.commitment_date.date(),
            expected_commitment_date_final.date(),
            "Commitment date for confirmed order should be "
            "recalculated correctly using date_order and holidays.",
        )

    def test_03_commitment_date_no_attribute_lead_time(self):
        test_creation_date = datetime(2025, 6, 25, 10, 0, 0)

        order = self.SaleOrder.create(
            {
                "partner_id": self.test_partner.id,
                "date_order": test_creation_date,
            }
        )
        self.SaleOrderLine.create(
            {
                "order_id": order.id,
                "product_id": self.product_a_blue.id,
                "product_uom_qty": 1,
            }
        )
        order._compute_commitment_date()

        expected_lead_time_days = 5

        expected_commitment_date = order._get_date_with_lead_time_from_calendar(
            test_creation_date, expected_lead_time_days
        )

        self.assertIsNotNone(
            order.commitment_date, "Commitment date should be calculated."
        )
        self.assertEqual(
            order.commitment_date.date(),
            expected_commitment_date.date(),
            "Commitment date should be calculated without attribute lead time.",
        )
        self.assertEqual(
            order.commitment_date.date(),
            datetime(2025, 7, 2).date(),
            "Commitment date should be July 2, 2025.",
        )

    def test_04_commitment_date_attribute_extend_lead_time_false(self):
        self.product_template_a.attribute_extend_lead_time = False

        test_creation_date = datetime(2025, 6, 25, 10, 0, 0)

        order = self.SaleOrder.create(
            {
                "partner_id": self.test_partner.id,
                "date_order": test_creation_date,
            }
        )
        self.SaleOrderLine.create(
            {
                "order_id": order.id,
                "product_id": self.product_a_red.id,
                "product_uom_qty": 1,
            }
        )
        order._compute_commitment_date()

        expected_lead_time_days = 5

        expected_commitment_date = order._get_date_with_lead_time_from_calendar(
            test_creation_date, expected_lead_time_days
        )

        self.assertIsNotNone(
            order.commitment_date, "Commitment date should be calculated."
        )
        self.assertEqual(
            order.commitment_date.date(),
            expected_commitment_date.date(),
            "Commitment date should not include attribute "
            "lead time when attribute_extend_lead_time is False.",
        )
        self.assertEqual(
            order.commitment_date.date(),
            datetime(2025, 7, 2).date(),
            "Commitment date should be July 2, 2025 when attribute_extend_lead_time "
            "is False.",
        )
