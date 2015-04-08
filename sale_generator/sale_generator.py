from openerp import fields, models , api

class SaleLineGenerator(models.Model):
	_name='sale.line.generator' 

	generator_id = fields.Many2one('sale.generator', string="Generator" ,required=True)
	product_id = fields.Many2one('product.product', string="Product" , required=True)
	product_qty= fields.Float('quantity' , required=True ,default=1)
	

class SaleOrder(models.Model):
	_inherit='sale.order'
	generator_id = fields.Many2one('sale.generator', string="Generator")


class SaleGenerator(models.Model):
    _name='sale.generator'


    line_ids = fields.One2many('sale.line.generator','generator_id', string="lines")
    partner_ids = fields.Many2many('res.partner', string="Partner")
    sale_ids = fields.One2many('sale.order','generator_id', string="Sales")
    date = fields.Date('Date')
    state = fields.Selection([('draft','Draft'),('confirmed','Confirmed')],'State',readonly=True, default='draft')

    def _prepare_generator_sale_vals(self, partner):
        return {
            'partner_id': partner.id,
            'generator_id': self.id,
             }

    def _prepare_sale_order_line(self, gline):
         return {
             'product_id': gline.product_id.id,
             'product_uom_qty': gline.product_qty,
         }   

    @api.one
    def _search_and_delete_partner(self):
	    sale_order_obj = self.env['sale.order']
	    partner_list = []
            for partner in self.partner_ids:
	        partner_list.append(partner.id)
                #import pdb; pdb.set_trace() 
	    for sale in self.sale_ids:
	        if sale.partner_id.id not in partner_list:
	            sale.unlink()
    @api.one
    def order_create(self):
            sale_order_obj = self.env['sale.order']
            for partner in self.partner_ids:
                vals = self._prepare_generator_sale_vals(partner)
                vals['order_line'] = []
                for gline in self.line_ids:
	            vals['order_line'].append((0, 0, self._prepare_sale_order_line(gline)))
		    #import pdb; pdb.set_trace()
		    sale_order_obj.create(vals)
	 
    @api.one
    def button_confirm(self):
        return self.write({'state': 'confirmed'})
    #@api.one
    #def write(self,vals):
	
    @api.depends('partner_ids')
    def order_test(self):
	sale_order_obj = self.env['sale.order']
	partner_make_order = []
	if self.state == 'confirmed':
            for sale in self.sale_ids:
	        partner_make_order.append(sale.partner_id.id)
	    for partner in self.partner_ids:
	        if partner.id not in partner_make_order:
	            vals = self._prepare_generator_sale_vals(partner)
		    vals['order_line'] = []
		    for gline in self.line_ids:
		        vals['order_line'].append((0, 0, self._prepare_sale_order_line(gline)))
		        sale_order_obj.create(vals)
	self._search_and_delete_partner()
	
    @api.multi
    def write(self,vals):
	res = super(SaleGenerator,self).write(vals)
	self.order_test()
	return res
	

    
    @api.model
    def create(self,vals):
	res = super(SaleGenerator,self).create(vals)
	self.order_test()
	return res

    def _prepare_url_with_id_partner(self,valeurid):
	return ('http://localhost:8069/{}'.format(valeurid))

    @api.multi
    def function_url_call(self):
	res = {
		"name": 'test',
		"type": "ir.actions.act_url",
                 "url": self._prepare_url_with_id_partner(self.id),
                 "target": "new",
	}
	self.ensure_one()
	#pdb.set_trace()
	return res



  