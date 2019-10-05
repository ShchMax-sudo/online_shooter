import socket
import threading
import time
import struct
from random import randint

MapSize = (1000, 1000)

Bullets = []
BSpeeds = []
BIndexes = []
UpdateTimes = []
Players = {}
BExplTimes = []
PExplTimes = []

BTimeExplosion = 1
PTimeExplosion = 2

SPEEDMUL = 240
BSPEEDMUL = SPEEDMUL * 3

PlayerRadius = 30
BulletRadius = 6
IsBulletUpdate = True

def ReadMap(FileName):
    file = open('Maps/' + FileName, 'r')
    n = int(file.readline())
    coords = []
    Radiuses = []
    StartLocations = []
    for i in range(n):
        coords.append([int(x) for x in file.readline().split()])
    for i in range(n):
        Radiuses.append(int(file.readline()))
    n = int(file.readline())
    for i in range(n):
        StartLocations.append([int(x) for x in file.readline().split()])
    return (coords, Radiuses, StartLocations)

def DecodeSpeed(code):
    comand = [0, 0]
    if code[0] == 'a':
        comand[0] = 1
    elif code[0] == 'c':
        comand[0] = -1
    if code[1] == 'a':
        comand[1] = 1
    elif code[1] == 'c':
        comand[1] = -1
    return comand

def SendSimple(key, value, sock):
    sock.send(struct.Struct(key).pack(valaue))

def GetSimple(key, sock):
    return struct.Struct(key).unpack(sock.recv(struct.Struct(key).size))

def SendBool(n, sock):
    sock.send(b'1' if n else b'0')

def SendNum(n, sock):
    sock.send(struct.Struct('i').pack(int(n)))

def SendFloat(n, sock):
    sock.send(struct.Struct('f').pack(n))

def SendCoord(coords, sock):
    sock.send(struct.Struct('ii').pack(*[int(x) for x in coords]))

def GetCoord(sock):
    inp = sock.recv(struct.Struct('ii').size)
    #print(inp)
    return struct.Struct('ii').unpack(inp)

def SendStr(string, sock):
    SendNum(len(string))
    sock.send(struct.Struct(str(len(string)) + 's').pack(string))

def SendMasCoords(mass, sock):
    mas = tuple(mass)
    SendNum(len(mas), sock)
    for elem in mas:
        SendCoord(elem, sock)

def SendMasInt(mass, sock):
    mas = tuple(mass)
    SendNum(len(mas), sock)
    for i in range(len(mas)):
        SendNum(mas[i], sock)

def SendMasFloat(mass, sock):
    mas = tuple(mass)
    SendNum(len(mas), sock)
    for i in range(len(mas)):
        SendFloat(mas[i], sock)

def SendMasBool(mass, sock):
    mas = tuple(mass)
    SendNum(len(mas), sock)
    for i in range(len(mas)):
        SendBool(mas[i], sock)

def SendPlayers(playerss, sock):
    players = playerss.copy()
    SendNum(len(players.items()), sock)
    for i in players.keys():
        SendNum(i, sock)
        SendCoord(players[i], sock)

