# oh-my-flask :: oh-my-zsh plugin
# Enables tab completion, convenience aliases, and ensures `omf` is on PATH.

# Make sure the common user-bin dirs are on PATH (pipx + pip --user land here).
for _omf_bin in "$HOME/.local/bin"; do
  if [[ -d "$_omf_bin" ]] && [[ ":$PATH:" != *":$_omf_bin:"* ]]; then
    export PATH="$_omf_bin:$PATH"
  fi
done
unset _omf_bin

# Click-powered tab completion. Silent if omf isn't installed yet.
if command -v omf >/dev/null 2>&1; then
  eval "$(_OMF_COMPLETE=zsh_source omf 2>/dev/null)" || true
fi

alias omfi='omf install'
alias omfm='omf make'
alias omfr='omf run'
alias omfls='omf recipes'
alias omfu='omf self-update'
