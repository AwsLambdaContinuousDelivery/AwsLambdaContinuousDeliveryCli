#!/usr/bin/env python3

import sys, os
import argparse
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


def create_default(stages: List[str], name:str):
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


def pipeline_source_code(stages: List[str]) -> str:
    pass


def main(args = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", help = "Function Name", required = True)
    parser.add_argument("--init", help = "create default folder structure", required = False, action = "store_true")
    parser.add_argument("--stages", nargs = "+", help="Set flag and add all stages EXCEPT PROD, if no flag is set, then there will be just a PROD stage", required = False)
    
    args = parser.parse_args()
    if not args.stages:
        args.stages = []

    if args.init:
        print("Starting creating the structure")
        create_default(args.stages, args.name)


if __name__ == "__main__":
    main()
