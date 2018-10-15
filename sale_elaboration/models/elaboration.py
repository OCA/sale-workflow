# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class Elaboration(models.Model):
    _name = 'product.elaboration'

    name = fields.Char(
        required=True,
    )
    code = fields.Char(
        string='Short Code',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        ondelete='restrict',
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be unique!'),
        ('code_uniq', 'unique(code)', 'Code must be unique!'),
    ]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('code', '=', name)] + args, limit=1)
        return (
            recs and recs.name_get() or
            super().name_search(name, args, operator, limit)
        )
