from grpc import insecure_channel, RpcError
import query_SDF_network_pb2 as SDF
import query_SDF_network_pb2_grpc

class Talker:
    def __init__(self, url:str, using_this_latent_code:[float]):
        self.comm = query_SDF_network_pb2_grpc.ClientToSDFStub(insecure_channel(url))
        self.latent_code = using_this_latent_code.copy()

    def askOne(self, x:float, y:float, z:float, t:float) -> float:
        msg = SDF.QueryMsg()
        msg.x = x
        msg.y = y
        msg.z = z
        msg.t = t
        for c in self.latent_code:
            msg.latent_code_elements.append(c)
        dist = self.comm.queryOne(msg)
        return dist.sdf_output

    def askMulti(self, listOfxyzt:[[float,float,float,float]]) -> [float]:
        msgs = []
        for x,y,z,t in listOfxyzt:
            msg = SDF.QueryMsg()
            msg.x = x
            msg.y = y
            msg.z = z
            msg.t = t
            for c in self.latent_code:
                msg.latent_code_elements.append(c)
            msgs.append(msg)
        dists = self.comm.queryStream(iter(msgs))
        return [dist.sdf_output for dist in dists]



def main():
    try:
        latent_code = [489.1,293.2,759.3,837.4,59.5]
        talker = Talker("localhost:10101", latent_code)

        keepAsking = True
        while keepAsking:
            cli_str:str = input("type x,y,z,t comma or white space separated, 'q' to quit: ")
            keepAsking = cli_str != 'q'

            # try with whitespace first
            cli_items = cli_str.split()
            if len(cli_items) != 4:
                #print("trying commas")
                cli_items = cli_str.split(",")

            if len(cli_items) == 4:
                [x,y,z,t] = cli_items
                x = float(x)
                y = float(y)
                z = float(z)
                t = float(t)
                dist = talker.askOne(x,y,z,t)
                #dist = talker.askMulti([[x,y,z,t],[x,y,z,t],[x,y,z,t],[x,y,z,t],[x,y,z,t]])
                print(f"{x},{y},{z},{t} -> {dist}")

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
