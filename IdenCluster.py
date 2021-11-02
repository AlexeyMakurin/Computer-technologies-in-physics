import numpy as np
import pandas as pd
import plotly.express as px




class IdenCluster:
    """Данный класс позволяет создать кластер базовой модели Идена, 
       визуальное представление итогово кластера, анимация роста кластера."""
    

    def __init__(self, lattice_size, time_record=False):
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

        #Необходимы для записи роста кластера
        self.cluster = []
        self.x = []
        self.y = []
        self.type = []
    

    def growth(self, records=False, frame=1):

        self.records = records
        self.frame = abs(frame)

        if self.records:
            self.__growth_recording()

        #Условие остановки роста
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
                self.__growth_recording()
        
        if self.records:
            self.df = pd.DataFrame({
                'count particles': self.cluster, 
                'x': [x - self.l for x in self.x], 
                'y': [y - self.l for y in self.y], 
                'type' : self.type
            })


    def __growth_recording(self):
        #Один фрейм анимации содержит кратное количество частиц значению фрейма
        if self.count_particles % self.frame == 0 or self.count_particles == 1:
            
            x, y = np.where(self.particles>=0)
            self.x.extend(x)
            self.y.extend(y)
            self.cluster.extend([self.count_particles] * len(x))
            
            #Сортируем ячейки сетки на заполненые и пустые
            for x, y in zip(x, y):
                if self.particles[x][y] == 0:
                    self.type.append(0)
                else:
                    self.type.append(1)
            

    def vizualization(self):
        px.defaults.width = 800
        px.defaults.height = 800

        colors = [
        px.colors.sequential.Burg, 
        px.colors.sequential.Purpor, 
        px.colors.sequential.Tealgrn,
        px.colors.sequential.PuBu
        ]
        
        if self.records:
            color_values = np.sin(np.sqrt(self.df['x']**2 + self.df['y']**2)) + np.log(np.sqrt(self.df['x']**2 + self.df['y']**2) + 1)

            self.fig = px.scatter(self.df, x='x', y='y', animation_frame='count particles', size="type", color=color_values, 
                range_x=[-self.l, self.l], range_y=[-self.l, self.l], size_max= 12, 
                    color_continuous_scale=colors[np.random.randint(0, 4)])
        else:
            x, y = np.where(self.particles)
            x = x - self.l
            y = y - self.l

            color_values = np.sin(np.sqrt(x**2 + y**2)) + np.log(np.sqrt(x**2 + y**2) + 1)

            self.fig = px.scatter(x=x, y=y, color=color_values, range_x=[-self.l, self.l], range_y=[-self.l, self.l], 
            color_continuous_scale=colors[np.random.randint(0, 4)], title=f'Count particles = {self.count_particles}')


        self.fig.show()

    def save_vizualization(self, name):
        if self.records:
            self.fig.write_html(f"iden_cluster_{name}.html")
        else:
            self.fig.write_image(f"images/iden_cluster_{name}.svg")




if __name__ == '__main__':
    for n in [21]:
        my_claster = IdenCluster(n)
        my_claster.growth(records=1, frame=10)
        my_claster.vizualization()
        #my_claster.save_vizualization(n)