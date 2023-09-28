from grpc import insecure_channel, RpcError
import query_SDF_network_pb2 as SDF
import query_SDF_network_pb2_grpc

class Talker:
    def __init__(self, url:str, latent_code:int):
        self.comm = query_SDF_network_pb2_grpc.ClientToSDFStub(insecure_channel(url))
        self.latent_code = latent_code

    def askOne(self, x:float, y:float, z:float) -> float:
        msg = SDF.QueryMsg()
        msg.x = x
        msg.y = y
        msg.z = z
        msg.latent_code = self.latent_code
        dist = self.comm.queryOne(msg)
        return dist.sdf_output

    def askMulti(self, listOfTripplets:[[float,float,float]]) -> [float]:
        msgs = []
        for x,y,z in listOfTripplets:
            msg = SDF.QueryMsg()
            msg.x = x
            msg.y = y
            msg.z = z
            msg.latent_code = self.latent_code
            msgs.append(msg)
        dists = self.comm.queryStream(iter(msgs))
        return [dist.sdf_output for dist in dists]



def main():
    try:
        talker = Talker("localhost:10101", 48929375983759)

        keepAsking = True
        while keepAsking:
            cli_str:str = input("type x,y,z comma or white space separated, 'q' to quit: ")
            keepAsking = cli_str != 'q'

            # try with whitespace first
            cli_items = cli_str.split()
            if len(cli_items) != 3:
                #print("trying commas")
                cli_items = cli_str.split(",")

            if len(cli_items) == 3:
                [x,y,z] = cli_items
                x = float(x)
                y = float(y)
                z = float(z)
                dist = talker.askOne(x,y,z)
                #dist = talker.askMulti([[x,y,z],[x,y,z],[x,y,z],[x,y,z],[x,y,z]])
                print(f"{x},{y},{z} -> {dist}")

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

if __name__ == '__main__':
    main()
