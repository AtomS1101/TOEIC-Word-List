import os
import re
import csv
import requests
import requests_cache
from bs4 import BeautifulSoup

# =============== Setting ================
class Setting:
	start = 1
	end = 100
	mode = 1
# ========================================
	wordRow = 3
	show_debug = True
	meaning_chr_limit = 10
	synonym_chr_limit = 20

def getSoup(url: str) -> BeautifulSoup:
	response = requests.get(url)
	html = response.text
	soup = BeautifulSoup(html, "html.parser")
	return soup

def formatMeaning(word: str, meaningTag) -> str:
	skip = [word, "三人称", "複数形", "過去形", "過去分詞", "または"]
	meaningText = meaningTag.get_text(strip=True) if len(meaningTag) > 0 else ""
	meaningText = re.sub(r"\(.*?\)|（.*?）", "", meaningText)
	searchList  = ["(", "（", ")", "）", "；", "; ", "。"]
	replaceList = ["", "", "", "", "、", "、", "、"]
	for search, item in zip(searchList, replaceList):
		meaningText = meaningText.replace(search, item)
	meaningList = meaningText.split("、")
	text = ""
	for i, meaning in enumerate(meaningList):
		if any(skipWord in meaning for skipWord in skip):
			continue
		text += meaning + "、"
		if i < len(meaningList)-1:
			if len(text + meaningList[i + 1]) > Setting.meaning_chr_limit:
				break
	return text[:-1]

def printDebug(index: int, word: str, contents: list):
	for i, n in enumerate(contents):
		contents[i] = n if n else "!Not found"
	print("-"*5)
	print(f"{index+Setting.start}: {word}")
	print(f"  meaning: [{contents[0]}] {contents[1]}")
	print(f"  synonym: {contents[2]}")

def getWords() -> list:
	thirdColumn = []
	with open("words.csv", "r", encoding="cp932") as fileW:
		reader = csv.reader(fileW)
		for row in reader:
			if len(row) > Setting.wordRow:
				word = (row[Setting.wordRow-1]).strip().lower()
				thirdColumn.append(word)
	return thirdColumn[Setting.start:Setting.end+1]

def checkUser() -> None:
	if Setting.end - Setting.start > 100:
		print("\nYou are about to scrape a large amount of data.\nAre you sure you want to continue?")
		response = input("(yes/no): ").lower()
		if response != "yes":
			print("Canceled")
			exit()

class Scraping:
	def __init__(self, index=0, word=""):
		self.index = index
		self._word = word
		self.synonymClass = ["Bf5RRqL5MiAp4gB8wAZa", "CPTwwN0qNO__USQgCKp8", "u7owlPWJz16NbHjXogfX", "word-chip synonym-antonym-word-chip similarity-100", "word-chip synonym-antonym-word-chip similarity-50", "word-chip synonym-antonym-word-chip similarity-10"]
		self.searchList = ["名", "動", "形", "副", "前", "接"]
		self.partsList = ["名詞", "動詞", "形容詞", "副詞", "前置詞", "接続詞"]

	@property
	def word(self):
		return self._word

	@word.setter
	def word(self, value):
		self._word = value

	def getMeaning(self) -> tuple:
		soup = getSoup(f"https://ejje.weblio.jp/content/{self._word}")
		if " " in self._word:
			parts = "フレーズ"
		else:
			partsTag = soup.find_all("div", class_="KnenjSub")
			parts = partsTag[0].get_text(strip=True) if len(partsTag) > 0 else ""
			for i, keyword in enumerate(self.searchList):
				if keyword in parts:
					parts = self.partsList[i]
					break
			else:
				parts = ""
		meaningTag = soup.find_all("span", class_="content-explanation ej")
		if not meaningTag:
			return parts, ""
		meaning = formatMeaning(self._word, meaningTag[0])
		return parts, meaning

	def getSynonyms(self) -> str:
		soup = getSoup(f"https://www.thesaurus.com/browse/{self._word}")
		synonymTag = []
		synonyms = []
		for className in self.synonymClass:
			synonymTag += soup.find_all("a", class_=className) # []+[]
		for item in synonymTag:
			synonyms.append(item.get_text(strip=True))
		if not synonyms:
			return ""
		text = ""
		for i, item in enumerate(synonyms):
			text += item + ", "
			if len(synonyms)-1 > i:
				if len(text + synonyms[i + 1]) > Setting.synonym_chr_limit:
					break
		return text[:-2]

class File:
	def __init__(self, wordsList: list[str]):
		self.wordsList = wordsList
		self._errors = []

	@property
	def errors(self):
		return self._errors

	def saveToFile(self):
		os.makedirs("results", exist_ok=True)
		with open("results/synonyms.txt", "w", encoding="utf-8") as fileS, \
			  open("results/parts.txt",    "w", encoding="utf-8") as fileP, \
			  open("results/meanings.txt", "w", encoding="utf-8") as fileM:
			scraping = Scraping()
			for index, word in enumerate(self.wordsList):
				scraping.word = word
				if word:
					parts, meaning = scraping.getMeaning()
					synonym = scraping.getSynonyms()
					if (not parts) and (not meaning) and (not synonym):
						self._errors.append(f"    {index+Setting.start}: {word}")
				else:
					parts, meaning, synonym = "", "", ""
				if Setting.show_debug:
					printDebug(index, word, [parts, meaning, synonym])
				fileP.write(parts + "\n")
				fileM.write(meaning + "\n")
				fileS.write(synonym + "\n")

def main():
	requests_cache.install_cache("cache")
	if Setting.mode == 1:
		checkUser()
		print("\nGetting words from your CSV file...")
		wordsList = getWords()
		print("\nStart Scraping...")
		file = File(wordsList)
		file.saveToFile()
		print("\n" + "-"*20)
		print("3 files saved successfully!\n\n")
		if file.errors:
			print("#"*30)
			print("  Something seems wrong about these words. Did you spell them correctly?")
			print("\n".join(file.errors) + "\n" + "#"*30 + "\n")
	else:
		word = input(">>>")
		scraping = Scraping()
		scraping.word = word
		parts, meaning = scraping.getMeaning()
		synonym = scraping.getSynonyms()
		printDebug(0, word, [parts, meaning, synonym])

if __name__ == "__main__":
	main()
