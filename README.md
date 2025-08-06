# Mergify pre-commit

This repository provides Mergify hooks for pre-commit.

## Usage

Update your `.pre-commit-config.yaml`:

```yml
repos:
-   repo: https://github.com/crsantos/mergify-pre-commit
    rev: 501ac354fc5581ce2e101c0fbae1db157fda5798 # Use a specific commmit hash
    hooks:
    -   id: mergify
```
