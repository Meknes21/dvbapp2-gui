SUBDIRS = skin_default spinner fonts extensions keymaps rc_models

dist_pkgdata_DATA = \
	encoding.conf \
	keymap.xml \
	menu.xml \
	black.mvi \
	rcpositions.xml \
	setup.xml \
	skin_subtitles.xml \
	startwizard.xml \
	userinterfacepositionerwizard.xml \
	freesat.t1 \
	freesat.t2 \
	unicable.xml \
	hd-testcard.mvi

if HAVE_TEXTLCD
SUBDIRS += displaytext
endif

if HAVE_COLORLCD
SUBDIRS += display96
endif

if HAVE_COLORLCD128
SUBDIRS += display128
endif

if HAVE_COLORLCD220
SUBDIRS += display220
endif

if HAVE_BWLCD255
SUBDIRS += display255
endif
