import math
import pygame
import time
resolution = [800, 800]
screen = pygame.display.set_mode(resolution)


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)

    def unit(self):
        if self.magnitude() == 0:
            return Vector(0, 0)
        return Vector(self.x/self.magnitude(), self.y/self.magnitude())

    def add(self, v):
        return Vector(self.x+v.x, self.y+v.y)

    def sub(self, v):
        return Vector(self.x-v.x, self.y-v.y)

    def multiply(self, n):
        return Vector(self.x*n, self.y*n)

    def dot(self, v):
        return self.x*v.x + self.y*v.y

    def vec(self):
        return [self.x, self.y]

    def components(self, v):
        dot = self.dot(v)
        divide = v.magnitude()**2
        if divide == 0:
            return Vector(0, 0), Vector(0, 0)
        parallel = v.multiply(dot/divide)
        perpendicular = self.sub(parallel)
        return parallel, perpendicular

    def drawVec(self, n, start_pos, colour):
        pos = start_pos.vec()
        pygame.draw.line(screen, colour, pos, [pos[0]+self.x*n, pos[1]+self.y*n])


class Ball:
    def __init__(self, center, radius, mass, colour, Velocity):
        self.center = Vector(center[0], center[1])
        self.radius = radius
        self.mass = mass
        self.velocity = Vector(Velocity[0], Velocity[1])
        self.friction = 0.002
        self.colour = colour

    def translate(self, v):
        self.center = self.center.add(v)

    def move(self):
        self.center = self.center.add(self.velocity)

    def vectorTo(self, pos):
        return pos.sub(self.center)

    def changeVel(self, velocity):
        self.velocity = self.velocity.add(velocity)

    def brake(self):
        self.velocity = self.velocity.multiply(0.99)

    def draw(self):
        pygame.draw.circle(screen, self.colour, self.center.vec(), self.radius, 0)
        pygame.draw.circle(screen, (0, 0, 0), self.center.vec(), self.radius, 1)
        self.velocity.drawVec(30, self.center, (0, 0, 0))


def collisionDetection(ball1, ball2):
    distance = (ball1.vectorTo(ball2.center)).magnitude()
    if distance < (ball1.radius + ball2.radius):
        magnitude = (ball1.radius+ball2.radius) - distance
        return True, magnitude

    center = ball1.center.vec()
    radius = ball1.radius
    velocity = ball1.velocity.vec()
    if center[0] + radius > resolution[0]:
        depth = resolution[0] - (center[0] + radius)
        ball1.translate(Vector(depth, 0))
        velocity[0] = velocity[0]*-1
    if center[0] - radius < 0:
        depth = 0 - (center[0] - radius)
        ball1.translate(Vector(depth, 0))
        velocity[0] = velocity[0] * -1
    if center[1] + radius > resolution[1]:
        depth = resolution[1] - (center[1] + radius)
        ball1.translate(Vector(0, depth))
        velocity[1] = velocity[1] * -1
    if center[1] - radius < 0:
        depth = 0 - (center[1] - radius)
        ball1.translate(Vector(0, depth))
        velocity[1] = velocity[1] * -1
    ball1.velocity = Vector(velocity[0], velocity[1])
    return False, 0


def collisionResponse(balls):
    excluded = []
    for i in balls:
        for j in balls:
            if i != j:
                comparison = {i, j}
                if comparison in excluded:
                    continue
                excluded.append(comparison)
                collided, magnitude = collisionDetection(i, j)
                if collided:
                    print(collided)
                    vector = i.vectorTo(j.center).unit()
                    vector = vector.multiply(-magnitude)
                    i.translate(vector)

                    iVel = i.velocity
                    iVec = i.vectorTo(j.center)
                    jVel = j.velocity
                    jVec = j.vectorTo(i.center)

                    iPar, iPer = iVel.components(iVec)
                    jPar, jPer = jVel.components(jVec)

                    m1 = i.mass
                    v1 = iPar.magnitude()
                    m2 = j.mass
                    v2 = jPar.magnitude()

                    iUnit = iVec.unit()
                    jUnit = jVec.unit()

                    v1Prime = ((m2 * v2 * 2) + (m1 * v1) - (m2 * v1)) / (m1 + m2)
                    v2Prime = ((m1 * v1 * 2) + (m2 * v2) - (m1 * v2)) / (m1 + m2)

                    iPar = iUnit.multiply(-v1Prime)
                    jPar = jUnit.multiply(-v2Prime)

                    i.velocity = iPer.add(iPar)
                    j.velocity = jPer.add(jPar)


def update(balls):
    for ball in balls:
        ball.move()
        ball.draw()


def applyFriction(balls):
    for ball in balls:
        normal = ball.mass * -1
        unit = ball.velocity.unit()
        friction = normal * ball.friction
        acceleration = friction / ball.mass
        acceleration = unit.multiply(acceleration)
        newVelocity = ball.velocity.add(acceleration)
        if newVelocity.magnitude() > ball.velocity.magnitude():
            ball.velocity = Vector(0, 0)
        else:
            ball.velocity = newVelocity


bList = []
cue = Ball((700, 350), 29, 29, (255, 255, 255), [0, 0])
bList.append(cue)

for j in range(5):
    for i in range(5-j):
        x = 100+j*50
        y = 230+(j*30)+(i*60)
        new = Ball((x, y), 30, 30, (255, 0, 0), [0, 0])
        bList.append(new)

running = True
while running:
    screen.fill((0, 160, 50))
    keys = pygame.key.get_pressed()
    applyFriction(bList)
    update(bList)
    collisionResponse(bList)

    if keys[pygame.K_w]:
        bList[0].changeVel(Vector(0, -0.02))
    if keys[pygame.K_s]:
        bList[0].changeVel(Vector(0, 0.02))
    if keys[pygame.K_d]:
        bList[0].changeVel(Vector(0.02, 0))
    if keys[pygame.K_a]:
        bList[0].changeVel(Vector(-0.02, 0))
    if keys[pygame.K_SPACE]:
        bList[0].brake()

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if keys[pygame.K_ESCAPE]:
        running = False

pygame.quit()
