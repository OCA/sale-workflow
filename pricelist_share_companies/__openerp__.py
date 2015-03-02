# -*- coding: utf-8 -*-
##############################################################################
#
# @author Grand-Guillaume Joel
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

{
     "name" : "Share pricelist between compagnies, not product",
     "version" : "1.0",
     "author" : "Camptocamp,Odoo Community Association (OCA)",
     "category" : "Generic Modules/Projects & Services",
     "description":
"""
In OpenERP, product prices (cost, list) are expressed in the currency of the price_type (by default the same than your company currency).

The idea here is to have the same products between compagnies (with each one their own currency through different price_type and different costs) but
only one pricelist for all. For that purpose, we add a company_id on price_type object and a rule to separate them for each company. This way,
the price computation of pricelist will take the right price_type currency as based price.

Concretely, to have a different cost price for a second company, you have to :
 - Create a new standard price on product.template
 - Create a new "Price Type" on this new field, with the desired currency and assigned to the new currency
 - Assign the existing "Cost Price" to your main company
 - On the setup of each company, in the "Configuration"'s Tab, select the product field used for the cost

The Price Type used is the first one found for the cost field configured on the company. To ensure the right Price Type
is selected, you have to put the company on the Price Types, and according to the security rule created, you will have access
only to the right Price Type.

Example:

I create a product A. it has 2 fields for cost prices : Cost Price and Cost Price CH

Price type Sale company A : Cost Price / EUR
Price type Sale company B : Cost Price CH / CHF

Cost Price of Product A, company A: 60
Cost Price CH of Product A, company B: 70

Product A in company A: The cost price is 60 * currency rate
Product A in company B: The cost price is 70 * currency rate


""",
     "website": "http://camptocamp.com",
     "depends" : [
            "product",
                ],
     "init_xml" : [],
     "demo_xml" : [],
     "update_xml" : [
        "pricelist_view.xml",
        "company_view.xml",
        "security/pricelist_security.xml",
     ],
     "active": False,
     "installable": True
}
