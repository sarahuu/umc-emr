# -*- coding: utf-8 -*-
{
    'name': "Laboratory Management Module",
    'description': """
This module is designed to manage laboratory processes efficiently. It allows for the creation, updating, and deletion of laboratory tests, ensuring that all test information is stored securely and can be accessed easily by authorized personnel. The module includes features for tracking test schedules, managing patient notifications, and storing test history.
    """,
    'author': "Sarah Unokerieghan",
    'website': "",
    'category': 'Medical',
    'version': '0.1',
    'depends': ['base','patient'],
    'data': [
        'data/lab_sequence.xml',
        'security/ir.model.access.csv',
        'views/lab_order.xml',
        'views/lab_result.xml',
        'views/lab_test.xml',
        'views/patient_record.xml',
        'views/menu.xml',
    ],
    'images': ['static/description/icon.png'],
    'application': True,
}

