#!/usr/bin/env nix-shell
#! nix-shell -i bash -p cbc "python3.withPackages (ps: [ps.docopt ps.pulp])"

python3 src "$@"
