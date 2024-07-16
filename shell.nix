{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python311
    python311Packages.pandas
    python311Packages.termcolor
    python311Packages.biplist
    python311Packages.textwrap3
    sqlite
    gcc
    gnumake
    gtk3
    gtk-mac-integration
    gtk-mac-bundler
    glib
    pango
    cairo
    gdk-pixbuf
    atk
    rustc
    cargo
  ];

  shellHook = ''
    export PYTHONPATH="${pkgs.python311Packages.pandas}/lib/python3.11/site-packages:$PYTHONPATH"
    export PYTHONPATH="${pkgs.python311Packages.termcolor}/lib/python3.11/site-packages:$PYTHONPATH"
    export PYTHONPATH="${pkgs.python311Packages.biplist}/lib/python3.11/site-packages:$PYTHONPATH"
    export PYTHONPATH="${pkgs.python311Packages.textwrap3}/lib/python3.11/site-packages:$PYTHONPATH"
    export PATH="${pkgs.sqlite}/bin:$PATH"
    export PKG_CONFIG_PATH="${pkgs.gtk3}/lib/pkgconfig:${pkgs.glib}/lib/pkgconfig:${pkgs.pango}/lib/pkgconfig:${pkgs.cairo}/lib/pkgconfig:${pkgs.gdk-pixbuf}/lib/pkgconfig:${pkgs.atk}/lib/pkgconfig:$PKG_CONFIG_PATH"
    
    echo "Maco development environment loaded"
    echo "Python packages available: pandas, termcolor, biplist, textwrap3"
    echo "SQLite is also available in the PATH"
    echo "GTK3 and related libraries are available for Rust GUI development"
    echo "Rust and Cargo are available for Rust development"
    echo "To compile and run the project, use the following Cargo commands:"
    echo "  cargo build    - Compile the project"
    echo "  cargo run      - Run the project"
    echo "  cargo test     - Run the tests"
  '';
}