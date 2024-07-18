# Maco
## Mako (wayland notif daemon), but for Mac.

### MAJOR WORK IN PROGRESS
Maco is currently in very early stages of development. The project aims to create a notification daemon for macOS inspired by Mako (the Wayland notification daemon).

### Current Status:
- Basic GUI functionality implemented using tkinter
- Generates CSV of macOS notification database
- Displays notifications in GUI window
- Reads configuration from `~/.config/maco/config`
- Configurable settings from config file:
  - Appearance:
    - Border color and radius
    - Background color
    - Font family, size, and color
  - Layout:
    - Window dimensions (width, height)
    - Margin and padding
  - Behavior:
    - Notification display duration in ms
    - Anchor (top-left, top-right, bottom-left, bottom-right, center-left, center-right, center)
- Maps application names from bundle identifiers in `app_id_list.json`
- Supports blacklist from separate file
- Implements configuration compatible with Mako

Please note that this project is highly experimental and subject to significant changes.

### Future Plans:
- Improve multi-screen support
- Add interactive features (e.g., clicking on notifications for actions)
- Create man pages for documentation
- Develop a background daemon for continuous operation
- Implement live config updates via hotkeys
- Add real-time notification display
- Create a notification preview feature for styling
- Develop more extensive rules file for app name mapping
- Enhance configuration options:
  - Set notification icon/photo
  - Set notification opacity
  - Set notification output display (which monitor)
- Implement notification grouping and stacking
- Add support for notification urgency levels
- Implement notification history and recall
- Add support for notification sounds
- Develop a CLI tool for sending test notifications
- Implement notification filtering and Do Not Disturb mode
- Add support for rich text and HTML content in notifications
- Implement notification actions (e.g., reply to messages, snooze reminders)
- Add support for notification replacement and updates
- Develop a plugin system for extending functionality?
- Package python application into binary

## License
MIT License