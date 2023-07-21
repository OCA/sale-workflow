from odoo.tests.common import TransactionCase


class TestSaleOrder(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestSaleOrder, self).setUp()
        self.sale_order_model = self.env["sale.order"]
        company = self.env.company
        company.keep_name_so = False
        self.quotation_sequence = self.env.ref(
            "sale_quotation_number.seq_sale_quotation", raise_if_not_found=False
        )

    def test_enumeration(self):
        order1 = self.sale_order_model.create(
            {"partner_id": self.env.ref("base.res_partner_1").id}
        )
        quotation1_name = order1.name
        order2 = self.sale_order_model.create(
            {"partner_id": self.env.ref("base.res_partner_1").id}
        )
        quotation2_name = order2.name

        self.assertRegex(quotation1_name, self.quotation_sequence.prefix)
        self.assertRegex(quotation2_name, self.quotation_sequence.prefix)
        self.assertLess(int(quotation1_name[2:]), int(quotation2_name[2:]))

        order2.action_confirm()
        order1.action_confirm()

        self.assertRegex(order1.name, "S")
        self.assertEqual(order1.origin, quotation1_name)

        self.assertRegex(order2.name, "S")
        self.assertEqual(order2.origin, quotation2_name)
        self.assertLess(int(order2.name[1:]), int(order1.name[1:]))

    def test_with_origin(self):
        origin = "origin"
        order1 = self.sale_order_model.create(
            {"origin": origin, "partner_id": self.env.ref("base.res_partner_1").id}
        )
        quotation1_name = order1.name
        order1.action_confirm()

        self.assertRegex(order1.name, "S")
        self.assertEqual(order1.origin, ", ".join([origin, quotation1_name]))

    def test_copy_no_origin(self):
        order1 = self.sale_order_model.create(
            {"partner_id": self.env.ref("base.res_partner_1").id}
        )
        order_copy = order1.copy()

        self.assertEqual(order1.name, order_copy.origin)

    def test_copy_with_origin(self):
        origin = "origin"
        order1 = self.sale_order_model.create(
            {"origin": origin, "partner_id": self.env.ref("base.res_partner_1").id}
        )
        order_copy = order1.copy()

        self.assertEqual(", ".join([origin, order1.name]), order_copy.origin)

    def test_confirmation_sequence(self):
        order = self.sale_order_model.create(
            {"partner_id": self.env.ref("base.res_partner_1").id}
        )
        sequence_id = self.env["ir.sequence"].search(
            [
                ("code", "=", "sale.order"),
                ("company_id", "in", [order.company_id.id, False]),
            ]
        )
        next_name = sequence_id.get_next_char(sequence_id.number_next_actual)
        order.action_confirm()
        self.assertEqual(next_name, order.name)
