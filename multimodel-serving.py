import json
import os

import kfp

search_path = os.path.dirname(os.path.abspath(__file__)) + "/../components"
component_store = kfp.components.ComponentStore(local_search_paths=[search_path])

dkube_serving_op = component_store.load_component("serving")

@kfp.dsl.pipeline(
    name='multimodel-pl',
    description='sample multimodel pipeline with dkube components'
)
def multimodel_pipeline(model,model_mount_path):
    
        list_models = kfp.dsl.ContainerOp(name="list-models",image="alpine",command="bash",arguments=["-c", "ls /model_mount_path"]
        serving = dkube_serving_op(model = str(model) , device='cpu', serving_image='{"image":"ocdr/inf-multimodel:latest"}')
