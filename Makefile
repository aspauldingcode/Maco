all:
	mkdir -p output
	clang -framework Cocoa -framework Foundation -framework AppKit -lsqlite3 -o output/Maco src/maco/Maco.m