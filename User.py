import socket
import struct
import random
import pygame

##def BuildLandscape(Map, MapR):
##    land = pygame.Surface((1000, 1000))
##    for i in range(len(Map)):
##        land.blit()

def DownloadBMPPicture(PName):
    pict = pygame.image.load('Assets/' + PName + '.bmp')
    ckey = pict.get_at((0, 0))
    pict.set_colorkey(ckey)
    return pict

def GetCentrixCoord(pict, coords):
    PRect = (pict.get_rect()[2], pict.get_rect()[3])
    return (coords[0] - PRect[0] // 2, coords[1] - PRect[1] // 2)

def DownloadBMP(PName):
    pict = pygame.image.load('Assets/' + PName + '.bmp')
    return pict

BLACK = (0, 0, 0)
GREY = (125, 125, 125)
GREEN = (0, 255, 0)
DGREEN = (0, 170, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PassColor = (31, 15, 72)

Player = DownloadBMPPicture('Player')
Bullet = DownloadBMPPicture('Bullet')
Stage1P = DownloadBMPPicture('PExplosionStage1')
Stage2P = DownloadBMPPicture('PExplosionStage2')
Stage3P = DownloadBMPPicture('PExplosionStage3')
Stage4P = DownloadBMPPicture('PExplosionStage4')
EBullet = DownloadBMPPicture('BExplosion')
EBullet1 = DownloadBMPPicture('BExplosion1')
Border = DownloadBMP('Border')

PExplosion = [Stage4P, Stage4P, Stage4P, Stage4P, Stage3P, Stage2P, Stage1P]
BExplosion = [EBullet, EBullet, EBullet, EBullet1]
StageChangeTimeP = 2 / (len(PExplosion))
StageChangeTimeB = 1 / (len(BExplosion))

def MakeBackground(Map, MapR, sides):
    srf = pygame.Surface(sides)
    srf.fill(PassColor)
    for i in range(len(Map)):
        pygame.draw.circle(srf, BLACK, Map[i], MapR[i])
        pygame.draw.circle(srf, GREY, Map[i], MapR[i] - 2)
    srf.set_colorkey(PassColor)
    return srf

def EncodeSpeed(speed):
    string = ''
    if speed[0] == 1:
        string = 'a'
    elif speed[0] == -1:
        string = 'c'
    else:
        string = 'b'
    if speed[1] == 1:
        string += 'a'
    elif speed[1] == -1:
        string += 'c'
    else:
        string += 'b'
    return string

def SendCoord(coords, sock):
    sock.send(struct.Struct('ii').pack(*[int(x) for x in coords]))

def SendSimple(key, value, sock):
    sock.send(struct.Struct(key).pack(value))

def GetBool(sock):
    if sock.recv(1) == b'1':
        return True
    else:
        return False

def GetNum(sock):
    return struct.Struct('i').unpack(sock.recv(struct.Struct('i').size))[0]

def GetFloat(sock):
    return struct.Struct('f').unpack(sock.recv(struct.Struct('f').size))[0]

def GetCoord(sock):
    inp = sock.recv(struct.Struct('ii').size)
    #print(inp)
    return struct.Struct('ii').unpack(inp)

def GetStr(sock):
    n = GetNum(sock)
    return struct.Struct(str(n) + 's').unpack(sock.recv(struct.Struct(str(n) + 's').size))

def GetMasCoords(sock):
    n = GetNum(sock)
    mas = []
    for i in range(n):
        mas.append(GetCoord(sock))
    return mas

def GetMasInt(sock):
    n = GetNum(sock)
    mas = []
    for i in range(n):
        mas.append(GetNum(sock))
    return mas

def GetMasFloat(sock):
    n = GetNum(sock)
    mas = []
    for i in range(n):
        mas.append(GetFloat(sock))
    return mas

def GetMasBool(sock):
    n = GetNum(sock)
    mas = []
    for i in range(n):
        mas.append(GetBool(sock))
    return mas

def GetPlayers(sock):
    n = GetNum(sock)
    mas = {}
    for i in range(n):
        numm = GetNum(sock)
        mas[numm] = GetCoord(sock)
    return mas

pygame.init()


sides = (600, 600)

clock = pygame.time.Clock()

KeepGoing = True

sock = socket.socket(socket.AF_INET)
print('Enter server IP (or press [Enter] to connect to your own PC)...')
IP = input()
if IP == '':
    IP = '127.0.0.1'
sock.connect((IP, 3579))

screen = pygame.display.set_mode(sides)
pygame.display.set_caption('Shooter client')

PI = GetNum(sock)
Map = GetMasCoords(sock)
MapR = GetMasInt(sock)

Background = MakeBackground(Map, MapR, (1000, 1000))

screen.blit(Background, (0, 0))
pygame.display.update()

Speed = [0, 0]

tick = 0
while KeepGoing:
    tick += 1
    screen.fill(DGREEN)
    Shot = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            KeepGoing = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                Speed[1] -= 1
            if event.key == pygame.K_s:
                Speed[1] += 1
            if event.key == pygame.K_a:
                Speed[0] -= 1
            if event.key == pygame.K_d:
                Speed[0] += 1
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                Speed[1] += 1
            if event.key == pygame.K_s:
                Speed[1] -= 1
            if event.key == pygame.K_a:
                Speed[0] += 1
            if event.key == pygame.K_d:
                Speed[0] -= 1
        if event.type == pygame.MOUSEBUTTONDOWN:
            Shot = True

    
    sock.send(EncodeSpeed(Speed).encode())

    if Shot:
        sock.send(b'1')
        ShotLocation = pygame.mouse.get_pos()
        ShotLocation = (ShotLocation[0] - sides[0] // 2, ShotLocation[1] - sides[1] // 2)
        SendCoord(ShotLocation, sock)
    else:
        sock.send(b'0')

    Players = GetPlayers(sock)
    ExplPlayers = GetMasFloat(sock)
    Bullets = GetMasCoords(sock)
    ExplBullets = GetMasFloat(sock)
    

    PPos = Players[PI]
    #print(PPos)
    #screen.blit(Background, (0, 0))
    screen.blit(Border, (sides[0] // 2 - PPos[0], sides[1] // 2 - PPos[1]))
    screen.blit(Background, (-PPos[0] + sides[0] // 2, -PPos[1] + sides[1] // 2))
    
    for i, bullet in enumerate(Bullets):
        if ExplBullets[i] != -200:
            CIndex = min(int(ExplBullets[i] // StageChangeTimeB), len(BExplosion) - 1)
            Costume = BExplosion[CIndex]
            screen.blit(Costume, GetCentrixCoord(Costume, (bullet[0] - PPos[0] + sides[0] // 2, bullet[1] - PPos[1] + sides[1] // 2)))
        else:
            screen.blit(Bullet, GetCentrixCoord(Bullet, (bullet[0] - PPos[0] + sides[0] // 2, bullet[1] - PPos[1] + sides[1] // 2)))
        #pygame.draw.circle(screen, BLACK, (bullet[0] - PPos[0] + sides[0] // 2, bullet[1] - PPos[1] + sides[1] // 2), 6)

    #print(PI)
    #print(Players)
    #pygame.draw.circle(screen, GREEN, (sides[0] // 2, sides[1] // 2), 30)
    for i, vertex in enumerate(Players.values()):
        if ExplPlayers[i] != -200:
            #print(ExplPlayers[i])
            #print(int(ExplPlayers[i] // StageChangeTimeP))
            CIndex = min(int(ExplPlayers[i] // StageChangeTimeP), len(PExplosion) - 1)
            Costume = PExplosion[CIndex]
            screen.blit(Costume, GetCentrixCoord(Costume, (vertex[0] - PPos[0] + sides[0] // 2, vertex[1] - PPos[1] + sides[1] // 2)))
        else:
            screen.blit(Player, GetCentrixCoord(Player, (vertex[0] - PPos[0] + sides[0] // 2, vertex[1] - PPos[1] + sides[1] // 2)))
    
    pygame.display.update()
    #print('Updated')
pygame.quit()
