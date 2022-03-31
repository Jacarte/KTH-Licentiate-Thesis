

from diagrams import Cluster, Diagram
from diagrams.aws.compute import ECS
from diagrams.aws.database import ElastiCache, RDS
from diagrams.aws.network import ELB
from diagrams.aws.network import Route53
from diagrams.programming.language import C
from diagrams.custom import Custom



ea = {
    "fontsize": "20",
}

ga = {
    "nodesep": "3.2",
    "pad": "1",
    "fontsize": "25",
}

ga2 = {

    "nodesep": "3.2",
    "pad": "30",
    "fontsize": "25",
    "labeljust": "b"
}

def method1():
    with Diagram("", show=False, outformat="pdf", graph_attr=ga, node_attr=ea, direction="TB", filename="Rq1", curvestyle="curved"):
        dns = Custom("program", "resources/program.png")
        lb = Custom("\nCROW", "resources/gear.png")

        with Cluster("\nStatic analysis\n of programs' population", graph_attr=ga2):
            svc_group = [Custom("\nWasm\nvariant n", "resources/wasm.png"),
                        Custom("\nWasm\nvariant 2", "resources/wasm.png"),
                        Custom("\nWasm\nvariant 1", "resources/wasm.png")]

        dns >> lb  >> svc_group
        #lb >> db_primary
        #svc_group >> memcached

def method2():
    with Diagram("", show=False, outformat="pdf", graph_attr=ga, node_attr=ea, direction="TB", filename="Rq2", curvestyle="curved"):
        dns = Custom("program", "resources/program.png")
        lb = Custom("\nCROW", "resources/gear.png")

        with Cluster("\nPrograms' population", graph_attr=ga2):
            a1 = Custom("\nWasm\nvariant n", "resources/wasm.png")
            a2 = Custom("\nWasm\nvariant 2", "resources/wasm.png")
            a3 = Custom("\nWasm\nvariant 1", "resources/wasm.png")

            gen_group = [a1,a2, a3]

        with Cluster("\nDynamic analysis", graph_attr=ga2):

            t1 = Custom("\nExecution\ntrace n", "resources/trace.png")

            tt1 = Custom("\nExecution\ntime n", "resources/time.png")
            
            t2 = Custom("\nExecution\ntrace 2", "resources/trace.png")
            tt2 = Custom("\nExecution\ntime 2", "resources/time.png")

            t3 = Custom("\nExecution\ntrace 1", "resources/trace.png")


            tt3 = Custom("\nExecution\ntime 1", "resources/time.png")

        #t1 - t2
        #t2 - t3
        #t3 - t1

        #tt1 - tt2 
        #tt2 - tt3
        #tt3 - tt1
        
        dns >> lb  >> gen_group
        a1 >> t1
        a2 >> t2
        a3 >> t3

        a1 >> tt1
        a2 >> tt2
        a3 >> tt3
        #lb >> db_primary
        #svc_group >> memcached


def method3():
    with Diagram("", show=False, outformat="pdf", graph_attr=ga, node_attr=ea, direction="TB", filename="Rq3", curvestyle="curved"):
        dns = Custom("program", "resources/program.png")
        lb = Custom("\nCROW", "resources/gear.png")

        with Cluster("\nPrograms' population", graph_attr=ga2):
            a1 = Custom("\nWasm\nvariant n", "resources/wasm.png")
            a2 = Custom("\nWasm\nvariant 2", "resources/wasm.png")
            a3 = Custom("\nWasm\nvariant 1", "resources/wasm.png")

            gen_group = [a1,a2, a3]

        #with Cluster("\nDynamic analysis", graph_attr=ga2):


        with Cluster("\nMultivariant creation", graph_attr=ga2):
            multivariant = Custom("\nMultivariant\nbinary", "resources/wasm.png")
        
        original = Custom("\nOriginal\nbinary", "resources/wasm.png")


        with Cluster("\nExecution time\nanalysis", graph_attr=ga2):

            tt1 = Custom("\nExecution\ntime", "resources/time.png")
            tt1o = Custom("\nExecution\ntime", "resources/time.png")

        dns >> lb  >> gen_group
        a1 >> multivariant
        a2 >> multivariant
        a3 >> multivariant

        dns >> original

        multivariant >> tt1
        original >> tt1o
        #lb >> db_primary
        #svc_group >> memcached



if __name__ == "__main__":
    method1()
    method2()
    method3()