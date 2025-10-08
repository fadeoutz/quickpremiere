<img src="assets/banner.png" width="520" height="150">
This program is a lightweight Premiere Pro launcher designed to quickly create a project file without having to navigate through the hell of the Premiere Pro home screen.

## Features
- Quickly create and automatically open a Premiere project file with preset resolutions and frame rates.
- Automatically applies standard audio settings (48kHz, 24bit).

## Installation
Installation files for Windows are provided in the [releases](https://github.com/fadeoutz/quickpremiere/releases) tab. 

To build this on your own, do the following using Python 12.3:

```pip install -r requirements.txt```

``py quickpremiere.py``

## Usage
1. **Specify Premiere Pro Installation Path**
   - This is automatically detected in most cases. If not, you'll need to manually browse for it.

2. **Choose a Directory for Your Project Files**
   - Select where you want your project files to be stored on your system.

3. **Name Your Project and Configure Preferences**
   - Enter a name for your project file and select your desired project preferences (e.g., resolution, frame rate).

4. **Create the Project**
   - Click on "Create Project" to generate your new Premiere project file.

5. **Wait for Premiere to Open**
   - Premiere Pro will launch automatically, and the project file will be opened.
   - Once the project is opened, **quickpremiere will automatically close**.

## Notes
- Only supported on Windows with Adobe Premiere 24.0.3+

  

*Created with hate and AI by @fadeoutz 💔*
