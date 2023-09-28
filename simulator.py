from grpc import insecure_channel, RpcError
import buckets_with_graphics_pb2 as PROTOCOL
import buckets_with_graphics_pb2_grpc


class BlenderDisplay:
    def __init__(self, url, session_name):
        self.blender_server = url
        self.session_name = session_name
        self.comm = buckets_with_graphics_pb2_grpc.ClientToServerStub( insecure_channel(url) )

    def greet_server(self) -> None:
        self.clientURL = "no callback"
        self.clientName = "spheres tracking SDF_of_t"
        #
        clientGreeting = PROTOCOL.ClientHello()
        clientGreeting.clientID.clientName = self.clientName
        clientGreeting.returnURL = self.clientURL
        self.comm.introduceClient(clientGreeting)

    def create_graphics_batch(self, content_title:str) -> PROTOCOL.BatchOfGraphics:
        msg = PROTOCOL.BatchOfGraphics()
        msg.clientID.clientName = self.clientName
        msg.collectionName = self.session_name
        msg.dataName = content_title
        msg.dataID = 1
        return msg

    def send_graphics_batch(self, the_batch:PROTOCOL.BatchOfGraphics) -> None:
        self.comm.addGraphics(iter([the_batch]))


class Sphere:
    def __init__(self, sphere_id, x,y,z, radius):
        self.id = sphere_id

        self.curr_x = x
        self.curr_y = y
        self.curr_z = z
        self.curr_r = radius

        self.next_x = -1
        self.next_y = -1
        self.next_z = -1
        self.next_r = radius


    def update_current_pos(self):
        self.curr_x = self.next_x
        self.curr_y = self.next_y
        self.curr_z = self.next_z
        self.curr_r = self.next_r


    def update_future_pos(self, sdf_query_machine, latent_code):
        # TODO, for now a fake translation to the right...
        # normally, however, it should ask the 'sdf_query_machine' and figure out the movement
        self.next_x = self.curr_x + 1
        self.next_y = self.curr_y
        self.next_z = self.curr_z
        self.next_r = self.curr_r


class Cell:
    def __init__(self):
        self.geometry = []
        self.geometry.append( Sphere(0,  0,10,0, 3) )
        self.geometry.append( Sphere(1,  3, 7,0, 3) )
        self.geometry.append( Sphere(2,  3, 3,0, 3) )
        self.geometry.append( Sphere(3,  0, 0,0, 3) )
        self.geometry.append( Sphere(4, -3, 3,0, 3) )
        self.geometry.append( Sphere(5, -3, 7,0, 3) )
        self.version = 0 #aka time

        self.this_shape_latent_code = 123456


    def report_curr_geometry(self, blender:BlenderDisplay) -> None:
        # iterates over the spheres and "beams" them to Blender for vizu
        print("Cell's current geometry:")
        msg = blender.create_graphics_batch("cell geometry")
        for s in self.geometry:
            print(f"  Sphere {s.id} now at {s.curr_x}, {s.curr_y}, {s.curr_z}, and with radius {s.curr_r}")
            #
            sphParams = PROTOCOL.SphereParameters()
            sphParams.centre.x = s.curr_x
            sphParams.centre.y = s.curr_y
            sphParams.centre.z = s.curr_z
            sphParams.radius = s.curr_r
            sphParams.time = self.version
            sphParams.colorIdx = s.id
            msg.spheres.append(sphParams)
        blender.send_graphics_batch(msg)
        self.version += 1


    def update_pos(self, sdf_query_machine):
        # update each sphere, one by one
        for s in self.geometry:
            s.update_future_pos(sdf_query_machine, self.this_shape_latent_code)

        # potential self-checks after the spheres have (possibly) moved
        # ...maybe TODO, maybe just empty...

        # after the updated geometry is in a good shape, promote it to become the current geometry
        for s in self.geometry:
            s.update_current_pos()



def connect_to_Blender(session_name:str) -> BlenderDisplay:
    serverURL = "localhost:9083"
    blender_display = BlenderDisplay(serverURL, session_name)
    blender_display.greet_server()
    return blender_display


def connect_to_SDF_oraculum() -> None:
    return None


def simulation(blender_display:BlenderDisplay, sdf_query_machine):
    cell = Cell()
    cell.report_curr_geometry(blender_display)

    key = ''
    while key != 'q':
         cell.update_pos(sdf_query_machine)
         cell.report_curr_geometry(blender_display)

         key = input("press a key to advance, 'q' to quit: ")


try:
    blender_display = connect_to_Blender("default view")
    sdf_query_machine = connect_to_SDF_oraculum()
    simulation(blender_display, sdf_query_machine)

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

print("done.")
