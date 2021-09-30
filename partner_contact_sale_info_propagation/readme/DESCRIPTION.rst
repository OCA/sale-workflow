This module propagates Salesperson and Sales Channel from Company to Contacts

* Put the *Salesperson* or *Sales Channel* of the parent company when the
  contact doesn't have a *Salesperson* or *Sales Channel* and this parent
  company is assigned.
* When the company changes the *Salesperson*, it fills with the same
  *Salesperson* all the contacts that don't have any or have the previous
  *Salesperson* of the parent company.
* When the company changes the *Sales Channel*, it fills with the same
  *Sales Channel* all the contacts that don't have any or have the previous
  *Sales Channel* of the parent company.
