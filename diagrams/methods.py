

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import ECS
from diagrams.aws.database import ElastiCache, RDS
from diagrams.aws.network import ELB
from diagrams.aws.network import Route53
from diagrams.programming.language import C
from diagrams.custom import Custom



na = {
    "fontsize": "20",
    "width": "1.1"
}

ea = {
    "penwidth": "6"
}
ga = {
    "nodesep": "1.5",
    "pad": "1",
    "fontsize": "25",
    "ranksep": "1.5"
}

ga2 = {

    "nodesep": "1.1",
    "pad": "30",
    "fontsize": "25",
    "labeljust": "b",
    "ranksep": "0.1"
}

def method1():
    gat = dict(**ga)
    gat['ranksep'] = "1.2"
    gat['nodesep'] = "0.3"
    with Diagram("", show=False, outformat="pdf", graph_attr=gat, node_attr=na, edge_attr=ea, direction="LR", filename="Rq1", curvestyle="curved"):
        lb = Custom("\nCROW", "resources/gear.png")
        lb2 = Custom("\nCROW ", "resources/gear.png")


        with Cluster("\nCorpus", graph_attr=ga2):
            dns = Custom("program1", "resources/program.png")
            p2 = Custom("program2","resources/program.png")
        

        with Cluster("\nCorpus's population", graph_attr=ga2):
            with Cluster("\nProgram1's population", graph_attr=ga2):

                v1 = Custom("\nWasm\nvariant n", "resources/wasm.png")
                v2 = Custom("\nWasm\nvariant 2", "resources/wasm.png")

            with Cluster("\nProgram2's population ", graph_attr=ga2):

                v3 = Custom("\nWasm\nvariant 1", "resources/wasm.png")
            
        with Cluster("\nCorpus's unique population", graph_attr=ga2):

            with Cluster("\nProgram1's unique\n population", graph_attr=ga2):

                u1 = Custom("\nWasm\nvariant n", "resources/wasm.png")
                
            with Cluster("\nProgram2's unique\n population", graph_attr=ga2):
    
                u2 = Custom("\nWasm\nvariant 1", "resources/wasm.png")
                            
        
        dns >> lb  
        lb >> v1
        lb >> v2
        p2 >> lb2
        lb2 >> v3

        v1 >> u1
        v3 >> u2

        #lb >> db_primary
        #svc_group >> memcached

def method2():

    gat = dict(**ga)
    gat['ranksep'] = "1.2"
    gat['nodesep'] = "0.3"
    with Diagram("", show=False, outformat="pdf", graph_attr=gat,  node_attr=na, edge_attr=ea, direction="LR", filename="Rq2", curvestyle="curved"):
        dns = Custom("\nprogram", "resources/program.png")
        lb = Custom("\nCROW", "resources/gear.png")

        with Cluster("\n  Programs' population  ", graph_attr=ga2, ):
            a1 = Custom("\n\nWasm\nvariant n", "resources/wasm.png")
            a2 = Custom("\n\nWasm\nvariant 2", "resources/wasm.png")
            a3 = Custom("\n\nWasm\nvariant 1", "resources/wasm.png")

            gen_group = [a1,a2, a3]

        with Cluster("\nDynamic analysis", graph_attr=ga2, direction="LR"):
            
            with Cluster("A", graph_attr=dict(**ga2, pencolor="transparent", bgcolor="transparent", fontcolor="transparent")):
                t1 = Custom("\nExecution\ntrace n", "resources/trace.png")
                #tt1 = Custom("\nExecution\ntime n", "resources/time.png")
            
                t2 = Custom("\nExecution\ntrace 2", "resources/trace.png")
                #tt2 = Custom("\nExecution\ntime 2", "resources/time.png")

                t3 = Custom("\nExecution\ntrace 1", "resources/trace.png")
                #tt3 = Custom("\nExecution\ntime 1", "resources/time.png")


            with Cluster("T", graph_attr=dict(**ga2, pencolor="transparent", bgcolor="transparent", fontcolor="transparent"), direction="LR"):
                
                #t1 = Custom("\nExecution\ntrace n", "resources/trace.png")
                tt1 = Custom("\nExecution\ntime n", "resources/time.png")
            
                #t2 = Custom("\nExecution\ntrace 2", "resources/trace.png")
                tt2 = Custom("\nExecution\ntime 2", "resources/time.png")

                #t3 = Custom("\nExecution\ntrace 1", "resources/trace.png")
                tt3 = Custom("\nExecution\ntime 1", "resources/time.png")

        #t1 - t2
        #t2 - t3
        #t3 - t1

        #tt1 - tt2 
        #tt2 - tt3
        #tt3 - tt1
        
        dns >> lb  >> gen_group
        a1 >> Edge(label="Execute", fontsize="23") >> t1
        a2 >> Edge(label="Execute", fontsize="23") >> t2
        a3 >> Edge(label="Execute", fontsize="23") >> t3

        t1 - Edge(color='transparent') - tt1
        t2 - Edge(color='transparent') - tt2
        t2 - Edge(color='transparent') - tt2

        #a1 >> tt1
        #a2 >> tt2
        #a3 >> tt3
        #lb >> db_primary
        #svc_group >> memcached


