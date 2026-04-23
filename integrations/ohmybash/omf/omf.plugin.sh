# oh-my-flask :: oh-my-bash plugin
# Enables tab completion, convenience aliases, and ensures `omf` is on PATH.

for _omf_bin in "$HOME/.local/bin"; do
  if [[ -d "$_omf_bin" ]] && [[ ":$PATH:" != *":$_omf_bin:"* ]]; then
    export PATH="$_omf_bin:$PATH"
  fi
done
unset _omf_bin

if command -v omf >/dev/null 2>&1; then
  eval "$(_OMF_COMPLETE=bash_source omf 2>/dev/null)" || true
fi

alias omfi='omf install'
alias omfm='omf make'
alias omfr='omf run'
alias omfls='omf recipes'
alias omfu='omf self-update'
