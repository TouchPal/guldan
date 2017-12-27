# -*- coding: utf-8 -*-

class NestedBlueprint(object):
    def __init__(self, blueprint, prefix):
        super(NestedBlueprint, self).__init__()
        self.blueprint = blueprint
        self.prefix = '/' + prefix

    def route(self, rule, **options):
        rule = self.prefix + rule
        return self.blueprint.route(rule, **options)
