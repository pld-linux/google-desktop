# TODO
# - stop bashism in extract_msoffice_content.sh, and make it secure with mktemp use
# - firefox plugin not firefox 3.x compatible
%define		buildid	0088
%define		rel		0.5
Summary:	Google Desktop: Personalize and organize your own computer
Name:		google-desktop
Version:	1.2.0
Release:	%{buildid}.%{rel}
License:	Copyright 2007 Google Inc. All Rights Reserved.
Group:		X11/Applications
%ifarch %{ix86}
Source0:	http://dl.google.com/linux/rpm/stable/i386/%{name}-linux-%{version}.%{buildid}.i386.rpm
# NoSource0-md5:	165d313c8592a007d7a0e42ca3af0dfb
NoSource:	0
%endif
%ifarch %{x8664}
Source1:	http://dl.google.com/linux/rpm/stable/x86_64/%{name}-linux-%{version}.%{buildid}.x86_64.rpm
# NoSource1-md5:	dac43d2ea9d4f1069a0bed0e754cffb1
NoSource:	1
%endif
URL:		http://desktop.google.com/linux/
Requires:	xdg-utils
ExclusiveArch:	%{ix86} %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_appdir		%{_libdir}/%{name}

%define		_enable_debug_packages	0
%define		no_install_post_strip	1

# sysdeps in lib dir
%define		sysdeps		libcurl.so libgcc_s.so.1 libgd.so libjpeg.so libjs.so libopenssl.so libplugins.so libpng12.so libsqlite.so libstdc++.so.6 libtag.so libuuid.so libz.so libzzip.so
# internal deps
%define		intdeps		libdesktop.so libgdl.so libgdl_firefox.so libgdl_thunderbird.so libbreakpad.so gdl_box

# list of script capabilities (regexps) not to be used in Provides
%define		_noautoprov		%{sysdeps}
# do not require them either
%define		_noautoreq		%{_noautoprov}

%description
Google Desktop is a desktop search application that gives you easy
access to information on your computer and from the web. Desktop makes
searching your own email, files, music, photos, and more as easy as
searching the web with Google.

%prep
%setup -qcT
%ifarch %{ix86}
SOURCE=%{S:0}
%endif
%ifarch %{x8664}
SOURCE=%{S:1}
%endif

V=$(rpm -qp --qf '%{V}' $SOURCE)
R=$(rpm -qp --qf '%{R}' $SOURCE)
if [ version:$V != version:%{version} -o buildid:$R != buildid:%{buildid} ]; then
	exit 1
fi
rpm2cpio $SOURCE | cpio -i -d

mv opt/google/desktop/* .
mv etc/cron.hourly .

sed -i -e 's,/opt/google/desktop,%{_appdir},' bin/{gdlinux,*.sh}
sed -i -e '
	s,/opt/google/desktop/bin/,,
	s,/opt/google/desktop,%{_appdir},
	s/Categories=.*/Categories=GTK;Network;/
' xdg/google-gdl.desktop

sed -i -e '
	s,/opt/google/desktop/bin/,,
	s,/opt/google/desktop,%{_appdir},
	s/Categories=.*/Categories=GTK;Settings;/
' xdg/google-gdl-preferences.desktop

# xdg-utils
rm bin/{xdg-open,xdg-desktop-menu}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_appdir},%{_bindir},%{_datadir}/autostart,%{_desktopdir},/etc/cron.daily,/var/cache/google/desktop}
cp -a xdg/google-gdl-preferences.desktop $RPM_BUILD_ROOT%{_desktopdir}
cp -a xdg/google-gdl.desktop $RPM_BUILD_ROOT%{_datadir}/autostart
cp -a resource plugin lib bin $RPM_BUILD_ROOT%{_appdir}
mv $RPM_BUILD_ROOT{%{_appdir}/bin,%{_bindir}}/gdlinux

%if 0
# XXX seems not needed
# path inside libraries which we cannot change
install -d $RPM_BUILD_ROOT/opt/google
ln -s %{_appdir} $RPM_BUILD_ROOT/opt/google/desktop
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%if 0
# TODO: see first what's the purpose, as it if it is related with browser
# plugin it is out of sync as browser plugin is installed in trigger
%post
# New installation.
if [ "$1" = "1" ]; then
	LD_LIBRARY_PATH=%{_appdir}/lib %{_appdir}/bin/gdl_stats install
elif [ "$1" -gt 1 ]; then
	LD_LIBRARY_PATH=%{_appdir}/lib %{_appdir}/bin/gdl_stats update
	killall -USR2 gdl_box 2> /dev/null || :
fi
%endif

%postun
# Delete repositories for all users when uninstall.
if [ "$1" = "0" ]; then
	if [ -d /var/cache/google/desktop ]; then
		for i in /var/cache/google/desktop/*; do
			# don't remove machine id file.
			if [ -d "$i" ]; then
				rm -rf "$i"
			fi
		done
	fi
fi

%triggerin -- mozilla-firefox-bin
if [ "$1" = "1" ] && [ "$2" = "1" ]; then
	ln -snf %{_appdir}/plugin/firefox %{_libdir}/mozilla-firefox-bin/extensions/desktop@google.com
fi

%triggerun -- mozilla-firefox-bin
# remove link if either of the packages are gone \
if [ "$1" = "0" ] || [ "$2" = "0" ]; then
	rm -f %{_libdir}/mozilla-firefox-bin/extensions/desktop@google.com
fi

%files
%defattr(644,root,root,755)
%doc README VERSION
%attr(755,root,root) %{_bindir}/gdlinux
%dir %{_appdir}
%dir %{_appdir}/bin
%dir %{_appdir}/lib
%dir %{_appdir}/plugin
%attr(755,root,root) %{_appdir}/bin/*
%attr(755,root,root) %{_appdir}/lib/*.so*
%{_appdir}/resource

%{_datadir}/autostart/*.desktop
%{_desktopdir}/*.desktop

%dir /var/cache/google
%dir %attr(2777,root,root) /var/cache/google/desktop

# subpackage for iceweasel
%dir %{_appdir}/plugin/firefox
%dir %{_appdir}/plugin/firefox/components
%{_appdir}/plugin/firefox/chrome.manifest
%attr(755,root,root) %{_appdir}/plugin/firefox/components/libdesktop.so
%{_appdir}/plugin/firefox/install.rdf

# subpackage for icedove
%dir %{_appdir}/plugin/thunderbird
%dir %{_appdir}/plugin/thunderbird/components
%{_appdir}/plugin/thunderbird/chrome.manifest
%attr(755,root,root) %{_appdir}/plugin/thunderbird/components/libdesktop.so
%{_appdir}/plugin/thunderbird/components/mozilla_mail_stub.js
%{_appdir}/plugin/thunderbird/components/mozilla_mail_stub.xpt
%{_appdir}/plugin/thunderbird/install.rdf
