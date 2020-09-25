import numpy as np
import cv2
from tqdm import tqdm
import argparse
import sys

#--------------------------------------------------------------------------------------
#---- Tiny code to generate various Julia fractals
#---- For a given function such as f=z^2+c or f=z^3+c the Julia set is defined on
#---- a complex grid minx < re(z) < maxx && miny < im(z) < maxy. The color is assigned
#---- depending on the number of iterations required to exceed a specified value zmax.
#--------------------------------------------------------------------------------------

class FunctionList:
    """
    Class of complex functions for generating fractals
    """

    @staticmethod
    def func_z2pc(z: complex, c: complex):
        return z * z + c

    @staticmethod
    def func_z3pc(z: complex, c: complex):
        return z * z * z+ c

#--------------------------------------------------------------------------------------

class FractalJulia:

    def __generate_color_scheme1__(self, value):
        h = value % 360
        X = 1 - abs((h / 60) % 2 - 1)
        color = [0,0,0]

        if h >= 0 and h < 60: color = [1, X, 0]
        elif h >= 60 and h < 120: color = [X, 1, 0]
        elif h >= 120 and h < 180: color = [0, 1, X]
        elif h >= 180 and h < 240: color = [0, X, 1]
        elif h >= 240 and h < 300: color = [X, 0, 1]
        elif h >= 300 and h < 360: color = [1, 0, X]

        return color


    def __generate_color_scheme2__(self, value):
        i = (value + 1) / self.iterations * 2
        if i > 1: i = 1

        return [i, i, i]

    def __generate_color__(self, value):
        if self.scheme == 1: return self.__generate_color_scheme1__(value)
        elif self.scheme == 2: return self.__generate_color_scheme2__(value)
        else: self.__generate_color_scheme2__(value)

    def __init__(self, image_size: list, grid_range: list, function, constant: complex=0.6-0.66j, iterations: int=100, zmax: int=16, color_scheme: int=1):
        """
        :param image_size: a list of image width, height [w,h]
        :param grid_range: a list of grid constraints [x_min, y_min, x_max, y_max]
        :param function: a callable function (for example from the FunctionList)
        :param iterations: maximum number of iterations
        :param zmax: threshold
        :param color_scheme: either 1 or 2 - specifies how the colors of the fractal will be generated
        """
        self.image_width = image_size[0]
        self.image_height = image_size[1]
        self.minx = grid_range[0]
        self.miny = grid_range[1]
        self.maxx = grid_range[2]
        self.maxy = grid_range[3]
        self.iterations = iterations
        self.constant = constant
        self.function = function
        self.zmax = zmax
        self.scheme = color_scheme



    def generate(self):
        image = np.zeros((self.image_height, self.image_width, 3), dtype=np.uint8)

        tp = tqdm(total=self.image_width, desc="Generating")
        for x in range(0, self.image_width):
            tp.update(1)
            z_r = self.minx + x * (self.maxx - self.minx) / self.image_width
            for y in range(0, self.image_height):
                z_i= self.miny + y * (self.maxy - self.miny) / self.image_height
                z = complex(z_r, z_i)

                temp1 = z

                for c in range(1, self.iterations + 1):
                    temp1 = self.function(temp1, self.constant)
                    rad = (temp1.real - z.real) * (temp1.real - z.real) + (temp1.imag - z.imag) * (temp1.imag - z.imag)

                    if rad > self.zmax:
                        color = self.__generate_color__(c)
                        break

                if image[x,y,1] == 0:
                    image[x,y,0] = int(color[0] * 255)
                    image[x,y,1] = int(color[1] * 255)
                    image[x,y,2] = int(color[2] * 255)
        tp.close()
        return image
#--------------------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a Julia set fractal")
    parser.add_argument("-s", "--size", nargs=2, metavar=('w', 'h'), help="image size", type=int, default=[500, 500])
    parser.add_argument("-g", "--grid", nargs=4, metavar=('xmin', 'ymin', 'xmax', 'ymax'), help="grid coordinates", type=float, default=[-1.5, -1.5, 1.5, 1.5])
    parser.add_argument("-f", "--function", type=int, metavar='function_id', default=2, help="function type: 1 or 2")
    parser.add_argument("-c", "--constant", nargs=2, metavar=('re', 'im'), help="constant", type=float, default=[0.6, -0.66])
    parser.add_argument("-i", "--iterations", type=int, metavar='i_max', default=100, help="max number of iterations")
    parser.add_argument("-t", "--threshold", type=int, metavar='thr', default=10, help="threshold for the z_max value")
    parser.add_argument("-p", "--palette", type=int, metavar='scheme_id', default=2, help="color scheme: 1 or 2")
    parser.add_argument("-o", "--output", type=str, metavar='file_path', default="output.png", help="path to generated JPG or PNG file")

    if True:
        args = parser.parse_args()
        if args.function != 1 and args.function != 2:
            print("[ERROR]: Incorrect value for the function ID!")
            sys.exit()
        if args.palette != 1 and args.palette != 2:
            print("[ERROR]: Incorrect value for the palette ID!")
            sys.exit()

        f = None
        if args.function == 1: f = FunctionList.func_z2pc
        elif args.function == 2: f = FunctionList.func_z3pc

        c = complex(args.constant[0], args.constant[1])

        g = FractalJulia(args.size, args.grid, f, c, args.iterations,args.threshold, args.palette)
        img = g.generate()
        cv2.imwrite(args.output, img)




