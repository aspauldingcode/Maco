{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python311
    python311Packages.pandas
    python311Packages.termcolor
    python311Packages.biplist
    python311Packages.textwrap3
    python311Packages.tkinter
    python311Packages.psutil
    sqlite
  ];

  shellHook = ''
    export PYTHONPATH="${pkgs.python311Packages.pandas}/lib/python3.11/site-packages:$PYTHONPATH"
    export PYTHONPATH="${pkgs.python311Packages.termcolor}/lib/python3.11/site-packages:$PYTHONPATH"
    export PYTHONPATH="${pkgs.python311Packages.biplist}/lib/python3.11/site-packages:$PYTHONPATH"
    export PYTHONPATH="${pkgs.python311Packages.textwrap3}/lib/python3.11/site-packages:$PYTHONPATH"
    export PYTHONPATH="${pkgs.python311Packages.tkinter}/lib/python3.11/site-packages:$PYTHONPATH"
    export PYTHONPATH="${pkgs.python311Packages.psutil}/lib/python3.11/site-packages:$PYTHONPATH"
    export PATH="${pkgs.sqlite}/bin:$PATH"
    
    echo "Maco development environment loaded"
    echo "Python packages available: pandas, termcolor, biplist, textwrap3, tkinter, psutil"
    echo "SQLite is also available in the PATH"
    echo "To run the project, use the following command:"
    echo "  python src/maco/mac_notifications_gui.py"
  '';
}