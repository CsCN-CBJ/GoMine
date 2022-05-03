import random
import numpy as np
import pyautogui
import win32gui
from PIL import ImageGrab


def mouseClick(x, y, lOrR="left"):
    pyautogui.click(x, y, clicks=1, interval=0.2, duration=0.2, button=lOrR)


class MyMiner:
    blockWidth = 16  # 左右距离
    blockHeight = 16  # 上下距离

    # mapLocate = tuple[left, top, right, bottom] 窗口位置, 单位:像素
    # mapSize = tuple[nRow, nCol]
    # mineMap = np.array(mapSize, dtype = np.int32)

    def __init__(self, mode=0):
        """
        现在只能打中级高级, 因为初级的边框不太一样
        :param mode: 设置难度(棋盘大小), 0自动识别, 1简单, 2中等, 3困难
        """
        # 获取窗口位置
        mapLocate = self.getWindowsLocate()  # 窗口位置, left, top, right, bottom, 单位:像素
        self.mapLocate = mapLocate
        # 识别地图大小
        if mode == 0:
            cols = int((mapLocate[2] - mapLocate[0]) / self.blockWidth)
            rows = int((mapLocate[3] - mapLocate[1]) / self.blockHeight)
            mapSize = (rows, cols)
        else:
            modToSize = ((8, 8), (16, 16), (16, 30))
            mapSize = modToSize[mode - 1]  # rows, cols
        self.mapSize = mapSize  # rows, cols
        # 初始化地图二维数组
        # self.mineMap = np.array(mapSize, dtype=np.int32)
        self.mineMap = np.zeros(mapSize, np.int32) - 1
        print('Map Size:{}'.format(str(self.mineMap.shape)))

    @staticmethod
    def getWindowsLocate():
        """
        通过窗口名字获取句柄, 进而分析窗口所占位置(四条边的坐标值), 去掉边框, 获得地图所在位置
        边框所占像素需要自己调
        """
        # 使用spy++查看
        class_name = "TMain"
        title_name = "Minesweeper Arbiter "
        # 窗口句柄
        hwnd = win32gui.FindWindow(class_name, title_name)
        if hwnd:
            print("找到窗口")
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            # win32gui.SetForegroundWindow(hwnd)
            print("窗口坐标：")
            print(str(left) + ' ' + str(right) + ' ' + str(top) + ' ' + str(bottom))
            # 获取实际地图位置,挺离谱的magic number
            left += 15
            top += 110
            right -= 15
            bottom -= 43
            print("雷区坐标:")
            print(str(left) + ' ' + str(right) + ' ' + str(top) + ' ' + str(bottom))
            # pyautogui.moveTo(left, top)
            # pyautogui.moveTo(right, bottom)
            return left, top, right, bottom
        else:
            exit("未找到窗口")

    def clickBlock(self, pos: tuple[int, int], left=True):
        """
        点击一个区块
        Index Start with 0
        此函数并未遵守代码规范, 将xy颠倒了
        :param pos: nRow, nCol
        :param left: if it is left click
        """
        x = self.mapLocate[1]
        y = self.mapLocate[0]
        x += int((pos[0] + 0.5) * self.blockWidth)
        y += int((pos[1] + 0.5) * self.blockHeight)
        if left:
            pyautogui.click(y, x, button="left")
        else:
            pyautogui.click(y, x, button="right")

    def analyzeMap(self):
        """
        没用
        根据blockSize信息, 对全地图进行切割并分析
        并未实际使用, 因为无法准确识别单独的方块
        """
        # 0-8已知的雷数 9标雷 -1未知
        img = ImageGrab.grab().crop(self.mapLocate)
        for row in range(self.mapSize[0]):
            for col in range(self.mapSize[1]):
                if self.mineMap[row][col] != -1:
                    continue
                x = int((col + 0.3) * self.blockWidth)
                y = int((row + 0.3) * self.blockHeight)
                colors = img.crop((x, y, x + 4, y + 4)).getcolors()
                print(colors)
                # 识别代码要重新写, 这里函数改掉了
                # self.mineMap[row][col] = self.analyzeBlockImg(colors)
        print(self.mineMap)

    def analyzeOneBlock(self, pos: tuple[int, int]):
        """
        分析一个方块的成分
        根据区域内是否有特征颜色来判断数字与旗帜
        目前较难实现精准分辨, 只能识别某些特征, 可以准确识别1234568, 7是黑色的, 雷同时有白色与黑色
        不能识别旗帜(其红色会被识别为3), 无法区分未探索方块与0雷方块
        :param pos: nRow, nCol
        :return: 识别结果
        """
        # 0-8已知的雷数 9标雷 -1未知
        # colorDict = {'red': (255, 0, 0), 'green': (0, 255, 0), 'blue': (0, 0, 255), 'white': (255, 255, 255),
        #              'black': (0, 0, 0), 'green2': (0, 128, 128)}

        # 截图并提取颜色
        left = self.mapLocate[0] + (pos[1] + 0.3) * self.blockWidth
        top = self.mapLocate[1] + (pos[0] + 0.3) * self.blockHeight
        colorList = ImageGrab.grab().crop((left, top, left + 5, top + 5)).getcolors()
        # 不需要每一个颜色出现数量信息, 简化数组
        colors = []
        for nColor in colorList:
            colors.append(nColor[1])
        # 通过特征颜色识别, 代码可以优化, 但是我累了
        if (255, 255, 255) in colors and (0, 0, 0) in colors:  # 雷同时拥有黑色与白色
            print(str(colorList))
            exit("BOOOOMB!")
        elif (0, 0, 255) in colors:
            return 1
        elif (0, 128, 0) in colors:
            return 2
        elif (255, 0, 0) in colors:
            return 3
        elif (0, 0, 128) in colors:
            return 4
        elif (128, 0, 0) in colors:
            return 5
        elif (0, 128, 128) in colors:
            return 6
        elif (0, 0, 0) in colors:  # 7数字是黑色, 背景是灰色
            return 7
        elif (128, 128, 128) in colors:
            return 8
        return 0

    def checkSurround(self, pos: tuple[int, int]):
        """
        某个数字周围是否可以完全分析清楚
        :param pos: nRow, nCol
        :return: 是否分析清楚
        """
        row, col = pos
        nMine = self.mineMap[row][col]
        blanks = []
        if not 0 < nMine < 9:
            exit('Check Surround Failed')
        # 识别周围的雷与空白数量, 因为当前方块本身是数字, 本来就不计入考虑
        for i in range(row - 1, row + 2):
            for j in range(col - 1, col + 2):
                if self.checkPos((i, j)):  # 防止超出边界
                    if self.mineMap[i][j] == -1:  # 未探索(空白)
                        blanks.append((i, j))
                    elif self.mineMap[i][j] == 9:  # 已经标雷
                        nMine -= 1
        # 识别完成
        if nMine == 0:  # 如果周围的雷已经全部插旗, 则点击所有剩下的
            for blank in blanks:
                self.clickBlock(blank)
                self.trace(blank)
            self.mineMap[pos] = 0  # 分析完毕的数字设置为0, 反正也没用
            return True
        elif len(blanks) == nMine:  # 如果空白数正好等于雷数, 则全部标雷
            for blank in blanks:
                self.mineMap[blank] = 9
                self.clickBlock(blank, False)
            self.mineMap[pos] = 0  # 分析完毕的数字设置为0, 反正也没用
            return True
        elif len(blanks) < nMine:
            print('Not enough blanks in {}'.format(str(pos)))
            print('blanks: ' + str(blanks))
            exit('Identification Error')
        else:
            return False

    def luckyClick(self):
        """
        用于无法分析时, 随机点击一个方块, 所有-1方块平均概率
        可重点优化
        """
        blanks = np.where(self.mineMap == -1)  # 所有未探索方块的索引
        nBlanks = (blanks[1].shape[0])  # 所有未探索方块的数量
        n = random.randint(0, nBlanks - 1)  # 平均随机
        pos = (blanks[0][n], blanks[1][n])
        self.clickBlock(pos)
        self.trace(pos)

    def checkPos(self, pos):
        """
        python可以识别-1下标, 所以需要这个函数来检查下标
        :return: 是否是合法坐标
        """
        if 0 <= pos[0] < self.mapSize[0] and 0 <= pos[1] < self.mapSize[1]:
            return True
        return False

    def trace(self, pos: tuple[int, int]):
        """
        分析已经被点过, 但未分析到数组中的方块
        :param pos:
        :return: 跟踪成功
        """
        if not self.checkPos(pos):  # 越界
            return False
        if self.mineMap[pos] != -1:  # 只能分析未定义的方块
            return False
        result = self.analyzeOneBlock(pos)  # 分析当前方块
        if 1 <= result <= 8:  # 如果是单纯的数字,则完成
            self.mineMap[pos] = result
            return True
        elif result == 0:
            self.mineMap[pos] = 0
            for i in range(pos[0] - 1, pos[0] + 2):
                for j in range(pos[1] - 1, pos[1] + 2):
                    self.trace((i, j))
            return True
        else:
            print("Img analyze Error in {}: {}".format(str(pos), result))
            raise IOError  # 我也觉得这个异常很蠢, 但是总比拦截我的KeyBoardInterrupt好

    def bfs(self):
        # 0-8已知的雷数 9标雷(插旗) -1未知
        # 当一个数字周围已经确定时, 他将被设置为0, 便于了解哪些数字还没有分析完毕
        print("CBJ 挖矿机")
        # 先点中间那个
        x = self.mapSize[0] // 2
        y = self.mapSize[1] // 2
        self.clickBlock((x, y))
        self.trace((x, y))
        # 主循环
        while True:
            # 选择当前还没有分析完毕的数字(分析完毕的数字设置为了0)
            numberPos = np.where((1 <= self.mineMap) & (self.mineMap <= 8))
            n = len(numberPos[0])
            if n == 0:
                exit("CBJNB")
            canAnalyze = False
            for i in range(n):
                if self.checkSurround((numberPos[0][i], numberPos[1][i])):
                    canAnalyze = True
            # 如果一个都分析不出来, 就随机来一个
            if not canAnalyze:
                self.luckyClick()


if __name__ == '__main__':
    a = MyMiner()
    # a.analyzeOneBlock((15, 15))
    # print(a.analyzeOneBlock((0,0)))
    # a.clickBlock((0,1))
    # a.analyzeMap()
    # a.luckyClick()
    a.bfs()
    # FailSafeException
