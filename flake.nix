{
  description = "MTG Atlas Bulk Loader DevShell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = with pkgs; [
          python312
          python312Packages.neo4j
          python312Packages.python-dotenv
          pyright
        ];
      };
    };
}
