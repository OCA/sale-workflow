from odoo import models, fields

class RemovedRecordLog(models.Model):
    _name = 'removed.record.log'
    _description = 'Abandoned removed Record Log'
    
    name = fields.Char(string='Name')
    date = fields.Datetime(string="Date")
    res_model = fields.Char('Model')
    res_id = fields.Integer('Record ID')
    user_id = fields.Many2one('res.users', string='User')
    
