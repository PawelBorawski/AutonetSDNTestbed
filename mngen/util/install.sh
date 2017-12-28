#!/bin/bash

MNGEN_DIR=$(pwd)
MININET_DIR=/opt/mininet

main() {
	while [ "$1" != "" ]; do
    	PARAM=`echo $1 | awk -F= '{print $1}'`
    	case $PARAM in
        -c| --clean)
            clean
	    ;;
        *)
            echo "ERROR: unknown parameter \"$PARAM\""
            usage
            exit 1
            ;;
        esac
        shift
	done

	install_mngen;
}

clean() {
	echo 'Cleaning up Mininet..'
	sudo rm -rf $MININET_DIR /usr/local/bin/mn /usr/local/bin/mnexec /usr/local/lib/python*/*/*mininet* /usr/local/bin/ovs-* /usr/local/sbin/ovs-*
}

install_mngen() {
	install_mininet;
	install_iperf;
	install_python_dependencies;
}

install_mininet() {
	echo 'Installing Mininet 2.2.1'
	sudo git clone git://github.com/mininet/mininet -b 2.2.1 $MININET_DIR
	cd $MININET_DIR
	util/install.sh -nfv
	echo 'Mininet has been installed'
}

install_iperf() {
    sudo apt-get install iperf
}

install_python_dependencies() {
	sudo pip install -r $MNGEN_DIR/requirements.txt
	echo 'Python dependencies installed.'
}

main "$@"
