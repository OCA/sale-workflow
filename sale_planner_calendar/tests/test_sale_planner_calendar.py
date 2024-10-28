# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, timedelta

from freezegun import freeze_time

from odoo.exceptions import AccessError
from odoo.tests.common import Form, TransactionCase, tagged


@tagged("-at_install", "post_install")
@freeze_time("2022-02-04 09:00:00")
class TestSalePlannerCalendar(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Remove this variable in v16 and put instead:
        # from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
        DISABLED_MAIL_CONTEXT = {
            "tracking_disable": True,
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.CalendarEvent = cls.env["calendar.event"]
        cls.ResUsers = cls.env["res.users"]
        cls.Partner = cls.env["res.partner"]
        cls.ProductTemplate = cls.env["product.template"]
        cls.Product = cls.env["product.product"]
        cls.AccountInvoice = cls.env["account.move"]
        cls.AccountInvoiceLine = cls.env["account.move.line"]
        cls.AccountJournal = cls.env["account.journal"]
        cls.SaleOrder = cls.env["sale.order"]
        cls.SalePlannerCalendarEvent = cls.env["calendar.event"]

        account_group = cls.env.ref("account.group_account_user")
        cls.env.user.write({"groups_id": [(4, account_group.id)]})

        cls.event_type_commercial_visit = cls.env.ref(
            "sale_planner_calendar.event_type_commercial_visit"
        )
        cls.event_type_delivery = cls.env.ref(
            "sale_planner_calendar.event_type_delivery"
        )
        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "Test pricelist", "currency_id": cls.env.company.currency_id.id}
        )

        # Create some products
        cls._create_products()

        # Create some commercial users
        cls._create_commercial_users()

        # Create some partners
        cls._create_partners()

        # Create some calendar planner events
        cls.create_calendar_planner_event()

        # Some account data
        cls.account = cls.env["account.account"].create(
            {
                "code": "test",
                "name": "Test account",
                "account_type": "income",
            }
        )

    @classmethod
    def _create_commercial_users(cls):
        # Create commercial_user_1 and commercial_user_2 with Own Documents
        # Only security group
        cls.commercial_users = cls.ResUsers.browse()
        for i in range(2):
            index = i + 1
            user = cls.ResUsers.create(
                {
                    "name": "Commercial user %s" % index,
                    "login": "Commercial user %s" % index,
                    "groups_id": [
                        (4, cls.env.ref("sales_team.group_sale_salesman").id)
                    ],
                }
            )
            setattr(cls, "commercial_user_%s" % index, user)
            cls.commercial_users |= user

    @classmethod
    def _create_partners(cls):
        cls.partners = cls.Partner.browse()
        cls.partner_1 = cls.Partner.create(
            {
                "name": "Partner 1",
                "user_id": cls.commercial_user_1.id,
                "property_product_pricelist": cls.pricelist.id,
            }
        )
        cls.partner_2 = cls.Partner.create(
            {
                "name": "Partner 2",
                "user_id": cls.commercial_user_1.id,
                "property_product_pricelist": cls.pricelist.id,
            }
        )
        cls.commercial_partner_3 = cls.Partner.create(
            {
                "name": "Company partner 3",
                "user_id": cls.commercial_user_2.id,
                "property_product_pricelist": cls.pricelist.id,
            }
        )
        cls.partner_3 = cls.Partner.create(
            {
                "name": "Partner 3",
                "user_id": cls.commercial_user_2.id,
                "property_product_pricelist": cls.pricelist.id,
                "parent_id": cls.commercial_partner_3.id,
            }
        )
        cls.partners = cls.partner_1 + cls.partner_2 + cls.partner_3

    @classmethod
    def _create_products(cls):
        cls.product = cls.Product.create(
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

    @classmethod
    def create_calendar_planner_event(cls):
        # Create one planned recurrent event for every partner.
        cls.planned_events = cls.CalendarEvent.browse()
        for i, partner in enumerate(cls.partners):
            action = partner.action_calendar_planner()
            context = dict(action["context"], default_wed=True, default_fri=True)
            # We use Form for auto-computing the recurrence model, that is triggered
            # directly from the initialization of it
            event_form = Form(cls.CalendarEvent.with_context(**context))
            cls.planned_events |= event_form.save()
            if i == 0:
                # Create a delivery event for partner 1. We can delivery goods
                # all mondays at 09:00
                context = dict(
                    action["context"],
                    default_name="Delivery",
                    default_start="2022-02-07 09:00:00",
                    default_stop="2022-02-07 10:00:00",
                    default_mon=True,
                    default_categ_ids=[(4, cls.event_type_delivery.id)],
                )
                event_form = Form(cls.CalendarEvent.with_context(**context))
                cls.planned_events |= event_form.save()

    def _create_sale_order_from_planner(self, event_planner_id):
        so_form = Form(
            self.SaleOrder.with_context(
                default_user_id=event_planner_id.user_id.id,
                default_sale_planner_calendar_event_id=event_planner_id.id,
                default_partner_id=event_planner_id.target_partner_id.id,
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
        self.assertEqual(
            event.location,
            event.target_partner_id._display_address(True).replace("\n", " "),
        )

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
        self.invoice1 = self._create_invoice(event_planner_id.target_partner_id)
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
        wiz_form.new_start = date.today()
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

    def test_reassign_wizard_apply(self):
        # When creating new recurring events for reallocated changes,
        # each event must have a new recurrence. This test is
        # incorporated to control that no event is left without recurrence.
        wiz_form = Form(self.env["sale.planner.calendar.reassign.wiz"])
        wiz_form.user_id = self.commercial_user_1
        wiz_form.assign_new_salesperson_to_partner = True
        wiz_form.new_start = date.today() + timedelta(days=8)
        wiz_form.new_end = wiz_form.new_start + timedelta(days=20)
        record = wiz_form.save()
        record.action_get_lines()
        record.line_ids[0].new_user_id = self.commercial_user_2
        old_event = record.line_ids[0].calendar_event_id
        recurrence_events = old_event.recurrence_id.calendar_event_ids
        new_base_event_start = recurrence_events.filtered(
            lambda ce: ce.start.date() >= record.new_start
        ).sorted("start")[:1]
        self.assertTrue(new_base_event_start.recurrence_id)
        self.assertEqual(new_base_event_start.recurrence_id, old_event.recurrence_id)
        new_base_event_end = recurrence_events.filtered(
            lambda ce: ce.start.date() >= record.new_end
        ).sorted("start")[:1]
        self.assertTrue(new_base_event_end.recurrence_id)
        self.assertEqual(new_base_event_end.recurrence_id, old_event.recurrence_id)
        record.apply()
        # Events created for changes must have a new recurrence created from the old event
        self.assertTrue(
            self.env["calendar.event"].browse(new_base_event_start.id).recurrence_id
        )
        self.assertNotEqual(
            self.env["calendar.event"].browse(new_base_event_start.id).recurrence_id,
            old_event.recurrence_id,
        )
        self.assertTrue(
            self.env["calendar.event"].browse(new_base_event_end.id).recurrence_id
        )
        self.assertNotEqual(
            self.env["calendar.event"].browse(new_base_event_end.id).recurrence_id,
            old_event.recurrence_id,
        )
        # The original event must maintain its recurrence
        self.assertEqual(
            self.env["calendar.event"].browse(old_event.id).recurrence_id,
            old_event.recurrence_id,
        )

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
        wiz_form.new_start = date.today()
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

    def test_parter_sale_order(self):
        """User can setup a system parameter to create sale order from a event planner
        for a event planner partner or commercial partner
        """
        sale_planned_event = self.planned_events.filtered(
            lambda p: p.target_partner_id == self.partner_3
        )[:1]
        so_action = sale_planned_event.action_open_sale_order()
        self.assertEqual(so_action["context"]["default_partner_id"], self.partner_3.id)
        # Set parameter to create sale order to commercial partner
        self.env["ir.config_parameter"].sudo().set_param(
            "sale_planner_calendar.create_so_to_commercial_partner", "True"
        )
        so_action = sale_planned_event.action_open_sale_order()
        self.assertEqual(
            so_action["context"]["default_partner_id"],
            self.partner_3.commercial_partner_id.id,
        )
