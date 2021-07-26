import json
import os

import kfp

search_path = os.path.dirname(os.path.abspath(__file__)) + "/../components"
component_store = kfp.components.ComponentStore(local_search_paths=[search_path])

dkube_serving_op = component_store.load_component("serving")
storage_op = component_store.load_component("storage")


@kfp.dsl.pipeline(
    name="multimodel-pl", description="sample multimodel pipeline with dkube components"
)
def multimodel_pipeline(model):


        list_models = kfp.dsl.ContainerOp(
            name="container-op",
            image="docker.io/ocdr/dkube-datascience-tf-cpu:v2.0.0-3",
            command="bash",
            arguments=["-c", "ls /model"])# add dkube model storage path here

        serving = dkube_serving_op(
            model=str(model),
            device="cpu",
            serving_image='{"image":"ocdr/inf-multimodel:latest"}',
        ).after(storage)
