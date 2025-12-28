# config.nu
#
# Installed by:
# version = "0.108.0"
#
# This file is used to override default Nushell settings, define
# (or import) custom commands, or run any other startup tasks.
# See https://www.nushell.sh/book/configuration.html
#
# Nushell sets "sensible defaults" for most configuration settings, 
# so your `config.nu` only needs to override these defaults if desired.
#
# You can open this file in your default editor using:
#     config nu
#
# You can also pretty-print and page through the documentation for configuration
# options using:
#     config nu --doc | nu-highlight | less -R

source ~/.config/nushell/catppuccin.nu
source ~/.config/nushell/env.nu

$env.config = {
  show_banner: false


  datetime_format: { normal: "%Y/%m/%d %H:%M:%S" }

  history: {
    max_size: 100_000
    sync_on_enter: true
    file_format: "plaintext"
    isolation: false
  }

  completions: {
      case_sensitive: false
      quick: true
      partial: true
      algorithm: "prefix"
      external: {
          enable: true
          max_results: 100
          completer: null
      }
      use_ls_colors: true
  }

  cursor_shape: {
      emacs: block
      vi_insert: block
      vi_normal: underscore
  }

  edit_mode: vi
}

alias l = ls
alias la = ls -a
alias ll = ls -l
alias lla = ls -al
alias lsdl = lsd -l
alias lsda = lsd -a
alias lsdla = lsd -al

alias gaa = git add .
alias ga = git add
alias gc = git commit
alias gm = git commit -m
alias gp = git push

mkdir ($nu.data-dir | path join "vendor/autoload")
starship init nu | save -f ($nu.data-dir | path join "vendor/autoload/starship.nu")

atuin init nu | save -f ~/.local/share/atuin.nu
source ~/.local/share/atuin/init.nu
zoxide init nushell | save -f ~/.zoxide.nu
source ~/.zoxide.nu

