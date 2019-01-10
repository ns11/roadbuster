#IMPORTS
import os
import sys
#import ipdb
import nox


#CONFIGS
NOX_CONFIG = {"PYTHON_VER": "LST", "DJANGO_VER": "MIN"}
PYTHON_DST = {
    "MAX": ["2.7", "3.2", "3.6", "3.7"], 
    "MIN": ["3.6"],
    "LST": ["3.7.1"],
    }
DJANGO_DST = {"MAX": ["1.9", "1.11.15", "2.0"], "MIN": ["1.11.15"]}

#NOX_CONFIG
# nox.options.stop_on_first_error = True
nox.options.envdir = ".fox/.cacheenv"
# nox.options.report = ".fox/reports/report.xml"
nox.options.error_on_external_run = False
# session_conf = {reuse_venv=True, external=True}
# nox.session.posargs.append(session_conf)


@nox.session(python=PYTHON_DST[NOX_CONFIG["PYTHON_VER"]], reuse_venv=True)
@nox.parametrize("django", DJANGO_DST[NOX_CONFIG["DJANGO_VER"]])
def build_envs(session, django):
    """Environment build coverage."""
    session.install(f"django=={django}")
    session.install("-r", "../test_requirements.txt")
    session.install("-r", "../dev_requirements.txt")


# use enclosed env (could be docker) python/django, include pep restrictions for you project
@nox.session(reuse_venv=True)
def peps(session): #pep it up
    # session.run("isort", "-rc .")
    # session.run("flake8", ".", external=True, *session.posargs)
    session.run("black", ".")
    # run all test from inside container (venv, dock)
    # test()


# use enclosed env (could be docker) python/django
@nox.session(reuse_venv=True)
def test(session):
    """Install the test tools"""
    # session.install("pytest")

    """Run your tests bellow"""
    session.run("pytest", external=True, *session.posargs)

    # create docs
    session.chdir("docs")
    session.run("sphinx-build", ".", "../docs/html", external=True)
