from setuptools import setup

setup( name = "awslambdacicd-cli",
       version = "0.1.1",
       author = "Janos Potecki",
       license = "MIT",
       packages = [
           "awslambdacontinuousdelivery.cli",
           "awslambdacontinuousdelivery.cli.templates.python"
       ],
       entry_points = {
           "console_scripts" : [
               "awslambdacicd = awslambdacontinuousdelivery.cli.__main__:main"
               ]
           }
       )
