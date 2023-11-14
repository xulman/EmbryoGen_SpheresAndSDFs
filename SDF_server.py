from grpc import server, RpcError
from concurrent import futures
import query_SDF_network_pb2 as SDF
import query_SDF_network_pb2_grpc
import numpy as np

from sdf_generator import sdf_gen

serverName = "SDF network"
serverPort = 10101

class TalkerService(query_SDF_network_pb2_grpc.ClientToSDFServicer):

    def init_SDF(self):
        self.network = sdf_gen.init_network()

    def get_SDF_answer(self, msg:SDF.QueryMsg) -> SDF.SDFvalue:
        ret_val = SDF.SDFvalue()
        ret_val.input.x = msg.x
        ret_val.input.y = msg.y
        ret_val.input.z = msg.z
        ret_val.input.t = msg.t
        for c in msg.latent_code_elements:
            ret_val.input.latent_code_elements.append(c)

        # latent code as numpy array
        code = [c for c in msg.latent_code_elements]
        code = np.array(code, dtype=np.float32)

        # output
        sdf_value = sdf_gen.get_sdf_value(msg.x, msg.y, msg.z, msg.t, code, self.network)
        print(f"processing request: {msg.x},{msg.y},{msg.z},{msg.t} -> {sdf_value}, using latent_code [{code[0]}...{code[-1]}]")

        ret_val.sdf_output = sdf_value
        return ret_val


    def queryOne(self, msg:SDF.QueryMsg, context):
        return self.get_SDF_answer(msg)

    def queryStream(self, msg_iterator:SDF.QueryMsg, context):
        print("multi-message")
        vals = []
        for msg in msg_iterator:
            vals.append( self.get_SDF_answer(msg) )
        return iter(vals)



try:
    serv = server( futures.ThreadPoolExecutor(2,serverName), maximum_concurrent_rpcs=5 )
    TS = TalkerService()
    TS.init_SDF()
    query_SDF_network_pb2_grpc.add_ClientToSDFServicer_to_server(TS,serv)
    serv.add_insecure_port('[::]:%d'%serverPort)

    serv.start()
    input("give me any input to stop this server...\n")
    serv.stop(5)

except RpcError as e:
    print("Some connection error, details follow:")
    print("==============")
    print(e)
    print("==============")
except Exception as e:
    print("Some general error, details follow:")
    print("==============")
    print(e)
    print("==============")
