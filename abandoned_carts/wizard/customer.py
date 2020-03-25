from odoo import models, fields, api
from datetime import datetime
from odoo.tools.safe_eval import safe_eval
import logging
_logger = logging.getLogger(__name__)

class CustomerWizardLine(models.TransientModel):
    _name = 'customer.wizard.line'
    _description = 'Abandoned Customer Line Popup'
    
    name = fields.Char('Name')
    partner_id = fields.Many2one('res.partner','Customer')
    email = fields.Char('Email')
    phone = fields.Char('Phone')
    wizard_id = fields.Many2one('customer.wizard','Wizard')
    
class CustomerWizard(models.TransientModel):
    _name = 'customer.wizard'
    _description = 'Abandoned Customer Popup'
    
    customer_ids = fields.One2many('customer.wizard.line','wizard_id', string='Customers')
    max_delete_limit = fields.Integer("Max Record delete limit")
    
    @api.model
    def default_get(self,fields):
        res = super(CustomerWizard,self).default_get(fields)
        max_delete_batch_limit = safe_eval(self.env['ir.config_parameter'].get_param('abandoned_carts.max_delete_batch_limit', '2000'))
        
        qry = """SELECT p.id
FROM res_partner p
    LEFT JOIN crm_lead lead ON lead.partner_id = p.id
    LEFT JOIN calendar_event_res_partner_rel ce ON ce.res_partner_id = p.id
    LEFT JOIN account_invoice inv ON inv.partner_id = p.id
    LEFT JOIN sale_order o ON o.partner_id = p.id
    LEFT JOIN account_move move ON move.partner_id = p.id
    LEFT JOIN account_move_line line ON line.partner_id = p.id
    LEFT JOIN project_task task ON task.partner_id = p.id
WHERE
    lead.partner_id is null and 
    ce.res_partner_id is null and
    inv.partner_id is null and
    o.partner_id is null and
    move.partner_id is null and
    line.partner_id is null and
    task.partner_id is null and 
    p.active and
    p.customer and
    p.id not in (select partner_id from res_users union all select partner_id from res_company order by partner_id)
    order by p.id desc
    limit %d
    """%(max_delete_batch_limit)
        partner_obj = self.env['res.partner']
#         if hasattr(partner_obj, 'newsletter_sendy'):
#             qry += " and not p.newsletter_sendy"   
        self._cr.execute(qry)
        data = self._cr.fetchall()
        customer_ids = [p[0] for p in data]
        lines = []
        for customer in partner_obj.browse(customer_ids):
            lines.append((0,0,{'partner_id': customer.id, 'email': customer.email, 'phone': customer.phone, 'name': customer.name}))
        res.update({'customer_ids':lines, 'max_delete_limit': max_delete_batch_limit})
        return res
    
    
    @api.multi
    def action_remove_customer(self):
        max_delete_batch_limit = safe_eval(self.env['ir.config_parameter'].get_param('abandoned_carts.max_delete_batch_limit', '2000'))
        if len(self.customer_ids)>max_delete_batch_limit:
            raise Warning('For safety reasons, you cannot delete more than %d Customer together. You can re-open the wizard several times if needed.'%(max_delete_batch_limit))
        
        current_date = datetime.now()
        log_obj = self.env['removed.record.log']
        user = self.env.user
        user_id = user.id
        
        customer_ids = self.customer_ids.mapped('partner_id').ids
        partner_obj = self.env['res.partner']
        newsletter_sendy = hasattr(partner_obj, 'newsletter_sendy') and True or False
            
        for partner_id in customer_ids:
            #Browse one record only, because if partner linked to some record and raise exception when deleting record, than system will just rollback that transaction.
            self._cr.execute('SAVEPOINT remove_partner')
            line = partner_obj.browse(partner_id)
            record_name = line.name
            record_id = line.id
            try:
                if newsletter_sendy and line.newsletter_sendy:
                    self._cr.execute("update res_partner set newsletter_sendy=false where id=%d"%(partner_id))
                    line.refresh()
                line.unlink()
            except Exception as e:
                self._cr.execute('ROLLBACK TO SAVEPOINT remove_partner')
                self._cr.execute('SAVEPOINT remove_partner')
                line = partner_obj.browse(partner_id)
                line.write({'active':False})
                
            log_obj.create({
                    'name' : record_name,
                    'date' : current_date,
                    'res_model': 'res.partner',
                    'res_id': record_id,
                    'user_id' : user_id,
                    })
            _logger.info('name %s, date %s, model %s, res_id %s, user %s',(record_name,current_date,'res.partner',record_id,user.name))          
            self._cr.execute('RELEASE SAVEPOINT remove_partner')
        return
    
    
