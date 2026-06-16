# PyProd Tutorial Application

A starter template for building productions with [PyProd](https://github.com/intersystems/pyprod) on InterSystems IRIS. PyProd lets you define IRIS interoperability productions — services, processes, and operations — entirely in Python. The Docker setup handles all environment configuration out of the box.

## Prerequisites

- Docker

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/gabriel-ing/pyprod-instruqt.git
   cd pyprod-instruqt
   ```

2. Build and start the container:
   ```bash
   docker-compose up -d --build
   ```

The repo directory is mounted to `/home/irisowner/dev` inside the container so changes are reflected immediately without rebuilding.

The management portal is at http://localhost:52777/csp/sys/%25CSP.Portal.Home.zen?$NAMESPACE=ENSEMBLE.

## Creating and Starting a Production

Inside the container, generate the required IRIS classes from your Python source files, then register the components:

```bash
intersystems_pyprod components.py
intersystems_pyprod census_components.py

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
