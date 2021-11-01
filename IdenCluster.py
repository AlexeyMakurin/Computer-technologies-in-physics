import numpy as np
import pandas as pd
import plotly.express as px

class IdenClaster():
    """Данный класс позволяет создать кластер базовой модели Идена."""
    
    def __init__(self, lattice_size):
        self.lattice_size = int(lattice_size)
        self.l = int(self.lattice_size / 2)
        
        #Массив координат частиц
        self.particles = np.zeros((self.lattice_size, self.lattice_size))
        #"Зерно" роста
        self.particles[self.l][self.l] = 1
        
        #Таблица сдвига
        self.displacement = np.array([[1, 0], [0, -1], [-1, 0], [0, 1]], dtype=int)
        
        #Узлы "зерна" роста
        self.perimeter = self.displacement + self.l

        #Необходимы для записи временных изменений
        self.time = []
        self.x_time = []
        self.y_time = []
        self.type = []
        
        self.__time_recording(0)
        self.count_number = 1
        
    def growth(self):
        #time = 0
        while np.max(self.perimeter) < self.lattice_size - 1 and np.min(self.perimeter) > 0:
            
            #Выбор случайного узла частицы
            i = np.random.randint(0, len(self.perimeter))
            #Присоединение частицы
            self.particles[self.perimeter[i][0]][self.perimeter[i][1]] = 1
            self.count_number += 1

            #Вычисление нового периметра кластера
            for d in self.displacement:

                node = self.perimeter[i] + d
                
                if not self.particles[node[0]][node[1]]:
                    self.perimeter = np.append(self.perimeter, [node], axis=0)

            self.perimeter = np.delete(self.perimeter, i, axis=0)

            #time += 1
            self.__time_recording(self.count_number)
            
        self.df = pd.DataFrame({
            'count number': self.time, 
            'x': [x - self.l for x in self.x_time], 
            'y': [y - self.l for y in self.y_time], 
            'type' : self.type
        })
    
    def __time_recording(self, count_number):
        if count_number % 25 == 0:
                
            x_time, y_time = np.where(self.particles >= 0)
            self.x_time.extend(x_time)
            self.y_time.extend(y_time)
            self.time.extend([count_number] * len(x_time))
            
            for x, y in zip(x_time, y_time):
                if self.particles[x][y] == 0:
                    self.type.append(0)
                else:
                    self.type.append(1)
            
    def vizualization(self):
        px.defaults.width = 800
        px.defaults.height = 800
        color_values = np.sqrt(self.df['x']**2 + self.df['y']**2)

        fig = px.scatter(self.df, x='x', y='y', animation_frame='count number', size="type", color=np.cos(color_values), 
        range_x=[-self.l, self.l], range_y=[-self.l, self.l], size_max=10, color_continuous_scale=px.colors.diverging.Tealrose)
        
        fig.show()


if __name__ == '__main__':
    n = 51
    for _ in range(1):
        my_claster = IdenClaster(n)
        my_claster.growth()
        my_claster.vizualization()
        print(my_claster.count_number)