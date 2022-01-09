# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
import networkx as nx
from .generate_testcases import rules
from nn_meter.builder.utils import builder_config as config


class FusionRuleTester:
    def __init__(self):
        self._rules = rules

    def _build_dep_dag(self):
        dag = nx.DiGraph()

        for name, cls in self._rules.items():
            dag.add_node(name)
            for dep in cls.deps:
                dag.add_edge(dep, name)

        self._dag = list(nx.topological_sort(dag))

    def generate(self):
        testcases = {}

        for name, cls in self._rules.items():
            testcases[name] = cls().save_testcase()

        return testcases

    def analyze(self, profile_results):
        self._build_dep_dag()
        result = {}

        for name in self._dag:
            if name not in profile_results:
                continue

            result[name] = {}
            rule_cls = self._rules[name]

            obey = True
            for dep, expect in rule_cls.deps.items():
                if result[dep]['obey'] != expect:
                    obey = False

            if obey:
                rule = rule_cls()
                rule.load_latency(profile_results[name])
                obey = rule.test()
                if config.get('DETAIL', 'ruletest'):
                    latency = {key: str(value) for key, value in rule.latency.items()}
                    result[name]['latency'] = latency

            result[name]['obey'] = obey

        return result