def Dist(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

def ColisionCheck(positions, index, coords, radius):
    for i, vertex in positions.items():
        if i != index and Dist(vertex, coords) <= radius * 2:
            return (True, (-vertex[0] + coords[0], -vertex[1] + coords[1]), Dist(vertex, coords), radius * 2, i)
    return (False, (0, 0), 0, 0, -1)

def LandColisionCheck(Map, Radiuses, Coords, PRadius):
    for i in range(len(Map)):
        if Dist(Coords, Map[i]) <= PRadius + Radiuses[i]:
            return (True, (-Map[i][0] + Coords[0], -Map[i][1] + Coords[1]), Dist(Coords, Map[i]), Radiuses[i] + PRadius)
    return (False, (0, 0), 0, 0)

print('Enter name of map file without format')
MAP, MAPR, StartLocs = ReadMap(input() + '.fls')

def BulUpdate():
    global Bullets, Players, BSpeeds, IsBulletUpdate, BIndexes
    if IsBulletUpdate:
        IsBulletUpdate = False
        for i in range(len(Bullets))[::-1]:
            NewTime = time.monotonic()
            DeltaTime = NewTime - UpdateTimes[i]
            UpdateTimes[i] = NewTime
            if BExplTimes[i] != -200:
                if BExplTimes[i] <= 0:
                    BSpeeds.pop(i)
                    Bullets.pop(i)
                    UpdateTimes.pop(i)
                    BExplTimes.pop(i)
                else:
                    BExplTimes[i] -= DeltaTime
            else:
                InBorders = (0 <= Bullets[i][0] <= MapSize[0] and 0 <= Bullets[i][1] <= MapSize[1])
                LColResult = LandColisionCheck(MAP, MAPR, Bullets[i], BulletRadius)
                if (not InBorders) or LColResult[0]:
                    BExplTimes[i] = BTimeExplosion
                else:
                    PColResult = ColisionCheck(Players, -1, Bullets[i], (BulletRadius + PlayerRadius) / 2)
                    #print(PColResult)
                    if PColResult[0]:
                        BExplTimes[i] = BTimeExplosion
                        if PExplTimes[PColResult[4]] == -200:
                            PExplTimes[PColResult[4]] = PTimeExplosion
                    else:
                        #print(Bullets, i)
                        #print(BSpeeds, i)
                        Bullets[i][0] += BSpeeds[i][0] * DeltaTime * BSPEEDMUL
                        Bullets[i][1] += BSpeeds[i][1] * DeltaTime * BSPEEDMUL
        IsBulletUpdate = True

def ClientWork(PI, conn):
    global Players,  Bullets, BIndexes, IsBulletUpdate
    tm = time.monotonic()
    with conn:

        conn.settimeout(3)
        
        SendNum(PI, conn)
        SendMasCoords(MAP, conn)
        SendMasInt(MAPR, conn)
        try:
            while True:
                Comand = DecodeSpeed(conn.recv(2).decode())
                #print(comand)
                if abs(Comand[0] * Comand[1]) != 0:
                    Comand[0] /= 2 ** 0.5
                    Comand[1] /= 2 ** 0.5

                timemonot = time.monotonic()
                DeltaTime = timemonot - tm
                tm = timemonot
                #print(PExplTimes)
                if PExplTimes[PI] == -200:
                    if conn.recv(1) == b'1':
                        #print('Shot')
                        ShotLocation = GetCoord(conn)
                        ShotDist = Dist((0, 0), ShotLocation)
                        BSpeed = [ShotLocation[0] / ShotDist, ShotLocation[1] / ShotDist]
                        BSpeeds.append(BSpeed)
                        Shift = 20
                        Bullets.append([Players[PI][0] + BSpeed[0] * (PlayerRadius + BulletRadius + Shift), Players[PI][1] + BSpeed[1] * (PlayerRadius + BulletRadius + Shift)])
                        UpdateTimes.append(time.monotonic())
                        BExplTimes.append(-200)
                        #print(Bullets[-1])
                        #BIndexes.append(PI)
                    
                    #print(Comand)
                    TestLocation = [0, 0]
                    TestLocation[0] = Players[PI][0] + Comand[0] * DeltaTime * SPEEDMUL
                    TestLocation[1] = Players[PI][1] + Comand[1] * DeltaTime * SPEEDMUL
                    PlayerColisionResult = ColisionCheck(Players, PI, TestLocation, PlayerRadius)
                    MapColisionResult = LandColisionCheck(MAP, MAPR, TestLocation, PlayerRadius)
                    while PlayerColisionResult[0] or MapColisionResult[0]:
                        if PlayerColisionResult[0]:
                            #print('PlayerColision')
                            TestLocation[0] += (PlayerColisionResult[1][0] / PlayerColisionResult[2]) * (PlayerColisionResult[3] - PlayerColisionResult[2] + 1)
                            TestLocation[1] += (PlayerColisionResult[1][1] / PlayerColisionResult[2]) * (PlayerColisionResult[3] - PlayerColisionResult[2] + 1)
                        elif MapColisionResult[0]:
                            #print('MapColision')
                            TestLocation[0] += (MapColisionResult[1][0] / MapColisionResult[2]) * (MapColisionResult[3] - MapColisionResult[2] + 1)
                            TestLocation[1] += (MapColisionResult[1][1] / MapColisionResult[2]) * (MapColisionResult[3] - MapColisionResult[2] + 1)
                        #print(TestLocation)
                        PlayerColisionResult = ColisionCheck(Players, PI, TestLocation, PlayerRadius)
                        MapColisionResult = LandColisionCheck(MAP, MAPR, TestLocation, PlayerRadius)
                        #print(ColisionCheck(Players, PI, TestLocation, PlayerRadius), LandColisionCheck(MAP, MAPR, TestLocation, PlayerRadius))
        ##            if PlayerColisionResult[0]:
        ##                TestLocation[0] = TestLocation[0] + (PlayerColisionResult[1][0] / PlayerColisionResult[2]) * (PlayerColisionResult[3] - PlayerColisionResult[2])
        ##                TestLocation[1] = TestLocation[1] + (PlayerColisionResult[1][1] / PlayerColisionResult[2]) * (PlayerColisionResult[3] - PlayerColisionResult[2])
        ##            elif MapColisionResult[0]:
        ##                TestLocation[0] = TestLocation[0] + (MapColisionResult[1][0] / MapColisionResult[2]) * (MapColisionResult[3] - MapColisionResult[2])
        ##                TestLocation[1] = TestLocation[1] + (MapColisionResult[1][1] / MapColisionResult[2]) * (MapColisionResult[3] - MapColisionResult[2])
        ##            if PlayerColisionResult[0]:
        ##                TestLocation[0] = TestLocation[0] + PlayerColisionResult[1][0] / 10
        ##                TestLocation[1] = TestLocation[1] + PlayerColisionResult[1][1] / 10
        ##            elif MapColisionResult[0]:
        ##                TestLocation[0] = TestLocation[0] + MapColisionResult[1][0] / 10
        ##                TestLocation[1] = TestLocation[1] + MapColisionResult[1][1] / 10
                    Players[PI] = TestLocation
                else:
                    
                    if conn.recv(1) == b'1':
                        GetCoord(conn)
                    
                    if PExplTimes[PI] >= 0:
                        PExplTimes[PI] -= DeltaTime
                    else:
                        Players[PI] = StartLocs[randint(0, len(StartLocs) - 1)]
                        PExplTimes[PI] = -200
                BulUpdate()
                IsBulletUpdate = False
                SendPlayers(Players, conn)
                #print(PExplTimes)
                SendMasFloat(PExplTimes, conn)
                #print(Bullets)
                SendMasCoords(Bullets, conn)
                SendMasFloat(BExplTimes, conn)
                IsBulletUpdate = True
        except socket.timeout:
            print('Client disconnected')
            Players.pop(PI)
            return

port = 3579
sock = socket.socket(socket.AF_INET)
IP = socket.gethostbyname(socket.gethostname())
print('Work started...')
sock.bind((IP, port))
print('Server IP -', IP, 'Port -', port)
sock.listen(1)
Index = 0
while True:
    print('Waiting for clients...')
    conn, addr = sock.accept()
    print('New client -', addr)
    StartLocation = StartLocs[randint(0, len(StartLocs) - 1)]
    Players[Index] = StartLocation
    PExplTimes.append(-200)
    print(Players)
    Upd = threading.Thread(target = ClientWork, args = (Index, conn))
    Upd.start()
    Index += 1
