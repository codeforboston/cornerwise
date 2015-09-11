#!/bin/bash
host_port=3000
project_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
docker_opts=""

# Don't hardcode the image name. We want to be able to change our
# project name every week. Iterate!
# This should not contain any spaces.
image_name="bdsand/cornerwise"

# space-delimited list of environment variables, to be set in the container
docker_environment="APP_PORT=$host_port APP_NAME=$(basename image_name)"

# Optionally specify a file containing environment settings
env_file=$project_dir/docker-support/env

function find_vm_name {
    echo $(docker-machine ls | awk '/virtualbox/ { print $1 }' | head -n 1)
}

function open_browser {
    if ( which xdg-open >/dev/null ); then
        xdg-open $1
    elif ( which open >/dev/null ); then
        open $1
    fi;
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

function print_help {
    echo "
Usage: ${BASH_SOURCE[0]} [options] [command]

Quickly build and launch the $image_name container. If a command is
specified, run that command in the container and exit.

Options:
  -F      Prevents the script's default behavior of setting up the
          VM to forward traffic on the host port to localhost.
  -m <name> Specify a docker-machine machine to use
  -O      Do not automatically open the Django application in
          browser.
  -p <port> Run on a port other than $host_port
  -r      Force Docker to run a new container, rather than
          attach to one that is already running
  -R      Do NOT remove the container after it has exited
  -x      If a running container is found, stop it
"
}

if [ -z "$image_name" ]; then
    image_name=$(basename $(git rev-parse --show-toplevel))
fi

# Indicates whether the image should be rebuild:
should_build=0
# If true, do not attach to a running container (if applicable):
force_run=0
vm_port_forwarding=1
open_in_browser=1
# How long should the script wait for the application to launch?
open_timeout=30
# Do not rebuild the image if support files have changed
ignore_changes=0
autostart=0
# If a running container is found, should we stop it?
stop_running=0
skip_build_prompt=0
remove_after=1

while getopts ":bBFm:Op:rRSthx" opt; do
    case $opt in
        b)
            should_build=1
            skip_build_prompt=1
            ;;
        B)
            ignore_changes=1
            skip_build_prompt=1
            ;;
        r)
            force_run=1
            ;;
        R)
            remove_after=0
            ;;
        S)
            autostart=0
            ;;
        F)
            vm_port_forwarding=0
            ;;
        m)
            vm_name="$OPTARG"
            ;;
        O)
            open_in_browser=0
            ;;
        p)
            if ! [[ $OPTARG =~ ^[0-9]{4,}$ ]]; then
                echo "Port must be an integer >=1000."
                exit 1
            fi
            host_port=$OPTARG
            ;;
        t)
            if ! [[ $OPTARG =~ ^[0-9]+$ ]]; then
                echo "Invalid timeout argument: $OPTARG"
                exit 1
            fi
            open_timeout=$OPTARG
            ;;
        x)
            stop_running=1
            ;;
        h)
            print_help
            exit 1
            ;;

        \?)
            echo "Unrecognized flag: -$OPTARG" >&2
            exit 1
            ;;
    esac
done

shift $((OPTIND-1))

if [ -z "$run_command" ]; then
    if [ -n "$1" ]; then
        run_command="$*"
    else
        run_command=/bin/bash
    fi
fi

##################

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

    if [ $(docker-machine status $vm_name) != "Running" ] ; then
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

#
docker pull $image_name


if ((!force_run || stop_running)); then
    # Determine if the container is already running:
    image_name_esc=$(echo "$image_name" | sed -n 's/\([\/.?]\)/\\\1/pg')
    container_id=$(docker ps | awk "/$image_name_esc/ { if (match(\$2, /^$image_name_esc/)) print \$1 }" | head -n 1)
else
    container_id=""
fi;

if [ -n "$container_id" ]; then
    if ((stop_running)); then
        echo "Stopping container: $container_id"
        docker stop $container_id
        container_id=""
    else
        echo "There's a $image_name container already running with id $container_id."
        echo "If you want to start a new container, re-run ${BASH_SOURCE[0]} -r."
    fi
fi

if [ -n "$container_id" ]; then
    # Found a container. Attach to it:
    echo "Attaching to running container ($container_id)."
    docker exec -it $container_id $run_command
else
    echo "Starting container..."

    env_opts=""
    # Build the environment options:
    for setting in $docker_environment; do
        env_opts="$env_opts -e $setting"
    done

    if [ -f $env_file ]; then
        env_opts="$env_opts --env-file=$env_file"
    fi

    if ((remove_after)); then
        docker_opts="$docker_opts --rm"
    fi

    docker_opts="$docker_opts -it -v $project_dir/server:/app -v $project_dir/client:/client -v $project_dir/data:/data -v $project_dir/docker-runtime:/scripts -p $host_port:$host_port $env_opts -e APP_DAEMONIZED=1 $image_name"

    if ((!autostart)); then
        docker run $docker_opts $run_command
    else
        # Start the server:
        container_id=$(docker run -d $docker_opts /app/start.sh)
        echo "Container started with id $container_id."

        if ((open_in_browser)); then
            ps_count=0
            wait_time=$open_timeout
            while ((ps_count==0)); do
                if ((wait_count <= 0)); then
                    break
                fi

                sleep 2
                wait_count -= 2
                ps_count=$((docker ps | grep runserver | wc -l))
            done

            if ((ps_count > 0)); then
                # The server is running in the container.
                if ((vm_port_forwarding || !use_machine)); then
                    vm_host="localhost"
                else
                    vm_host=$(docker-machine ip "$vm_name")
                fi
                open_browser "http://$vm_host:$host_port/index.html"
            fi
        fi

        # Attach to the container, and we're done
        docker exec -it $container_id $run_command
    fi
fi;

if [ $? -eq 1 ]; then
    # TODO: Is it possible to distinguish between a failure to start the
    # container and a timeout? Both apparently return exit code 1.
    exit
fi;
