#!/bin/bash
host_port=3000
project_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
docker_opts=""

# Don't hardcode the image name. We want to be able to change our
# project name every week. Iterate!
# This should not contain any spaces.
image_name="cornerwise"

# space-delimited list of environment variables, to be set in the container
docker_environment="APP_PORT=$host_port APP_NAME=$image_name"

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
  -b      Force Docker to build a new image, even if one exists
  -B      Ignore changes to dependencies when determining whether
          to build a new image. Only build if there is no
          existing image
  -c      Clean up old containers (those where status =~ /Exited/)
  -F      Prevents the script's default behavior of setting up the
          VM to forward traffic on the host port to localhost.
  -m <name> Specify a docker-machine machine to use
  -O      Do not automatically open the Django application in
          browser.
  -p <port> Run on a port other than $host_port
  -r      Force Docker to run a new container, rather than
          attach to one that is already running
  -x      If a running container is found, stop it
"
}

# Indicates whether the image should be rebuild:
should_build=0
# If true, do not attach to a running container (if applicable):
FORCE_RUN=0
vm_port_forwarding=1
open_in_browser=1
# How long should the script wait for the application to launch?
open_timeout=30
IGNORE_CHANGES=0
AUTOSTART=0
STOP_RUNNING=0
skip_build_prompt=0

while getopts ":bBcFmOprSthx" opt; do
    case $opt in
        b)
            should_build=1
            skip_build_prompt=1
            ;;
        B)
            IGNORE_CHANGES=1
            skip_build_prompt=1
            ;;
        b)
            cleanup_old=1
            ;;
        r)
            FORCE_RUN=1
            ;;
        S)
            AUTOSTART=0
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
            check_re='^[0-9]{4,}$'
            if ! [[ $OPTARG =~ $check_re ]]; then
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
            STOP_RUNNING=1
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

if [ -z "$RUN_COMMAND" ]; then
    if [ -n "$1" ]; then
        RUN_COMMAND="$*"
    else
        RUN_COMMAND=/bin/bash
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

if ((cleanup_old)); then
    echo "Are you sure you want to permanently delete all exited $image_name containers? (y/N)"
    read response
fi

if ((!IGNORE_CHANGES)); then
    # Determine if the image should be rebuilt.

    # Some jiggery-pokery to determine the date that the existing
    # cornerwise image was created.
    image_created=$(docker inspect $image_name | grep "Created" | perl -n -e'/"Created": "(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)\.\d+Z"/ && print $1')
    NO_EXISTING=$?

    if ((!$should_build)); then
        should_build=1

        if [ -n "$image_created" ]; then
            echo "Found existing $image_name image (created: $image_created)"
            should_build=0

            if ((!skip_build_prompt)); then
                # Convert edit date to a timestamp
                CREATED_STAMP=$(date -j -f "%Y-%m-%dT%H:%M:%S" "$image_created" "+%s")
                DOCKERFILE_MODIFIED=$(stat -f %m $project_dir/Dockerfile)
                changed_file=""

                if [ $DOCKERFILE_MODIFIED -gt $CREATED_STAMP ]; then
                    changed_file="Dockerfile"

                else
                    for path in $project_dir/docker-support/*; do
                        if [ $(stat -f %m $path) -gt $CREATED_STAMP ]; then
                            changed_file="$path"

                            break
                        fi
                    done
                fi

                if [ -n "$changed_file" ]; then
                    echo "$changed_file has changed since the image was created."

                    echo "Rebuild $image_name image? (y/N)"
                    read -t 10 response
                    if ((response)); then
                        # Request timed out
                        should_build=0
                    else
                        if [[ "$response" =~ ^[yY] ]]; then
                            should_build=1
                        else
                            should_build=0
                        fi

                    fi
                fi
            fi
        fi
    fi
fi

if ((should_build)); then
    echo "Building $image_name image. This may take a few moments."
    docker build -t $image_name $project_dir
fi;

if ((!FORCE_RUN || STOP_RUNNING)); then
    # Determine if the container is already running:
    CONTAINER_ID=$(docker ps | awk "/$image_name/ { if (match(\$2, /^$image_name/)) print \$1 }" | head -n 1)
else
    CONTAINER_ID=""
fi;

if [ -n "$CONTAINER_ID" ]; then
    if ((STOP_RUNNING)); then
        echo "Stopping container: $CONTAINER_ID"
        docker stop $CONTAINER_ID
        CONTAINER_ID=""
    else
        echo "There's a $image_name container already running with id $CONTAINER_ID."
        echo "If you want to start a new container, re-run ${BASH_SOURCE[0]} -r."
    fi
fi

if [ -n "$CONTAINER_ID" ]; then
    # Found a container. Attach to it:
    echo "Attaching to running container ($CONTAINER_ID)."
    docker exec -it $CONTAINER_ID $RUN_COMMAND
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

    docker_opts="$docker_opts -it -v $project_dir/server:/app -v $project_dir/client:/client -v $project_dir/data:/data -p $host_port:$host_port $env_opts -e APP_DAEMONIZED=1 $image_name"

    if ((! AUTOSTART)); then
        docker run $docker_opts $RUN_COMMAND
    else
        # Start the server:
        CONTAINER_ID=$(docker run -d $docker_opts /app/start.sh)
        echo "Container started with id $CONTAINER_ID."

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
        docker exec -it $CONTAINER_ID $RUN_COMMAND
    fi
fi;

if [ $? -eq 1 ]; then
    # TODO: Is it possible to distinguish between a failure to start the
    # container and a timeout? Both apparently return exit code 1.
    exit
fi;
