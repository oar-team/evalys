with import <nixpkgs> {};
with import /home/mercierm/Projects/datamove-nix {};

rWrapper.override {
  packages = [
      python3
      evalys
      ];
}
