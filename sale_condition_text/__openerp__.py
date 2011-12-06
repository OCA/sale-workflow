# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright Camptocamp SA 
# author nbessi
#
##############################################################################
{"name" : "Sale/invoice condition",
 "version" : "1.3",
 "depends" : ["sale", "account"],
 "author" : "Camptocamp",
 "init_xml" : [],
 "update_xml" : ["account_invoice_view.xml",
                 "sale_order_view.xml",
                 "condition_view.xml"],
 "category": "Sale",
 "installable" : True,
 "active" : False,}
