# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo.exceptions import AccessError
from odoo.tests.common import Form, TransactionCase, tagged


@tagged("-at_install", "post_install")
@freeze_time("2022-02-04 09:00:00")
class TestSalePlannerCalendar(TransactionCase):
    def setUp(self):
        super().setUp()
        self.env = self.env(context=dict(self.env.context, tracking_disable=True))
        self.CalendarEvent = self.env["calendar.event"]
        self.ResUsers = self.env["res.users"]
        self.Partner = self.env["res.partner"]
        self.ProductTemplate = self.env["product.template"]
        self.Product = self.env["product.product"]
        self.AccountInvoice = self.env["account.move"]
        self.AccountInvoiceLine = self.env["account.move.line"]
        self.AccountJournal = self.env["account.journal"]
        self.SaleOrder = self.env["sale.order"]

        self.event_type_commercial_visit = self.env.ref(
            "sale_planner_calendar.event_type_commercial_visit"
        )
        self.event_type_delivery = self.env.ref(
            "sale_planner_calendar.event_type_delivery"
        )
        self.pricelist = self.env["product.pricelist"].create(
            {"name": "Test pricelist", "currency_id": self.env.company.currency_id.id}
        )

        # Create some products
        self._create_products()

        # Create some commercial users
        self._create_commercial_users()

        # Create some partners
        self._create_partners()

        # Create some calendar planner events
        self.create_calendar_planner_event()

        # Some account data
        account_type_income = self.env.ref("account.data_account_type_revenue")
        self.account = self.env["account.account"].create(
            {
                "code": "test",
                "name": "Test account",
                "user_type_id": account_type_income.id,
            }
        )

    def _create_commercial_users(self):
        # Create commercial_user_1 and commercial_user_2 with Own Documents
        # Only security group
        self.commercial_users = self.ResUsers.browse()
        for i in range(2):
            index = i + 1
            user = self.ResUsers.create(
                {
                    "name": "Commercial user %s" % index,
                    "login": "Commercial user %s" % index,
                    "groups_id": [
                        (4, self.env.ref("sales_team.group_sale_salesman").id)
                    ],
                }
            )
            setattr(self, "commercial_user_%s" % index, user)
            self.commercial_users |= user

    def _create_partners(self):
        self.partners = self.Partner.browse()
        self.partner_1 = self.Partner.create(
            {
                "name": "Partner 1",
                "user_id": self.commercial_user_1.id,
                "property_product_pricelist": self.pricelist.id,
            }
        )
        self.partner_2 = self.Partner.create(
            {
                "name": "Partner 2",
                "user_id": self.commercial_user_1.id,
                "property_product_pricelist": self.pricelist.id,
            }
        )
        self.partner_3 = self.Partner.create(
            {
                "name": "Partner 3",
                "user_id": self.commercial_user_2.id,
                "property_product_pricelist": self.pricelist.id,
            }
        )
        self.partners = self.partner_1 + self.partner_2 + self.partner_3

    def _create_products(self):
        self.product = self.Product.create(
            {
                "name": "Product test 1",
                "list_price": 100.00,
            }
        )

    def _create_sale_order(self):
        so_form = Form(self.SaleOrder)
        so_form.partner_id = self.partner_1
        with so_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.tax_id.remove(index=0)
        return so_form.save()

    def create_calendar_planner_event(self):
        # Create one planned recurrent event for every partner.
        self.planned_events = self.CalendarEvent.browse()
        for i, partner in enumerate(self.partners):
            action = partner.action_calendar_planner()
            context = dict(action["context"], default_wed=True, default_fri=True)
            # We use Form for auto-computing the recurrence model, that is triggered
            # directly from the initialization of it
            event_form = Form(self.CalendarEvent.with_context(**context))
            self.planned_events |= event_form.save()
            if i == 0:
                # Create a delivery event for partner 1. We can delivery goods
                # all mondays at 09:00
                context = dict(
                    action["context"],
                    default_name="Delivery",
                    default_start="2022-02-07 09:00:00",
                    default_stop="2022-02-07 10:00:00",
                    default_mon=True,
                    default_categ_ids=[(4, self.event_type_delivery.id)],
                )
                event_form = Form(self.CalendarEvent.with_context(**context))
                self.planned_events |= event_form.save()

    def _create_sale_order_from_planner(self, event_planner_id):
        so_form = Form(
            self.SaleOrder.with_context(
                default_user_id=event_planner_id.user_id.id,
                default_sale_planner_calendar_event_id=event_planner_id.id,
                default_partner_id=event_planner_id.partner_id.id,
            )
        )
        with so_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.product_uom_qty = 1
            line_form.tax_id.remove(index=0)
        return so_form.save()

    def _create_invoice(self, partner):
        with Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        ) as invoice_form:
            invoice_form.partner_id = partner
            with invoice_form.invoice_line_ids.new() as line_form:
                line_form.name = "invoice test"
                line_form.account_id = self.account
                line_form.quantity = 1.0
                line_form.price_unit = 100.00
                line_form.tax_ids.remove(index=0)
        return invoice_form.save()

    def test_create_calendar_planner_event(self):
        # Test the values for one planned recurrent event created
        event = self.planned_events[0]
        self.assertTrue(event.user_id in self.commercial_users)
        self.assertEqual(event.rrule_type, "weekly")
        self.assertEqual(event.location, event.target_partner_id._display_address())

    def test_planner_calendar_wizard(self):
        wiz_form = Form(self.env["sale.planner.calendar.wizard"])
        # This user has three planned events
        wiz_form.user_id = self.commercial_user_1
        self.assertEqual(len(wiz_form.calendar_event_ids), 3)
        wiz_form.event_type_id = self.event_type_delivery
        self.assertEqual(len(wiz_form.calendar_event_ids), 1)
        wiz_form.event_type_id = self.event_type_commercial_visit
        self.assertEqual(len(wiz_form.calendar_event_ids), 2)

    def test_summary_and_event_today(self):
        summary_obj = self.env["sale.planner.calendar.summary"]
        summary_form = Form(summary_obj)
        summary_form.user_id = self.commercial_user_1
        summary = summary_form.save()
        summary.action_process()
        self.assertEqual(summary.event_total_count, 2)

        event_planner_id = summary.sale_planner_calendar_event_ids[0]
        # Create a new sale order from planner event
        self._create_sale_order_from_planner(event_planner_id)
        self.assertEqual(summary.sale_order_count, 1)
        self.assertEqual(summary.sale_order_subtotal, 100)
        self._create_sale_order_from_planner(event_planner_id)
        self.assertEqual(summary.sale_order_count, 2)
        self.assertEqual(summary.sale_order_subtotal, 200)
        # Create a new invoice from planner event
        self.invoice1 = self._create_invoice(event_planner_id.partner_id)
        self.invoice1.action_post()
        self.assertEqual(event_planner_id.invoice_amount_residual, 100)
        # Set event to done state
        event_planner_id.action_done()
        self.assertEqual(summary.event_total_count, 2)
        self.assertEqual(summary.event_done_count, 1)
        self.assertEqual(summary.event_effective_count, 1)

    def test_reassign_wizard(self):
        wiz_form = Form(self.env["sale.planner.calendar.reassign.wiz"])
        wiz_form.user_id = self.commercial_user_1
        record = wiz_form.save()
        # Recover all planned event lines for commercial user 1
        record.action_get_lines()
        self.assertEqual(len(record.line_ids), 3)
        # Select line behaviour for update new commercial user
        wiz_form.new_user_id = self.commercial_user_2
        record = wiz_form.save()
        record.select_all_lines()
        record.action_assign_new_salesperson()
        self.assertEqual(len(record.line_ids.mapped("new_user_id")), 1)
        wiz_form.new_user_id = self.commercial_user_2
        record = wiz_form.save()
        record.line_ids = False
        record.action_get_lines()
        record.line_ids[0].selected = True
        record.action_assign_new_salesperson()
        self.assertEqual(len(record.line_ids.filtered(lambda ln: ln.new_user_id)), 1)

    def test_reassign_wizard_subscriptions(self):
        # Create a SO for partner 1 and user commercial 1
        sale_order = self._create_sale_order()
        invoice = self._create_invoice(self.partner_1)

        # Check document permissions based on followers
        with self.assertRaises(AccessError):
            self.assertIsNotNone(
                sale_order.with_user(self.commercial_user_2).check_access_rule("read")
            )
            self.assertIsNotNone(
                sale_order.with_user(self.commercial_user_2).check_access_rule("write")
            )
            self.assertIsNotNone(
                invoice.with_user(self.commercial_user_2).check_access_rule("read")
            )
            self.assertIsNotNone(
                invoice.with_user(self.commercial_user_2).check_access_rule("write")
            )

        wiz_form = Form(self.env["sale.planner.calendar.reassign.wiz"])
        wiz_form.user_id = self.commercial_user_1
        record = wiz_form.save()
        # Recover all planned event lines for commercial user 1
        record.action_get_lines()
        wiz_form.new_user_id = self.commercial_user_2
        record = wiz_form.save()
        event_planner_partner_1 = record.line_ids.filtered(
            lambda ln: ln.partner_id == self.partner_1
        )
        event_planner_partner_1.selected = True
        record.action_assign_new_salesperson()
        record.apply()
        # Check document permissions based on followers
        # Sale order
        self.assertIsNone(
            sale_order.with_user(self.commercial_user_2).check_access_rule("read")
        )
        self.assertIsNone(
            sale_order.with_user(self.commercial_user_2).check_access_rule("write")
        )
        # Account move (Invoice)
        self.assertIsNone(
            invoice.with_user(self.commercial_user_2).check_access_rule("read")
        )
        self.assertIsNone(
            invoice.with_user(self.commercial_user_2).check_access_rule("write")
        )
