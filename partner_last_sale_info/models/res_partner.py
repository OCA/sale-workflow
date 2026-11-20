# Copyright 2026 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    last_sale_order_date = fields.Datetime(
        compute="_compute_last_sale_order_date",
        store=True,
        readonly=False,  # Allows data imports
        help="Date of the last confirmed sale order for this customer",
    )
    last_sale_order_id = fields.Many2one(
        "sale.order",
        compute="_compute_last_sale_order_date",
        store=True,
        readonly=False,
        help="Last confirmed sale order for this customer",
    )

    @api.depends("sale_order_ids", "sale_order_ids.state", "sale_order_ids.date_order")
    def _compute_last_sale_order_date(self):
        # Raw SQL: the ORM has no argmax aggregate, and DISTINCT ON resolves
        # the latest confirmed order per partner in a single pass. Flush
        # pending sale order writes first, as a raw query does not trigger
        # the flush that search() would.
        partner_ids = [id_ for id_ in self._ids if isinstance(id_, int)]
        if not partner_ids:
            return
        self.env["sale.order"].flush_model(["state", "date_order", "partner_id"])
        self.env.cr.execute(
            """
            SELECT DISTINCT ON (partner_id) partner_id, id, date_order
            FROM sale_order
            WHERE partner_id IN %s AND state = 'sale'
            ORDER BY partner_id, date_order DESC, id DESC
            """,
            [tuple(partner_ids)],
        )
        last_orders = {
            partner_id: (order_id, date_order)
            for partner_id, order_id, date_order in self.env.cr.fetchall()
        }
        for partner in self:
            last_order = last_orders.get(partner.id)
            if last_order:
                order_id, date_order = last_order
                partner.last_sale_order_date = date_order
                partner.last_sale_order_id = order_id
        # Do not reset any imported data when there is no confirmed order
