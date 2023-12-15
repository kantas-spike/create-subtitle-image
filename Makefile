# ディレクトリ
DST_DIR=~/opt/create_subtitle_image-by-gimp
BIN_DIR=~/bin
PKG_BIN_DIR=${DST_DIR}/bin
LIB_DIR=${DST_DIR}/lib
CONFIG_DIR=${DST_DIR}/config

MAIN_SHELL=create-subtitle-image-by-gimp.sh
MAIN_SHELL_TEMPLATE=create-subtitle-image-by-gimp.sh.tmpl
INNER_SCRIPT=create-subtitle-image-by-gimp.py
LIB_FILES=my_settings.py my_srt.py subtitle_creator.py
CONFIG_FILES=default_settings.json

OUTPUT_DIRS=$(BIN_DIR) $(PKG_BIN_DIR) $(LIB_DIR) $(CONFIG_DIR)

.PHONY: make_dirs install clean reinstall
.PHONY: install_bin install_lib install_config

all: install

make_dirs:
	mkdir -p $(OUTPUT_DIRS)

$(MAIN_SHELL): $(MAIN_SHELL_TEMPLATE)
	cat $< | sed -e s:{@@SCRIPT_PATH@@}:$(LIB_DIR)/$(INNER_SCRIPT): | sed -e s:{@@LIB_PATH@@}:$(LIB_DIR): | sed -e s:{@@CONFIG_PATH@@}:$(CONFIG_DIR): > $@


install_bin: $(MAIN_SHELL)
	cp -p $< $(PKG_BIN_DIR)
	chmod u+x $(PKG_BIN_DIR)/${<F}
	ln -s $(PKG_BIN_DIR)/${<F} $(BIN_DIR)/${<F}

install_lib: $(INNER_SCRIPT) $(LIB_FILES)
	cp -p $^ $(LIB_DIR)

install_config: $(CONFIG_FILES)
	cp -p $^ $(CONFIG_DIR)

install: make_dirs install_config install_lib install_bin

clean: $(BIN_DIR)/$(MAIN_SHELL)
	rm $<
	rm -r ${DST_DIR}

reinstall: clean install

