from flask import Flask

app = Flask(__name__)


@app.cli.command()
def ipython():
    """Starts IPython shell instead of the default Python shell."""
    import sys
    import IPython
    from flask.globals import _app_ctx_stack
    app = _app_ctx_stack.top.app

    banner = '\nPython %s on %s\nIPython: %s\n\n' % (
        sys.version, sys.platform, IPython.__version__
    )

    ctx = {}
    ctx.update(app.make_shell_context())

    IPython.embed(banner1=banner, user_ns=ctx)
