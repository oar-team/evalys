# Use this environment to publish this package on pypi:
#
#   # Enter the environment
#   nix-shell release.nix
#
#   # create the package
#   python setup.py sdist
#
#   # register to pypi (if not registered yet)
#   twine register dist/project_name-x.y.z.tar.gz
#
#   # upload you package
#   twine upload dist/project_name-x.y.z.tar.gz

with import <nixpkgs> {};

(pkgs.python36.withPackages (ps: with ps; [twine setuptools])).env

