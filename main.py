import os
import re
import csv
from typing_extensions import Text
import requests
import requests_cache
from bs4 import BeautifulSoup

# =============== Setting ================
class Setting:
	start = 120
	end = 130
	meaning_limit  = 3
	synonyms_limit = 3
# ========================================
	show_debug = True
	meaning_chr_limit  = 10
	synonyms_chr_limit = 25

class Scraping:
	def __init__(self, index: int, word: str):
		self.index = index
		self.word = word

	def getMeaning(self) -> tuple:
		url = f"https://ejje.weblio.jp/content/{self.word}"
		response = requests.get(url)
		html = response.text
		soup = BeautifulSoup(html, "html.parser")
		if " " in self.word:
			parts = "フレーズ"
		else:
			partsItems = soup.find_all("div", class_="KnenjSub")
			parts = partsItems[0].get_text(strip=True) if len(partsItems) > 0 else ""
			searchList = ["名", "動", "形", "副", "前", "接"]
			partsList = ["名詞", "動詞", "形容詞", "副詞", "前置詞", "接続詞"]
			for i, keyword in enumerate(searchList):
				if keyword in parts:
					parts = partsList[i]
					break
		meaningItems = soup.find_all("span", class_="content-explanation ej")
		meaning = meaningItems[0].get_text(strip=True) if len(meaningItems) > 0 else ""
		meaning = re.sub(r"\([^)]*\)", "", meaning)
		meaning = meaning.split("、")[:Setting.meaning_limit]
		text = meaning[0] + "、"
		for item in meaning[1:Setting.meaning_limit]:
			if len(text + item) > Setting.meaning_chr_limit:
				break
			text += item + "、"
		return parts, text[:-1]

	def getExample(self) -> str:
		return ""

	def getSynonyms(self) -> str:
		url = f"https://www.thesaurus.com/browse/{self.word}"
		response = requests.get(url)
		html = response.text
		soup = BeautifulSoup(html, "html.parser")
		classList = ["Bf5RRqL5MiAp4gB8wAZa", "CPTwwN0qNO__USQgCKp8", "u7owlPWJz16NbHjXogfX"]
		# Class to check if synonyms exist -> "paaTrWKrgAb_hKTZ4zFV"
		items = []
		for className in classList:
			items += soup.find_all("a", class_=className)
		text = items[0].get_text(strip=True) + ", "
		for item in items[1:Setting.synonyms_limit]:
			synonym = item.get_text(strip=True)
			if len(text + synonym) > Setting.synonyms_chr_limit:
				break
			text += synonym + ", "
		return text[:-2]

def printDebug(index: int, word: str, contents: list):
	for i, n in enumerate(contents):
		contents[i] = n if n else "!Not found"
	print("-"*5)
	print(f"{index+Setting.start}: {word}")
	print(f"  meaning: [{contents[0]}] {contents[1]}")
	print(f"  example: {contents[2]}")
	print(f"  synonym: {contents[3]}")

class File:
	def __init__(self, wordsList: list[str]):
		self.wordsList = wordsList

	def saveToFile(self) -> list:
		os.makedirs("results", exist_ok=True)
		with open("results/synonyms.txt", "w", encoding="utf-8") as fileS, \
			  open("results/parts.txt",    "w", encoding="utf-8") as fileP, \
			  open("results/meanings.txt", "w", encoding="utf-8") as fileM, \
			  open("results/examples.txt", "w", encoding="utf-8") as fileE:

			errors = []
			for index, word in enumerate(self.wordsList):
				if word != "":
					scraping = Scraping(index, word)
					parts, meaning = scraping.getMeaning()
					example = scraping.getExample()
					synonym = scraping.getSynonyms()
					if not parts and not meaning and not example and not synonym:
						errors.append(f"  {index+Setting.start}: {word}")
				else:
					parts, meaning, example, synonym = "", "", "", ""
				if Setting.show_debug:
					printDebug(index, word, [parts, meaning, example, synonym])
				fileP.write(parts + "\n")
				fileM.write(meaning + "\n")
				fileE.write(example + "\n")
				fileS.write(synonym + "\n")
		return errors

def getWords() -> list:
	thirdColumn = []
	with open("words.csv", "r", encoding="utf-8") as fileW:
		reader = csv.reader(fileW)
		for row in reader:
			if len(row) > 3:
				word = (row[2]).strip().lower()
				thirdColumn.append(word)
	return thirdColumn[Setting.start:Setting.end+1]

def main():
	print("\nGetting words from your CSV file...")
	wordsList = getWords()
	requests_cache.install_cache("cache")
	print("\nStart Scraping...\nCollecting data...")
	file = File(wordsList)
	errors = file.saveToFile()
	print("\n" + "-"*20)
	print("4 files saved successfully!.\n\n")
	if errors:
		print("-"*10)
		print("Something seems wrong about these words. Did you spell them correctly?")
		print("\n".join(errors))
	# ======= debug =======
	# word = input(">>>")
	# scraping = Scraping(1, word)
	# parts, meaning = scraping.getMeaning()
	# example = scraping.getExample()
	# synonym = scraping.getSynonyms()
	# printDebug(1, word, [parts, meaning, example, synonym])

if __name__ == "__main__":
	main()
