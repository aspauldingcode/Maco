# Maco
## Mako (wayland notif daemon), but for Mac.

### how to use:
currently, it does not behave like it will.
we are (I am) in early stages, where we generate a csv of the macOS notification database, then we can view it in terminal.

That is the extent so far.. A prettified terminal output of your notifications.

## Liscense: FOSS
BSD3.

Plans:
- Mako's config ideology: Configure Maco notif style with 1:1 manpages of Mako config
- GUI for Maco: actually SHOW the notifications on the screen (Somehow with multi-screen support) (outside of cli)
- Interactive: allow user to click on Notification for actions
- Man pages: Include documentation for configuring Maco or invoking the command.
- Daemon: You know, the actual part that always runs in the background.
- Hotkey changes: Read config and update live.
- Notifications: Actually show new notifications for n seconds (automatically determine changes in notif database)
- Invoke Maco Notifications: Preview an example notification for the user to style it properly like Mako does
- Rules file: For app bundle identifiers to display the app name instead of identifier ("com.example.appnameexample" would be mappable to App Name)
