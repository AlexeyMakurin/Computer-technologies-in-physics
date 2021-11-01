import numpy as np
import pandas as pd
import plotly.express as px




class IdenCluster():
    """Данный класс позволяет создать кластер базовой модели Идена, 
       визуальное представление итогово кластера, анимация роста кластера."""
    
    
    colors = [
        px.colors.sequential.Burg, 
        px.colors.sequential.Purpor, 
        px.colors.sequential.Tealgrn,
        px.colors.sequential.PuBu
        ]

    def __init__(self, lattice_size, time_record=None):
        self.lattice_size = int(lattice_size)
        self.time_record = time_record
        self.l = int(self.lattice_size / 2)

        #Массив координат частиц
        self.particles = np.zeros((self.lattice_size, self.lattice_size))
        #"Зерно" роста
        self.particles[self.l][self.l] = 1
        self.count_particles = 1

        #Таблица сдвига
        self.displacement = np.array([[1, 0], [0, -1], [-1, 0], [0, 1]], dtype=int)
        
        #Узлы "зерна" роста
        self.perimeter = self.displacement + self.l

        #Необходимы для записи временных изменений
        self.time = []
        self.x_time = []
        self.y_time = []
        self.type = []
        
    def growth(self, records=None, frame=1):

        self.records = records
        self.frame = frame

        if self.records:
            self.__time_recording()

        while np.max(self.perimeter) < self.lattice_size - 1 and np.min(self.perimeter) > 0:
            
            #Выбор случайного узла частицы
            i = np.random.randint(0, len(self.perimeter))
            #Присоединение частицы
            if self.particles[self.perimeter[i][0]][self.perimeter[i][1]] == 0:
                self.particles[self.perimeter[i][0]][self.perimeter[i][1]] = 1
                self.count_particles += 1
            else:
                continue

            #Вычисление нового периметра кластера
            for d in self.displacement:
                node = self.perimeter[i] + d
                
                if not self.particles[node[0]][node[1]]:
                    self.perimeter = np.append(self.perimeter, [node], axis=0)

            self.perimeter = np.delete(self.perimeter, i, axis=0)

            if self.records:
                self.__time_recording()
        
        if self.records:
            self.df = pd.DataFrame({
                'count particles': self.time, 
                'x': [x - self.l for x in self.x_time], 
                'y': [y - self.l for y in self.y_time], 
                'type' : self.type
            })
        

    def __time_recording(self):
        if (self.count_particles - 1) % self.frame == 0:
            
            x_time, y_time = np.where(self.particles >= 0)
            self.x_time.extend(x_time)
            self.y_time.extend(y_time)
            self.time.extend([self.count_particles] * len(x_time))
            
            for x, y in zip(x_time, y_time):
                if self.particles[x][y] == 0:
                    self.type.append(0)
                else:
                    self.type.append(1)
            

    def animation(self):
        px.defaults.width = 800
        px.defaults.height = 800

        color_values = np.sin(np.sqrt(self.df['x']**2 + self.df['y']**2)) + np.log(np.sqrt(self.df['x']**2 + self.df['y']**2) + 1)
        
        self.fig = px.scatter(self.df, x='x', y='y', animation_frame='count particles', size="type", color=color_values, 
            range_x=[-self.l, self.l], range_y=[-self.l, self.l], size_max= 12, 
                color_continuous_scale=IdenCluster.colors[np.random.randint(0, 3)])

        self.fig.show()


    def save_animation(self, path):
        self.fig.write_html(f"{path}.html")


    def vizualization(self):
        px.defaults.width = 800
        px.defaults.height = 800

        x, y = np.where(self.particles != 0)
        x = x - self.l
        y = y - self.l

        print(len(x))

        color_values = np.sin(np.sqrt(x**2 + y**2)) + np.log(np.sqrt(x**2 + y**2))
        self.fig_v = px.scatter(x=x, y=y, color=color_values, range_x=[-self.l, self.l], range_y=[-self.l, self.l], 
        color_continuous_scale=IdenCluster.colors[np.random.randint(0, 3)])

        self.fig_v.update_traces(marker_size=8)
        self.fig_v.show()
        

    def save_vizualization(self, name):
         self.fig_v.write_image(f"images/{name}.svg")


#color_continuous_scale=px.colors.cyclical.IceFire
#color_continuous_scale=px.colors.sequential.Inferno
#color_continuous_scale=px.colors.diverging.Tealrose
#color_continuous_scale=px.colors.sequential.Viridis

if __name__ == '__main__':
    n = 51
    for _ in range(1):
        my_claster = IdenCluster(n)
        my_claster.growth(records=1, frame=10)
        my_claster.growth()
        #my_claster.vizualization()
        my_claster.animation()