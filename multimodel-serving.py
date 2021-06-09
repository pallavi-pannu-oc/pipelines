import json
import os

import kfp

search_path = os.path.dirname(os.path.abspath(__file__)) + "/../components"
component_store = kfp.components.ComponentStore(local_search_paths=[search_path])


storage_op = component_store.load_component("storage")
dkube_serving_op = component_store.load_component("serving")

@kfp.dsl.pipeline(
    name='multimodel-pl',
    description='sample multimodel pipeline with dkube components'
)
def multimodel_pipeline(model):
  
  model_volume = json.dumps(["{{workflow.uid}}-model@model://" + str(model)])
  storage = storage_op("export", namespace="kubeflow", input_volumes=model_volume)
  
  list_models = kfp.dsl.ContainerOp(name="list-models",image="alpine",command="bash",arguments=["-c", "ls /model"],
                                    pvolumes={"/model": kfp.dsl.PipelineVolume(pvc="{{workflow.uid}}-model")}})
  
  serving = dkube_serving_op(model = str(model) , device='cpu', serving_image='{"image":"ocdr/inf-multimodel:latest"}')
