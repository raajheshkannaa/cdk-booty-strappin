#!/usr/bin/env python3

from aws_cdk import core

from stacks.booty_strappin_stack import BootyStrappinStack


app = core.App()
BootyStrappinStack(app, "booty-strappin")

app.synth()
