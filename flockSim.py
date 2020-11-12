import pygame, time, random 
from pygame_widgets import Slider, TextBox, Button
from os import system 
import numpy as np
from numpy.linalg import norm 

POPSIZE = 150
BOIDSIZE = (1,1)
init_speed = 5
perRadius = [50,40,40]
weights = np.array([.5,.2,.2])

pygame.init()
fps = 30
clock = pygame.time.Clock()
white = (255,255,255)
black = (0,0,0)
peach=(255,218,185)
width, height = 1200,600
displaySize = (width, height)
div = 0.8
flockDisplay = pygame.display.set_mode(displaySize)
pygame.display.set_caption('Flocking of Birds')
pygame.mouse.set_cursor(*pygame.cursors.tri_left)
p1_cam = pygame.Rect(0, 0, (div*width)//1, height)
p2_cam = pygame.Rect((div*width)//1, 0, width-(div*width)//1, height)
canvas1 = pygame.Surface(p1_cam[2:])
canvas2 = pygame.Surface(p2_cam[2:])
pygame.draw.rect(flockDisplay, black, p1_cam,width=4)
pygame.draw.rect(flockDisplay, black, p2_cam,width=1)
forceNames = ["Alignment","Cohesion","Separation"]
params = ["Perception Radius", "Force Weights"]

reset_button = Button(
            flockDisplay, p2_cam.x+150, 40+(6+1)*70, 70, 40, text='Reset',
            fontSize=20, margin=20,
            inactiveColour=(128, 128, 128),
            hoverColour=(255,255,255),
            pressedColour=(153, 255, 255), radius=2,
            onClick=lambda:True
         )

font1 = pygame.font.Font('freesansbold.ttf', 16)
head_texts, head_rects, side_texts, side_rects = [], [], [], []
k=0
for i,param in enumerate(params):
	head_texts.append(font1.render(param, True, white, black))  
	head_rects.append(head_texts[0].get_rect())  
	head_rects[-1].center = [p2_cam.x+120,20+250*i]
	font2 = pygame.font.Font('freesansbold.ttf', 10)
	for j,force in enumerate(forceNames):
		force = force + " : "
		side_texts.append(font2.render(force, True, white, black))  
		side_rects.append(head_texts[0].get_rect())  
		side_rects[-1].center = [p2_cam.x+100,60+70*k+40*i]
		k+=1

class Boid(pygame.sprite.Sprite):
	def __init__(self, pos, speed, theta, acc=0):
		super().__init__()
		self.vel = np.array([speed*np.cos(theta), speed*np.sin(theta)])
		self.acc = np.array([acc*np.cos(theta), acc*np.sin(theta)])
		self.images = []
		self.val = 0
		for i in range(2):
			self.image = pygame.image.load(f"bird{i+1}.png").convert()
			self.image.set_colorkey(white)
			self.image = pygame.transform.scale(self.image, (20,20))
			self.images.append(self.image)
		self.sprite = self.images[self.val]
		img = self.sprite.copy()
		#rotangle = -(np.arctan(self.vel[1]/self.vel[0])*180./np.pi+180*self.sig(vel[0])+90)
		self.image = pygame.transform.rotate(img, -90-theta*180./np.pi)
		self.rect = self.image.get_rect()
		self.rect.centerx = pos[0]
		self.rect.centery = pos[1]
		self.maxSpeed = 5.
	
	def sig(self,val):
		return 0 if val>0 else 1

	def onscreen(self, res):
		if self.rect.centerx > res.width-10:
			self.rect.centerx = 10
		elif self.rect.centerx < 10:
			self.rect.centerx = res.width-10
		if self.rect.centery > res.height-10:
			self.rect.centery = 10
		elif self.rect.centery < 10:
			self.rect.centery = res.height-10

	def update(self, forces, weights):
		self.acc = np.dot(weights, forces)
		self.vel += self.acc
		self.vel = self.maxSpeed*self.vel/norm(self.vel)
		self.rect.center += self.vel
		self.val = not self.val
		self.sprite = self.images[self.val]
		img = self.sprite.copy()
		rotangle = -(np.arctan(self.vel[1]/self.vel[0])*180./np.pi+180*self.sig(self.vel[0])+90)
		self.image = pygame.transform.rotate(img, rotangle)
		self.rect = self.image.get_rect(center = self.rect.center)

class BoidGroup(pygame.sprite.Group):
	def __init__(self,num,res):
		super().__init__()
		for i in range(num):
			pos = np.array([(res.width-10)*random.random()+10, (res.height-5)*random.random()+10])
			speed, theta = init_speed, 2*np.pi*random.random()
			boid = Boid(pos, speed, theta)
			self.add(boid)
		self.res = res

	def dist(self,s1,s2):
		return np.sqrt((s1[0]-s2[0])**2+(s1[1]-s2[1])**2)

	def update(self, perRadius, weights):
		boids = []
		for boid in self.sprites():
			count = [0,0,0]
			forces = np.zeros((3,2))
			boid.onscreen(self.res)
			for other in self.sprites():
				distance = self.dist(boid.rect.center,other.rect.center)
				if other != boid:
					if distance < perRadius[0]:
						forces[0] += other.vel
						count[0] += 1
					if distance < perRadius[1]:
						forces[1] += np.array(other.rect.center)
						count[1] += 1
					if distance < perRadius[2]:
						forces[2] += (np.array(boid.rect.center)-np.array(other.rect.center))
						count[2] += 1
			if count[0] > 0:
				forces[0] = forces[0]/count[0]-boid.vel
			if count[1] > 0:
				forces[1] = forces[1]/count[1]-boid.rect.center-boid.vel
			if count[2] > 0:
				forces[2] = forces[2]/count[2]-boid.vel
			boid.update(forces, weights)


def setup():
	Boid_List = BoidGroup(POPSIZE, p1_cam)
	sliders, values = [], []
	for i in range(6):
		if i < 3:
			sliders.append(Slider(flockDisplay, p2_cam.x+30, (i+1)*70, 
				(width-div*width)//1-60, 16, min=0., max=100., step=1,
				colour = white, handleRadius = 8, initial = perRadius[i] ))
			values.append(TextBox(flockDisplay, p2_cam.x+190, (i+1)*70-25, 
				20, 20, fontSize=10, colour=black, textColour=white))
		else:
			sliders.append(Slider(flockDisplay, p2_cam.x+30, 40+(i+1)*70,
			 (width-div*width)//1-60, 16, min=0., max=1., step=0.01,
			 colour = white, handleRadius = 8, initial = weights[i%3] ))
			values.append(TextBox(flockDisplay, p2_cam.x+180, 40+(i+1)*70-25, 
				20, 20, fontSize=10, colour=black, textColour=white))
	return Boid_List, sliders, values



def GameLoop():
	run = True
	reset = False
	Boid_List, sliders, values = setup()
	while run:
		if reset:
			Boid_List, sliders, values = setup()
			reset = False
		canvas1.fill(white)
		canvas2.fill(black)
		flockDisplay.blit(canvas1,p1_cam)
		flockDisplay.blit(canvas2,p2_cam)
		Boid_List.draw(flockDisplay)
		Boid_List.update(perRadius, weights)
		for i,text in enumerate(head_texts):
			flockDisplay.blit(text, head_rects[i])
		for i,text in enumerate(side_texts):
			flockDisplay.blit(text, side_rects[i])
		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				run = False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_q:
					run = False
		for i in range(6):
			sliders[i].listen(events)
			sliders[i].draw()
			val = sliders[i].getValue()
			if i < 3:
				perRadius[i] = val
				values[i].setText("{:d}".format(val))
			else:
				weights[i%3] = val
				values[i].setText("{:.2f}".format(val))
			values[i].draw()
		reset = reset_button.listen(events)
		reset_button.draw()
		pygame.display.update()
		clock.tick(fps)
	pygame.quit()
	quit()

if __name__ == "__main__":
	GameLoop()