%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define module_name photoboard
%define _unpackaged_files_terminate_build 0

Name:           python-%{module_name}
Version:        0.1.0
Release:        1
Summary:        A decentralized group photo sharing app.

License:        ASLv2
URL:            https://github.com/teriyakichild/photoboard
Source0:        %{module_name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python-setuptools
Requires(pre): shadow-utils


%description

%pre
getent passwd photoboard >/dev/null || \
    useradd -r -d /opt/photoboard -s /sbin/nologin \
    -c "Useful comment about the purpose of this account" USERNAME
exit 0


%prep
%setup -q -n %{module_name}-%{version}


%build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --root $RPM_BUILD_ROOT
install -d -o photoboard -g photoboard photoboard/db /opt/photoboard/db

%files
%doc README.md LICENSE.md CHANGELOG INSTALL
%{python_sitelib}/%{module_name}/install_helper.py
%{python_sitelib}/*
%attr(0755,-,-) %{_bindir}/photoboard

%changelog
* Sat May 10 2014 Tony Rogers <tony@tonyrogers.me> - 0.1.0-1
- Initial spec
