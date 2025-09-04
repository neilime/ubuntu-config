{
  description = "Ubuntu development environment with Home Manager";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    home-manager = {
      url = "github:nix-community/home-manager";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { nixpkgs, home-manager, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      homeConfigurations = {
        # Default user configuration
        "ubuntu" = home-manager.lib.homeManagerConfiguration {
          inherit pkgs;
          modules = [ ./home.nix ];
        };
        
        # Alternative configuration for different usernames
        "user" = home-manager.lib.homeManagerConfiguration {
          inherit pkgs;
          modules = [ ./home.nix ];
        };
      };
      
      # Development shell for this flake
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          home-manager
          direnv
          nix-direnv
        ];
        
        shellHook = ''
          echo "Ubuntu Development Environment"
          echo "Available commands:"
          echo "  home-manager switch --flake .#ubuntu"
          echo "  direnv allow (for project-specific environments)"
        '';
      };
    };
}