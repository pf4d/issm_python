name = mismip

all: presentation

final: presentation_final

clean: 
	rm texput.log $(name).aux $(name).bbl $(name).bcf $(name).blg $(name).idx $(name).ilg $(name).ind $(name).loa $(name).lof $(name).log $(name).lot $(name).out $(name).pdf $(name).run.xml $(name).toc $(name)-blx.bib $(name).nav $(name).snm

presentation:
	sh ./build.sh $(name) 

presentation_final:
	sh ./build.sh $(name) --final

