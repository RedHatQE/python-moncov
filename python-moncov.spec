Name:		python-moncov
Version:	0.5.14
Release:	1%{?dist}
Summary:	Python code coverage using MongoDB

Group:		Development/Python
License:	GPLv3+
URL:		https://github.com/RedHatQE/python-moncov
Source0:	%{name}-%{version}.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildArch:      noarch

BuildRequires:	python-devel
Requires:	python-redis, hiredis, PyYAML, python-lxml, python-coverage

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
%{python_sitelib}/moncov/stats
%{_bindir}/moncov

%changelog
* Mon Jul 07 2014 dparalen <vetrisko@gmail.com> 0.5.14-1
- fix: missing coverage.py dependency (vetrisko@gmail.com)
- updating readme (vetrisko@gmail.com)
- fix: black-listing test cases FIXME: port to redis (vetrisko@gmail.com)
- update to redis datastore (vetrisko@gmail.com)
- fix: tracing context manager now expects redis datastore (vetrisko@gmail.com)
- fix: data compatibility (vetrisko@gmail.com)
- fix: version-dependant args handling (vetrisko@gmail.com)
- introducing coveragepy deps (vetrisko@gmail.com)
- introducing coveragepy stats (vetrisko@gmail.com)
- fix: filtering (vetrisko@gmail.com)
- introducing a redis-based version (vetrisko@gmail.com)
- fix: leaking commits (vetrisko@gmail.com)
- new xml tests (igulina@redhat.com)
- removing trailing whitespaces (igulina@redhat.com)
- xml test (igulina@redhat.com)

* Tue May 06 2014 dparalen <vetrisko@gmail.com> 0.5.13-1
- fix: covered/valid values (vetrisko@gmail.com)
- fix/enhance: sometimes no process/thread happened to set any pivot at all;
  the result would have been no lines collected; should fix issue#1, too
  (vetrisko@gmail.com)
- fix conditions in xml (igulina@redhat.com)
- introducing line_rate tests (igulina@redhat.com)

* Mon Apr 28 2014 dparalen <vetrisko@gmail.com> 0.5.12-1
- fix: changed connection- to client-based communication+caching
  (vetrisko@gmail.com)

* Fri Apr 25 2014 dparalen <vetrisko@gmail.com> 0.5.11-1
- Update README.md (vetrisko@gmail.com)
- fix: no stats handling (vetrisko@gmail.com)
- fix: error display (vetrisko@gmail.com)

* Wed Apr 23 2014 dparalen <vetrisko@gmail.com> 0.5.10-1
- 

* Fri Apr 18 2014 dparalen <vetrisko@gmail.com> 0.5.9-1
- Update README.md (vetrisko@gmail.com)
- introducing simple xml output (vetrisko@gmail.com)
- introducing custom str (vetrisko@gmail.com)
- introducing nesting branch--non-branch code (vetrisko@gmail.com)
- removing trailing whitespaces (vetrisko@gmail.com)
- test cases branch_rate (igulina@redhat.com)

* Mon Apr 14 2014 dparalen <vetrisko@gmail.com> 0.5.8-1
- fix issue#7 (vetrisko@gmail.com)
- add weird test cases for while false (igulina@redhat.com)

* Mon Apr 14 2014 dparalen <vetrisko@gmail.com> 0.5.7-1
- fix accidently del lines (igulina@redhat.com)
- add while and for in xml (igulina@redhat.com)
- add while and for in parser (igulina@redhat.com)
- deleted print (igulina@redhat.com)
- fix xml for class lines (igulina@redhat.com)
- introducing few more branch rate test cases (vetrisko@gmail.com)
- introducing function call tests (vetrisko@gmail.com)
- introducing branch rate tests (vetrisko@gmail.com)
- fix pyfilename whitelist and introduce a generic moncov test class
  (vetrisko@gmail.com)
- housekeeping---moving Rate to a custom module (vetrisko@gmail.com)
- cleanup (vetrisko@gmail.com)
- fix: debug print (vetrisko@gmail.com)
- fix: remove debug print (vetrisko@gmail.com)
- a facepalm-moment fix (vetrisko@gmail.com)
- fix xml generation (igulina@redhat.com)
- Update README.md (vetrisko@gmail.com)
- introducing default events_count value (vetrisko@gmail.com)
- fix: division by zero in case no branches excercised (vetrisko@gmail.com)
- fix: avoid counting test, iter and target fields lines (vetrisko@gmail.com)
- fix black/white-list propagation (vetrisko@gmail.com)
- fix black/white-list propagation (vetrisko@gmail.com)
- introducing test tools.py module (vetrisko@gmail.com)
- moving tools to tools.py module (vetrisko@gmail.com)
- introducing For and While branch rates (vetrisko@gmail.com)
- introducing and fixing test cases (vetrisko@gmail.com)
- treat hits as set (vetrisko@gmail.com)
- enhanced debugging messages (vetrisko@gmail.com)
- fix branch-rate calculation (igulina@redhat.com)
- fix branch-rate calculation (igulina@redhat.com)
- fix issue#1 issue#3 (vetrisko@gmail.com)
- fixing line-rate calculation (igulina@redhat.com)
- Test cases for line-rate (igulina@redhat.com)
- Test cases for branch-rate (igulina@redhat.com)
- split stats gathering and printing (vetrisko@gmail.com)
- avoid stack dumps on None (vetrisko@gmail.com)
- fix recursion entry point (vetrisko@gmail.com)
- trying with setup.py install (vetrisko@gmail.com)
- fix missing lxml dependency (vetrisko@gmail.com)
- make pip run in sudo (vetrisko@gmail.com)
- introducing travis config (vetrisko@gmail.com)
- Automatic commit of package [python-moncov] release [0.5.6-1].
  (mkovacik@localhost.localdomain)
