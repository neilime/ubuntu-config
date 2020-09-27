# Load Antigen
source ~/antigen.zsh

# Load Antigen configurations
antigen init ~/.antigenrc

eval "$(starship init zsh)"

# Aliases

if [ "$(command -v batcat)" ]; then
  unalias -m 'cat'
  alias cat='batcat -pp'
fi

# Path

export PATH="$(yarn global bin):$(realpath ~/.local/bin):$PATH"
