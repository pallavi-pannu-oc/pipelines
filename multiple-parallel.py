import kfp.compiler as compiler
import kfp
import tempfile
import kfp.components as kfplc
import json,os
import datetime
import random
import string

from dkube.sdk import *
from dkube.pipelines import *

from kubernetes.client import V1Affinity, V1NodeSelector, V1NodeSelectorRequirement, V1NodeSelectorTerm, \
  V1NodeAffinity, V1Toleration

def generate(name):
    timestamp = datetime.datetime.now().strftime("%H%M%S")
    return "{}-{}{}".format(
        name, timestamp, "".join([random.choice(string.digits) for n in range(4)])
    )
name = generate("multiple-parallel")

@kfp.dsl.pipeline(
    name='Parallel stages pipeline',
    description='An example pipeline to launch number of stages in parallel'
)
def parallel_pipeline():
    count = 22
    for i in range(count):
        op = kfp.dsl.ContainerOp(name='parallel',
            image="ocdr/d3-datascience-tf-cpu:v1.14",
            command=["sleep", "5s"])
        op.add_toleration(V1Toleration( effect='NoSchedule', key='node.kubernetes.io/unschedulable', operator='Exists'))


token = os.getenv("DKUBE_USER_ACCESS_TOKEN")
client = kfp.Client(existing_token=token)
f = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
kfp.compiler.Compiler().compile(parallel_pipeline, f.name)
client.upload_pipeline(f.name, pipeline_name=name)
client.create_run_from_pipeline_package(f.name, {}, name)


