# Maco
## Mako (wayland notif daemon), but for Mac.

### MAJOR WORK IN PROGRESS

Maco is currently in very early stages of development. The project aims to create a notification daemon for macOS inspired by Mako (the Wayland notification daemon).

### Current Status:
- Basic GUI functionality implemented using tkinter
- Can generate a CSV of the macOS notification database
- Displays notifications in a simple GUI window
- Can read configuration from Maco's config file `~/.config/maco/config`
- Can set border color from config file
- Can set background color from config file
- Can set duration notification is displayed for in ms
- Can set Application Name mapped from bundle identifiers

Please note that this project is highly experimental and subject to significant changes.

### Future Plans:
- Implement Mako-style configuration
- Improve multi-screen support
- Add interactive features (e.g., clicking on notifications for actions)
- Create man pages for documentation
- Develop a background daemon for continuous operation
- Implement live config updates via hotkeys
- Add real-time notification display
- Create a notification preview feature for styling
- Develop more extensive rules file for app name mapping
- Enhance configuration options:
  - Set border radius
  - Set font family
  - Set font color
  - Set font size
  - Set notification icon/photo
  - Set notification opacity
  - Set notification location (which corner)
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

## License
MIT License