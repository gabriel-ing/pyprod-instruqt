ARG IMAGE=intersystems/iris-community:latest-em
FROM $IMAGE

ENV IRISINSTALLDIR "/usr/irissys"
ENV LD_LIBRARY_PATH "$IRISINSTALLDIR/bin:$LD_LIBRARY_PATH"
ENV IRISUSERNAME "SuperUser"
ENV IRISPASSWORD "SYS"
ENV IRISNAMESPACE "ENSEMBLE"
ENV COMLIB "$IRISINSTALLDIR/bin"
ENV PYTHONPATH "$IRISINSTALLDIR/lib/python"
ENV PATH "/usr/irissys/lib/python/bin:/usr/irissys/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/irisowner/bin:/home/irisowner/.local/bin"



WORKDIR /home/irisowner/dev

# COPY src/pyprod /home/irisowner/dev/pyprod
# RUN chown -R irisowner:irisowner /home/irisowner/dev/pyprod


RUN python3 -m pip install --break-system-packages intersystems_pyprod --target /usr/irissys/lib/python

# Patch to allow restarting the production from the command line
RUN python3 - <<'PY'
from pathlib import Path

parser_path = Path("/usr/irissys/lib/python/intersystems_pyprod/_parser.py")
source = parser_path.read_text(encoding="utf-8")

argument_anchor = '    parser.add_argument("input_script", nargs="?", help="Path to a .py file (used when -m/--module is not provided)")\n'
argument_insertion = argument_anchor + '    parser.add_argument("-r", "--restart", action="store_true", help="Restart the production")\n'
restart_block = (
    '    args = parser.parse_args(argv)\n\n'
    '    if args.restart:\n'
    '        import iris\n'
    '        iris.Ens.Director.RestartProduction()\n'

)

if 'parser.add_argument("-r", "--restart"' not in source:
    if argument_anchor not in source:
        raise RuntimeError("Could not find CLI argument insertion point in _parser.py")
    source = source.replace(argument_anchor, argument_insertion, 1)

if 'iris.Ens.Director.RestartProduction()' not in source:
    parse_args_anchor = '    args = parser.parse_args(argv)\n\n'
    if parse_args_anchor not in source:
        raise RuntimeError("Could not find parse_args insertion point in _parser.py")
    source = source.replace(parse_args_anchor, restart_block, 1)

parser_path.write_text(source, encoding="utf-8")
PY



RUN --mount=type=bind,src=.,dst=. \
    iris start IRIS && \
    iris merge IRIS merge.cpf && \
	iris session IRIS < iris.script && \
    iris stop IRIS quietly