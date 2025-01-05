# declare the phony targets
.PHONY: clean dist

dist:
	@echo "Building binary in dist folder using pyinstaller"
	pyinstaller --name=streakdottxt streakdottxt.py

clean:
	@echo "Cleaning up the dist folder"
	rm -rf dist/