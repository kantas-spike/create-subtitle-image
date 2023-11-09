DST_DIR=~/opt/create_subtitle_image
BIN_DIR=~/bin

install: ./create-subtitle-image.sh ./create-subtitle-image.py
	mkdir -p ${DST_DIR}
	mkdir -p ${DST_DIR}/bin
	mkdir -p ${BIN_DIR}
	cp -p $^ ${DST_DIR}/bin
	chmod u+x ${DST_DIR}/bin/${<F}
	ln -s ${DST_DIR}/bin/${<F} ${BIN_DIR}/${<F}

clean:
	rm ${BIN_DIR}/create-subtitle-image.sh
	rm -r ${DST_DIR}

reinstall:
	make clean
	make install
