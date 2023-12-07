from grpc import insecure_channel, RpcError
import query_SDF_network_pb2 as SDF
import query_SDF_network_pb2_grpc
import numpy as np

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

    def askBox(self, xmin,xmax, ymin,ymax, zmin,zmax, t, delta) -> [float]:
        msg = SDF.QueryBox()
        msg.x_min = xmin
        msg.x_max = xmax
        msg.y_min = ymin
        msg.y_max = ymax
        msg.z_min = zmin
        msg.z_max = zmax
        msg.t = t
        msg.xyz_max_delta = delta
        for c in self.latent_code:
            msg.latent_code_elements.append(c)
        return self.comm.queryBox(msg)


def assureBound(val:float) -> float:
    return max(-1.0, min(val, 1.0))

def sidesPair(centre:float, sideStep:float) -> tuple[float,float]:
    return assureBound(centre-sideStep),assureBound(centre+sideStep)


def main():
    try:
        latent_code = np.random.normal(0.0, 0.001, 
                                       size=(64)).astype(np.float32).tolist()
        # override with one fixed code
        latent_code = [-2.3986192e-03,-1.4570372e-03,-8.4780599e-04,-7.6979552e-05,
                        3.5935736e-04, 1.3442944e-03, 2.9896368e-05,-1.5221010e-03,
                       -6.4682774e-04,-3.6120944e-04,-6.9270295e-04,-3.1744636e-04,
                        5.4595369e-04,-1.6224104e-03, 1.4707424e-05, 1.0374220e-03,
                        6.7014078e-04,-9.5641374e-04,-7.4461532e-05,-9.4221265e-04,
                        5.0656375e-04, 1.1499496e-03, 4.9177761e-04, 1.5869462e-04,
                        1.4416642e-03,-2.7567349e-04, 1.4699948e-03, 4.6477004e-04,
                        1.7223452e-03,-6.5159419e-04, 3.5255714e-04,-2.9482346e-05,
                       -2.2739265e-04,-3.7028556e-04,-5.1660632e-04,-3.6994013e-04,
                       -5.1494868e-04,-4.4057367e-04, 6.4848794e-04,-7.0317026e-04,
                        4.4765539e-04, 3.3289418e-04,-1.2737118e-03,-6.4152142e-04,
                        5.1582122e-04,-8.6294074e-04, 3.9858691e-04,-2.1431916e-03,
                        3.1408685e-04,-1.0366687e-03,-1.3511841e-03, 4.6981624e-04,
                        1.5995891e-03, 1.2120566e-03,-7.0597831e-04, 3.1308763e-04,
                        7.9303415e-04, 9.5366704e-04,-3.2047727e-05, 5.2187120e-04,
                        4.8843864e-04,-3.3936172e-04,-1.4731282e-04, 1.0076733e-03]

        talker = Talker("localhost:10101", latent_code)

        keepAsking = True
        while keepAsking:
            cli_str:str = input("type x,y,z,t comma or white space separated, 'q' to quit: ")
            keepAsking = cli_str != 'q'

            # try with commas first
            cli_items = cli_str.split(",")
            if len(cli_items) != 4:
                # try with whitespace second
                cli_items = cli_str.split()

            if len(cli_items) == 4:
                [x,y,z,t] = cli_items
                x = float(x)
                y = float(y)
                z = float(z)
                t = float(t)
                dist = talker.askOne(x,y,z,t)
                #dist = talker.askMulti([[x,y,z,t],[x,y,z,t],[x,y,z,t],[x,y,z,t],[x,y,z,t]])
                #mix,max = sidesPair(x,0.2)
                #miy,may = sidesPair(y,0.1)
                #miz,maz = sidesPair(z,0.05)
                #dist = talker.askBox( mix,max,miy,may,miz,maz, t, 0.105)
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
