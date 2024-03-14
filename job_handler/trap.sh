# BEGIN
set -o errtrace
trap 'catch $?' ERR
catch() {
echo "apptests caught an error:"
if [ "$1" != "0" ]; then
    echo "Error code $1. Terminating!"
    exit $1
fi
}

modules="ml"

for module in "$@"; do
modules+=" $module"
done
module purge .

eval "$modules"
# END