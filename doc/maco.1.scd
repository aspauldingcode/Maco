maco(1)

# NAME

maco - notification daemon for macOS

# SYNOPSIS

*maco* [options...]

# DESCRIPTION

Maco is a notification daemon for macOS. It retrieves notifications from system databases, caches them, and displays the decoded notification information to the user.

# OPTIONS

*-h, --help*
    Show help message and quit.

*-c, --config*
    Custom path to the config file. Default is ~/.config/maco/config.

Additionally, global configuration options can be specified. Passing *--key=value* is equivalent to a *key=value* line in the configuration file. See *maco*(5) for a list of options.

# AUTHORS

Maintained by Alex Spaulding. <aspauldingcode@gmail.com>

# SEE ALSO

*maco*(5) *macoctl*(1)
