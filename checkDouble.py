import csv

class Setting:
	start = 1
	end = 600
	encoding = "utf-8"
	wordsRow = 3

def main():
	thirdColumn = []
	with open("words.csv", "r", encoding=Setting.encoding) as fileW:
		reader = csv.reader(fileW)
		for row in reader:
			if len(row) > Setting.wordsRow:
				word = (row[Setting.wordsRow-1]).strip().lower()
				thirdColumn.append(word)
	thirdColumn = thirdColumn[Setting.start:Setting.end+1]
	dic = {}
	flg = False
	for i, word in enumerate(thirdColumn):
		wordLower = word.lower()
		if wordLower not in dic:
			dic[wordLower] = [1, [i+Setting.start]]
		else:
			dic[wordLower][0] += 1
			dic[wordLower][1].append(i+Setting.start)
			print(f"{word} : {dic[wordLower][1]}")
			flg = True

	if not flg:
		print("There are no duplicate words")

if __name__ == "__main__":
	main()
