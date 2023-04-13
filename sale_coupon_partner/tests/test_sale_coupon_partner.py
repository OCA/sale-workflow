from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleCouponReport(TransactionCase):
    def test_sale_report(self):
        report = self.env["sale.report"].sudo().search([], order="id", limit=1)
        query1 = report._query()
        self.assertNotEqual(
            query1.find("scp.partner_id"), -1, msg="The request must have a partner"
        )
        query2 = report._query(fields=None)
        self.assertNotEqual(
            query2.find("scp.partner_id"), -1, msg="The request must have a partner"
        )
