import csv

class Setting:
	start = 1
	end = 300

def main():
	with open("words.csv", "r", encoding="utf-8") as fileW:
		reader = csv.reader(fileW)
		line = list(reader)
		errors = []
		for i, row in enumerate(line[Setting.start:Setting.end+1]):
			checkArea = row[2: 6]
			noBlank = [n.replace(" ", "").replace("\u3000", "") for n in checkArea]
			if not all(noBlank):
				position = ["[word]", "[parts]", "[meaning]", "[example]"]
				errorCell = [j for j, cell in enumerate(checkArea) if not cell]
				errors.append(f"{i+Setting.start}: {' '.join([position[j] for j in errorCell])}")
	if errors:
		print("\nErrors found:")
		for error in errors:
			print(error)
	else:
		print("No blank cells found.")

if __name__ == "__main__":
	main()
