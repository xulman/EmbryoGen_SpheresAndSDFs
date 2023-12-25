from grpc import server, RpcError
from concurrent import futures
import query_SDF_network_pb2 as SDF
import query_SDF_network_pb2_grpc
import numpy as np
import time

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

        # get latent code as numpy array
        code = [c for c in msg.latent_code_elements]
        code = np.array(code, dtype=np.float32)

        # get generator output
        sdf_value = sdf_gen.get_sdf_value(msg.x, msg.y, msg.z, msg.t, code, self.network)
        print(f"processing request: {msg.x},{msg.y},{msg.z},{msg.t} -> {sdf_value}, using latent_code [{code[0]}...{code[-1]}]")

        ret_val.sdf_output = sdf_value
        return ret_val


    def queryOne(self, msg:SDF.QueryMsg, context):
        return self.get_SDF_answer(msg)

    def queryStream(self, msg_iterator:SDF.QueryMsg, context):
        vals = []
        time_start = time.time()
        for msg in msg_iterator:
            vals.append( self.get_SDF_answer(msg) )
        time_stop = time.time()
        print(f"multi-message of {len(vals)} msgs took {time_stop-time_start} seconds")
        return iter(vals)


    def queryBox(self, msg:SDF.QueryBox, context):
        print("box-message")

        answer = SDF.SDFboxValues()
        for c in msg.latent_code_elements:
            answer.latent_code_elements.append(c)

        steps_x = msg.xyz_intermediate_steps if msg.HasField('xyz_intermediate_steps') \
               else self.getIntermediateStepsForIntervalWithDelta(msg.x_min, msg.x_max, msg.xyz_max_delta)
        answer.x_start, answer.x_delta, answer.x_num_values = self.getStartDeltaNumValues(msg.x_min, msg.x_max, steps_x)

        steps_y = msg.xyz_intermediate_steps if msg.HasField('xyz_intermediate_steps') \
               else self.getIntermediateStepsForIntervalWithDelta(msg.y_min, msg.y_max, msg.xyz_max_delta)
        answer.y_start, answer.y_delta, answer.y_num_values = self.getStartDeltaNumValues(msg.y_min, msg.y_max, steps_y)

        steps_z = msg.xyz_intermediate_steps if msg.HasField('xyz_intermediate_steps') \
               else self.getIntermediateStepsForIntervalWithDelta(msg.z_min, msg.z_max, msg.xyz_max_delta)
        answer.z_start, answer.z_delta, answer.z_num_values = self.getStartDeltaNumValues(msg.z_min, msg.z_max, steps_z)
        answer.t = msg.t
        
        # steps is non-inclusive (i.e., not counting first and last value)
        # X_num_values is inclusive
        # X_num_values = steps+2 (+2 for the edge/side values)

        '''
        xyzt_in_this_order = list()
        for iz in range(answer.z_num_values):
            z = answer.z_start + iz*answer.z_delta

            for iy in range(answer.y_num_values):
                y = answer.y_start + iy*answer.y_delta

                for ix in range(answer.x_num_values):
                    x = answer.x_start + ix*answer.x_delta

                    xyzt_in_this_order.append([x,y,z,answer.t])
        '''
                    
        # prepare network inputs of shape [n, 4]
        x = np.linspace(msg.x_min, msg.x_max, num=answer.x_num_values, endpoint=True)
        y = np.linspace(msg.y_min, msg.y_max, num=answer.y_num_values, endpoint=True)
        z = np.linspace(msg.z_min, msg.z_max, num=answer.z_num_values, endpoint=True)
        xyz_coords = np.stack(np.meshgrid(x, y, z, indexing='ij'), axis=-1)
        xyz_coords = xyz_coords.reshape(-1, xyz_coords.shape[-1])
        t_coords = np.tile(msg.t, (xyz_coords.shape[0], 1))
        xyzt_coords = np.append(xyz_coords, t_coords, axis=1).astype(np.float32)
        
        # get latent code as numpy array
        code = [c for c in msg.latent_code_elements]
        code = np.array(code, dtype=np.float32)
        
        # get generator output
        sdf_values = sdf_gen.get_sdf_values(xyzt_coords, code, self.network)
        
        '''
        for x,y,z,t in xyzt_in_this_order:
            print(f"positions: {x},{y},{z}")
            answer.sdf_outputs.append(x+y)
        '''
        
        ############ Can this be done more efficiently? ############
        # prepare the answer    
        for i in range(xyzt_coords.shape[0]):
            # printing the values results in a considerable slowdown
            '''
            print(f'position [{xyzt_coords[i, 0]:.6f}, '
                  f'{xyzt_coords[i, 1]:.6f}, '
                  f'{xyzt_coords[i, 2]:.6f}] '
                  f'@ {sdf_values[i]:.6f}')
            '''
            answer.sdf_outputs.append(sdf_values[i])

        return answer


    def getIntermediateStepsForIntervalWithDelta(self, min:float, max:float, delta:float) -> int:
        """Return the number of intermediate steps when sampling 'min' to 'max' in not more than 'delta'-long jumps"""
        if max <= min:
            return 0

        full_dist = max - min
        steps = int(full_dist // delta)
        # make one less if the distance is an integeer multiple of the delta
        steps -= 1 if steps*delta == full_dist else 0
        return steps

    def getStartDeltaNumValues(self, min:float, max:float, steps:int) -> [float,float,int]:
        """Returns starting point, step size and number of steps needed to reach the 'max' from 'min' using intermediate 'steps'"""
        delta = (max-min) / (1.0+steps)
        return min,delta,steps+2
        #                     +2 for the edge/side values


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