- introducing branch rates (vetrisko@gmail.com)
- ctl init returns used db object (vetrisko@gmail.com)
- fix wrong default attr values (vetrisko@gmail.com)

* Sat Mar 15 2014 Unknown name 0.5.6-1
- Update README.md (vetrisko@gmail.com)
- fix: adopting the key shape change (vetrisko@gmail.com)
- fix: logging (vetrisko@gmail.com)
- introducing an updater daemon (vetrisko@gmail.com)
- merging drop&init into reset (vetrisko@gmail.com)
- introducing race test cases (vetrisko@gmail.com)
- introducing config parameters (vetrisko@gmail.com)
- result info logging (vetrisko@gmail.com)
- introducing get_dbdetails (vetrisko@gmail.com)
- introducing basic test cases (vetrisko@gmail.com)
- fix requires explicit init call (vetrisko@gmail.com)
- fix: disabling disabling (vetrisko@gmail.com)
- enable in medias res counting (vetrisko@gmail.com)
- moving initialization code (vetrisko@gmail.com)
- return the collector object (vetrisko@gmail.com)
- logging (vetrisko@gmail.com)
- fixes (vetrisko@gmail.com)
- fix import error (vetrisko@gmail.com)
- fix call signature (vetrisko@gmail.com)
- new call interface (vetrisko@gmail.com)
- introducing explicit db inint (vetrisko@gmail.com)
- fix: count the calls, too (vetrisko@gmail.com)
- fix: exit when there's nothing to count (vetrisko@gmail.com)
- allow custom collecting properties (vetrisko@gmail.com)
- allow custom collecting properties (vetrisko@gmail.com)
- fix comment (vetrisko@gmail.com)
- fix: order inversion issue (vetrisko@gmail.com)
- Update README.md (vetrisko@gmail.com)
- fix race in between find last event and update last event record
  (vetrisko@gmail.com)
- fix race in between find last event and update last event record
  (vetrisko@gmail.com)
- Fix: concurrent counting (vetrisko@gmail.com)
- fix: create collection function name (vetrisko@gmail.com)
- fix: off-by-one (vetrisko@gmail.com)
- fix missing update module import and ctl call (vetrisko@gmail.com)
- fix: exception message display (vetrisko@gmail.com)
- introducing hits counting (vetrisko@gmail.com)
- introducing hit-counts (vetrisko@gmail.com)

* Wed Mar 12 2014 dparalen <vetrisko@gmail.com> 0.5.5-1
- introducing cobertura moncov output (igulina@redhat.com)
- Introducing output filename (igulina@redhat.com)
- Fixed package name and hits counts (igulina@redhat.com)
- Introducing cobertura xml (igulina@redhat.com)

* Wed Mar 05 2014 dparalen <vetrisko@gmail.com> 0.5.4-1
- fix requires (vetrisko@gmail.com)
- fix: longer timeout (vetrisko@gmail.com)
- got rid of cement (vetrisko@gmail.com)
- fix missing PyYAML dependency (vetrisko@gmail.com)
- got rid of cement (vetrisko@gmail.com)
- reimplemented using aaargh (vetrisko@gmail.com)
- Automatic commit of package [python-moncov] release [0.5.3-1].
  (vetrisko@gmail.com)
- fix: provides (vetrisko@gmail.com)
- Update README.md (vetrisko@gmail.com)

* Tue Mar 04 2014 dparalen <vetrisko@gmail.com> 0.5.3-1
- fix: provides (vetrisko@gmail.com)

* Tue Mar 04 2014 dparalen <vetrisko@gmail.com> 0.5.2-1
- Fix: setup/deployment (vetrisko@gmail.com)

* Tue Mar 04 2014 dparalen <vetrisko@gmail.com> 0.5.1-1
- introducing three-digit versions (vetrisko@gmail.com)
- introducing manifests (vetrisko@gmail.com)
- fix: PyYAML dependency; put 'remote' in the description (vetrisko@gmail.com)
- introducing IF statement parsing for future branch coverage reference
  (vetrisko@gmail.com)

* Fri Feb 28 2014 dparalen <vetrisko@gmail.com> 0.5-1
- Update README.md (vetrisko@gmail.com)
- simple stats command (vetrisko@gmail.com)
- fix: arg (vetrisko@gmail.com)
- fix import (vetrisko@gmail.com)
- fix expression (vetrisko@gmail.com)
- introducing simple stats (vetrisko@gmail.com)
- Fixing the pattern args (vetrisko@gmail.com)
- introducing custom filter lists (vetrisko@gmail.com)
- fix missing import (vetrisko@gmail.com)
- fix params (vetrisko@gmail.com)
- allow non-regexp params (vetrisko@gmail.com)
- added fixme (vetrisko@gmail.com)
- fix: dropping (vetrisko@gmail.com)
- fix: avoid self-collecting (vetrisko@gmail.com)
- fix: cement requires /home/mkovacik (vetrisko@gmail.com)
- introduce the moncov tool (vetrisko@gmail.com)
- fix name (vetrisko@gmail.com)
- Fix: naming (vetrisko@gmail.com)
- fix missing sha-bang (vetrisko@gmail.com)
- fix: missing moncov.py (vetrisko@gmail.com)
- fix: moncov.py (vetrisko@gmail.com)
- introducing moncov tool (vetrisko@gmail.com)
- display node names (vetrisko@gmail.com)

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

