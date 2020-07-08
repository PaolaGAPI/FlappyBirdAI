from Clases import * #importa todas las clases

VEN_ANCHO = 500 #Ancho de la ventana de videojuego
VEN_LARGO = 800 #Largo de la ventana del videojueg

def draw_window(birds,win,suelo,tuberia,puntaje):#dibuja los objetos,el orden importa a la hora de dibujarlos
    win.blit(IMG_FONDO,(0,0))# blit sirve para dibujar en pygame ciertas imagenes como el fondo
    for tuberias in tuberia:
        tuberias.draw(win) # dibuja la tuberia
    texto = FONT.render("Puntaje: "+ str(puntaje),1,(255,255,255))
    win.blit(texto,(VEN_ANCHO - 10 - texto.get_width(),10))

    suelo.draw(win)  # dibuja el suelo
    for bird1 in birds:
        bird1.draw(win)#dibuja al pajaro

    pygame.display.update()#se va actualizando

def main(genomes,config):
    nets = []
    ge = []
    birds = []

    for _,g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Ave(230, 350))
        g.fitness = 0
        ge.append(g)

    suelo = Suelo(730) # se crea el obbjeto suelo y se pasa el parametro inicial en la coordenada y
    tuberia =[Tuberia(600)]# se crea las tuberias
    win = pygame.display.set_mode((VEN_ANCHO,VEN_LARGO))#se crea la ventana de juego, opcion del modulo de pygame
    pygame.display.set_caption(" FlappyBirdAI")
    reloj = pygame.time.Clock()#pygame tiene una opcion en donde se puede configurar como pasa el tiempo encuanto frames
    puntaje = 0
    run = True

    while run: #mantiene la ventana actualizando si esta en true
        reloj.tick(30)#hace que el pajaro no caiga tan rapido y le da una animacion mas lenta
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        tub_ind = 0
        if len(birds) > 0:
            if len(tuberia) > 1 and birds[0].x > tuberia[0].x + tuberia[0].tub_arriba.get_width():
                tub_ind = 1
        else:
            run = False
            break

        for x,bird1 in enumerate(birds):
            bird1.movimiento()
            ge[x].fitness += 0.1

            output = nets[x].activate((bird1.y, abs(bird1.y - tuberia[tub_ind].height),abs(bird1.y - tuberia[tub_ind].abajo)))

            if output[0] > 0.5:
                bird1.saltar()


        añadir_tub = False
        quitar = []

        for tuberias in tuberia:
            for x,bird1 in enumerate(birds):
                if tuberias.colision(bird1):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not tuberias.passed and tuberias.x<bird1.x:
                    tuberias.passed = True
                    añadir_tub = True

            if tuberias.x + tuberias.tub_arriba.get_width() < 0:
                quitar.append(tuberias)

            tuberias.movimiento()

        if añadir_tub:
            puntaje +=1
            for g in ge:
                g.fitness += 5
            tuberia.append(Tuberia(600))
        for r in quitar:
            tuberia.remove(r)

        for x,bird1 in enumerate(birds):
            if bird1.y + bird1.img.get_height() > 730 or bird1.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        suelo.movimiento()
        draw_window(birds,win,suelo,tuberia,puntaje)


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation
                                ,config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    ganador = p.run(main, 50)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,"config-feedforward.txt")
    run(config_path)



