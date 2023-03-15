with import <nixpkgs> {};
with pkgs.python37Packages;

stdenv.mkDerivation {
  name = "pplan-env";
  buildInputs = [
    python37Full
    python37Packages.pip
  ];
  src = null;
  shellHook = ''
    # Setting SOURCE_DATE_EPOCH apparently needed to make Python wheels usable
    SOURCE_DATE_EPOCH=$(date +%s)
    python -m venv env
    export PATH=$PWD/env/bin:$PATH
    python -m pip install -r requirements.txt
    source env/bin/activate
  '';
}
