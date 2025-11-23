import os
import re
import csv
import requests
import requests_cache
from bs4 import BeautifulSoup

# =============== Setting ================
class Setting:
	start = 1
	end = 5
	mode = 1
# ========================================
	show_debug = True
	meaning_chr_limit = 10
	synonym_chr_limit = 20

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
		if not meaningItems:
			return parts, ""
		meaning = meaningItems[0].get_text(strip=True) if len(meaningItems) > 0 else ""
		meaning = re.sub(r"\(.*?\)|（.*?）", "", meaning)
		searchList =  ["(", "（", ")", "）", "；", "; ", "。"]
		replaceList = ["","", "", "", "、", "、", "、"]
		for search, item in zip(searchList, replaceList):
			meaning = meaning.replace(search, item)
		items = meaning.split("、")
		text = ""
		skip = [self.word, "三人称", "複数形", "過去形", "過去分詞", "または"]
		for i in range(len(items)):
			flag = False
			for skipWord in skip:
				if skipWord in items[i]:
					flag = True
					break
			if flag:
				continue
			text += items[i] + "、"
			if len(items)-1 > i:
				if len(text + items[i + 1]) > Setting.meaning_chr_limit:
					break
		return parts, text[:-1]

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
		if not items:
			return ""
		text = ""
		for i, item in enumerate(items):
			text += item.get_text(strip=True) + ", "
			if len(items)-1 > i:
				if len(text + items[i + 1].get_text(strip=True)) > Setting.synonym_chr_limit:
					break
		return text[:-2]

def printDebug(index: int, word: str, contents: list):
	for i, n in enumerate(contents):
		contents[i] = n if n else "!Not found"
	print("-"*5)
	print(f"{index+Setting.start}: {word}")
	print(f"  meaning: [{contents[0]}] {contents[1]}")
	print(f"  synonym: {contents[2]}")

class File:
	def __init__(self, wordsList: list[str]):
		self.wordsList = wordsList

	def saveToFile(self) -> list:
		os.makedirs("results", exist_ok=True)
		with open("results/synonyms.txt", "w", encoding="utf-8") as fileS, \
			  open("results/parts.txt",    "w", encoding="utf-8") as fileP, \
			  open("results/meanings.txt", "w", encoding="utf-8") as fileM:
			errors = []
			for index, word in enumerate(self.wordsList):
				if word != "":
					scraping = Scraping(index, word)
					parts, meaning = scraping.getMeaning()
					synonym = scraping.getSynonyms()
					if not parts and not meaning and not synonym:
						errors.append(f"  {index+Setting.start}: {word}")
				else:
					parts, meaning, synonym = "", "", ""
				if Setting.show_debug:
					printDebug(index, word, [parts, meaning, synonym])
				fileP.write(parts + "\n")
				fileM.write(meaning + "\n")
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
	if Setting.mode == 1:
		print("\nGetting words from your CSV file...")
		wordsList = getWords()
		requests_cache.install_cache("cache")
		print("\nStart Scraping...\nCollecting data...")
		file = File(wordsList)
		errors = file.saveToFile()
		print("\n" + "-"*20)
		print("3 files saved successfully!\n\n")
		if errors:
			print("-"*10)
			print("Something seems wrong about these words. Did you spell them correctly?")
			print("\n".join(errors))
	else:
		word = input(">>>")
		requests_cache.install_cache("cache")
		scraping = Scraping(1, word)
		parts, meaning = scraping.getMeaning()
		synonym = scraping.getSynonyms()
		printDebug(0, word, [parts, meaning, synonym])

if __name__ == "__main__":
	main()
