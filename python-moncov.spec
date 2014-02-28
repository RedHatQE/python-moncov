Name:		python-moncov
Version:	0.4
Release:	1%{?dist}
Summary:	Python code coverage using MongoDB

Group:		Development/Python
License:	GPLv3+
URL:		https://github.com/RedHatQE/python-moncov
Source0:	%{name}-%{version}.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildArch:      noarch

BuildRequires:	python-devel
Requires:	pymongo

%description
Python code coverage using MongoDB

%prep
%setup -q

%build

%install
%{__python} setup.py install -O1 --root $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT


%post
%if 0%{?fedora} >= 15
/bin/systemctl daemon-reload &> /dev/null ||:
%endif

%preun
%if 0%{?fedora} >= 15
/bin/systemctl --no-reload disable moncov.service
/bin/systemctl stop moncov.service
%endif

%postun
%if 0%{?fedora} >= 15
/bin/systemctl daemon-reload &> /dev/null
if [ "$1" -ge "1" ] ; then
   /bin/systemctl try-restart moncov.service &> /dev/null
fi
%endif

%files
%doc COPYING
%defattr(-,root,root,-)
%config(noreplace) %attr(0644, root, root) %{_sysconfdir}/moncov.yaml
%config(noreplace) %attr(0640, root, root) %{_unitdir}/moncov.service
%{python_sitelib}/*.egg-info
%{python_sitelib}/moncov
%{_bindir}/moncov.py

%changelog
* Wed Feb 26 2014 dparalen <vetrisko@gmail.com> 0.4-1
- Automatic commit of package [python-moncov] release [0.3-1].
  (vetrisko@gmail.com)
- Update README.md (vetrisko@gmail.com)

* Wed Feb 26 2014 dparalen <vetrisko@gmail.com> 0.3-1
- fix: import (vetrisko@gmail.com)
- fix: lazy eval (vetrisko@gmail.com)
- fix: disable collecting for this script to make it run faster
  (vetrisko@gmail.com)
- fix: missed the ctl import (vetrisko@gmail.com)
- introducing moncov ctl (vetrisko@gmail.com)
- introducing moncov.conf (vetrisko@gmail.com)
- introducing config (vetrisko@gmail.com)
- introducing black/white lists (vetrisko@gmail.com)
- enhancing output&separating sample code (vetrisko@gmail.com)
- fix: simplification (vetrisko@gmail.com)
- fix: counting (vetrisko@gmail.com)
- fix: removing not used query (vetrisko@gmail.com)
- Update README.md (vetrisko@gmail.com)
- introducing config file (vetrisko@gmail.com)
- introducing simple stats dumping (vetrisko@gmail.com)
- adding some more sample src (vetrisko@gmail.com)
- fix: default value issue (vetrisko@gmail.com)
- experimental PDA for cobertura--moncov processing (vetrisko@gmail.com)
- Update README.md (vetrisko@gmail.com)
- introducing moncov.service (vetrisko@gmail.com)
- fix vim swap files (vetrisko@gmail.com)
- some simplifications (vetrisko@gmail.com)
- fix: insert only doesn't work; dunno why... everything just stops working
  although records keep appearing... and error logs (vetrisko@gmail.com)
- schema change, unique index (vetrisko@gmail.com)
- add gplv3 license (vitty@redhat.com)
- move python_lib ignorance to regexp, add some more packages to ignore
  (vitty@redhat.com)
- write propper documents to mongo (vitty@redhat.com)
- implement ignore list (vitty@redhat.com)
- do not construct keys() (vitty@redhat.com)
- throw away _collectors (vitty@redhat.com)
- README.md (vitty@redhat.com)
- pth (vitty@redhat.com)
- __init__ (vitty@redhat.com)
- check for db (vitty@redhat.com)

* Mon Jan 14 2013 Vitaly Kuznetsov <vitty@redhat.com> 0.2-1
- new package built with tito

