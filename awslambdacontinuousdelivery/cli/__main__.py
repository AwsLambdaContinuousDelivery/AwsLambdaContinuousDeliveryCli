#!/usr/bin/env python3

import sys, os, subprocess
import argparse
import inspect
from os.path import abspath, join
from pathlib import Path
from typing import List



prod = "PROD"
config = "config"
test = "tests"
src = "src"
integration = join(test, "integrationtests")
unit = join(test, "unittests")

folders = [ src
          , test
          , config
          , integration
          , unit
          ]

packages = [ "https://github.com/AwsLambdaContinuousDelivery/pyAwsLambdaContinuousDeliveryIntegrationTests.git",
             "https://github.com/AwsLambdaContinuousDelivery/pyAwsLambdaContinuousDeliveryBuild.git",
             "https://github.com/AwsLambdaContinuousDelivery/pyAwsLambdaContinuousDeliveryUnittest.git",
             "https://github.com/AwsLambdaContinuousDelivery/AwsLambdaContinuousDeliveryDeploy.git",
             "https://github.com/AwsLambdaContinuousDelivery/AwsLambdaContinuousDeliveryNotifications.git",
             "https://github.com/AwsLambdaContinuousDelivery/AwsLambdaContinuousDeliverySourceGitHub.git",
             "https://github.com/AwsLambdaContinuousDelivery/AwsLambdaContinuousDeliverySourceCodeCommit.git",
             "https://github.com/AwsLambdaContinuousDelivery/AwsLambdaContinuousDeliveryTools.git"
]


def install(package: str):
    subprocess.call(["sudo", sys.executable, "-m", "pip", "install", package])
    return


def update():
    url = "https://github.com/AwsLambdaContinuousDelivery/AwsLambdaContinuousDeliveryCli/tarball/master"
    subprocess.call(["sudo", sys.executable, "-m", "pip", "install", url])
    return


def provision():
    pkgs = map(lambda x: x[:-4], packages)
    pkgs = map(lambda x: x + "/tarball/master", pkgs)
    for pkg in list(pkgs):
        install(pkg)
    print("Done Provisioning")
    return


def create_pipeline_template(stages: List[str], name = None, init = False):
    import awslambdacontinuousdelivery.cli.templates.python.pipeline as pipeline
    folder_location = os.getcwd()
    if name is not None and init is True:
        folder_location = join(folder_location, name, "pipeline")
    source_code = inspect.getsourcelines(pipeline)[0]
    stages = list(filter(lambda x: x != "PROD", stages))
    source_code[17] = "  stages = " + str(stages).replace("'", "\"") + "\n"
    filename = join(folder_location, "pipeline.py")
    os.mkdir(folder_location)
    Path(filename).touch()
    with open(filename, "w") as output:
        for line in source_code:
            output.write(str(line))

    jsonfile = join(folder_location, "stack.json")
    Path(jsonfile).touch()
    proc = subprocess.Popen( ['python3', filename ],
                             stdout = subprocess.PIPE,
                             stderr=subprocess.STDOUT
    )
    template =  proc.communicate()[0]
    with open(jsonfile, "w") as output:
        output.write(template.decode("utf-8"))
    return


def create_default(stages: List[str], name: str):
    if prod not in stages: stages.append(prod)
    root_folder = join(os.getcwd(), name)
    os.mkdir(root_folder)
    create_folders(stages, root_folder)
    create_requirements(root_folder)
    create_function(root_folder, name)
    create_config_yaml(root_folder, name)
    create_stage_configs(root_folder, stages)
    return


def create_function(root_folder: str, name: str):
    filepath = abspath(join(root_folder, src, "function.py")) 
    Path(filepath).touch()
    with open(filepath, "w") as output:
        output.write("def handler(event, context):\n")
        output.write("  return\n")
    return


def create_config_yaml(root_folder: str, name: str):
    filepath = abspath(join(root_folder, config, "config.yaml"))
    Path(filepath).touch()
    with open(filepath, "w") as output:
        output.write("Name: " + name + "\n")
        output.write("Handler: " + "function.handler\n")
        output.write("Memory: 128\n")
        output.write("Timeout: 3\n")
        output.write("Unittests: " + unit + "\n")
        output.write("Integrationtests: " + integration + "\n")
    return


def create_stage_configs(root_folder: str, stages: List[str]):
    env_str = "def get_env() -> dict:\n" \
              "  return {}"
    iam_str = "from awslambdacontinuousdelivery.tools.iam import (\n" \
              "    defaultAssumeRolePolicyDocument\n" \
              "  , oneClickCreateLogsPolicy\n" \
              "  )\n\n" \
              "from troposphere.iam import Role\n\n" \
              "def get_iam(ref_name: str) -> Role:\n" \
              "  assume = defaultAssumeRolePolicyDocument(\"lambda.amazonaws.com\")\n" \
              "  return Role( ref_name\n" \
              "             , RoleName = ref_name\n" \
              "             , AssumeRolePolicyDocument = assume\n" \
              "             , Policies = [oneClickCreateLogsPolicy()]\n" \
              "             )\n"
    for stage in stages:
        filepath = abspath(join(root_folder, config, stage))
        envfile = abspath(join(filepath, "env.py"))
        iamfile = abspath(join(filepath, "iam.py"))
        Path(envfile).touch()
        Path(iamfile).touch()
        with open(envfile, "w") as env:
            env.write(env_str)
        with open(iamfile, "w") as iam:
            iam.write(iam_str)
    return


def create_requirements(root_folder: str):
    requirements = [ "", integration, unit ]
    for folder in requirements:
        Path(
            abspath(
                join(
                    root_folder, folder, "requirements.txt")
            )
        ).touch()
    return


def create_folders(stages: List[str], root_folder: str):
    stages = map(lambda s: abspath(join(root_folder, config, s)), stages)
    folders_ = map(lambda f: abspath(join(root_folder, f)), folders)
    folders_ = list(folders_) + list(stages)
    for folder in folders_:
        os.mkdir(folder)
    return


def main(args = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", "-i", help = "Create default folder structure. Must additionally use `--name`.", required = False, action = "store_true")
    parser.add_argument("--name", "-n",  help = "Function/Folder name. The cli will create a folder with this name and place all files inside.", required = False)
    parser.add_argument("--stages", "-s", nargs = "+", help="Set flag and add all stages EXCEPT PROD, if no flag is set, then there will be just a PROD stage", required = False)

    parser.add_argument("--pipeline", "-p", help = "Create Pipeline template. If run with `--init` it will create a separate `pipeline` folder. Otherwise, it will simply place a template pipeline from where the command is run.", required = False, action = "store_true") 

    parser.add_argument("--provision", help = "Install/Update AwsLambda CI/CD tools libraries/packages (it might be necessary to run this command with `sudo`", required = False, action = "store_true", default = False)

    parser.add_argument("--update", help = "Update this CLI", required = False, action = "store_true", default = False)


    args = parser.parse_args()

    if args.update:
        update()
        sys.exit()

    if args.provision:
        provision()

    if not args.stages:
        args.stages = []

    if args.init:
        if args.name is None:
            print("--name, -n for --init neccessary")
            sys.exit()
        else:    
            create_default(args.stages, args.name)

    if args.pipeline:
        create_pipeline_template(args.stages, args.name, args.init)
    return


if __name__ == "__main__":
    main()
