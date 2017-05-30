# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    track_service = fields.Selection(selection_add=[
        ('completed_task', 'Completed Task')]
    )


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _need_procurement(self):
        for product in self:
            if (product.type == 'service' and
               product.track_service == 'completed_task'):
                return True
        return super(ProductProduct, self)._need_procurement()