def method3():

    gat = dict(**ga)
    gat['ranksep'] = "1.2"
    gat['nodesep'] = "0.3"

    with Diagram("", show=False, outformat="pdf", graph_attr=gat,  node_attr=na, edge_attr=ea, direction="LR", filename="Rq3", curvestyle="curved"):
        dns = Custom("\nprogram", "resources/program.png")
        lb = Custom("\nCROW", "resources/gear.png")

        with Cluster("\nPrograms' population", graph_attr=ga2, direction="TB"):
            a1 = Custom("\n\nWasm\nvariant n", "resources/wasm.png")
            a2 = Custom("\n\nWasm\nvariant 2", "resources/wasm.png")
            a3 = Custom("\n\nWasm\nvariant 1", "resources/wasm.png")

            gen_group = [a1,a2, a3]

        #with Cluster("\nDynamic analysis", graph_attr=ga2):


        with Cluster("\nMultivariant creation\n\n\n", graph_attr=ga2):
            multivariant = Custom("\n\nMultivariant\nbinary", "resources/wasm.png")
        
        original = Custom("\n\nOriginal\nbinary", "resources/wasm.png")


        with Cluster("\n    Execution time   \nanalysis", graph_attr=ga2):

            tt1 = Custom("\n\n\nCloud execution\ntime", "resources/time.png")
            tt1o = Custom("\n\n\nCloud execution\ntime", "resources/time.png")

        dns >> original
        dns >> lb  >> gen_group
        a1 >> multivariant
        a2 >> multivariant
        a3 >> multivariant


        multivariant >> Edge(label="Execute\n\n\n", fontsize="23") >> tt1
        original >> Edge(label="Execute", fontsize="23") >> tt1o
        #lb >> db_primary
        #svc_group >> memcached



def wasm_workflow():

    gat = dict(**ga)
    gat['ranksep'] = "1.2"
    gat['nodesep'] = "0.3"

    with Diagram("", show=False, outformat="pdf", graph_attr=gat,  node_attr=na, edge_attr=ea, direction="LR", filename="wasm_workflow", curvestyle="curved"):
        
        dns = Custom("\nprogram", "resources/program.png")
        lb = Custom("\nWasm Compiler", "resources/gear.png")
        wasm = Custom("\n\nWasm binary", "resources/wasm.png")
        browser = Custom("\n\n", "resources/screenshot_game.png")
        browser._height = 15

        #multivariant >> Edge(label="Execute\n\n\n", fontsize="23") >> tt1
        #original >> Edge(label="Execute", fontsize="23") >> tt1o
        
        
        dns >> lb >> wasm 
        wasm >> browser
        #lb >> db_primary
        #svc_group >> memcached



if __name__ == "__main__":
    na['width'] = "1.3"
    method1()
    na['width'] = "1.4"
    method2()
    na['width'] = "1.6"
    method3()