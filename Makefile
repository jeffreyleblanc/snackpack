.PHONY: help install uninstall

APP=snackpack.py
INSTALL_PATH=/usr/local/bin/snackpack

.DEFAULT=help
help:
	@echo "install		Install as $(INSTALL_PATH)"
	@echo "uninstall	Removes $(INSTALL_PATH)"

install:
	sudo cp $(APP) $(INSTALL_PATH)
	sudo chmod 755 $(INSTALL_PATH)

uninstall:
	sudo rm -r $(INSTALL_PATH)


