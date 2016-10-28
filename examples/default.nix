with import <nixpkgs> {};
rWrapper.override {
  packages = [
      python35
      python35Packages.pyqt5
      python35Packages.docopt
      python35Packages.matplotlib
      python35Packages.pip
      ];
}
