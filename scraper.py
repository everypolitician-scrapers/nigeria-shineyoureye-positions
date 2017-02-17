#!/usr/bin/env python

from __future__ import print_function

from collections import defaultdict

import requests
import scraperwiki

persons_url = 'http://www.shineyoureye.org/media_root/popolo_json/persons.json'
memberships_url = 'http://www.shineyoureye.org/media_root/popolo_json/memberships.json'
organizations_url = 'http://www.shineyoureye.org/media_root/popolo_json/organizations.json'

persons_data = requests.get(persons_url).json()
memberships_data = requests.get(memberships_url).json()
organizations_data = requests.get(organizations_url).json()

person_id_to_person = {}
person_id_to_memberships = defaultdict(list)
organization_id_to_organizations = {}

for person in persons_data:
    person_id_to_person[person['id']] = person

for organization in organizations_data:
    organization_id_to_organizations[organization['id']] = \
        organization

for membership in memberships_data:
    membership['person'] = person_id_to_person[membership['person_id']]
    organization_id = membership.get('organization_id')
    if organization_id is not None:
        membership['organization'] =\
            organization_id_to_organizations[organization_id]
    person_id_to_memberships[membership['person_id']].append(membership)

def membership_sort_key(m):
    end_date = m.get('end_date', '9999-12-31')
    start_date = m.get('start_date', '0001-01-01')
    return (end_date, start_date)
    
for memberships_for_person in person_id_to_memberships.values():
    memberships_for_person.sort(reverse=True, key=membership_sort_key)

for person_id, memberships in person_id_to_memberships.items():
    for m in memberships:
        o = m.get('organization', '')
        row = {
            'person_id': person_id,
            'person_name': m['person']['name'],
            'person_summary': m['person'].get('summary', ''),
            'membership_id': m['id'],
            'role': m.get('role', ''),
            'start_date': m.get('start_date', ''),
            'end_date': m.get('end_date', ''),
            'organization_id': m.get('organization_id', ''),
            'organization_name': o and o['name'],
            'organization_category': o and o ['category'],
            'organization_classification': o and o['classification'],
        }
        scraperwiki.sqlite.save(
            unique_keys=['person_id', 'membership_id'],
            data=row
        )
