import numpy as np
import plotly.express as px



class BD:
    """Simulation ballistic deposition model."""

    def __init__(self, size_x: int, size_y=None, 
                    max_particles=None, initial_deposition=None, frame=10):

        self.size_x = size_x
        self.size_y = size_x if size_y is None else size_y
        self.frame = frame
        self.color = 0

        if initial_deposition  is None:
            self.deposition = np.zeros((self.size_x, self.size_y - 1))
            for item in self.deposition:
                item[0] = 1
        else:
            self.deposition  = initial_deposition 

        self.height_profile = np.array([np.sum(item) for item in self.deposition], dtype=int)

        self.max = max_particles
        self.count_p = 0


    def growth(self):

        while True:
            i = np.random.randint(0, self.size_x)

            lefth = self.height_profile[i - 1] if i != 0 else 0
            right = self.height_profile[i + 1] if i != self.size_x - 1 else 0

            if lefth == 0 and right == 0:
                continue

            self.height_profile[i] = np.max([lefth, self.height_profile[i] + 1, right])

            if self.height_profile[i] > self.size_y - 2 or self.count_p == self.max:
                break

            self.deposition [i][self.height_profile[i]] = self.color

            self.count_p += 1

            if self.count_p % self.frame == 0:
                self.color += self.frame / self.size_y

    
    def visualization(self):
        self.deposition  = np.where(self.deposition  == 0, None, self.deposition )
        fig = px.imshow(self.deposition .T, color_continuous_scale='Agsunset', 
            origin='lower', template="plotly_dark", title= f'Count particles = {self.count_p}')

        fig.show()


if __name__ == '__main__':
    size_x, size_y = 2001, 500
    deposition = np.zeros(( size_x, size_y))
    for i in range(0, size_x, 500):
        deposition[i][0] = 1

    my_deposition = BD(size_x, size_y = size_y, initial_deposition=deposition , frame=10)
    my_deposition.growth()
    my_deposition.visualization()