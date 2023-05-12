# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from freezegun import freeze_time

from odoo.tests.common import SavepointCase

WORKING_DAYS = list(range(5))  # working days are from monday to friday included
CUTOFF_TIME = 8.0  # cutoff time will be set at 8 a.m.

FRIDAY = "2021-08-13"
SATURDAY = "2021-08-14"
NEXT_MONDAY = "2021-08-16"
NEXT_TUESDAY = "2021-08-17"
NEXT_WEDNESDAY = "2021-08-18"
NEXT_THURSDAY = "2021-08-19"
FRIDAY_BEFORE_CUTOFF = "2021-08-13 07:00:00"
FRIDAY_AFTER_CUTOFF = "2021-08-13 09:00:00"
SATURDAY_BEFORE_CUTOFF = "2021-08-14 07:00:00"
SATURDAY_AFTER_CUTOFF = "2021-08-15 09:00:00"


class TestSaleOrderDates(SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super(TestSaleOrderDates, cls).setUpClass()
        cls.env = cls.env(
            context=dict(cls.env.context, tracking_disable=True, tz="UTC")
        )
        cls.setupClassCompany()
        cls.setUpClassCalendar()
        cls.setUpClassWarehouse()
        cls.setUpClassPartner()
        cls.setUpClassProduct()

    @classmethod
    def _define_calendar(cls, name, attendances):
        return cls.env["resource.calendar"].create(
            {
                "name": name,
                "attendance_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "%s_%d" % (name, index),
                            "hour_from": att[0],
                            "hour_to": att[1],
                            "dayofweek": str(att[2]),
                        },
                    )
                    for index, att in enumerate(attendances)
                ],
            }
        )

    @classmethod
    def setupClassCompany(cls):
        cls.company = cls.env.user.company_id
        cls.company.security_lead = 1

    @classmethod
    def setUpClassCalendar(cls):
        cls.calendar = cls._define_calendar(
            "40 Hours",
            [(8, 16, i) for i in range(5)],
        )

    @classmethod
    def setUpClassWarehouse(cls):
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.write(
            {
                "cutoff_time": CUTOFF_TIME,
                "apply_cutoff": True,
                "calendar2_id": cls.calendar,
            }
        )

    @classmethod
    def setUpClassPartner(cls):
        cls.customer = cls.env.ref("base.res_partner_12")
        cls.customer.order_delivery_cutoff_preference = "warehouse_cutoff"
        cls.customer.delivery_time_preference = "workdays"

    @classmethod
    def setUpClassProduct(cls):
        cls.product = cls.env.ref("product.product_product_3")

    def _create_order(self, customer_lead=1):
        order = self.env["sale.order"].create(
            {"partner_id": self.customer.id, "warehouse_id": self.warehouse.id}
        )
        self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "customer_lead": customer_lead,
            }
        )
        return order

    @freeze_time(FRIDAY_BEFORE_CUTOFF)
    def test_confirm_before_cutoff_last_weekday(self):
        # - preparation is friday since sale_cutoff_time_delivery,
        #   has not postponed the delivery
        # - friday is compatible with the warehouse calendar.
        # - customer is only avaiable on weekdays
        # - delivery should be done on monday
        order = self._create_order()
        order.action_confirm()
        self.assertEqual(str(order.expected_date.date()), NEXT_MONDAY)
        picking = order.picking_ids
        self.assertEqual(str(picking.scheduled_date.date()), FRIDAY)

    @freeze_time(FRIDAY_AFTER_CUTOFF)
    def test_confirm_after_cutoff_last_weekday(self):
        # - preparation is delayed by 1 day (sale_cutoff_time_delivery)
        # - preparation is postponned to monday (stock_warehouse_calendar)
        # - delivery should be done on tuesday
        order = self._create_order()
        order.action_confirm()
        self.assertEqual(str(order.expected_date.date()), NEXT_TUESDAY)
        picking = order.picking_ids
        self.assertEqual(str(picking.scheduled_date.date()), NEXT_MONDAY)

    @freeze_time(FRIDAY_BEFORE_CUTOFF)
    def test_confirm_before_cutoff_last_weekday_3_days_preparation(self):
        # initial expected_date NEXT_MONDAY
        # - preparation isn't delayed by sale_cutoff_time_delivery
        # - preparation is postponned to TUESDAY by sale_warehouse_calendar
        # - delivery should be done on NEXT_WEDNESDAY
        order = self._create_order(customer_lead=3)
        # (Pdb++) order.order_line._get_delays()
        # (3.0, 1.0, 2.0)
        # (Pdb++) datetime.now()
        # FakeDatetime(2021, 8, 13, 7, 0)
        # (Pdb++) order.get_cutoff_time()
        # {'hour': 8, 'minute': 0, 'tz': False}
        # (Pdb++) order.partner_shipping_id.delivery_time_preference
        # 'workdays'
        # WH calendar, monday to friday, from 08:00 to 16:00
        # - date order: 2021-08-13 07:00:00
        # - with cutoff: 2021-08-13 08:00:00
        # - to working day: 2021-08-13 08:00:00
        # - apply workload: 2021-08-17 16:00:00 (2 days delay converted to 3 days)
        # - apply security lead: 2021-08-18 16:00:00
        # - apply delivery window: 2021-08-18 00:00:00
        # delivery_date = 2021-08-18 00:00:00
        # - deduct security_lead: 2021-08-16 00:00:00
        # - apply time.max(): 2021-08-16 23:59:59
        # - end of last attendance: 2021-08-16 16:00:00
        # - deduct workload: 2021-08-13 08:00:00
        # - with cutoff: 2021-08-13 08:00:00
        # preparation_date 2021-08-13 08:00:00
        order.action_confirm()
        self.assertEqual(str(order.expected_date), "2021-08-18 00:00:00")
        picking = order.picking_ids
        self.assertEqual(str(picking.scheduled_date), "2021-08-13 08:00:00")

    @freeze_time(SATURDAY_BEFORE_CUTOFF)
    def test_confirm_before_cutoff_weekend_3_days_preparation(self):
        order = self._create_order(customer_lead=3)
        # (Pdb++) order.order_line._get_delays()
        # (3.0, 1.0, 2.0)
        # (Pdb++) datetime.now()
        # FakeDatetime(2021, 8, 14, 7, 0)
        # (Pdb++) order.get_cutoff_time()
        # {'hour': 8, 'minute': 0, 'tz': False}
        # (Pdb++) order.partner_shipping_id.delivery_time_preference
        # 'workdays'
        # WH calendar, monday to friday, from 08:00 to 16:00
        # - date order: 2021-08-14 07:00:00
        # - with cutoff: 2021-08-14 08:00:00
        # - to working day: 2021-08-16 08:00:00
        # - apply workload: 2021-08-18 16:00:00 (2 days delay converted to 3 days)
        # - apply security lead: 2021-08-19 16:00:00
        # - apply delivery window: 2021-08-19 00:00:00
        # delivery_date = 2021-08-19 00:00:00
        # - deduct security_lead: 2021-08-18 00:00:00
        # - apply time.max(): 2021-08-18 23:59:59
        # - end of last attendance: 2021-08-18 16:00:00
        # - deduct workload: 2021-08-15 08:00:00
        # - with cutoff: 2021-08-15 08:00:00
        # preparation_date 2021-08-15 08:00:00
        order.action_confirm()
        self.assertEqual(str(order.expected_date), "2021-08-19 00:00:00")
        picking = order.picking_ids
        self.assertEqual(str(picking.scheduled_date), "2021-08-16 08:00:00")
