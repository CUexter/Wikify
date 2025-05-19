{ ... }:

{
  languages.python = {
    enable = true;
    uv.enable = true;
  };

  enterShell = ''
    source $DEVENV_STATE/venv/bin/activate
  '';
}
