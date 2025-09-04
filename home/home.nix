{ config, pkgs, ... }:

{
  # Home Manager configuration for Ubuntu developer environment
  home.username = builtins.getEnv "USER";
  home.homeDirectory = "/home/${config.home.username}";
  home.stateVersion = "23.11"; # Please read the comment before changing.

  # Enable Nix flakes support
  nix = {
    package = pkgs.nix;
    settings.experimental-features = [ "nix-command" "flakes" ];
  };

  # Enable Home Manager
  programs.home-manager.enable = true;

  # USER LAYER - Shell configuration
  programs.zsh = {
    enable = true;
    enableCompletion = true;
    autosuggestion.enable = true;
    syntaxHighlighting.enable = true;
    
    oh-my-zsh = {
      enable = true;
      plugins = [
        "git"
        "docker"
        "docker-compose"
        "yarn"
        "npm"
        "aws"
        "command-not-found"
        "pre-commit"
      ];
      theme = "robbyrussell";
    };
    
    shellAliases = {
      cat = "bat --style=plain";
      ll = "ls -alF";
      la = "ls -A";
      l = "ls -CF";
      # Enforce security for git aliases
      ggl = "echo '\\e[31mUse \\e[1;31mggfl\\e[0m!' && return 1";
      gcam = "echo '\\e[31mUse \\e[1;31mgcasm\\e[0m!' && return 1";
      "gcan!" = "echo '\\e[31mUse \\e[1;31mgcans!\\e[0m!' && return 1";
    };
  };

  # USER LAYER - Git configuration
  programs.git = {
    enable = true;
    userName = "Emilien Escalle";
    userEmail = "emilien.escalle@escemi.com";
    
    extraConfig = {
      init.defaultBranch = "main";
      push.default = "simple";
      pull.rebase = false;
      core.editor = "nvim";
      commit.gpgsign = true;
    };
    
    includes = [
      { path = "~/.config/git/clients/allopneus"; }
    ];
  };

  # USER LAYER - Development tools
  programs.neovim = {
    enable = true;
    defaultEditor = true;
    viAlias = true;
    vimAlias = true;
  };

  programs.tmux = {
    enable = true;
    terminal = "screen-256color";
    shortcut = "a";
    keyMode = "vi";
    extraConfig = ''
      set -g mouse on
      set -g status-style bg=black,fg=white
    '';
  };

  programs.direnv = {
    enable = true;
    enableZshIntegration = true;
    nix-direnv.enable = true;
  };

  programs.bat = {
    enable = true;
    config = {
      theme = "TwoDark";
      style = "numbers,changes,header";
    };
  };

  programs.fzf = {
    enable = true;
    enableZshIntegration = true;
  };

  # USER LAYER - Development packages
  home.packages = with pkgs; [
    # Shell utilities
    htop
    curl
    wget
    unzip
    tree
    jq
    
    # Development tools
    gh
    just
    gnumake
    
    # Password management
    bitwarden-cli
    
    # Python development
    python3
    python3Packages.pip
    python3Packages.setuptools
    
    # Node.js development
    nodejs
    yarn
    
    # Fonts
    fira-code
    fira-code-symbols
  ];

  # USER LAYER - Fonts configuration
  fonts.fontconfig.enable = true;

  # USER LAYER - Environment variables
  home.sessionVariables = {
    EDITOR = "nvim";
    BROWSER = "chromium";
    TERMINAL = "gnome-terminal";
  };

  # USER LAYER - XDG directories
  xdg.enable = true;
  
  # Create project template for direnv
  home.file.".envrc.template".text = ''
    # Project-specific environment template
    # Copy this to your project root and customize as needed
    
    # Example: Use specific Node.js version
    # use node 18
    
    # Example: Load Python environment
    # layout python python3
    
    # Example: Load Nix shell
    # use flake .
    
    # Example: Set project-specific environment variables
    # export PROJECT_NAME="my-project"
    # export DATABASE_URL="sqlite:///tmp/dev.db"
  '';

  # Create sample project flake template
  home.file."Documents/project-template/flake.nix".text = ''
    {
      description = "Project development environment";
      
      inputs = {
        nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
        flake-utils.url = "github:numtide/flake-utils";
      };
      
      outputs = { self, nixpkgs, flake-utils }:
        flake-utils.lib.eachDefaultSystem (system:
          let
            pkgs = nixpkgs.legacyPackages.''${system};
          in
          {
            devShells.default = pkgs.mkShell {
              buildInputs = with pkgs; [
                # Add project-specific dependencies here
                # nodejs
                # python3
                # go
                # rust
              ];
              
              shellHook = '''
                echo "Project development environment loaded"
              ''';
            };
          });
    }
  '';

  home.file."Documents/project-template/.envrc".text = ''
    use flake .
  '';
}