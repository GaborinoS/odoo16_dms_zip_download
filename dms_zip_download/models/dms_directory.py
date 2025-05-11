# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import zipfile
import io
import os
import logging

_logger = logging.getLogger(__name__)

class DMSDirectory(models.Model):
    _inherit = 'dms.directory'
    
    def action_download_zip(self):
        """Download directory and all its contents as a zip file"""
        self.ensure_one()
        
        # Create a BytesIO object to store the zip file
        zip_buffer = io.BytesIO()
        
        # Create a zipfile
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add files from the root directory directly at the root of the ZIP
            files = self.env['dms.file'].search([('directory_id', '=', self.id)])
            for file in files:
                try:
                    # Add file directly at the root level of the ZIP
                    zip_file.writestr(file.name, base64.b64decode(file.content))
                except Exception as e:
                    _logger.error(f"Error adding file {file.name} to zip: {str(e)}")
            
            # Process subdirectories recursively starting from root directory
            subdirectories = self.env['dms.directory'].search([('parent_id', '=', self.id)])
            for subdir in subdirectories:
                self._add_subdirectory_to_zip(zip_file, subdir, "")
        
        # Get the zip file content
        zip_buffer.seek(0)
        zip_content = base64.b64encode(zip_buffer.read())
        
        # Create an attachment for download
        attachment = self.env['ir.attachment'].create({
            'name': f"{self.name}.zip",
            'type': 'binary',
            'datas': zip_content,
            'res_model': self._name,
            'res_id': self.id,
        })
        
        # Return the download action
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
    
    def _add_subdirectory_to_zip(self, zip_file, directory, parent_path):
        """Recursively add subdirectories and their files to zip"""
        # Determine the path for this directory
        current_path = os.path.join(parent_path, directory.name)
        
        # Create directory entry in the zip
        # The trailing slash is important for empty directories
        zip_file.writestr(f"{current_path}/", "")
        
        # Add all files in the current directory
        files = self.env['dms.file'].search([('directory_id', '=', directory.id)])
        for file in files:
            try:
                file_path = os.path.join(current_path, file.name)
                zip_file.writestr(file_path, base64.b64decode(file.content))
            except Exception as e:
                _logger.error(f"Error adding file {file.name} to zip: {str(e)}")
        
        # Recursively process subdirectories
        subdirectories = self.env['dms.directory'].search([('parent_id', '=', directory.id)])
        for subdir in subdirectories:
            self._add_subdirectory_to_zip(zip_file, subdir, current_path)