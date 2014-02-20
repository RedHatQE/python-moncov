Name:		python-moncov
Version:	0.2
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

%changelog
* Mon Jan 14 2013 Vitaly Kuznetsov <vitty@redhat.com> 0.2-1
- new package built with tito

