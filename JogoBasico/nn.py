import keras
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from keras.utils.np_utils import to_categorical
import numpy as np
from random import randint

import matplotlib.pyplot as plt

from game import controlled_run

# importando as variaveis do jogo game.py
from game import DO_NOTHING
from game import JUMP

# variaveis que limita o numero de jogos da Rede neural
total_number_of_games = 100
games_count = 0

# Dados da Rede nautal, sendo eles os pesos para calcular se uma ação deve ou não ser executada.
x_train = np.array([])
y_train = np.array([])

really_huge_number = 1000

# Frequencia de treinamento, a cada 10 jogos, a rede neural pega o melhor deste 10, e o usa como referencia para os
# proximo, ate concluir outros 10, e repetir o procedimento até concluit todos os jogos.
train_frequency = 10

# Código da rede neural utilizando Keras
# crindo um modelo sequancial keras
model = Sequential()

# adicionando as camadas no modelo, utilizando dense.
# primeiro parametro indica a camada que esta mexendo
# segundo parametro de input_dim, indica o numero de entradas, ou seja a camada de entrada tem apenas 1 nó.
# o parametro de activation, indica a função que esta sendo utilizado naquela camada, neste caso, sigmoid e softmax.
model.add(Dense(1, input_dim=1, activation='sigmoid'))
model.add(Dense(2, activation='softmax'))

# aqui ocorre o ajuste dos valores, em que ocorre sempre a mudança de 0.1 e com o modo preciso, a função vai ajustar
# até o mais proximo possível antes do erro com aproximação de 0.1.
# a categoria crossentropy é utilizado bastante para verificação de probabilidade, útil de caso de erros em camadas
# extensas, para visualizar a probabilidade de acerto e verificar as probabilidade de cada erro.
model.compile(Adam(lr=0.1), loss='categorical_crossentropy', metrics=['accuracy'])

# funções para criação do grafico e seu loyout do matplotlib
fig, _ = plt.subplots(ncols=1, nrows=3, figsize=(6, 6))
fig.tight_layout()

all_scores = []
average_scores = []
average_score_rate = 10
all_x, all_y = np.array([]), np.array([])

class Wrapper(object):

	def __init__(self):
		# Start the game
		controlled_run(self, 0)

	@staticmethod
	def visualize():
		global all_x
		global all_y

		global average_scores
		global all_scores

		global x_train
		global y_train

		#Criação da tabelas para melhor visualização do processo de crescimento.
		plt.subplot(3, 1, 1)
		x = np.linspace(1, len(all_scores), len(all_scores))
		plt.plot(x, all_scores, 'o-', color = 'r')
		plt.xlabel("Numero de Jogos")
		plt.ylabel("Pontos")
		plt.title("Pontos por jogos")

		plt.subplot(3, 1, 2)
		plt.scatter(x_train[y_train==0], y_train[y_train==0], color='r', label='Stay still')
		plt.scatter(x_train[y_train==1], y_train[y_train==1], color='b', label='Jump')
		plt.xlabel('Distância do inimigo ao do pulo')
		plt.ylabel("Ponto obtido pelo pulo")
		plt.title('Treinamento de dados (precisão)')

		plt.subplot(3, 1, 3)
		x2 = np.linspace(1, len(average_scores), len(average_scores))
		plt.plot(x2, average_scores, 'o-', color = 'b')
		plt.xlabel("Jogos")
		plt.ylabel("Pontos")
		plt.title("Media de pontos a cada 10 jogos")

		plt.pause(0.001)

	def control(self, values):
		global x_train
		global y_train

		global games_count

		global model

		# Caso não tenha inimigo por perto, faça nada, até que pareça o inimig, entçao faz o calculo com rede neural
		# para calcular a próxima ação.
		if values['closest_enemy'] == -1:
			return DO_NOTHING
		# Para quando inimigo esta aproximando, calcule a próxima ação.
		if values['old_closest_enemy'] is not -1:
			if values['score_increased'] == 1:
				x_train = np.append(x_train, [values['old_closest_enemy']/really_huge_number])
				y_train = np.append(y_train, [values['action']])

		# predição feita pela rede neural, utilizando o vetor de np, que possui os valores de x_train, para fazer as
		# predições, das proximas ações com base do que ja aprendeu.
		prediction2 = model.predict(np.array([values['closest_enemy']/really_huge_number]))
		prediction = model.predict_classes(np.array([[values['closest_enemy']/really_huge_number]]))

		# sistema de trazer numeros aleatorio para acontecer alguns casos diferentes, para ver se melhora ou não.
		r = randint(0, 100)
		# o comportamento vai de modo alatório até que atinja x = 50, ou seja na geração 50, para de ter comportamentos
		# aleatórios
		random_rate = 50*(1 - games_count/50)

		#ação contraria pelo numero aleatorio obtido anteriormente
		if r < random_rate:
			if prediction == DO_NOTHING:
				return JUMP
			else:
				return DO_NOTHING
		#faz a ação devida obtida pelo modelo criado
		else:
			if prediction == JUMP:
				return JUMP
			else:
				return DO_NOTHING

	def gameover(self, score):
		global games_count
		global x_train
		global y_train 
		global model

		global all_x
		global all_y
		global all_scores
		global average_scores
		global average_score_rate

		games_count += 1

		# mosntando os valores de x_train e y_train
		print(x_train)
		print(y_train)

		# adicionando os valores de x e y train, em um vetor, para utilizar posteriormente
		all_x = np.append(all_x, x_train)
		all_y = np.append(all_y, y_train)

		all_scores.append(score)

		Wrapper.visualize()

		#formula para colocar na tabela o media de pontos a nas partidas
		if games_count is not 0 and games_count % average_score_rate is 0:
			average_score = sum(all_scores)/len(all_scores)
			average_scores.append(average_score)

		if games_count is not 0 and games_count % train_frequency is 0:
			# formula para colocar na tabela da frequencia de treino
			y_train_cat = to_categorical(y_train, num_classes = 2)

			print(x_train)

			# Treinar a rede neural
			model.fit(x_train, y_train_cat, epochs = 50, verbose=1, shuffle=1)

			# Resetar o treinamento
			x_train = np.array([])
			y_train = np.array([])

		if games_count>=total_number_of_games:
			# Sair do jogo quando atingir o limite de jogos
			return

		# Começando outro jogo
		controlled_run(self, games_count)

if __name__ == '__main__':
	w = Wrapper()
