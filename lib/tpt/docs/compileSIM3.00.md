# Compilation SIM (v3.00)

## For Ubuntu
1.Install dependencies:
```
sudo apt-get install flex zip
```

2.Comment Windows lines (put "#" before each line):
```
################################################################
# For MSDOS + MinGW

#SYSTEM =	MSDOS
#SUBSYSTEM =	MinGW

# Locations
#DIR =		C:/BIN
#BINDIR =	C:/BIN
#MAN1DIR =	C:/BIN

# Commands (cp required, since xcopy cannot handle forward slashes)
#COPY =		cp -p
#EXE =		.exe
#LEX =		flex
#LN =		ln
#ZIP =		zip -o

################################################################
```

3.Check if Linux parameters are correct. In Ubuntu case, this is the configuration:
```
################################################################
# For UNIX-like systems

SYSTEM =	UNIX
SUBSYSTEM =	SOLARIS

# Locations
#DIR =		/home/dick
DIR =		/usr
#BINDIR =	$(DIR)/bin.`$(DIR)/bin/arch`
BINDIR =	$(DIR)/bin
#MAN1DIR =	$(DIR)/man/man1
MAN1DIR =	$(DIR)/local/share/man/man1

# Commands
COPY =		cp -p
EXE =		#
LEX =		flex
LN =		ln
ZIP =		zip -o

################################################################
```

4.Execute make:
```
sudo make binaries
```

5.Copy binaries to correct system operative folder:
```
   tpt/lib/sim/linux|osx|win32
```

Also update README and LICENSE.txt file

6.Update VERSION file with correct SIM version
```
   tpt/lib/sim/VERSION
```

7.Execute unit tests to check if everything is working with this update:
```
    python -m pytest tpt
```

or 

```
   pytest tpt
```

8.Enjoy
