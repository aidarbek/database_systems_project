 #!/usr/bin/env python # -*- coding: utf-8 -*-
import string
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import euclidean_distances
from sklearn import datasets, linear_model
import codecs
import numpy as np
from scipy.sparse import coo_matrix, vstack
def normalize(s):
	sentences = s.split(".")
	ans = []
	for s in sentences:
		res = re.sub("[^\w]", " ",  s.lower())
		ans.append(' '.join(res.split()))
	return ans

f = open("train.txt", "rb")
answers = f.read()
f.close()

answers = answers.replace("\r", "\n").split("\n\n")
answers = [ans for ans in answers if len(re.sub("[^\w]", " ",  ans.lower()).split()) >= 5]
norm_answers = [normalize(ans) for ans in answers]
Y = []
X = []
for i in range(len(norm_answers)):
	for sentence in norm_answers[i]:
		Y.append(i)
		X.append(sentence)
X = X * 1

vectorizer = CountVectorizer()
train_answers = vectorizer.fit_transform(X)

Y = np.array(Y)

# Create linear regression object
regr = linear_model.LogisticRegression(C=1e5)

# Train the model using the training sets
regr.fit(train_answers, Y)


def generate_answer(userInput):
	no_ans = "Sorry, I didn't understand your request"
	try:
		userInput = unicode(userInput, "utf-8")
		words = " ".join(normalize(userInput))
		user_vector = vectorizer.transform([words])
		ans = answers[regr.predict(user_vector)[0]]
		prob = regr.predict_proba(user_vector[0])
		if np.max(prob) < 0.02:
			ans = no_ans
		return ans
	except Exception as e:
		return no_ans
def main():
	print(generate_answer("What is JSC?"))
	print("------")
	print(generate_answer("What is LLP?"))
	print("------")
	print(generate_answer("What is Kazakhstan's rank in the Ease of Doing Business Rating?"))
	print("------")
	print(generate_answer("When are Kazakhstan business offices open?")) # x
	print("------")
	print(generate_answer("What countries are included in trial visa-free regime?"))
	print("------")
	print(generate_answer("What is the minimum capital requirement for LLP?"))
	print("------")
	print(generate_answer("Tell me about JSC?"))
	print("------")
	print(generate_answer("What is Kazakhstan's GDP growth from 2003 to 2015?"))
	print("------")
	print(generate_answer("What is the place of Kazakhstan in Ease of Doing Business rating and according to what?"))
	print("------")
	print(generate_answer("What does include the special economic zone (SEZ) Khorgos-Eastern Gate"))
	print("------")
	print(generate_answer("When the Republic of Kazakhstan gained the independence"))
	print("------")
	print(generate_answer("When Kazakhstan offices are open?"))  # x
	print("------")
	print(generate_answer("Time zones of Kazakhstan in relevance to Greenwinch zone"))
	print("------")
	print(generate_answer("What is the principle of Kazakhstan state registration?")) # x
	print("------")
	print(generate_answer("In what currency can bank accounts be opened?"))
	print("------")
	print(generate_answer("What is the state registration fee?"))
	print("------")
	print(generate_answer("What is included in taxable income?"))
	print("------")
	print(generate_answer("Length of maternity leave"))
	print("------")
	print(generate_answer("additional paid vacation dated for people working in hazardous conditions"))
	print("------")
	print(generate_answer("how work permits are granted?"))
	print("------")
	print(generate_answer("What does VAT mean?"))
	print("------")
	print(generate_answer(u"КОгда у Айдарбека месячные?"))
	print("------")

if __name__ == "__main__":
	main()