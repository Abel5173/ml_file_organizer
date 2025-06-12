import os
import mimetypes
from pathlib import Path
import magic  # python-magic library for better file type detection

def get_file_type(file_path):
    """Get the type of file based on its extension, mime type, and content analysis."""
    # Get file extension
    ext = os.path.splitext(file_path)[1].lower()
    
    # Map of extensions to file types
    extension_map = {
        # Images
        '.jpg': 'Images',
        '.jpeg': 'Images',
        '.png': 'Images',
        '.gif': 'Images',
        '.bmp': 'Images',
        '.webp': 'Images',
        '.svg': 'Images',
        '.tiff': 'Images',
        '.ico': 'Images',
        '.psd': 'Images',
        '.ai': 'Images',
        '.eps': 'Images',
        '.raw': 'Images',
        '.cr2': 'Images',
        '.nef': 'Images',
        '.arw': 'Images',
        '.heic': 'Images',
        '.heif': 'Images',
        
        # Documents
        '.pdf': 'Documents',
        '.doc': 'Documents',
        '.docx': 'Documents',
        '.txt': 'Documents',
        '.rtf': 'Documents',
        '.odt': 'Documents',
        '.md': 'Documents',
        '.csv': 'Documents',
        '.xls': 'Documents',
        '.xlsx': 'Documents',
        '.ppt': 'Documents',
        '.pptx': 'Documents',
        '.pages': 'Documents',
        '.numbers': 'Documents',
        '.key': 'Documents',
        '.epub': 'Documents',
        '.mobi': 'Documents',
        '.azw3': 'Documents',
        '.fb2': 'Documents',
        '.djvu': 'Documents',
        '.chm': 'Documents',
        '.tex': 'Documents',
        '.odp': 'Documents',
        '.ods': 'Documents',
        
        # Code
        '.py': 'Code',
        '.js': 'Code',
        '.java': 'Code',
        '.cpp': 'Code',
        '.c': 'Code',
        '.h': 'Code',
        '.html': 'Code',
        '.css': 'Code',
        '.php': 'Code',
        '.rb': 'Code',
        '.go': 'Code',
        '.rs': 'Code',
        '.ts': 'Code',
        '.jsx': 'Code',
        '.tsx': 'Code',
        '.swift': 'Code',
        '.kt': 'Code',
        '.scala': 'Code',
        '.pl': 'Code',
        '.sh': 'Code',
        '.bash': 'Code',
        '.zsh': 'Code',
        '.ps1': 'Code',
        '.bat': 'Code',
        '.cmd': 'Code',
        '.sql': 'Code',
        '.json': 'Code',
        '.xml': 'Code',
        '.yaml': 'Code',
        '.yml': 'Code',
        '.toml': 'Code',
        '.ini': 'Code',
        '.conf': 'Code',
        '.config': 'Code',
        '.env': 'Code',
        '.gitignore': 'Code',
        '.dockerfile': 'Code',
        '.dockerignore': 'Code',
        
        # Audio
        '.mp3': 'Music',
        '.wav': 'Music',
        '.ogg': 'Music',
        '.flac': 'Music',
        '.m4a': 'Music',
        '.aac': 'Music',
        '.wma': 'Music',
        '.aiff': 'Music',
        '.alac': 'Music',
        '.mid': 'Music',
        '.midi': 'Music',
        '.opus': 'Music',
        '.amr': 'Music',
        '.ape': 'Music',
        '.wv': 'Music',
        
        # Video
        '.mp4': 'Videos',
        '.avi': 'Videos',
        '.mkv': 'Videos',
        '.mov': 'Videos',
        '.wmv': 'Videos',
        '.flv': 'Videos',
        '.webm': 'Videos',
        '.m4v': 'Videos',
        '.mpg': 'Videos',
        '.mpeg': 'Videos',
        '.3gp': 'Videos',
        '.ts': 'Videos',
        '.mts': 'Videos',
        '.m2ts': 'Videos',
        '.vob': 'Videos',
        '.ogv': 'Videos',
        '.drc': 'Videos',
        '.gifv': 'Videos',
        '.mng': 'Videos',
        '.qt': 'Videos',
        '.yuv': 'Videos',
        '.rm': 'Videos',
        '.rmvb': 'Videos',
        '.asf': 'Videos',
        '.amv': 'Videos',
        '.svi': 'Videos',
        
        # Archives
        '.zip': 'Archives',
        '.rar': 'Archives',
        '.7z': 'Archives',
        '.tar': 'Archives',
        '.gz': 'Archives',
        '.bz2': 'Archives',
        '.xz': 'Archives',
        '.lz': 'Archives',
        '.lzma': 'Archives',
        '.lzo': 'Archives',
        '.z': 'Archives',
        '.iso': 'Archives',
        '.dmg': 'Archives',
        '.pkg': 'Archives',
        '.deb': 'Archives',
        '.rpm': 'Archives',
        '.apk': 'Archives',
        
        # Fonts
        '.ttf': 'Fonts',
        '.otf': 'Fonts',
        '.woff': 'Fonts',
        '.woff2': 'Fonts',
        '.eot': 'Fonts',
        '.sfnt': 'Fonts',
        '.pfb': 'Fonts',
        '.pfm': 'Fonts',
        '.bdf': 'Fonts',
        '.pcf': 'Fonts',
        '.psf': 'Fonts',
        
        # CAD and 3D
        '.dwg': 'CAD',
        '.dxf': 'CAD',
        '.stl': 'CAD',
        '.obj': 'CAD',
        '.3ds': 'CAD',
        '.max': 'CAD',
        '.blend': 'CAD',
        '.fbx': 'CAD',
        '.dae': 'CAD',
        '.skp': 'CAD',
        '.step': 'CAD',
        '.iges': 'CAD',
        
        # Database
        '.db': 'Database',
        '.sqlite': 'Database',
        '.sqlite3': 'Database',
        '.mdb': 'Database',
        '.accdb': 'Database',
        '.dbf': 'Database',
        
        # Executables
        '.exe': 'Executables',
        '.msi': 'Executables',
        '.app': 'Executables',
        '.dmg': 'Executables',
        '.bin': 'Executables',
        '.run': 'Executables',
        
        # Virtual Machines
        '.vmdk': 'Virtual Machines',
        '.vdi': 'Virtual Machines',
        '.vhd': 'Virtual Machines',
        '.vhdx': 'Virtual Machines',
        '.ova': 'Virtual Machines',
        '.ovf': 'Virtual Machines',
        
        # Disk Images
        '.iso': 'Disk Images',
        '.img': 'Disk Images',
        '.dmg': 'Disk Images',
        '.vcd': 'Disk Images',
        
        # Certificates
        '.pem': 'Certificates',
        '.cer': 'Certificates',
        '.crt': 'Certificates',
        '.key': 'Certificates',
        '.p12': 'Certificates',
        '.pfx': 'Certificates',
        
        # Logs
        '.log': 'Logs',
        '.logs': 'Logs',
        '.txt': 'Logs',
    }
    
    # Try to get type from extension first
    if ext in extension_map:
        return extension_map[ext]
    
    # If extension not found, try using python-magic for better mime type detection
    try:
        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(file_path)
        
        if mime_type:
            if mime_type.startswith('image/'):
                return 'Images'
            elif mime_type.startswith('video/'):
                return 'Videos'
            elif mime_type.startswith('audio/'):
                return 'Music'
            elif mime_type.startswith('text/'):
                return 'Documents'
            elif mime_type.startswith('application/'):
                if 'pdf' in mime_type:
                    return 'Documents'
                elif 'zip' in mime_type or 'x-compressed' in mime_type:
                    return 'Archives'
                elif 'msword' in mime_type or 'document' in mime_type:
                    return 'Documents'
                elif 'spreadsheet' in mime_type or 'excel' in mime_type:
                    return 'Documents'
                elif 'presentation' in mime_type or 'powerpoint' in mime_type:
                    return 'Documents'
                elif 'font' in mime_type:
                    return 'Fonts'
                elif 'database' in mime_type:
                    return 'Database'
                elif 'executable' in mime_type:
                    return 'Executables'
    except:
        # Fallback to standard mimetypes if python-magic fails
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            if mime_type.startswith('image/'):
                return 'Images'
            elif mime_type.startswith('video/'):
                return 'Videos'
            elif mime_type.startswith('audio/'):
                return 'Music'
            elif mime_type.startswith('text/'):
                return 'Documents'
    
    # If still unknown, try to read the file content
    try:
        with open(file_path, 'rb') as f:
            header = f.read(16)  # Read first 16 bytes for better detection
            
            # Check for common file signatures
            if header.startswith(b'\x89PNG\r\n\x1a\n'):
                return 'Images'
            elif header.startswith(b'\xff\xd8\xff'):  # JPEG
                return 'Images'
            elif header.startswith(b'GIF87a') or header.startswith(b'GIF89a'):
                return 'Images'
            elif header.startswith(b'%PDF'):
                return 'Documents'
            elif header.startswith(b'PK\x03\x04'):  # ZIP
                return 'Archives'
            elif header.startswith(b'\x1f\x8b'):  # GZIP
                return 'Archives'
            elif header.startswith(b'BM'):  # BMP
                return 'Images'
            elif header.startswith(b'RIFF') and header[8:12] == b'WEBP':  # WEBP
                return 'Images'
            elif header.startswith(b'\x00\x00\x01\x00'):  # ICO
                return 'Images'
            elif header.startswith(b'OggS'):  # OGG
                return 'Music'
            elif header.startswith(b'ID3'):  # MP3 with ID3v2
                return 'Music'
            elif header.startswith(b'\xff\xfb'):  # MP3 without ID3
                return 'Music'
            elif header.startswith(b'FLAC'):  # FLAC
                return 'Music'
            elif header.startswith(b'fLaC'):  # FLAC
                return 'Music'
            elif header.startswith(b'SQLite'):  # SQLite
                return 'Database'
            elif header.startswith(b'PK\x03\x04'):  # Office documents
                return 'Documents'
    except:
        pass
    
    # Try to determine type from file content analysis
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(1024)  # Read first 1KB
            
            # Check for common patterns
            if any(pattern in content for pattern in ['<?xml', '<html', '<!DOCTYPE html']):
                return 'Code'
            elif any(pattern in content for pattern in ['function', 'class', 'import', 'def ']):
                return 'Code'
            elif any(pattern in content for pattern in ['SELECT', 'INSERT', 'UPDATE', 'CREATE TABLE']):
                return 'Database'
            elif any(pattern in content for pattern in ['[INFO]', '[ERROR]', '[WARNING]', '[DEBUG]']):
                return 'Logs'
    except:
        pass
    
    return 'Unknown'
