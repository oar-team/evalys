let
  kapack = import (fetchTarball https://github.com/oar-team/kapack/archive/master.tar.gz) {};
in

with kapack.pkgs;

mkShell rec {
  buildInputs = [
    python36Packages.sphinx
    python36Packages.sphinx_rtd_theme
    kapack.evalys4
  ];
  shellHook = ''
    sphinx-build . build
  '';
}
