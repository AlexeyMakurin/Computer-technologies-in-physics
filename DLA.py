import numpy as np
import plotly.express as px




class LevelMap:

    def __init__(self, size, transition_map=3):
        self.size_map = int(size)

        self.radius = int(size / 2)
        self.start, self.stop = self.radius + 5, self.radius + 100

        self.map = np.zeros((self.size_map, self.size_map))
        self.tm = transition_map

        self.last_x = self.radius
        self.last_y = self.radius

        self.map[self.last_x][self.last_x] = 1


    def update(self, prev_level, values=1):
        
        if len(prev_level.map) != self.tm * len(self.map):
            raise

        for row in range(len(prev_level.map)):
            for col in range(len(prev_level.map[row])):
                if prev_level.map[row][col]:
                    s = self.map[int(row / self.tm)][int(col / self.tm)]
                    self.map[int(row / self.tm)][int(col / self.tm)] = values if s == 0 else s
        
        self.last_x = int(prev_level.last_x / self.tm)
        self.last_y = int(prev_level.last_y / self.tm)

    
    def get_count(self):
        return len(np.where(self.map != 0)[0])





class DLA:

    def __init__(self, size: int, transition_map=3):
        
        self.size = size if size % 3 == 0 and 1 <= size / 3 <= 8 else size - size % 3
        self.radius = int(size / 2)
        self.list_maps = []
        
        i = self.size
        self.tm = transition_map

        while i >= 8:
            self.list_maps.append(LevelMap(i, transition_map=self.tm))
            i /= self.tm
           
        self.step = np.array([
            [1, 0], [-1, 0], [0, 1], [0, -1],
            [1, 1], [-1, 1], [1, -1], [-1, -1]
        ])

        self.time = 1
        self.count = 1

        self.radius_g, self.particles_count = [], []


    def growth(self, level_map=None, jump=None, x_=None, y_=None):
        jump = len(self.list_maps) - 1 if jump is None else jump
        level_map = self.list_maps[jump] if level_map is None else level_map

        while self.radius**2 > (self.list_maps[0].last_x - self.radius)**2 + (self.list_maps[0].last_y - self.radius)**2:
     
            #Генерация рондомного угла
            angle = np.random.uniform(0, 6 * np.pi)
            #Определение координта частицы на окружности с радиусом равным start_walk
            x = int(level_map.start * np.cos(angle) + level_map.size_map / 2) if x_ is None else x_
            y = int(level_map.start * np.sin(angle) + level_map.size_map / 2) if y_ is None else y_

            move = True
            while move:
                
                #Если частица заходит в область роста кластера
                #if (x - level_map.radius)**2 + (y - level_map.radius)**2 < level_map.radius**2:
                    #Проверка присоединения
                    for step in self.step:
                        s_x = 1 <= (x + step[0]) < level_map.size_map - 1
                        s_y = 1 <= (y + step[1]) < level_map.size_map - 1
                        if s_x and s_y:
                            if level_map.map[x + step[0]][y + step[1]]:
                                if jump != 0:
                                    self.growth(level_map=self.list_maps[jump - 1], jump=jump - 1, x_=self.tm*x, y_=y*self.tm)
                                    level_map.update(self.list_maps[jump - 1], values=self.time)
                                    if jump != len(self.list_maps) - 1: return None
                                            
                                else:
                                    self.time += 0.2
                                    level_map.map[x][y] = self.time
                                    level_map.last_x = x
                                    level_map.last_y = y

                                    self.radius_g.append(self.radius_of_gyration())
                                    self.particles_count.append(self.count)

                                    self.count += 1

                                    if len(self.list_maps) > 1: return None

                                move = False
                                break
                
                #Рандомный выбор шага
                    walk = self.step[np.random.randint(0, len(self.step))]
                    x += walk[0]
                    y += walk[1] 

                #Если частица выходит за допустимы пределы, то ее блуждание останавливается 
                    if (x - level_map.radius)**2 + (y - level_map.radius)**2 > level_map.stop**2:
                        break
    
    
    def radius_of_gyration(self):
        x, y = np.where(self.list_maps[0].map != 0)
        return np.sqrt(np.sum((x - np.mean(x))**2 + (y - np.mean(y))**2) / len(x))


    def visualization(self):
        for item in self.list_maps:
            map = np.where(item.map == 0, None, item.map)
            fig = px.imshow(map.T, color_continuous_scale='Agsunset', origin='lower', template="plotly_dark", 
            title=f'Count particals {self.count}; Resolution x{np.round(item.size_map / self.list_maps[0].size_map, 2)}')
            fig.show()



class DLAMGC:
    def __init__(self, size):
        self.size = size + 1 if size % 2 == 0 else size
        self.radius = int(self.size / 2)

        self.last_x = 0
        self.last_y = 0

        self.dla = np.zeros((self.size, self.size))

        for row in range(self.size):
            for col in range(self.size):
                if self.radius**2 + self.size > (row - self.radius)**2 + (col - self.radius)**2 >= self.radius**2:
                    self.dla[row][col] = 1

        self.time = 1
        self.count = 1
        
        self.steps = np.array([
            [1, 0], [-1, 0], [0, 1], [0, -1],
            [1, 1], [-1, 1], [1, -1], [-1, -1]
        ])


    def growth(self):
        while self.last_x != self.radius or self.last_y != self.radius:
            move = True
            x, y = self.radius, self.radius

            while move:
                for step in self.steps:
                    if self.dla[x + step[0]][y + step[1]]:
                        self.time += 0.2
                        self.dla[x][y] = self.time
                        self.count += 1
                        self.last_x = x
                        self.last_y = y

                        move = False
                        break
                    
                step = self.steps[np.random.randint(0, len(self.steps))]
                x += step[0]
                y += step[1]


    def visualization(self):
        map = np.where(self.dla == 0, None, self.dla)
        fig = px.imshow(map.T, color_continuous_scale='Agsunset', origin='lower', template="plotly_dark", 
        title=f'Count particals {self.count}')
        fig.show()



if __name__ == '__main__':
    my_dla = DLAMGC(216)
    my_dla.growth()
    my_dla.visualization()
    
    #dla = DLAMGC(128)
    #dla.growth()
    
    