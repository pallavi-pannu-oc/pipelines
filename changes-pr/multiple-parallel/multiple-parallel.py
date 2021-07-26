import kfp

@kfp.dsl.pipeline(
    name='Parallel stages pipeline',
    description='An example pipeline to launch number of stages in parallel'
)
def parallel_pipeline(count):
    for i in range(count):
        op = kfp.dsl.ContainerOp(name='parallel',image="alpine",command=["sleep", "5s"])

