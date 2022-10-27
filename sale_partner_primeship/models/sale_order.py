from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        rv = super().action_confirm()
        for record in self:
            partner = record.partner_id.commercial_partner_id

            for line in record.order_line:
                product_template = line.product_template_id

                if product_template.primeship_activation:
                    # We do not take in account product_qty for now:
                    duration = product_template.primeship_duration
                    start = fields.Date.context_today(record)
                    end = start + relativedelta(months=duration)

                    # If we have already some primeships, we need to check for overlaps
                    if partner.primeship_ids:
                        # We assume no overlaps between partner primeships
                        for primeship in partner.primeship_ids.sorted("start_date"):
                            if primeship.overlaps(start, end):
                                start = primeship.end_date
                                end = start + relativedelta(months=duration)

                    self.env["sale.primeship"].create(
                        {
                            "start_date": start,
                            "end_date": end,
                            "partner_id": partner.id,
                            "order_line_id": line.id,
                        }
                    )
        return rv

    def action_cancel(self):
        rv = super().action_cancel()

        for record in self:
            record.order_line.mapped("primeship_id").active = False

        return rv


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    primeship_id = fields.Many2one(
        string="Primeships",
        comodel_name="sale.primeship",
        compute="_compute_primeship_id",
        inverse="_inverse_primeship_id",
    )

    # One2one impl
    primeship_ids = fields.One2many(
        comodel_name="sale.primeship", inverse_name="order_line_id"
    )

    @api.depends("primeship_ids")
    def _compute_primeship_id(self):
        for record in self:
            if record.primeship_ids:
                record.primeship_id = record.primeship_ids[0]

    def _inverse_primeship_id(self):
        for record in self:
            if record.primeship_ids:
                primeship = record.env["sale.primeship"].browse(
                    record.primeship_ids[0].id
                )
                primeship.order_line_id = record

            record.primeship_id.order_line_id = record

    # Update invoice start/end dates
    def _prepare_invoice_line(self, **optional_values):
        # Set invoice start/end dates to primeship start/end dates
        # In case of multi quantity, this assumes continuous date ranges
        self.ensure_one()
        res = super()._prepare_invoice_line(**optional_values)
        if self.primeship_id:
            res.update(
                {
                    "start_date": self.primeship_id.start_date,
                    "end_date": self.primeship_id.end_date,
                }
            )
        return res
