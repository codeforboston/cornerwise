host_port=3000
vm_port_forwarding=1

function find_vm_name {
    echo $(docker-machine ls | awk '/virtualbox/ { print $1 }' | head -n 1)
}

function download_docker_toolbox {
    # Determine the latest version of Docker Toolbox and download it.
    release_tag=$(curl -s https://api.github.com/repos/docker/toolbox/releases/latest | grep "tag_name" | perl -n -e '/"tag_name": "v([^"]+)"/ && print $1')

    if [ -n "$release_tag" ]; then
        echo "Downloading latest version of Docker Toolbox ($release_tag)."
        open "https://github.com/docker/toolbox/releases/download/v$release_tag/DockerToolbox-$release_tag.pkg"
    else
        echo "Failed to determine the latest version of Docker Toolbox"
        open_browser "https://www.docker.com/toolbox"
    fi
}

while getopts ":F" opt; do
    case $opt in
        F)
            vm_port_forwarding=0
            ;;
    esac
done


if (! (which docker >/dev/null)); then
    # Docker is not installed
    echo "Docker is not installed."

    if [ $(uname) == "Darwin" ]; then
        download_docker_toolbox
        echo "Please re-run this script after you've installed Docker Toolbox."
    else
        open_browser "http://docs.docker.com/installation/"
        echo "Please re-run this script after you've installed Docker."
    fi

    exit 1
fi;

use_machine=0
# Using Docker-Machine?
if (which docker-machine >/dev/null); then
    use_machine=1

    if [ -z "$vm_name" ]; then
        vm_name=$(find_vm_name)
    fi

    if [ -z "$vm_name" ]; then
        vm_name=dev
        # Initialize, if necessary:
        docker-machine create -d virtualbox "$vm_name" >/dev/null
    fi

    machine_status=$(docker-machine status $vm_name)

    if [ "$machine_status" = "Timeout" ] ; then
        docker-machine restart $vm_name
    elif [ "$machine_status" != "Running" ]; then
        docker-machine start $vm_name
    fi;

    # Set up the environment variables so that the Docker client can
    # connect to the VM.
    eval $(docker-machine env $vm_name)

    # Forward the VM port to localhost
    if ((vm_port_forwarding)); then
        VBoxManage controlvm $vm_name natpf1 delete django
        # Only using VirtualBox... for now
        VBoxManage controlvm $vm_name natpf1 "django,tcp,127.0.0.1,$host_port,,$host_port"
    fi;
elif [ $(uname) == "Darwin" ]; then
    # In case the user installed Docker separately

    echo "You're running OS X, so you should install Docker Machine (part of Docker Toolbox)."
    download_docker_toolbox
    echo "Please re-run this script once you've installed Docker Toolbox."
    exit 1
fi

docker-compose up
