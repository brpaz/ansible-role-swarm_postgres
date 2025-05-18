{ pkgs, ... }:

{
  env.LC_ALL = "en_US.UTF-8";

  # https://devenv.sh/packages/
  packages = [
    pkgs.python312
    pkgs.git
    pkgs.go-task
    pkgs.molecule
    pkgs.python312Packages.pytest
    pkgs.python312Packages.docker
    pkgs.python312Packages.pytest-testinfra
  ];

  enterShell = ''
    ansible --version
  '';

  languages.ansible.enable = true;
}
