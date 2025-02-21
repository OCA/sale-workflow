This module propagates Salesperson and Sales Teams from Company to
Contacts

- Put the *Salesperson* or *Sales Teams* of the parent company when
  the contact doesn't have a *Salesperson* or *Sales Teams* and this
  parent company is assigned.
- When the company changes the *Salesperson*, it fills with the same
  *Salesperson* all the contacts that don't have any or have the
  previous *Salesperson* of the parent company.
- When the company changes the *Sales Teams*, it fills with the same
  *Sales Teams* all the contacts that don't have any or have the
  previous *Sales Teams* of the parent company.
