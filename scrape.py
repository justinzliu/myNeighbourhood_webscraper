import compareSchool as cs

DRIVER_PATH = "/usr/lib/chromium-browser/chromedriver"
CITY = "Burnaby"

def main():
	cs.get_schools(CITY, DRIVER_PATH)

if __name__ == "__main__":
	main()