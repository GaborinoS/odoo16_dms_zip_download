# -*- coding: utf-8 -*-
{
    'name': "DMS Image Gallery",
    'summary': """
        Image gallery with navigation for Document Management System
    """,
    'description': """
        This module extends the Document Management System (DMS) module
        to provide an enhanced image gallery with navigation capabilities.
        
        Features:
        - Full screen image gallery
        - Navigation between images in the same directory
        - Image zoom functionality
        - Slideshow capability
        - Direct download option
    """,
    'author': "Your Company",
    'website': "https://www.yourcompany.com",
    'category': 'Document Management',
    'version': '16.0.1.0.0',
    'depends': ['dms', 'web'],
    'data': [
        'views/dms_file_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dms_image_gallery/static/src/js/image_gallery.js',
            'dms_image_gallery/static/src/css/image_gallery.css',
            'dms_image_gallery/static/src/xml/image_gallery.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}