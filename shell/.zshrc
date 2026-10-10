# Enable Powerlevel10k / prompt instant prompt or oh-my-posh
export PATH="$HOME/.local/bin:$PATH"

# History configuration
HISTFILE="$HOME/.zsh_history"
HISTSIZE=10000
SAVEHIST=10000
setopt APPEND_HISTORY
setopt SHARE_HISTORY
setopt HIST_IGNORE_DUPS
setopt HIST_IGNORE_SPACE

# Common aliases
alias ls='ls --color=auto'
alias grep='grep --color=auto'
alias ll='ls -lah --color=auto'

# Oh My Posh initialization
if command -v oh-my-posh >/dev/null 2>&1; then
    eval "$(oh-my-posh init zsh --config "$HOME/.cache/oh-my-posh/themes/night-owl.omp.json")"
fi
