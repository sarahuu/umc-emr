# -*- coding: utf-8 -*-
{
    'name': "Appointment Management Module",
    'description': """
This module is designed to manage patient appointments efficiently. It allows for the creation, updating, and deletion of patient appointments, ensuring that all appointment information is stored securely and can be accessed easily by authorized personnel. The module includes features for tracking appointment schedules, managing patient notifications, and storing appointment history.
    """,
    'author': "Sarah Unokerieghan",
    'website': "",
    'category': 'Medical',
    'version': '0.1',
    'depends': ['base','emr_config','patient'],
    'data': [
        'data/app_sequence.xml',
        'data/cron.xml',
        'security/ir.model.access.csv',
        'views/available_slots.xml',
        'views/timeslot.xml',
        'views/appointment_visit.xml',
        'views/appointment.xml',
        'views/patient_record.xml',
        'wizard/reschedule.xml',
        'views/menu.xml'
    ],
    'images': ['static/description/icon.png'],
    'application': True,
}

