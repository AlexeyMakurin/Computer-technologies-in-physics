import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class IdenCluster:
    """Данный класс позволяет создать кластер базовой модели Идена, 
       визуальное представление итогово кластера, анимация роста кластера."""
    
    def __init__(self, lattice_size):
        self.lattice_size = int(lattice_size)
        #self.time_record = time_record
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
        self.cluster, self.type = [], []
        self.x, self.y = [], []
        self.radius_g, self.particles_count, self.count_node = [], [], []


    def add_particles(self, random_node):
        i = random_node
        if self.particles[self.perimeter[i][0]][self.perimeter[i][1]] == 0:
            self.particles[self.perimeter[i][0]][self.perimeter[i][1]] = 1
            self.count_particles += 1
            return True
        else:
            return False


    def update_perimeter(self, random_node):
        i = random_node
        for d in self.displacement:
            node = self.perimeter[i] + d
                
            if self.particles[node[0]][node[1]] == 0 and\
                len(np.where(np.sum(np.isclose(self.perimeter, node), axis=1) == 2)[0]) == 0:
                 
                self.perimeter = np.append(self.perimeter, [node], axis=0)

        self.perimeter = np.delete(self.perimeter, i, axis=0)


    def radius_of_gyration(self):
        x, y = np.where(self.particles != 0)
        return np.sqrt(np.sum((x - np.mean(x))**2 +  (y - np.mean(y))**2)) / len(x), len(x), len(self.perimeter)


    def _growth_recording(self):
        #Один фрейм анимации содержит кратное количество частиц значению фрейма
        if self.count_particles % self.frame == 0 or self.count_particles == 1:
            
            x, y = np.where(self.particles >= 0)
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
        
        if self.frame:

            self.df = pd.DataFrame({
                'count particles': self.cluster, 
                'x': [x - self.l for x in self.x], 
                'y': [y - self.l for y in self.y], 
                'type' : self.type
            })

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
        if self.frame:
            self.fig.write_html(f"iden_cluster_{name}.html")
        else:
            self.fig.write_image(f"images/iden_cluster_{name}.svg")




class BasicModel(IdenCluster):
    def growth(self, frame=0, R_g=False):

        self.R_g = R_g
        self.frame = abs(frame)

        if self.frame:
            self._growth_recording()

        #Условие остановки роста
        while np.max(self.perimeter) < self.lattice_size - 1 and np.min(self.perimeter) > 0:
            
            if self.R_g and self.count_particles % 10 == 0:
                r_g = self.radius_of_gyration()
                self.radius_g.append(r_g[0])
                self.particles_count.append(r_g[1])
                self.count_node.append(r_g[2])


            #Выбор случайного узла частицы
            i = np.random.randint(0, len(self.perimeter))

            #Присоединение частицы
            if not self.add_particles(i): continue
            
            #Вычисление нового периметра кластера
            self.update_perimeter(i)

            if self.frame:
                self._growth_recording()    



class ScreenedGrowthModel(IdenCluster):

    def __init__(self, lattice_size, a, psi, probability):
        super().__init__(lattice_size)
        self.a = a
        self.psi = psi
        self.probability = probability


    def probabilitys_join(self):
        x, y = np.where(self.particles != 0)
        probabilitys = np.empty(len(self.perimeter))

        for id, node  in enumerate(self.perimeter):
            distance = np.sqrt((x - node[0])**2 + (y - node[1])**2)
            probabilitys[id] = np.prod(np.exp(-self.a / (distance**self.psi)))

        stat_sum = np.sum(probabilitys)
        probabilitys = probabilitys / stat_sum

        index = np.where(probabilitys >= self.probability)[0]
        return index


    def growth(self, frame=0, R_g=False):
        self.frame = abs(frame)
        self.R_g = R_g

        if self.frame:
            self._growth_recording()

        while np.max(self.perimeter) < self.lattice_size - 1 and np.min(self.perimeter) > 0:
            
            if self.R_g and self.count_particles % 10 == 0:
                r_g = self.radius_of_gyration()
                self.radius_g.append(r_g[0])
                self.particles_count.append(r_g[1])
                self.count_node.append(r_g[2])


            #Вероятность присоединения
            index = self.probabilitys_join()
            if len(index) == 0:
                break

            #Выбор случайного узла частицы
            i = np.random.choice(index)
            #Присоединение частицы
            if not self.add_particles(i): continue
            #Вычисление нового периметра кластера
            self.update_perimeter(i)

            if self.frame:
                self._growth_recording()




if __name__ == '__main__':
    for n in [121]:
        my_claster = ScreenedGrowthModel(n, 1, 2, 0.005)
        #my_claster = BasicModel(n)
        my_claster.growth()
        my_claster.vizualization()
      
        #my_claster.save_vizualization(f'/screened_growth_model/')
    #y = my_claster.radius_g
    #x = my_claster.particles_count

    #fig = px.scatter(x=x, y=y, log_y=True, log_x=True)
    #fig.show()