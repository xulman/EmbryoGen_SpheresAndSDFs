from grpc import server, RpcError
from concurrent import futures
import query_SDF_network_pb2 as SDF
import query_SDF_network_pb2_grpc

serverName = "SDF network"
serverPort = 10101

class TalkerService(query_SDF_network_pb2_grpc.ClientToSDFServicer):

    def get_SDF_answer(self, msg:SDF.QueryMsg) -> SDF.SDFvalue:
        ret_val = SDF.SDFvalue()
        ret_val.input.x = msg.x
        ret_val.input.y = msg.y
        ret_val.input.z = msg.z
        ret_val.input.latent_code = msg.latent_code

        ############ fix this ############
        # input
        x = msg.x
        y = msg.y
        z = msg.z
        code = msg.latent_code
        #
        # output
        sdf_value = x+y+z
        print(f"processing request: {x},{y},{z},{code} -> {sdf_value}")
        ############ fix this ############

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
    query_SDF_network_pb2_grpc.add_ClientToSDFServicer_to_server(TalkerService(),serv)
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
