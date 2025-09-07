# slice_infra

See [Slice_TEMP](https://github.com/FEASTorg/Slice_TEMP) for the required auxiliary and template files.

## Usage

This repo contains reusable workflows and scripts for Slice hardware repos.
It is not meant to be triggered directly.

To use in other repos, call the workflow like this:

```yaml
name: Docs Pipeline

on:
  push:
    branches: [main]
    paths:
      - "hardware/**"
      - "docs/**"
      - "scripts/**"
      - ".github/workflows/**"
  workflow_dispatch:

jobs:
  kibot:
    uses: FEASTorg/slice-infra/.github/workflows/kibot-ci.yml@main

  gen-kibot-index:
    uses: FEASTorg/slice-infra/.github/workflows/publish-kibot.yml@main
    needs: [kibot]
    with:
      kibot_run_id: ${{ needs.kibot.outputs.kibot_run_id }}

  deploy-pages:
    uses: FEASTorg/slice-infra/.github/workflows/deploy-pages.yml@main
    needs: [gen-kibot-index]
    with:
      kibot_run_id: ${{ needs.kibot.outputs.kibot_run_id }}
      commit_sha: ${{ needs.gen-kibot-index.outputs.kibot_index_sha }}
```
