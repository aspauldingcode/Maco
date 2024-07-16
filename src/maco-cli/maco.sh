
#!/bin/bash

# Function to display usage information
usage() {
    echo "Usage: $0 [command] [options...]"
    echo "Commands:"
    echo "  dismiss [-a|--all] [-g|--group] [-n <id>]"
    echo "  restore"
    echo "  invoke [-n <id>] [action]"
    echo "  menu [-n <id>] <program> [argument...]"
    echo "  list"
    echo "  history"
    echo "  reload"
    echo "  mode [-s <mode>...] [-a mode]... [-r mode]... [-t mode]..."
    echo "  help, -h, --help"
    exit 1
}

# Check if at least one argument is provided
if [ $# -lt 1 ]; then
    usage
fi

# Execute the maco CLI command
case "$1" in
    dismiss)
        shift
        python3 view_notifications.py dismiss "$@"
        ;;
    restore)
        python3 view_notifications.py restore
        ;;
    invoke)
        shift
        python3 view_notifications.py invoke "$@"
        ;;
    menu)
        shift
        python3 view_notifications.py menu "$@"
        ;;
    list)
        python3 view_notifications.py list
        ;;
    history)
        python3 view_notifications.py history
        ;;
    reload)
        python3 view_notifications.py reload
        ;;
    mode)
        shift
        python3 view_notifications.py mode "$@"
        ;;
    help|-h|--help)
        usage
        ;;
    *)
        usage
        ;;
esac
