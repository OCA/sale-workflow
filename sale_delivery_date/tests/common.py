# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import Form, SavepointCase
from odoo.tools import mute_logger

PARTNER_CUTOFF_TIME = 9.0
WAREHOUSE_CUTOFF_TIME = 10.0
TZ = "Europe/Paris"


class Common(SavepointCase):
    """Common test class providing helpful methods when writing tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.setUpClassCompany()
        cls.setUpClassPartner()
        cls.setUpClassProduct()
        cls.setUpClassCommon()
        cls.setUpClassCalendar()
        cls.setUpClassWarehouse()
        cls.setUpClassOrder()

    @classmethod
    def setUpClassCompany(cls):
        cls.company = cls.env.ref("base.main_company")
        report_layout = cls.env.ref("web.external_layout_standard")
        paperformat_a4 = cls.env.ref("base.paperformat_euro")
        cls.company.write(
            {
                # the global lead time will always plan 1 day before
                "security_lead": 1.00,
                "external_report_layout_id": report_layout.id,
                "paperformat_id": paperformat_a4.id,
            }
        )

    @classmethod
    def setUpClassPartner(cls):
        cls.customer_partner_cutoff = cls.env["res.partner"].create(
            {
                "name": "Partner cutoff",
                "order_delivery_cutoff_preference": "partner_cutoff",
                "tz": TZ,
                "cutoff_time": PARTNER_CUTOFF_TIME,
            }
        )
        cls.customer_warehouse_cutoff = cls.env["res.partner"].create(
            {
                "name": "Partner warehouse cutoff",
                "order_delivery_cutoff_preference": "warehouse_cutoff",
                "tz": TZ,
            }
        )
        cls.customers = cls.customer_partner_cutoff | cls.customer_warehouse_cutoff

    @classmethod
    def setUpClassOrder(cls):
        products = cls._get_default_products()
        cls.order_partner_cutoff = cls._create_sale_order(
            cls.customer_partner_cutoff, products
        )
        cls.order_warehouse_cutoff = cls._create_sale_order(
            cls.customer_warehouse_cutoff, products
        )

    @classmethod
    def setUpClassCalendar(cls):
        name = "40 Hours"
        [(9, 17, i) for i in range(5)]
        cls.calendar = cls.env["resource.calendar"].create({"name": name})
        weekday_numbers = tuple(range(5))
        time_ranges = [(9.0, 17.0)]
        cls._set_calendar_attendances(cls.calendar, weekday_numbers, time_ranges)

    @classmethod
    def _get_attendance_values(cls, weekday_numbers, time_ranges):
        values = [(5, 0, 0)]
        for weekday_number in weekday_numbers:
            for hour_from, hour_to in time_ranges:
                values.append(
                    (
                        0,
                        0,
                        {
                            "name": f"{weekday_number}_{hour_from}_{hour_to}",
                            "hour_from": hour_from,
                            "hour_to": hour_to,
                            "dayofweek": str(weekday_number),
                        },
                    )
                )
        return values

    @classmethod
    def _set_calendar_attendances(cls, calendar, weekday_numbers, time_ranges):
        values = cls._get_attendance_values(weekday_numbers, time_ranges)
        calendar.attendance_ids = values

    @classmethod
    def setUpClassWarehouse(cls):
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.apply_cutoff = True
        cls.warehouse.cutoff_time = WAREHOUSE_CUTOFF_TIME
        cls.warehouse.tz = TZ
        cls.warehouse.calendar2_id = cls.calendar

    @classmethod
    def setUpClassProduct(cls):
        cls.product = cls.env.ref("product.product_product_9")
        cls.product.sale_delay = 1

    @classmethod
    def setUpClassCommon(cls):
        cls.carrier = cls.env.ref("delivery.delivery_carrier")

    @classmethod
    def _get_default_products(cls):
        return [(cls.product, 1)]

    @classmethod
    def _create_sale_order(cls, partner, products, partner_shipping=None):
        """Create a sale order for the given `partner`.

        - `products` is a list of tuples `[(product, qty), ...]`
        - `partner_shipping` is an optional delivery address
        """
        sale_form = Form(cls.env["sale.order"])
        sale_form.partner_id = partner
        if partner_shipping:
            sale_form.partner_shipping_id = partner_shipping
        with mute_logger("odoo.tests.common.onchange"):
            for product, qty in products:
                with sale_form.order_line.new() as line:
                    line.product_id = product
                    line.product_uom_qty = qty
        return sale_form.save()

    @classmethod
    def _add_shipping_on_sale_order(cls, order):
        delivery_wizard = Form(
            cls.env["choose.delivery.carrier"].with_context(
                {
                    "default_order_id": order.id,
                    "default_carrier_id": cls.carrier.id,
                }
            )
        )
        choose_delivery_carrier = delivery_wizard.save()
        choose_delivery_carrier.button_confirm()

    @classmethod
    def _set_partner_time_window(cls, partner, weekday_numbers, date_ranges):
        weekdays = cls.env["time.weekday"].search(
            [("name", "in", [str(i) for i in weekday_numbers])]
        )
        partner.write(
            {
                "delivery_time_preference": "time_windows",
                "delivery_time_window_ids": [
                    (
                        0,
                        0,
                        {
                            "tz": TZ,
                            "time_window_start": start,
                            "time_window_end": end,
                            "time_window_weekday_ids": [(6, 0, weekdays.ids)],
                        },
                    ) for start, end in date_ranges
                ],
            }
        )

    @classmethod
    def _set_partner_time_window_working_days(cls, partner):
        partner.write(
            {
                "delivery_time_preference": "workdays",
                "delivery_time_window_ids": [(5, 0, 0)],
            }
        )

    @classmethod
    def _add_calendar_leaves(cls, calendar, leave_dates=()):
        return cls.env["resource.calendar.leaves"].create(
            [
                {
                    "name": f"leave {date}",
                    "date_from": f"{date} 00:00:00",
                    "date_to": f"{date} 23:59:59",
                    "calendar_id": calendar.id,
                }
                for date in leave_dates
            ]
        )
