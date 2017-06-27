with import <nixpkgs> {};
with import /home/adfaure/datamove-nix {};

rWrapper.override {
  packages = [
      python3
      python35Packages.seaborn
      python35Packages.numpy
      texlive.combined.scheme-small
      inkscape
      ghostscript
      asymptote
      evalys
      ];
}

