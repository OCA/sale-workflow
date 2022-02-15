from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def name_get(self):
        # Method replaced. Similar to name_get of product.product.
        partner_id = self._context.get('partner_id')
        if partner_id:
            partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
        else:
            partner_ids = []
        company_id = self.env.context.get('company_id')
        result = []
        if partner_ids:
            supplier_info = self.env['product.supplierinfo'].sudo().with_context(customerinfo=True).search([
                ('product_tmpl_id', 'in', self.ids),
                ('name', 'in', partner_ids),
            ])
            supplier_info.sudo().read(['product_tmpl_id', 'product_id', 'product_name', 'product_code'], load=False)
            supplier_info_by_template = {}
            for r in supplier_info:
                supplier_info_by_template.setdefault(r.product_tmpl_id, []).append(r)
        for product_template in self:
            name = '%s%s' % (product_template.default_code and '[%s] ' % product_template.default_code or '', product_template.name)
            sellers = []
            if not sellers and partner_ids:
                product_supplier_info = supplier_info_by_template.get(product_template, [])
                if not sellers:
                    sellers = [x for x in product_supplier_info if not x.product_id and (x.product_code or x.product_name)]
                if company_id:
                    sellers = [x for x in sellers if x.company_id.id in [company_id, False]]
            if sellers:
                for s in sellers:
                    seller_name = '%s%s' % (s.product_code and '[%s] ' % s.product_code or '', s.product_name)
                    seller_pt = (product_template.id, seller_name)
                    if seller_pt not in result:
                        result.append(seller_pt)
            else:
                result.append((product_template.id, name))
        return result
