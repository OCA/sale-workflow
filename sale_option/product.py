# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for Odoo
#   Copyright (C) 2015 Akretion (http://www.akretion.com).
#   @author Valentin CHEMIERE <valentin.chemiere@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import fields, api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    option_ids = fields.Many2many('product.product', relation="product_option",
                                  column1="product_id", column2="option_id",
                                  string="Options")


class ProductProduct(models.Model):
    _inherit = "product.product"

    option_for_product_ids = fields.Many2many('product.template',
                                              relation="product_option",
                                              column1="option_id",
                                              column2="product_id",
                                              string="Option for")
