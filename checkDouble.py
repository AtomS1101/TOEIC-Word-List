import csv

class Setting:
	start = 1
	end = 300

def main():
	thirdColumn = []
	with open("words.csv", "r", encoding="utf-8") as fileW:
		reader = csv.reader(fileW)
		for row in reader:
			if len(row) > 3:
				word = (row[2]).strip().lower()
				thirdColumn.append(word)
	thirdColumn = thirdColumn[Setting.start:Setting.end+1]
	dic = {}
	for word in thirdColumn:
		if word not in dic:
			dic[word] = 1
		else:
			dic[word] += 1
			print(word)


if __name__ == "__main__":
	main()
