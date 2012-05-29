# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joël Grand-guillaume (Camptocamp) 
#    Contributor: Yannick Vaucher (Camptocamp)
#    Copyright 2011 Camptocamp SA
#    Donors:
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name" : "CRM with Department Categorization",
    "version" : "1.0",
    "author" : "Camptocamp",
    "category" : "Generic Modules/CRM & SRM",
    "description": """
    
Add the department on Sales Team (with related field on Lead & Opportunities)
as well as the related filter and button in the search form.

    
""",
    "website": "http://camptocamp.com",
    "depends" : [
            "crm",
            "hr"
                ],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
           "crm_view.xml",
                   ],
    "active": False,
    "installable": True
}
