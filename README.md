# Halky Launcher Meta

Scripts to generate jsons and jars that the Halky Launcher will access. 
Based on the original Prism Launcher Meta repository.

## 🚀 Deployment & Updates (GitHub Actions)

This repository is fully automated using GitHub Actions.

- Metadata is updated **automatically every 2 days**.
- Upstream data (from Mojang, Forge, Fabric, Quilt, Adoptium, etc.) is fetched and processed.
- The generated files, along with the `index.html` landing page, are pushed directly to the `meta` branch.
- The `meta` branch serves as the root for **GitHub Pages**, meaning the launcher gets the latest data instantly.

### Need a manual update?
You can trigger an update at any time:
1. Go to the **Actions** tab in this GitHub repository.
2. Select the **Update Meta** workflow.
3. Click **Run workflow**.

🔗 **Main Launcher Website:** [Halky Launcher](https://halkylauncher.alex1811.ovh/)

---

## 🛠️ Legacy / Local Deployment (NixOS)

Assuming you have a Flake-based NixOS configuration

- Add Flake input:

    ```nix
    {
      inputs.prism-meta.url = "github:PrismLauncher/meta";
    }
    ```

- Import NixOS module and configure

    ```nix
    {inputs, ...}: {
      imports = [inputs.prism-meta.nixosModules.default];
      services.blockgame-meta = {
        enable = true;
        settings = {
          DEPLOY_TO_GIT = "true";
          GIT_AUTHOR_NAME = "Herpington Derpson";
          GIT_AUTHOR_EMAIL = "herpderp@derpmail.com";
          GIT_COMMITTER_NAME = "Herpington Derpson";
          GIT_COMMITTER_EMAIL = "herpderp@derpmail.com";
        };
      };
    }
    ```

- Rebuild and activate!
- Trigger it `systemctl start blockgame-meta.service`
- Monitor it `journalctl -fu blockgame-meta.service`
