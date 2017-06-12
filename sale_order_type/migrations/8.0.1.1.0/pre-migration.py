# -*- coding: utf-8 -*-
# Copyright 2017 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import SUPERUSER_ID
from datetime import datetime


def migrate(cr, version):
    if not version:
        return
    cr.execute(
        "SELECT id, sale_type FROM res_partner WHERE sale_type IS NOT NULL")
    partners = cr.fetchall()
    cr.execute(
        "SELECT f.id "
        "FROM ir_model_fields f "
        "JOIN ir_model m ON m.id = f.model_id "
        "WHERE m.model = 'res.partner' AND f.name = 'sale_type'")
    type_fields = cr.fetchall()
    if len(type_fields) != 1:
        raise Exception("Can't find 1 'sale_type' field")
    cr.execute(
        "SELECT id FROM res_company")
    companies = cr.fetchall()
    for partner in partners:
        for company in companies:
            utcnow = str(datetime.utcnow())
            cr.execute(
                "INSERT INTO ir_property("
                "create_date, create_uid, write_date, name, company_id, type, "
                "fields_id, res_id, value_reference) "
                "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"
                % (
                    utcnow, SUPERUSER_ID, utcnow, 'sale_type', company[0],
                    'many2one', type_fields[0][0],
                    'res.partner,%s' % partner[0],
                    'sale.order.type,%s' % partner[1]
                )
            )
