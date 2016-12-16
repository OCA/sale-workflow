# -*- coding: utf-8 -*-
# Copyright 2014 Carlos Sánchez Cifuentes <csanchez@grupovermon.com>
# Copyright 2015 Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# Copyright 2015 Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
# Copyright 2016 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def recalculate_prices(self):
        for line in self.mapped('order_line'):
            line.product_uom_change()
        return True

    @api.multi
    def recalculate_names(self):
        for line in self.mapped('order_line'):
            name = line.product_id.name_get()[0][1]
            if line.product_id.description_sale:
                name += '\n' + line.product_id.description_sale
            line.name = name
        return True
