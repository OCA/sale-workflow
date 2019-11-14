# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class ResPartner(models.Model):

    _inherit = 'res.partner'

    wishlists_count = fields.Integer(
        compute='_compute_wishlists_count',
        string="# Wishlists"
    )

    def _compute_wishlists_count(self):
        # do just one query for all records
        data = self.env['product.set'].read_group(
            self._wishlist_domain(), ['partner_id'], ['partner_id'])
        data_mapped = {
            count['partner_id'][0]: count['partner_id_count']
            for count in data
        }
        for rec in self:
            rec.wishlists_count = data_mapped.get(rec.id, 0)

    def _wishlist_domain(self):
        return [
            ('partner_id', 'in', self.ids),
            ('typology', '=', 'wishlist'),
        ]

    @api.multi
    def action_view_wishlists(self):
        self.ensure_one()
        action = self.env.ref("sale_product_set.act_open_product_set_view")
        res = action.read()[0]
        res.update({
            'name': _('Wishlists'),
            'domain': self._wishlist_domain(),
            'context': {
                'default_typology': 'wishlist',
                'default_partner_id': self.id,
            },
        })
        return res
