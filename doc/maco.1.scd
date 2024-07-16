maco(1)

# NAME

maco - notification daemon for macOS

# SYNOPSIS

*maco* [options...]

# DESCRIPTION

Maco is a notification daemon for macOS. It retrieves notifications from system databases, saves them to a CSV file, and allows viewing them through a separate script. Notifications remain visible until dismissed.

# OPTIONS

*-h, --help*
    Show help message and quit.

*-c, --config*
    Custom path to the config file.

Additionally, global configuration options can be specified. Passing *--key=value* is equivalent to a *key=value* line in the configuration file. See *maco*(5) for a list of options.

# AUTHORS

Maintained by Alex S. <aspauldingcode@gmail.com>

# SEE ALSO

*maco*(5) *macoctl*(1)
