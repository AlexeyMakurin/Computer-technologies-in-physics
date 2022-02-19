import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt



class BD:
    """Simulation ballistic deposition model."""

    def __init__(self, size_x: int, size_y=None, initial_deposition=None, frame=10):

        self.size_x = size_x
        self.size_y = size_x if size_y is None else size_y
        self.frame = frame
        self.color = 1 + self.frame / self.size_y

        if initial_deposition  is None:
            self.deposition = np.zeros((self.size_x, self.size_y - 1))
            for item in self.deposition:
                item[0] = 1
        else:
            self.deposition = initial_deposition 

        self.height_profile = np.array([np.sum(item) for item in self.deposition], dtype=int)

        self.count_p = 0


    def growth(self, max_particles=None):

        self.max = max_particles

        while True:
            i = np.random.randint(0, self.size_x)

            lefth = self.height_profile[i - 1] if i != 0 else 0
            right = self.height_profile[i + 1] if i != self.size_x - 1 else 0

            if lefth == 0 and right == 0 and self.height_profile[i] == 0:
                continue
            
            
            self.height_profile[i] = np.max([lefth, self.height_profile[i] + 1, right])

            #self.height_profile[i] - 1 Отсчет уровня идет от нуля!
            self.deposition[i][self.height_profile[i] - 1] = self.color

            if self.height_profile[i] > self.size_y - 2 or self.count_p == self.max:
                break

            self.count_p += 1

            if self.count_p % self.frame == 0:
                self.color += self.frame / self.size_y

    
    def visualization(self, path_name=None, width=None, height=None):
        self.deposition = np.where(self.deposition == 0, None, self.deposition )

        fig = px.imshow(self.deposition.T, color_continuous_scale='Agsunset', 
            origin='lower', template="plotly_dark", title= f'Count particles = {self.count_p}', width=width, height=height)

        
        fig.show()

        if path_name:
           fig.write_image(f"{path_name}.webp")




if __name__ == '__main__':
    #size_x = 1000
    #deposition = np.zeros(( size_x, size_y))
    #for i in range(0, size_x, 500):
    #deposition[500][0] = 1

    #for _ in range(1):
        #Размер сетки
        size_ = 10

        #Формируем исходный осадок
        init_dep = np.zeros((size_, size_))
        init_dep[int(size_ / 2)][0] = 1

    
    
        d = BD(size_, initial_deposition=init_dep)
        d.growth()
        d.visualization();

    #my_deposition = BD(size_x, frame=10)
    #my_deposition.growth()
    #my_deposition.visualization('images/BD')