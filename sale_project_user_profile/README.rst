.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================
Sale Project User Profile
=========================

This module allow to define a mapping for project user task.
The goal is to sell (at customer) services with different user profiles (Project manager, developer).
The mapping allow to the project manager to decide which user profile is used in timesheet invoicing for given task.


Usage
=====

* You can define a new type of tracking service on product template: 'User profile'.
* When you confirm a sale order with a service of this type, a project is automatically created.
* On the project, you can define a mapping for user, task and sale order line.
* When you define a timesheet on the project, the sale order line used in account analytic line is get in the mapping.


Credits
=======

Contributors
------------

* Julien Coux <julien.coux@camptocamp.com>


Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
