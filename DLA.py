import numpy as np
import plotly.express as px




def visualization(map, count):
        map = np.where(map == 0, None, map)
        fig = px.imshow(map.T, color_continuous_scale='Agsunset', origin='lower', template="plotly_dark", 
        title=f'Count particals {count}')
        fig.show()




class LevelMap:

    def __init__(self, size, transition_map=2):
        self.size_map = int(size)
        self.map = np.zeros((self.size_map, self.size_map))
        self.tm = transition_map


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




class LevelMapDLA(LevelMap):
    def __init__(self,  size, start, stop, transition_map=2):
        super().__init__(size, transition_map=transition_map)
        self.last_x = int(self.size_map / 2)
        self.last_y = int(self.size_map / 2)

        self.map[self.last_x][self.last_x] = 1

        self.start = start
        self.stop = stop




class LevelMapDLAMGC(LevelMap):
    def __init__(self, size, transition_map=2):
        super().__init__(size, transition_map=transition_map)
        self.last_x = 0
        self.last_y = 0






class DLA:

    def __init__(self, size, start_walk, stop_walk, transition_map=2):
        
        self.size = size
        self.start_walk, self.stop_walk = start_walk, stop_walk

        self.list_maps = []
        
        start = self.start_walk
        stop = self.stop_walk
        i = self.size
        self.tm = transition_map

        while i >= 8:
            self.list_maps.append(LevelMapDLA(i, start, stop, transition_map=self.tm))
            i /= self.tm
            start /= self.tm
            stop /= self.tm

        self.step = np.array([
            [1, 0], [-1, 0], [0, 1], [0, -1],
            [1, 1], [-1, 1], [1, -1], [-1, -1]
        ])

        self.time = 1
        self.count = 1


    def growth(self, level_map=None, jump=None, x_=None, y_=None):
        jump = len(self.list_maps) - 1 if jump is None else jump
        level_map = self.list_maps[jump] if level_map is None else level_map

        while 0 < self.list_maps[0].last_x < self.list_maps[0].size_map - 1 and 0 < self.list_maps[0].last_y < self.list_maps[0].size_map - 1:
     
            #Генерация рондомного угла
            angle = np.random.uniform(0, 6 * np.pi)
            #Определение координта частицы на окружности с радиусом равным start_walk
            x = int(level_map.start * np.cos(angle) + level_map.size_map / 2) if x_ is None else x_
            y = int(level_map.start * np.sin(angle) + level_map.size_map / 2) if y_ is None else y_

            while True:
                #Рандомный выбор шага
                walk = self.step[np.random.randint(0, len(self.step))]
                x += walk[0]
                y += walk[1] 

                #Если частица выходит за допустимы пределы, то ее блуждание останавливается 
                if x**2 + y**2 > level_map.stop**2:
                    break
                
                #Факт присоеднения частицы
                join = False

                #Если частица заходит в область роста кластера
                if 0 <= x < level_map.size_map and 0 <= y < level_map.size_map:
                    #Проверка присоединения
                    for step in self.step:
                        s_x = 0 <= x + step[0] < level_map.size_map
                        s_y = 0 <= y + step[1] < level_map.size_map
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
                                    self.count += 1

                                    if len(self.list_maps) > 1: return None

                                join = True
                                break

                if join: break
    



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




if __name__ == '__main__':
    #my_dla = DLA(128, 133, 228, transition_map=4)
    #my_dla.growth()
    
    dla = DLAMGC(100)
    dla.growth()
    visualization(dla.dla, count=1)
    