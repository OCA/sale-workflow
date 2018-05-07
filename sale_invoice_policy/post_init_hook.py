# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, pool):
    """
    As we change the invoice policy to computed field, we must initialize
    the default policy with original values
    :param cr:
    :return:
    """

    env = api.Environment(cr, SUPERUSER_ID, {})
    query = """UPDATE %s
     SET default_invoice_policy = invoice_policy
     WHERE invoice_policy IS NOT NULL""" % env['product.template']._table
    cr.execute(query)
