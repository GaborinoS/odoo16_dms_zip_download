# -*- coding: utf-8 -*-
{
    'name': "DMS Directory ZIP Download",
    'summary': """
        Download complete directories as ZIP files
    """,
    'description': """
        This module extends the Document Management System (DMS) module
        to allow downloading a directory and all its contents as a ZIP file.
    """,
    'author': "Your Company",
    'website': "https://www.yourcompany.com",
    'category': 'Document Management',
    'version': '16.0.1.0.0',
    'depends': ['dms'],
    'data': [
        'views/dms_directory_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}