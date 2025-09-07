# slice_infra

## Usage

This repo contains reusable workflows and scripts for Slice hardware repos.
It is not meant to be triggered directly.

To use in other repos, call the workflows like this:

```yaml
jobs:
  orchestrate:
    uses: FEASTorg/slice-infra/.github/workflows/docs-pipeline.yml@v1
```
