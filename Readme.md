# PyProd Tutorial Application


> [!WARNING]
> This branch is an intermediate step for the interactive Instruqt Tutorial. To view the end state, change to the "main" branch.


A starter template for building productions with [PyProd](https://github.com/intersystems/pyprod) on InterSystems IRIS. PyProd lets you define IRIS interoperability productions — services, processes, and operations — entirely in Python. The Docker setup handles all environment configuration out of the box.

## Prerequisites

- Docker

## Installation

1. Clone this repository:
   ```bash
   git clone <repo-url>
   cd pyprod-tutorial-application
   ```

2. Build and start the container:
   ```bash
   docker build -t pyprod-tutorial .
   docker run -p 52773:52773 pyprod-tutorial
   ```

Your source files go in `./src` — this directory is mounted to `/home/irisowner/dev` inside the container so changes are reflected immediately without rebuilding.

## Creating and Starting a Production

Inside the container, generate the required IRIS classes from your Python source files, then register the components:

```bash
intersystems_pyprod components.py
```
Then register the production: 
```bash
intersystems_pyprod production.py
```

Then start the production with the helper CLI `controls.py`:

```bash
python3 controls.py start RedLights.MyProduction
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `IRISNAMESPACE` | `ENSEMBLE` | IRIS namespace used by PyProd |
| `IRISUSERNAME` | `SuperUser` | IRIS login username |
| `IRISPASSWORD` | `SYS` | IRIS login password |
