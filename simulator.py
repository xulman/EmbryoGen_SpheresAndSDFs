from grpc import insecure_channel, RpcError
import buckets_with_graphics_pb2 as PROTOCOL
import buckets_with_graphics_pb2_grpc
from SDF_CLI_client import Talker as SDF


class Display:
    def greet_server(self) -> None:
        pass

    def create_graphics_batch(self, content_title:str) -> PROTOCOL.BatchOfGraphics:
        return PROTOCOL.BatchOfGraphics()

    def send_graphics_batch(self, the_batch:PROTOCOL.BatchOfGraphics, shouldResetGraphics:bool = False) -> None:
        pass


class BlenderDisplay(Display):
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

    def send_graphics_batch(self, the_batch:PROTOCOL.BatchOfGraphics, shouldResetGraphics:bool = False) -> None:
        if shouldResetGraphics:
            self.comm.replaceGraphics(iter([the_batch]))
        else:
            self.comm.addGraphics(iter([the_batch]))


class Sphere:
    def __init__(self, sphere_id, x,y,z, radius, color):
        self.id = sphere_id

        self.curr_x = x
        self.curr_y = y
        self.curr_z = z
        self.curr_r = radius
        self.color = color

        self.next_x = -1
        self.next_y = -1
        self.next_z = -1
        self.next_r = radius


    def update_current_pos(self):
        self.curr_x = self.next_x
        self.curr_y = self.next_y
        self.curr_z = self.next_z
        self.curr_r = self.next_r


    def update_future_pos(self, sdf_query_machine:SDF, current_timepoint:int):
        # ask the 'sdf_query_machine' and figure out the movement into the upcoming timepoint
        delta = sdf_query_machine.askOne(self.curr_x, self.curr_y, self.curr_z, current_timepoint+1);
        # maybe query around to get direction of the shift whose magnitude is |delta|

        # TODO: but for now, a fake translation to the right...
        self.next_x = self.curr_x + 1
        self.next_y = self.curr_y
        self.next_z = self.curr_z
        self.next_r = self.curr_r


class Cell:
    def __init__(self, using_this_latent_code:[float]):
        self.geometry = []
        self.geometry.append( Sphere(0,  0,10,0, 3, 0xFFFFFF) )
        self.geometry.append( Sphere(1,  3, 7,0, 3, 0xFF0000) )
        self.geometry.append( Sphere(2,  3, 3,0, 3, 0x00FF00) )
        self.geometry.append( Sphere(3,  0, 0,0, 3, 0x0000FF) )
        self.geometry.append( Sphere(4, -3, 3,0, 3, 0xFFFF00) )
        self.geometry.append( Sphere(5, -3, 7,0, 3, 0x00FFFF) )
        #self.geometry.append( Sphere(6, -3, 7,0, 3, 0xFF00FF) ) #example of another color
        self.version = 0 #aka time

        self.this_shape_latent_code = using_this_latent_code.copy()


    def report_curr_geometry(self, blender:Display) -> None:
        # iterates over the spheres and "beams" them to Blender for vizu
        print(f"Cell's current geometry, version = {self.version}:")
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
            sphParams.colorXRGB = s.color
            msg.spheres.append(sphParams)
        blender.send_graphics_batch(msg, self.version == 0)


    def update_pos(self, sdf_query_machine:SDF):
        # update each sphere, one by one
        for s in self.geometry:
            s.update_future_pos(sdf_query_machine, self.version)

        # potential self-checks after the spheres have (possibly) moved
        # ...maybe TODO, maybe just empty...

        # after the updated geometry is in a good shape, promote it to become the current geometry
        for s in self.geometry:
            s.update_current_pos()
        self.version += 1



def connect_to_Blender(session_name:str) -> Display:
    serverURL = "localhost:9083"
    blender_display = BlenderDisplay(serverURL, session_name)
    blender_display.greet_server()
    return blender_display


def connect_to_SDF_oraculum(da_latent_code:[float]) -> SDF:
    return SDF("localhost:10101", da_latent_code)


def report_SDF_cloud_surface(blender:Display, version:int, sdf_query_machine:SDF) -> None:
    # TODO don't know how zero-level set is read out
    # query the SDF at least once...
    sdf_query_machine.askOne(-1,-1,-1,version)
    #
    # make up a couple of points to have now something to show
    cloudPoint = []
    for q,w in [[x,y] for x in range(10) for y in range(10)]:
        cloudPoint.append([q,w,5])

    msg = blender.create_graphics_batch("cloud point")
    for x,y,z in cloudPoint:
        sphParams = PROTOCOL.SphereParameters()
        sphParams.centre.x = x
        sphParams.centre.y = y
        sphParams.centre.z = z+ 0.1*version
        sphParams.radius = 0.5
        sphParams.time = version
        sphParams.colorXRGB = 0xAAAAAA
        msg.spheres.append(sphParams)
    blender.send_graphics_batch(msg, version == 0)


def simulation(blender_display:Display, sdf_query_machine:SDF):
    cell = Cell( sdf_query_machine.latent_code ) # use the same cached latent_code
    cell.report_curr_geometry(blender_display)

    display_time = 0
    report_SDF_cloud_surface(blender_display, display_time, sdf_query_machine)

    key = ''
    while key != 'q':
        cell.update_pos(sdf_query_machine)
        cell.report_curr_geometry(blender_display)

        display_time += 1
        report_SDF_cloud_surface(blender_display, display_time, sdf_query_machine)

        key = input("press a key to advance, 'q' to quit: ")


try:
    display = Display() # sends nothing, requires no Blender
    #display = connect_to_Blender("default view")

    da_latent_code:[float] = [1,23,4,56]
    sdf_query_machine = connect_to_SDF_oraculum(da_latent_code)

    simulation(display, sdf_query_machine)

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
