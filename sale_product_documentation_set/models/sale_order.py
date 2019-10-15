# Copyright 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class SaleOrder(models.Model):

    _inherit = "sale.order"

    product_doc_set_ids = fields.Many2many(
        "product.doc.set", string="Product Documentation"
    )

    @api.multi
    def product_documentation_reset(self):
        for order in self:
            country = self.partner_id.country_id
            lang = self.partner_id.lang
            products = self.order_line.mapped('product_id.product_tmpl_id')
            doc_sets = self.env['product.doc.set']
            for product in products:
                doc_sets |= product.get_usage_document_sets(
                    'sale', country, lang)
                # TODO: try parcials when not found with full parameters
            self.product_doc_set_ids = doc_sets
            # TODO: improve update button UI

    @api.onchange('partner_id')
    def onchange_partner_id_documentation_set_id(self):
        self.product_documentation_reset()
        # TODO: onchange not working :-(
