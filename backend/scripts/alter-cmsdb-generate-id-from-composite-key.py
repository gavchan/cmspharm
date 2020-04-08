#!/usr/bin/env python
"""Script to modify legacy CMS database to include primary key `id` for tables with composite keys"""
import MySQLdb

db = MySQLdb.connect('host.docker.internal', 'root', 'cmsyw', 'cmsyw')
cur = db.cursor()

INV_SUPP = {
    'name': 'inventory_item_supplier_manufacturer',
    'col1': 'inventory_item_suppliers_id',
    'col2': 'supplier_manufacturer_id',
}
DEPL_DEPLITEM = {
    'name': 'depletion_depletion_item',
    'col1': 'depletion_items_id',
    'col2': 'depletion_item_id',
}

def check_and_add_id(dbtable):
    """
    Check table for existence of ID column
    """
    print(f"Checking table {dbtable.get('name')}")
    db.query(
        """
        select count(*) from information_schema.`COLUMNS` c 
        where TABLE_NAME = '%s'
        and COLUMN_NAME = 'id'
        and TABLE_SCHEMA = database()
        """ % dbtable.get('name'))
    r = db.store_result()
    col_exists = bool(r.fetch_row()[0][0])
    if col_exists:
        print('Column `id` already exists')
    else:
        print('Creating column `id`')
        # Add ID column
        cur.execute ('ALTER TABLE %s ADD COLUMN id INTEGER' % dbtable.get('name'))

def enumerate_id(dbtable):
    """
    Generate IDs from two columns forming a composite key
    """
    cur.execute(f"SELECT {dbtable.get('col1')}, {dbtable.get('col2')} from {dbtable.get('name')}")
    rows = cur.fetchall()
    for i, (col1, col2) in enumerate(rows):
        cur.execute(f"UPDATE {dbtable.get('name')} SET id = {i+1} WHERE {dbtable.get('col1')} = {col1} AND {dbtable.get('col2')} = {col2}")
    db.commit()

    # Drop composite primary keys, add new primary key and set as "AUTO_INCREMENT"
    cur.execute(f"ALTER TABLE {dbtable.get('name')} ADD PRIMARY KEY(id)")
    cur.execute(f"ALTER TABLE {dbtable.get('name')} CHANGE COLUMN id id INTEGER AUTO_INCREMENT")

if __name__ == '__main__':
    check_and_add_id(INV_SUPP)
    enumerate_id(INV_SUPP)
    check_and_add_id(DEPL_DEPLITEM)
    enumerate_id(DEPL_DEPLITEM)

    db.close()
