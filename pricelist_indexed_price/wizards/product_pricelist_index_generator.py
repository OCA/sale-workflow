# -*- coding: utf-8 -*-
# © 2018 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from dateutil.rrule import rrule, YEARLY, MONTHLY, WEEKLY
from dateutil.relativedelta import relativedelta
from openerp import api, fields, models


class ProductPricelistIndexGenerator(models.TransientModel):
    _name = 'product.pricelist.index.generator'
    _description = 'Index generator'

    pricelist_id = fields.Many2one(
        'product.pricelist', required=True, default=lambda self:
        self.env.context.get('active_model') == 'product.pricelist' and
        self.env.context.get('active_id') or
        self.env['product.pricelist'].browse([]),
    )
    index_start = fields.Integer('Index start', required=True, default=100)
    index_step = fields.Integer('Index step', required=True, default=10)
    date_start = fields.Date('Start', required=True)
    date_end = fields.Date('End', required=True)
    frequency = fields.Selection(
        [
            (WEEKLY, 'Weekly'),
            (MONTHLY, 'Monthly'),
            (YEARLY, 'Yearly'),
        ],
        'Frequency', required=True, default=MONTHLY,
    )

    @api.multi
    def action_generate(self):
        self.ensure_one()
        this = self
        index = this.index_start
        dates = list(rrule(
            freq=this.frequency, interval=1,
            dtstart=fields.Datetime.from_string(this.date_start),
            until=fields.Datetime.from_string(this.date_end) + relativedelta(
                days=1,
            ),
        ))
        for i in range(1, len(dates)):
            this.pricelist_id.write({
                'item_ids': [(0, 0, {
                    'applied_on': '3_global',
                    'date_start': fields.Date.to_string(dates[i - 1]),
                    'date_end': fields.Date.to_string(
                        dates[i] - relativedelta(days=1),
                    ),
                    'compute_price': 'percentage',
                    'index_price': index,
                })],
            })
            index += this.index_step
        return {
            'type': 'ir.actions.act_window.close',
        }
