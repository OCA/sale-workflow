# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    total_cashondelivery = fields.Float(
        string='Total cashondelivery'
    )

    @api.model
    def create(self, values):
        return_object = super(StockPicking, self).create(values)
        #operations
        if return_object.origin!=False:
            sale_order_ids = self.env['sale.order'].sudo().search([('name', '=', return_object.origin)])
            if len(sale_order_ids)>0:
                return_object.total_cashondelivery = sale_order_ids[0].total_cashondelivery
        #return
        return return_object
