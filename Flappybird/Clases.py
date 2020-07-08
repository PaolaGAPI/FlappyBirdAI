import pygame #Modulo de pygame especializada para videojuegos de dos dimensiones
import os
import random #Modulo que da un numero aleatorio
import neat


pygame.font.init()

"""pygame transform scale hara que los pajaros se vean mas grandes para una mejor visualizacion y el pygame.image
carga las imagenes de los pajaros para hacerlo de forma animada"""
IMG_PAJARO =[pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))]
"""Se cargan el resto de imagenes"""
IMG_FONDO = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))#cargamos imagen del fondo
IMG_SUELO= pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png"))) #cargamos imagen del suelo
IMG_TUBERIA = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png"))) #cargamos imagen de la tuberia
FONT = pygame.font.SysFont("comicsans",50)

class Ave:

    Imagenes = IMG_PAJARO #carga las imagenes del pajaro
    Rotacion = 25 #Cuanto va a rotar el pajaro para dar la animacion cuando sube o cuando baja
    Vel_Rotacion = 20 #Cuanto vamos a rotar en cada frame cada vez que el pajaro se mueva
    Tiempo_Anima = 3 #Cuanto va a durar la animacion entre cada frame para que anime el movimiento de las alas

    def __init__(self, x,y):#constructor con parametros x,y que son los atributos de las coordenadas de la posicion inicial del jugador
        self.x = x
        self.y = y
        self.tilt = 0 #cuanto se a inclinado el pajaro
        self.tick_cont = 0 #
        self.vel = 0 #este atributo tiene la velocidad del pajaro que empieza en 0 ya que no se va a estar moviendo
        self.height = self.y#
        self.im_cont =0 #este atrbuto almacena el tiempo para comparar y mostrar que imagen se esta mostrando del pajaro cada vez que aumenta el tiempo, con esto se hara la animacion
        self.img = self.Imagenes[0]

    def saltar(self):
        """esto hace que el pajaro suba, pues pygame ubica las coordenadas (0,0) en la esquina superior izquierda de la pantalla
          por lo tanto para subir el valor debe ser negativo"""
        self.vel = -10.5
        self.tick_cont = 0
        self.height = self.y #este atributo va a tener el valor para saber desde que altura el pajaro esta saltando

    def movimiento(self):
        self.tick_cont +=1  #cada frame que se mueva se va contando cuantos veces se movio desde el ultimo salto
        d = self.vel*self.tick_cont + 1.5*self.tick_cont**2   #desplazamiento , es decir cuantos pixeles se va a mover el bajaro hacia arriba o hacia abajo segun la velocidad
        # -10.5*1 + 1.5 = -9...-7...-3...0....2..
        if d >= 16: #si se esta moviendo hacia abajo a mas de 16 pixeles se regulara la velocidad a que solo baje de a 16 pixeles
            d = 16
        if d<0:
            d-=2
        self.y = self.y + d  #aqui agregamos a la posicion inicial el desplazamiento ya sea hacia arriba o hacia abajo

        if d < 0 or self.y < self.height + 50: #si la distancia en la que sube no excede de los 50 pixeles, que siga subiendo desde la posicion inicial
            if self.tilt < self.Rotacion:#rotacion del pajaro mirando hacia arriba
                self.tilt = self.Rotacion
        else:
            if self.tilt > -90:#rotacion del pajaro callendo
                self.tilt -= self.Vel_Rotacion

    def draw(self,win):#Aimacion del pajaro
        self.im_cont += 1  #para animar el pajaro debemos saber cuantas veces se repite el loop del juego y muestrar la imagen segun el "tiempo" va trancurriendo
        if self.im_cont < self.Tiempo_Anima:
            self.img = self.Imagenes[0]
        elif self.im_cont < self.Tiempo_Anima*2:
            self.img = self.Imagenes[1]
        elif self.im_cont < self.Tiempo_Anima*3:
            self.img = self.Imagenes[2]
        elif self.im_cont < self.Tiempo_Anima*4:
            self.img = self.Imagenes[1]
        elif self.im_cont == self.Tiempo_Anima*4 + 1:
            self.img = self.Imagenes[0]
            self.im_cont = 0

        if self.tilt <= -80:
            self.img = self.Imagenes[1]
            self.im_cont = self.Tiempo_Anima*2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image .get_rect(center= self.img.get_rect(topleft=(self.x,self.y)).center)#centra la imagen del pajaro
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        """
         #es una funcion del modulo de pygame que te ayuda a omitir esos pixeles transparentes para tener los de la figura y
          asi hacer la colision entre las tuberias y el pajaro
        """
        return pygame.mask.from_surface(self.img)


class Suelo:

    vel = 5
    Ancho = IMG_SUELO.get_width() #funcion de pygame que te permite saber la cantidad de pixeles de ancho que tiene la imagen
    img = IMG_SUELO

    def __init__(self,y):
        self.y= y
        self.x1 = 0 #primera coordenada de la primera imagen
        self.x2 = self.Ancho

    def movimiento(self):
        self.x1 -= self.vel #genera el movimiento hacia la izquierda del suelo con el fin de dar dinamismo
        self.x2 -= self.vel

        if self.x1 + self.Ancho < 0: # bucle en donde cada vez que los frames
            self.x1 = self.x2 + self.Ancho
        if self.x2 + self.Ancho < 0:
            self.x2 = self.x1 + self.Ancho

    def draw(self,win): #se pintan los dos suelos que van a estar en bucle
        win.blit(self.img,(self.x1,self.y))
        win.blit(self.img,(self.x2,self.y))


class Tuberia:

    espacio = 200 #espacio que hay entre una tuberia y la otra
    vel = 5 #dara la ilusion de que las tuberias se estan moviendo hacia el pajaro

    def __init__(self,x):
        self.x = x
        self.height = 0

        self.arriba= 0 #se crean variables para saber en donde se van a crear las imagenes de las tuberias
        self.abajo=0
        self.tub_arriba= pygame.transform.flip(IMG_TUBERIA,False,True) #se crea la imagen de la tuberia de arriba usando el flip de pygame para revertir la imagen
        self.tub_abajo = IMG_TUBERIA #imagen de la tuberia de abajo

        self.passed = False  #si pasa el pajaro despues de una tuberia
        self.set_height()

    def set_height(self):#en este metodo se dan valores randoms para que las tuberias aparezcan en diferentes
        self.height = random.randrange(50,450)
        self.arriba = self.height - self.tub_arriba.get_height()
        self.abajo = self.height + self.espacio

    def movimiento(self):
        self.x -= self.vel #mueve la tuberia hacia la izquierda para dar la sensacion de movimiento

    def draw(self,win):
        win.blit(self.tub_arriba,(self.x,self.arriba)) #se dibujan las tuberias
        win.blit(self.tub_abajo,(self.x,self.abajo))

    def colision(self, bird1):
        bird1_mask = bird1.get_mask()
        arriba_mask = pygame.mask.from_surface(self.tub_arriba)
        abajo_mask = pygame.mask.from_surface(self.tub_abajo)

        dis_top = (self.x - bird1.x, self.arriba - round(bird1.y))
        dis_bottom = (self.x - bird1.x, self.abajo - round(bird1.y))

        punto_coliB = bird1_mask.overlap(abajo_mask, dis_bottom)
        punto_coliT = bird1_mask.overlap(arriba_mask, dis_top)

        if punto_coliB or punto_coliT:
            return True
        else:
            return False




