# Software Distribution Manager

A complete software distribution system with GUI, download management, and executable packaging.

## Features

- **GUI Application**: Easy-to-use interface for managing software catalog
- **Download Management**: Handle software downloads with progress tracking
- **Link Generation**: Create and share download links
- **HTML Export**: Generate distribution webpage with download links
- **Checksum Verification**: Automatic file integrity verification
- **Executable**: Builds as standalone .exe file for easy distribution

## Quick Start

### Running from Source

1. Install requirements:
```bash
pip install -r requirements_distributor.txt
```

2. Run the application:
```bash
python software_distributor.py
```

### Building Executable

1. Run the build script:
```bash
python build_exe.py
```

2. Choose option 1 for GUI executable or option 2 for console version

3. Find your executable in the `dist/` folder

### Using Pre-built Executable

Simply double-click `SoftwareDistributor.exe` to launch the application.

## Usage Guide

### Adding Software to Catalog

1. Open the "Add Software" tab
2. Fill in the details:
   - Name: Software name
   - Version: Version number
   - Download URL: Direct download link
   - File Size: Size in bytes
   - Checksum: SHA256 hash for verification
   - Description: Optional description
3. Click "Add Software"

### Managing Downloads

1. Go to "Software Catalog" tab
2. Select software from the list
3. Options:
   - **Copy Download Link**: Copy URL to clipboard
   - **Download Selected**: Download to local system
   - **Refresh**: Update the list

### Exporting Catalog

1. Go to "Export Catalog" tab
2. Click "Export to HTML"
3. Choose save location
4. Share the HTML file as your software distribution page

## Configuration

The application uses `distribution_config.json` for settings:

```json
{
    "download_directory": "./downloads",
    "cdn_enabled": true,
    "auto_verify_checksums": true,
    "max_concurrent_downloads": 3,
    "retry_attempts": 3,
    "timeout_seconds": 300
}
```

## API Usage (Programmatic)

```python
from software_distributor import SoftwareDistributor

# Initialize
distributor = SoftwareDistributor()

# Add software
distributor.add_software(
    name="MyApp",
    version="1.0.0",
    download_url="https://example.com/myapp.zip",
    file_size=1048576,
    checksum="abc123...",
    description="My application"
)

# Generate download link
link = distributor.generate_download_link(software_id)

# Download software
distributor.download_software(software_id)

# Export as HTML
distributor.export_catalog_html("catalog.html")
```

## Building Advanced Installer

For creating a full installer with NSIS:

1. Run build script and choose option 4
2. Install NSIS: https://nsis.sourceforge.io/
3. Run: `makensis installer_script.nsi`
4. Distribute the `SoftwareDistributor_Setup.exe`

**Local installer bundle:** A local installer bundle was generated and added to the repository at `installers/SoftwareDistributor_bundle.zip`. It contains `SoftwareDistributor.exe` and `installer_script.nsi` so you can distribute the bundle directly or extract and run `makensis installer_script.nsi` inside the `installers/` folder to produce the final NSIS installer.

## Distribution Workflow

### For Software Publishers:

1. **Setup**: Create catalog with your software
2. **Configure**: Set download URLs and checksums
3. **Export**: Generate HTML distribution page
4. **Deploy**: Upload HTML to your web server
5. **Share**: Provide link to users

### For End Users:

1. Visit the distribution page
2. Browse available software
3. Click download links
4. Files download with integrity verification

## Security Features

- **Checksum Verification**: SHA256 hash validation
- **Secure Downloads**: HTTPS support
- **No Credentials Storage**: External download sources only
- **Integrity Checks**: Automatic verification after download

## Customization

### Custom Download Links

```python
# Generate with custom base URL
link = distributor.generate_download_link(
    software_id, 
    base_url="https://cdn.example.com"
)
```

### Custom Progress Tracking

```python
def my_progress_callback(progress):
    print(f"Download progress: {progress}%")

distributor.download_software(
    software_id,
    progress_callback=my_progress_callback
)
```

## Troubleshooting

### Build Issues

- **PyInstaller not found**: Run `pip install pyinstaller`
- **Import errors**: Install requirements: `pip install -r requirements_distributor.txt`
- **Executable won't run**: Try console version for debugging

### Runtime Issues

- **Download fails**: Check URL accessibility
- **Checksum mismatch**: Verify checksum value in catalog
- **Permission errors**: Run as administrator or change download directory

## File Structure

```
software_distributor.py          # Main application
build_exe.py                      # Build script for creating .exe
requirements_distributor.txt      # Python dependencies
distribution_config.json          # Configuration file (auto-generated)
downloads/                        # Downloaded files (auto-created)
checkpoints/                      # For AI pipeline integration
dist/                            # Built executables
```

## Integration with AI Pipeline

This distributor can work with the AI Training Pipeline:

```python
# Example: Distribute trained models
from software_distributor import SoftwareDistributor
from ai_training_pipeline import AITrainingPipeline

# Train model
pipeline = AITrainingPipeline()
pipeline.train(data, labels)
pipeline.export_model("model.onnx")

# Add to distribution
distributor = SoftwareDistributor()
distributor.add_software(
    name="Trained AI Model",
    version="1.0",
    download_url="https://models.example.com/model.onnx",
    file_size=os.path.getsize("model.onnx"),
    checksum=calculate_checksum("model.onnx"),
    description="Pre-trained robot control model"
)
```

## License

See main project license.

## Support

For issues or questions, refer to main project documentation.
