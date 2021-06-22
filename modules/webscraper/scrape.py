import compareSchool as cs

DRIVER_PATH = "/usr/lib/chromium-browser/chromedriver"
CITY = "Burnaby"

def main():
	schools = cs.get_schools(CITY, DRIVER_PATH)
	print(*schools, sep="\n")

if __name__ == "__main__":
	main()