# -*- coding: utf-8 -*-

from odoo import models, fields, api

class DMSDirectory(models.Model):
    _inherit = 'dms.directory'
    
    image_count = fields.Integer(string="Images", compute="_compute_image_count")
    
    def _compute_image_count(self):
        for record in self:
            record.image_count = self.env['dms.file'].search_count([
                ('directory_id', '=', record.id),
                ('is_image', '=', True)
            ])
    
    def action_view_image_gallery(self):
        """Open the image gallery for this directory"""
        self.ensure_one()
        
        # Get first image in directory
        first_image = self.env['dms.file'].search([
            ('directory_id', '=', self.id),
            ('is_image', '=', True)
        ], limit=1)
        
        if not first_image:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No images',
                    'message': 'This directory does not contain any images.',
                    'sticky': False,
                    'type': 'warning',
                }
            }
        
        return {
            'type': 'ir.actions.client',
            'tag': 'dms_image_gallery',
            'name': 'Image Gallery',
            'params': {
                'file_id': first_image.id,
                'directory_id': self.id,
                'file_name': first_image.name,
            },
        }