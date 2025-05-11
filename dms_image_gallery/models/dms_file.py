# -*- coding: utf-8 -*-

from odoo import models, fields, api

class DMSFile(models.Model):
    _inherit = 'dms.file'
    
    is_image = fields.Boolean(string="Is Image", compute="_compute_is_image", store=True)
    
    @api.depends('mimetype', 'extension')
    def _compute_is_image(self):
        image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']
        image_mimetypes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp', 'image/svg+xml']
        
        for record in self:
            record.is_image = (
                record.mimetype in image_mimetypes or 
                (record.extension and record.extension.lower() in image_extensions)
            )
    
    def action_view_image(self):
        """Open the image gallery for this file"""
        self.ensure_one()
        if not self.is_image:
            return
        
        return {
            'type': 'ir.actions.client',
            'tag': 'dms_image_gallery',
            'name': self.name,
            'params': {
                'file_id': self.id,
                'directory_id': self.directory_id.id,
                'file_name': self.name,
            },
        }