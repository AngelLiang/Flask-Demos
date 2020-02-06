import click

from app.extensions import db


def register_commands(app):

    @app.cli.command()
    def build():
        """Build sb-admin-2 frontend"""
        import os
        import subprocess

        path = os.path.join(app.root_path, 'static', 'sb-admin-2')
        os.chdir(path)
        subprocess.call(['bower', 'install'], shell=True)

    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database."""
        if drop:
            click.confirm(
                'This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def fake(drop):
        """fake data."""
        from app.fake import fake_admin, initdata

        if drop:
            click.confirm(
                'This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()

        fake_admin()
        initdata()

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
