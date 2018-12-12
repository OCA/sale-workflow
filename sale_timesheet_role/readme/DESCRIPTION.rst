This module allows setting right Product on Time Log entries according to
the Employee/Role.

Features:
 * "At Employee/Role Rate" billing
 * Specific Employee with specific Role to a Product mapping
 * Specific Employee with any Role to a Product mapping
 * Any Employee with Specific Role to a Product mapping

Matching is performed in following order:
 * Exact "Employee and Role"-to-product match
 * "Employee without Role"-to-product match
 * "Role without Employee"-to-product match

Let's go though the following use-case:

There's a project named "Project A", where following team members do various things:
 * John Doe, as a Project Manager
 * same John Doe, as a Account Manager
 * Bob Smith, as Designer

Only Project Manager and Designer hours are billed to the customer, so Odoo is
unable to handle such use-case out of the box using the "At Employee Rate"
configuration.

This module was introduced in order to handle such use-case. In addition to
example above, it can handle use-cases when hours are billed at the same
rate regardless of employee, yet depending on role.
