# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from .common import Common


class TestReports(Common):
    @classmethod
    def _get_report_data(cls, report):
        return {"report_type": report.report_type}

    def test_reports(self):
        # One of those should raise an exception is anything wrong occurs
        order = self._create_order_partner_cutoff()
        order.action_confirm()
        sale_report = self.env.ref("sale.action_report_saleorder")
        content, _ = sale_report._render(
            order.ids, data=self._get_report_data(sale_report)
        )
        picking = order.picking_ids
        picking_report = self.env.ref("stock.action_report_delivery")
        content, _ = picking_report._render(
            picking.ids, data=self._get_report_data(picking_report)
        )
