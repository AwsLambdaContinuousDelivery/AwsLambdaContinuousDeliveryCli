from setuptools import setup

setup( name = "awslambdacicd-cli",
       version = "0.1.0",
       packages = ["awslambdacicd_console_tool"],
       entry_points = {
           "console_scripts" : [
               "awslambdacicd = awslambdacicd_console_tool.__main__:main"
               ]
           }
       )
