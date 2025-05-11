# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
import base64
import json


class DMSImageGalleryController(http.Controller):
    
    @http.route('/dms_image_gallery/image_content/<int:file_id>', type='http', auth='user')
    def get_image_content(self, file_id, **kwargs):
        """Return the image content for the given file ID"""
        dms_file = request.env['dms.file'].browse(file_id)
        
        # Check if file exists and is an image
        if not dms_file.exists() or not dms_file.is_image:
            return request.not_found()
        
        # Check access rights
        if not dms_file.permission_read:
            return request.forbidden()
        
        # Return image content
        image_content = base64.b64decode(dms_file.content)
        
        content_type = dms_file.mimetype or 'image/jpeg'
        
        headers = [
            ('Content-Type', content_type),
            ('Content-Length', len(image_content)),
            ('Content-Disposition', f'inline; filename="{dms_file.name}"')
        ]
        
        return request.make_response(image_content, headers=headers)
    
    @http.route('/dms_image_gallery/directory_images/<int:directory_id>', type='json', auth='user')
    def get_directory_images(self, directory_id, **kwargs):
        """Return all image files in the directory"""
        dms_directory = request.env['dms.directory'].browse(directory_id)
        
        # Check if directory exists
        if not dms_directory.exists():
            return {'error': _('Directory not found')}
        
        # Check access rights
        if not dms_directory.permission_read:
            return {'error': _('Access denied')}
        
        # Get all image files
        image_files = request.env['dms.file'].search([
            ('directory_id', '=', directory_id),
            ('is_image', '=', True)
        ], order='name')
        
        # Prepare result
        result = []
        for image_file in image_files:
            result.append({
                'id': image_file.id,
                'name': image_file.name,
                'mimetype': image_file.mimetype,
                'url': f'/dms_image_gallery/image_content/{image_file.id}',
                'create_date': image_file.create_date,
                'create_uid': image_file.create_uid.name,
            })
        
        return result