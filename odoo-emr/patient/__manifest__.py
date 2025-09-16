# -*- coding: utf-8 -*-
{
    'name': "Patient Record Management Module",
    'description': """
This module is designed to manage patient records efficiently. It allows for the creation, updating, and deletion of patient records, ensuring that all patient information is stored securely and can be accessed easily by authorized personnel. The module includes features for tracking patient visits, managing medical history, and storing contact information.
    """,
    'author': "Sarah Unokerieghan",
    'website': "",
    'category': 'Medical',
    'version': '0.1',
    'depends': ['base','emr_config'],
    'data': [
        'security/ir.model.access.csv',
        'security/user_groups.xml',
        'data/patient_sequence.xml',
        'data/patient_immunization.xml',
        'views/patient_vitals.xml',
        'views/patient_biometrics.xml',
        'views/patient_conditions.xml',
        'views/patient_allergies.xml',
        'views/patient_immunization.xml',
        'views/patient_forms.xml',
        'views/patient_record.xml',
        'views/menu.xml',
    ],
    'images': ['static/description/icon.png'],
    'application': True,
}

