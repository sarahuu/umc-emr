# -*- coding: utf-8 -*-
{
    'name': "Pharmacy Management Module",
    'description': """
This module is designed to manage pharmacy operations efficiently. It allows for the creation, updating, and deletion of drug records, ensuring that all drug information is stored securely and can be accessed easily by authorized personnel. The module includes features for tracking drug inventory, managing prescriptions, and storing dispensing information.
    """,
    'author': "Sarah Unokerieghan",
    'website': "",
    'category': 'Medical',
    'version': '0.1',
    'depends': ['base','patient'],
    'data': [
        'security/ir.model.access.csv',
        'data/prescription.xml',
        'views/pharmacy_drug.xml',
        'views/prescription_order_line.xml',
        'views/prescription_order.xml',
        'wizard/prescription_order.xml',
        'views/patient_record.xml',
        # 'views/prescription_dispense.xml',
        'views/menu.xml',
    ],
    'images': ['static/description/icon.png'],
    'application': True,
}

