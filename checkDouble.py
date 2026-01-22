import csv

class Setting:
	start = 1
	end = 600

def main():
	thirdColumn = []
	with open("words.csv", "r", encoding="cp932") as fileW:
		reader = csv.reader(fileW)
		for row in reader:
			if len(row) > 3:
				word = (row[2]).strip().lower()
				thirdColumn.append(word)
	thirdColumn = thirdColumn[Setting.start:Setting.end+1]
	dic = {}
	flg = False
	for i, word in enumerate(thirdColumn):
		if word not in dic:
			dic[word] = 1
		else:
			dic[word] += 1
			print(f"{i+Setting.start}: {word}")
			flg = True

	if not flg:
		print("There are no duplicate words")

if __name__ == "__main__":
	main()
