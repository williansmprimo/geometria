# ###############################################
# Desenhando Terrenos (MDTs e Imagens)
# ###############################################

import 	sys
import os
import 	pyglet
from 	pyglet.window  	import key
import math
import random

WIN_X 	= 500
WIN_Y 	= 500

drawMDT	= True
EPS = 5
nivelMaximo = 10



# *******************************************************
# ***                                                 ***
# *******************************************************
def leImagem(arq):

	# Chama a função de leitura de uma imagem do Pyglet, 
	# passando como parametro a localização do arquivo

	img = pyglet.image.load(arq)

	# Uma vez lida a imagem o obj criado possui atributos como largura e altura da imagem
	# que pode ser consultados

	print(f'{img.width} x {img.height} => {img.width*img.height}')

	# O objeto image criado pelo Pyglet é retornado

	return img

######
class Ponto:
	def __init__(self, x, y, v = 0):
		self.x = x
		self.y = y
		self.v = v

	def meio(self, b):
		return Ponto((self.x + b.x) // 2, (self.y + b.y) // 2)

	def distancia(self, b):
		x1 = self.x - b.x
		y1 = self.y - b.y
		return math.floor(math.sqrt(x1 * x1 + y1 * y1))

class Linha:
	def __init__(self, a, b):
		self.a = a
		self.b = b

	def aEsquerda(self, c):
  		return ((self.b.x - self.a.x)*(c.y - self.a.y) - (self.b.y - self.a.y)*(c.x - self.a.x)) > 0
		#print('prod escalar: ', (self.b.x - self.a.x)*(c.y - self.a.y) - (self.b.y - self.a.y)*(c.x - self.a.x))
		#return (self.b.x - self.a.x)*(c.y - self.a.y) > (self.b.y - self.a.y)*(c.x - self.a.x)
		#return (b.x - a.x)*(c.y - a.y) > (b.y - a.y)*(c.x - a.x);
		#return random.randint(0, 10) > 5

class Triangulo:
	def __init__(self, a, b, c):
		self.a = a
		self.b = b
		self.c = c

class NoArvore:
	def __init__(self, pontos, triangulo):
		self.pontos = pontos
		self.triangulo = triangulo
		self.esquerda = None
		self.direita = None


def gerarPontosImagem(imagem):
	pontos = []
	format = 'I'
	pitch = imagem.width * len(format)
	amostras = imagem.get_image_data().get_data(format, pitch)

	for i in range(imagem.width):		
		for j in range(imagem.height):
			elevacao = amostras[i * pitch + j]
			p = Ponto(i, j, elevacao)
			pontos.append(p)

	return pontos


def dividirPontos(pontos, linha):
	esquerda = []
	direita = []
	for p in pontos:
		if(linha.aEsquerda(p)):
			esquerda.append(p)
		else:
			direita.append(p)
	# print('div: ', len(esquerda), ', ', len(direita))
	return esquerda, direita

def ordenarTriangulo(triangulo):
	a = triangulo.a
	b = triangulo.b
	c = triangulo.c
	d1 = a.distancia(b)
	d2 = b.distancia(c)
	d3 = c.distancia(a)
	print('dist: ', d1, ', ', d2, ', ', d3)
	if (d1 > d2) and (d1 > d3):
		return Triangulo(a, b, c)
	if (d2 > d1) and (d2 > d3):
		return Triangulo(b, c, a)
	if (d3 > d1) and (d3 > d2):
		return Triangulo(c, a, b)

def deveDividir(pontos, eps):

	if len(pontos) <= 1:
		print('Entrou aqui...........................................')
		return False

	contElev = [0] * 256

	eMax = 0
	eMin = 256
	eMedia = 0
	eSoma = 0

	for p in pontos:
		elevacao = p.v
		if elevacao > eMax: eMax = elevacao
		elif elevacao < eMin: eMin = elevacao
		contElev[elevacao] += 1 

	eSoma = 0
	for k in range(256):
		# eSoma += contElev[k] * k
		eSoma += contElev[k]

	eMedia = eSoma / len(pontos)

	print('dif: ', abs(eMax - eMin))
	return abs(eMax - eMin) > eps

def continuarTriangulacao(raiz, eps, nivel):
	if(nivel >= nivelMaximo):
		return
	# print("Triangulo: (", raiz.triangulo.a.x, raiz.triangulo.b.x, raiz.triangulo.c.x)
	# print(raiz.triangulo.a.y, raiz.triangulo.b.y, raiz.triangulo.c.y, ")")
	if(deveDividir(raiz.pontos, eps)):
		tri = ordenarTriangulo(raiz.triangulo)
		meio = tri.a.meio(tri.b)
		linha = Linha(tri.c, meio)
		pts_esq, pts_dir = dividirPontos(raiz.pontos, linha)
		tri_esq = ordenarTriangulo(Triangulo(tri.a, tri.c, meio))
		tri_dir = ordenarTriangulo(Triangulo(tri.b, tri.c, meio))
		raiz.esquerda = NoArvore(pts_esq, tri_esq)
		raiz.direita = NoArvore(pts_dir, tri_dir)
		continuarTriangulacao(raiz.esquerda, eps, nivel + 1)
		continuarTriangulacao(raiz.direita, eps, nivel + 1)


def iniciarTriangulacao(imagem):
	x0 = 1
	y0 = 1
	x1 = WIN_X
	y1 = 1
	x2 = WIN_X
	y2 = WIN_Y
	x3 = 1
	y3 = WIN_Y

	te = ordenarTriangulo(Triangulo(Ponto(x0, y0), Ponto(x3, y3), Ponto(x2, y2)))
	td = ordenarTriangulo(Triangulo(Ponto(x0, y0), Ponto(x1, y1), Ponto(x2, y2)))
	linha = Linha(Ponto(x0, y0), Ponto(x2, y2))

	pontos = gerarPontosImagem(imagem)
	pe, pd = dividirPontos(pontos, linha)

	raiz = NoArvore(pontos, None)
	raiz.esquerda = NoArvore(pe, te)
	raiz.direita = NoArvore(pd, td)

	continuarTriangulacao(raiz.esquerda, EPS, 1)
	continuarTriangulacao(raiz.direita, EPS, 1)

	return raiz


def imprimirTriangulo(triangulo, bat, fill, triangles):
	print("Triangulo: (", triangulo.a.x, triangulo.b.x, triangulo.c.x, triangulo.a.y, triangulo.b.y, triangulo.c.y, ")")

	x0 = triangulo.a.x
	y0 = triangulo.a.y
	x1 = triangulo.b.x
	y1 = triangulo.b.y
	x2 = triangulo.c.x
	y2 = triangulo.c.y

	tri = pyglet.shapes.Line(x0, y0, x1, y1, color=(0, 255, 0, 255), batch=bat)
	triangles.append(tri)
	#tri = pyglet.shapes.Line(x1, y1, x2, y2, color=(0, 255, 0, 255), batch=bat)
	tri = pyglet.shapes.Line(x1, y1, x2, y2, color=(0, 255, 0, 255), batch=bat)
	triangles.append(tri)
	#tri = pyglet.shapes.Line(x2, y2, x0, y0, color=(0, 0, 255, 255), batch=bat)
	tri = pyglet.shapes.Line(x2, y2, x0, y0, color=(0, 255, 0, 255), batch=bat)
	triangles.append(tri)

	# Indicador triangulo
	xt = (x0 + x1 + x2) // 3
	yt = (y0 + y1 + y2) // 3
	triangles.append(pyglet.shapes.Circle(xt, yt, 1, color=(0, 255, 0, 255), batch=bat))


def imprimir_pontos(raiz, bat, triangles):
	a = 1
	for p in raiz.pontos:
		a += 1
		if(a % 30 == 0):
			triangles.append(pyglet.shapes.Circle(p.x, p.y, 2, color=(0, 255, 0, 255), batch=bat))


def imprimirArvoreTriangular(raiz, bat, fill, tri):
	if(raiz != None):
		if(raiz.triangulo != None):
			imprimirTriangulo(raiz.triangulo, bat, fill, tri)
		#else:
		#	imprimir_pontos(raiz, bat, tri)
		imprimirArvoreTriangular(raiz.esquerda, bat, fill, tri)
		imprimirArvoreTriangular(raiz.direita, bat, fill, tri)


#####



# *******************************************************
# ***                                                 ***
# *******************************************************
if __name__ == '__main__':

	global window, MDT_Image, MDT_Triang

	# Para testar com outra imagem deve-se alterar o caminho
	#MDT_Image 	= leImagem('./DEMs/Terreno1K.png')
	MDT_Image 	= leImagem('./DEMs/Terreno0.5K.jpg')

	WIN_X = MDT_Image.width
	WIN_Y = MDT_Image.height

	window = pyglet.window.Window(WIN_X + 5, WIN_Y + 5)
	window.set_caption('Visualizando um Modelo Digital de Terreno')

	MDT_Triang 	= pyglet.graphics.Batch()

	tri = []
	raiz = iniciarTriangulacao(MDT_Image)
	imprimirArvoreTriangular(raiz, MDT_Triang, True, tri)

	@window.event
	def on_draw():
		global drawMDT

		window.clear()

		# com base no valor armazenado em "drawMDT" decide se será mostrada a imagem do terreno ou
		# sua representação como uma triangulação
		if drawMDT:
			MDT_Image.blit(0, 0, 0)
		else:
			MDT_Image.blit(0, 0, 0)
			MDT_Triang.draw()

	# key press event	
	@window.event
	def on_key_press(symbol, modifier):
		global drawMDT

		# Mapeia as teclas que deverão gerar alguma ação dentro da aplicação
		# No caso a tecla 'I' chaveia entre a imagem e a triangulação
		# enquanto que a tecla 'T' recria os elementos de desenho alternando 
		# entre triangulos preenchidos ou só com o contorno. 
		# O parametro "modifier" indica se a tecla "SHIFT" estava acionada
		# permitindo diferenciar entre 'I' e 'i'
		if symbol == key.I:
			drawMDT = True
		elif symbol == key.T:
			drawMDT = False
			os.system('clear')
			tri.clear()
			imprimirArvoreTriangular(raiz, MDT_Triang, True, tri);
			#criaTriangulacao(tri, MDT_Triang, modifier & key.MOD_SHIFT)				

	# Aqui a aplicação entra no loop de eventos e só retorna quando a tecla 'ESC' for pressionada
	pyglet.app.run()

	print("Obrigado por utilizar, espero que tenha gostado!")
