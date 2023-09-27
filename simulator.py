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
        self.next_x += 1


class Cell:
    def __init__(self):
        self.geometry = []
        self.geometry.append( Sphere(0,  0,10,0, 3) )
        self.geometry.append( Sphere(1,  3, 7,0, 3) )
        self.geometry.append( Sphere(2,  3, 3,0, 3) )
        self.geometry.append( Sphere(3,  0, 0,0, 3) )
        self.geometry.append( Sphere(4, -3, 3,0, 3) )
        self.geometry.append( Sphere(5, -3, 7,0, 3) )

        self.shape_latent_code = 123456


    def report_curr_geometry(self, blender_server):
        # iterates over the spheres and "beams" them to Blender for vizu

        # for now only, report on the console (TODO)
        print("Cell's current geometry:")
        for s in self.geometry:
            print(f"  Sphere {s.id} now at {s.curr_x}, {s.curr_y}, {s.curr_z}")
        pass


    def update_pos(self, sdf_query_machine):
        # update each sphere, one by one
        for s in self.geometry:
            s.update_future_pos(sdf_query_machine, self.latent_code)

        # potential self-checks after the spheres have (possibly) moved
        # ...maybe TODO, maybe just empty...

        # after the updated geometry is in a good shape, promote it to become the current geometry
        for s in self.geometry:
            s.update_current_pos()



cell = Cell()
cell.report_curr_geometry()
