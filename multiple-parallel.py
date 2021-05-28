import kfp.compiler as compiler
import kfp
import kfp.components as kfplc
import json,os

from dkube.sdk import *
from dkube.pipelines import *

from kubernetes.client import V1Affinity, V1NodeSelector, V1NodeSelectorRequirement, V1NodeSelectorTerm, \
  V1NodeAffinity, V1Toleration

@kfp.dsl.pipeline(
    name='Parallel stages pipeline',
    description='An example pipeline to launch number of stages in parallel'
)
def parallel_pipeline():
    count = 22
    for i in range(count):
        op = kfp.dsl.ContainerOp(name='parallel',
            image="ocdr/d3-datascience-tf-cpu:v1.14",
            command=["sleep", "1m"])

        affinity = V1Affinity(
            node_affinity=V1NodeAffinity(
              required_during_scheduling_ignored_during_execution=V1NodeSelector(
                node_selector_terms=[V1NodeSelectorTerm(
                  match_expressions=[V1NodeSelectorRequirement(
                    key='alpha.eksctl.io/instance-id', operator='In', values=['i-051a46d2261ed8733'])])])))
        op.add_affinity(affinity)
        op.add_toleration(V1Toleration( effect='NoSchedule', key='node.kubernetes.io/unschedulable', operator='Exists'))

compiler.Compiler().compile(parallel_pipeline, __file__ + '.tar.gz')
token = os.getenv("DKUBE_USER_ACCESS_TOKEN")
client = kfp.Client(existing_token=token)
client.upload_pipeline("multiple-parallel.py.tar.gz")

