---
title: Setup
parent: Chart Review
nav_order: 1
# audience: lightly technical folks
# type: how-to
---

# Setting Up Chart Review

## Installing

`pip install chart-review`

## Make Project Directory

1. Make a new directory to hold your project files.
2. Export your Label Studio project and put the resulting JSON file
   in this directory with the name `labelstudio-export.json`.
3. Create a [config file](config.md) in this directory.

## Run Chart Review

The only current command is `accuracy`,
which will print agreement statistics between two annotators.

Read more about it in its own [accuracy command documentation](accuracy.md).