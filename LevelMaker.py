import pygame

def Save(MAP, radiuses, starts, name):
    file = open('Maps/' + name + '.fls', 'w')
    file.write(str(len(MAP)) + '\n')
    for elem in MAP:
        file.write(' '.join([str(x) for x in elem]) + '\n')
    for elem in radiuses:
        file.write(str(elem) + '\n')
    file.write(str(len(starts)) + '\n')
    for start in starts:
        file.write(' '.join([str(x) for x in start]) + '\n')

def ReadMap(FileName):
    try:
        file = open('Maps/' + FileName + '.fls', 'r')
        n = int(file.readline())
        coords = []
        Radiuses = []
        StartPos = []
        for i in range(n):
            coords.append([int(x) for x in file.readline().split()])
        for i in range(n):
            Radiuses.append(int(file.readline()))
        n = int(file.readline())
        for i in range(n):
            StartPos.append([int(x) for x in file.readline().split()])
        return (coords, Radiuses, StartPos)
    except FileNotFoundError:
        return 'NoFile'

def Dist(c1, c2):
    return ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2) ** 0.5

def PressCheckCircle(coords, Buttons):
    for i, but in enumerate(Buttons):
        #print(but)
        if Dist(coords, but[0]) <= but[1]:
            return (True, i)
    return (False, -1)

def PressCheckRect(coords, Buttons):
    for i, but in enumerate(Buttons):
        #print(but)
        InRect = (min(but[0][0], but[1][0]) <= coords[0] <= max(but[0][0], but[1][0]) and min(but[0][1], but[1][1]) <= coords[1] <= max(but[0][1], but[1][1]))
        if InRect:
            return (True, i)
    return (False, -1)

def ButtonPress(coords, ButtonsRect, ButtonsCircle):
    RectResult = PressCheckRect(coords, ButtonsRect)
    if RectResult[0]:
        return ('Rect', RectResult)
    CircResult = PressCheckCircle(coords, ButtonsCircle)
    if CircResult[0]:
        return ('Circ', CircResult)
    else:
        return ('NoBut', (False, -1))

def ToGlobal(pos, PPos):
    return (pos[0] + PPos[0], pos[1] + PPos[1])

def DownloadBMPPicture(PName):
    pict = pygame.image.load('Assets/' + PName + '.bmp')
    ckey = pict.get_at((0, 0))
    pict.set_colorkey(ckey)
    return pict

def GetCentrixCoord(pict, coords):
    print(coords)
    PRect = (pict.get_rect()[2], pict.get_rect()[3])
    return (coords[0] - PRect[0] // 2, coords[1] - PRect[1] // 2)

def DownloadBMP(PName):
    pict = pygame.image.load('Assets/' + PName + '.bmp')
    return pict

def ToGlobalRect(rect, PPos):
    return (ToGlobal(rect[0], PPos), ToGlobal(rect[1], PPos))

ScrSize = (1000, 700)
PlayerRadius = 30

Border = DownloadBMP('Border')
SaveB = DownloadBMP('SaveButton')
SaveBP = DownloadBMP('SaveButtonPressed')
PlayerStart = DownloadBMPPicture('Player')

RButtons = [((0, 0), (100, 60))]

print('Enter name of file to open or name of new file.')
name = input()
ReadResult = ReadMap(name)
if ReadResult == 'NoFile':
    MAP = []
    MAPR = []
    Starts = []
else:
    MAP, MAPR, Starts = ReadResult

pygame.init()

screen = pygame.Surface((1000, 1000))
TrueScreen = pygame.display.set_mode(ScrSize)

KeepGoing = True

PPos = [0, 0]

MouseRel = 'NoRel'
ButtonPressed = [False] * len(RButtons)
SwipeL = False
SwipeR = False

clock = pygame.time.Clock()

while KeepGoing:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            KeepGoing = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                Result = ButtonPress(pygame.mouse.get_pos(), [ToGlobalRect(x, PPos) for x in RButtons], [[MAP[y], MAPR[y]] for y in range(len(MAP))] + [[x,  PlayerRadius] for x in Starts])
                if Result[0] == 'NoBut':
                    SwipeL = True
                    CentrixPoint = ToGlobal(pygame.mouse.get_pos(), PPos)
                if Result[0] == 'Circ':
                    if Result[1][1] >= len(MAP):
                        Starts.pop(Result[1][1] - len(MAP))
                    else:
                        MAP.pop(Result[1][1])
                        MAPR.pop(Result[1][1])
                if Result[0] == 'Rect':
                    ButtonPressed[Result[1][1]] = True
                    if Result[1][1] == 0:
                        Save(MAP, MAPR, Starts, name)
            if pygame.mouse.get_pressed()[2]:
                SwipeR = True
                pygame.mouse.get_rel()
        if event.type == pygame.MOUSEBUTTONUP:
            #print(end = '')
            if event.button == 1:
                if SwipeL:
                    SwipeL = False
                    MAP.append(CentrixPoint)
                    MAPR.append(max(int(Dist(CentrixPoint, ToGlobal(pygame.mouse.get_pos(), PPos))), 2))
                else:
                    ButtonPressed = [False] * len(RButtons)
            if event.button == 3:
                SwipeR = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                Starts.append(ToGlobal(pygame.mouse.get_pos(), PPos))

    if SwipeR:
        MouseRel = pygame.mouse.get_rel()
        PPos[0] += MouseRel[0]
        PPos[1] += MouseRel[1]
    screen.fill((0, 0, 0))
    screen.blit(Border, (0, 0))
    for i in range(len(MAP)):
        pygame.draw.circle(screen, (0, 0, 0), MAP[i], MAPR[i])
        pygame.draw.circle(screen, (125, 125, 125), MAP[i], MAPR[i] - 2)
    if SwipeL:
        #print(CentrixPoint)
        CurrentRadius = Dist(CentrixPoint, ToGlobal(pygame.mouse.get_pos(), PPos))
        pygame.draw.circle(screen, (0, 0, 0), CentrixPoint, max(2, int(CurrentRadius)))
        pygame.draw.circle(screen, (125, 125, 125), CentrixPoint, max(0, int(CurrentRadius) - 2))
    for i in range(len(Starts)):
        screen.blit(PlayerStart, GetCentrixCoord(PlayerStart, Starts[i]))
        TrueScreen.fill((0, 0, 0))
    TrueScreen.fill((0, 0, 0))
    TrueScreen.blit(screen, PPos)

    if ButtonPressed[0] == True:
        TrueScreen.blit(SaveBP, (0, 0))
    else:
        TrueScreen.blit(SaveB, (0, 0))
    
    pygame.display.update()
    clock.tick(60)

pygame.quit()
